from __future__ import annotations

import re
import shlex
import threading
import time
from dataclasses import dataclass

import paramiko

from temporal.core.models import OdasStreamConfig, RemoteOdasConfig


@dataclass(slots=True)
class CommandResult:
    code: int
    stdout: str
    stderr: str


@dataclass(slots=True)
class _PreflightRuntime:
    home_dir: str
    working_dir: str
    resolved_command: str


class _ControlShellLost(RuntimeError):
    def __init__(self, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.retryable = retryable


def _strip_cfg_comments(text: str) -> str:
    cleaned_lines: list[str] = []
    for raw_line in text.splitlines():
        chars: list[str] = []
        in_quotes = False
        escaped = False
        for char in raw_line:
            if escaped:
                chars.append(char)
                escaped = False
                continue
            if char == "\\":
                chars.append(char)
                escaped = True
                continue
            if char == '"':
                chars.append(char)
                in_quotes = not in_quotes
                continue
            if char == "#" and not in_quotes:
                break
            chars.append(char)
        cleaned_lines.append("".join(chars))
    return "\n".join(cleaned_lines)


def _extract_braced_body(text: str, brace_index: int) -> str | None:
    depth = 0
    in_quotes = False
    escaped = False
    for index in range(brace_index, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_quotes = not in_quotes
            continue
        if in_quotes:
            continue
        if char == "{":
            depth += 1
            continue
        if char == "}":
            depth -= 1
            if depth == 0:
                return text[brace_index + 1 : index]
    return None


def _extract_cfg_block_body(cfg_text: str, name: str) -> str | None:
    pattern = re.compile(rf"\b{re.escape(name)}\b\s*[:=]\s*\{{")
    match = pattern.search(cfg_text)
    if match is None:
        return None
    brace_index = cfg_text.find("{", match.start())
    if brace_index < 0:
        return None
    return _extract_braced_body(cfg_text, brace_index)


def _extract_cfg_string(body: str, *keys: str) -> str | None:
    for key in keys:
        match = re.search(rf'\b{re.escape(key)}\s*=\s*"([^"]+)"', body)
        if match is not None:
            return match.group(1).strip()
    return None


def _extract_cfg_port(body: str) -> int | None:
    match = re.search(r"\bport\s*=\s*(\d+)", body)
    if match is None:
        return None
    return int(match.group(1))


def _extract_wrapper_cfg_path(wrapper_text: str) -> str | None:
    match = re.search(
        r"""(?x)
        (?:^|\s)
        (?:-c|--config|--cfg)
        (?:\s+|=)
        (?P<path>"[^"]+"|'[^']+'|[^\s"'#;]+)
        """,
        wrapper_text,
    )
    if match is None:
        return None
    token = match.group("path").strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in {'"', "'"}:
        return token[1:-1]
    return token


def _resolve_home_relative_path(path_input: str, home_dir: str) -> str:
    if path_input.startswith("/"):
        return path_input
    if path_input == "~":
        return home_dir
    if path_input.startswith("~/"):
        return f"{home_dir}/{path_input[2:]}"
    return f"{home_dir}/{path_input}"


def _resolve_cfg_path(raw_cfg_path: str, runtime: _PreflightRuntime) -> str:
    if raw_cfg_path.startswith("/"):
        return raw_cfg_path
    if raw_cfg_path == "~" or raw_cfg_path.startswith("~/"):
        return _resolve_home_relative_path(raw_cfg_path, runtime.home_dir)
    return f"{runtime.working_dir}/{raw_cfg_path}"


def _sink_targets_match(cfg_text: str, streams: OdasStreamConfig) -> str | None:
    cleaned_cfg = _strip_cfg_comments(cfg_text)
    validate_host = streams.sst.host not in {"", "0.0.0.0", "::"}
    sink_specs = (
        ("tracked", "tracked", streams.sst.host, streams.sst.port),
        ("potential", "potential", streams.ssl.host, streams.ssl.port),
        ("separated", "separated", streams.sss_sep.host, streams.sss_sep.port),
        ("postfiltered", "postfiltered", streams.sss_pf.host, streams.sss_pf.port),
    )
    for sink_name, label, expected_host, expected_port in sink_specs:
        body = _extract_cfg_block_body(cleaned_cfg, sink_name)
        if body is None:
            return f"preflight: {label} sink missing"
        interface_body = _extract_cfg_block_body(body, "interface")
        if interface_body is None:
            return f"preflight: {label} sink missing"
        actual_host = _extract_cfg_string(interface_body, "ip", "host")
        actual_port = _extract_cfg_port(interface_body)
        if validate_host and actual_host != expected_host:
            return "preflight: sink host mismatch"
        if actual_port != expected_port:
            return f"preflight: {label} sink port mismatch"
    return None


class RemoteOdasController:
    """Manage one odaslive instance on a Linux server over SSH."""

    _STOP_WAIT_ATTEMPTS = 10
    _STOP_WAIT_SEC = 0.1
    _SHELL_TIMEOUT_SEC = 8.0
    _SHELL_POLL_SEC = 0.02
    _MARKER = "\x1e"
    _BOOTSTRAP_NAME = "TEMPORAL_BOOTSTRAP_READY"

    def __init__(self, config: RemoteOdasConfig, streams: OdasStreamConfig) -> None:
        self._cfg = config
        self._streams = streams
        self._client: paramiko.SSHClient | None = None
        self._shell: paramiko.Channel | None = None
        self._shell_stdout_buffer = ""
        self._shell_stderr_buffer = ""
        self._request_counter = 0
        self._lock = threading.Lock()
        self._shell_config_assignments = self._build_config_assignments()
        self._shell_path_shell = self._build_path_shell()
        self._shell_command_shell = self._build_command_shell()
        self._shell_pid_shell = self._build_pid_shell()
        self._helper_shell = self._build_helper_shell()

    def connect(self) -> None:
        with self._lock:
            if self._transport_is_active_locked():
                self._ensure_control_shell_locked()
                return
            self._close_shell_locked()
            self._close_client_locked()
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self._cfg.host,
                port=self._cfg.port,
                username=self._cfg.username,
                key_filename=self._cfg.private_key,
                timeout=8,
            )
            self._client = client
            self._ensure_control_shell_locked()

    def close(self) -> None:
        with self._lock:
            self._close_shell_locked()
            self._close_client_locked()

    def is_connected(self) -> bool:
        with self._lock:
            return self._transport_is_active_locked() and self._shell_is_active_locked()

    def _close_shell_locked(self) -> None:
        if self._shell is not None:
            try:
                self._shell.close()
            except Exception:
                pass
            self._shell = None
        self._shell_stdout_buffer = ""
        self._shell_stderr_buffer = ""

    def _close_client_locked(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def _transport_is_active_locked(self) -> bool:
        if self._client is None:
            return False
        transport = self._client.get_transport()
        return bool(transport is not None and transport.is_active())

    def _shell_is_active_locked(self) -> bool:
        if self._shell is None:
            return False
        try:
            return not self._shell.closed and not self._shell.exit_status_ready()
        except Exception:
            return False

    def _compose_shell(self, *parts: str) -> str:
        return "\n".join(part for part in parts if part)

    def _build_config_assignments(self) -> str:
        return "\n".join(
            [
                f"cfg_cwd={shlex.quote(self._cfg.odas_cwd or '')}",
                f"cfg_log={shlex.quote(self._cfg.odas_log)}",
                f"cfg_command={shlex.quote(self._cfg.odas_command)}",
            ]
        )

    def _quoted_command(self) -> str:
        return " ".join(
            [
                shlex.quote(self._cfg.odas_command),
                *[shlex.quote(arg) for arg in self._cfg.odas_args],
            ]
        )

    def _cfg_arg_path(self) -> str | None:
        args = self._cfg.odas_args
        for index, arg in enumerate(args):
            if arg in {"-c", "--config", "--cfg"} and index + 1 < len(args):
                return args[index + 1]
            if arg.startswith("-c") and len(arg) > 2:
                return arg[2:]
            for prefix in ("--config=", "--cfg="):
                if arg.startswith(prefix):
                    return arg[len(prefix) :]
        return None

    def _should_validate_sink_host(self) -> bool:
        return self._streams.sst.host not in {"", "0.0.0.0", "::"}

    def _preflight_failed(self, reason: str) -> CommandResult:
        return CommandResult(code=1, stdout="", stderr=reason)

    def _build_path_shell(self) -> str:
        return r"""
resolve_home_relative() {
    path_input="$1"
    if [ -z "$path_input" ]; then
        printf '%s\n' ""
        return 0
    fi
    case "$path_input" in
        /*)
            printf '%s\n' "$path_input"
            ;;
        "~")
            printf '%s\n' "$HOME"
            ;;
        "~/"*)
            printf '%s\n' "$HOME/${path_input#"~/"}"
            ;;
        *)
            printf '%s\n' "$HOME/$path_input"
            ;;
    esac
}

resolve_runtime_paths() {
    cd "$HOME" || {
        printf 'preflight: remote working directory inaccessible\n' >&2
        return 1
    }
    resolved_cwd="$(resolve_home_relative "$cfg_cwd")"
    if [ -n "$resolved_cwd" ]; then
        if [ ! -d "$resolved_cwd" ]; then
            printf 'preflight: remote working directory missing\n' >&2
            return 1
        fi
        cd "$resolved_cwd" || {
            printf 'preflight: remote working directory inaccessible\n' >&2
            return 1
        }
    fi
    working_dir="$(pwd -P)"

    if [ -n "$cfg_log" ]; then
        case "$cfg_log" in
            /*)
                resolved_log="$cfg_log"
                ;;
            *)
                resolved_log="$working_dir/$cfg_log"
                ;;
        esac
    fi

    log_dir="$(dirname "$resolved_log")"
    log_file="$(basename "$resolved_log")"
    case "$log_file" in
        *.*)
            pid_file="${log_file%.*}.pid"
            ;;
        *)
            pid_file="${log_file}.pid"
            ;;
    esac
    pid_path="$log_dir/$pid_file"
}
""".strip()

    def _build_command_shell(self) -> str:
        return r"""
resolve_command_path() {
    case "$cfg_command" in
        */*)
            if [ "${cfg_command#/}" != "$cfg_command" ]; then
                resolved_command="$cfg_command"
            else
                resolved_command="$(pwd -P)/$cfg_command"
            fi
            ;;
        *)
            resolved_command="$(command -v "$cfg_command" 2>/dev/null || printf '')"
            ;;
    esac

    if [ -z "$resolved_command" ] || [ ! -e "$resolved_command" ]; then
        printf 'preflight: remote command missing\n' >&2
        return 1
    fi
    if [ ! -x "$resolved_command" ]; then
        printf 'preflight: remote command not executable\n' >&2
        return 1
    fi
}

preflight_or_exit() {
    resolve_runtime_paths || return 1
    resolve_command_path || return 1
}
""".strip()

    def _build_pid_shell(self) -> str:
        arg_check_lines: list[str] = []
        for arg in self._cfg.odas_args:
            arg_check_lines.extend(
                [
                    f"    if ! printf '%s\\n' \"$actual_cmdline\" | grep -Fxq -- {shlex.quote(arg)}; then",
                    "        cleanup_pid",
                    "        return 1",
                    "    fi",
                ]
            )
        flattened_arg_checks = "\n".join(arg_check_lines)
        return r"""
cleanup_pid() {
    rm -f "$pid_path"
}

load_valid_pid() {
    pid=""
    if [ ! -f "$pid_path" ]; then
        return 1
    fi
    pid="$(tr -d '[:space:]' < "$pid_path" 2>/dev/null || printf '')"
    case "$pid" in
        ''|*[!0-9]*)
            cleanup_pid
            return 1
            ;;
    esac
    if ! kill -0 "$pid" 2>/dev/null; then
        cleanup_pid
        return 1
    fi
    cmdline_path="/proc/$pid/cmdline"
    if [ ! -r "$cmdline_path" ]; then
        cleanup_pid
        return 1
    fi
    actual_cmdline="$(tr '\000' '\n' < "$cmdline_path")"
    if ! printf '%s\n' "$actual_cmdline" | grep -Fxq -- "$cfg_command"; then
        if [ -z "$resolved_command" ] || ! printf '%s\n' "$actual_cmdline" | grep -Fxq -- "$resolved_command"; then
            cleanup_pid
            return 1
        fi
    fi
__ARG_CHECKS__
    actual_cwd="$(readlink "/proc/$pid/cwd" 2>/dev/null || printf '')"
    expected_cwd="$(pwd -P)"
    if [ -n "$resolved_cwd" ] && { [ -z "$actual_cwd" ] || [ "$actual_cwd" != "$expected_cwd" ]; }; then
        cleanup_pid
        return 1
    fi
    return 0
}
""".replace("__ARG_CHECKS__", flattened_arg_checks).strip()

    def _bootstrap_marker(self) -> str:
        return f"{self._MARKER}{self._BOOTSTRAP_NAME}{self._MARKER}"

    def _marker(self, kind: str, payload: str) -> str:
        return f"{self._MARKER}TEMPORAL_{kind}:{payload}{self._MARKER}"

    def _build_helper_shell(self) -> str:
        return self._compose_shell(
            self._shell_config_assignments,
            self._shell_path_shell,
            self._shell_command_shell,
            self._shell_pid_shell,
            self._build_public_helper_shell(),
            f"printf {shlex.quote(self._bootstrap_marker())}",
        )

    def _build_public_helper_shell(self) -> str:
        stop_body = f"""
temporal_stop() {{
    resolve_runtime_paths >/dev/null 2>&1 || return 0
    resolve_command_path >/dev/null 2>&1 || return 0
    if ! load_valid_pid; then
        return 0
    fi
    if ! kill -TERM -- "-$pid" 2>/dev/null; then
        if ! kill -TERM "$pid" 2>/dev/null; then
            if ! kill -0 "$pid" 2>/dev/null; then
                cleanup_pid
                return 0
            fi
            printf "failed to stop pid %s\\n" "$pid" >&2
            return 1
        fi
    fi
    attempt=0
    while kill -0 -- "-$pid" 2>/dev/null || kill -0 "$pid" 2>/dev/null; do
        attempt=$((attempt + 1))
        if [ "$attempt" -ge {self._STOP_WAIT_ATTEMPTS} ]; then
            printf "failed to stop pid %s\\n" "$pid" >&2
            return 1
        fi
        sleep {self._STOP_WAIT_SEC}
    done
    cleanup_pid
}}
""".strip()
        return self._compose_shell(
            r"""
temporal_metadata() {
    preflight_or_exit || return 1
    printf 'home=%s\n' "$HOME"
    printf 'working_dir=%s\n' "$working_dir"
    printf 'resolved_command=%s\n' "$resolved_command"
}

temporal_cat_file() {
    file_path="$1"
    missing_reason="$2"
    if [ ! -f "$file_path" ]; then
        printf '%s\n' "$missing_reason" >&2
        return 1
    fi
    cat -- "$file_path"
}

temporal_start() {
    preflight_or_exit || return 1
    if load_valid_pid; then
        printf '%s\n' "$pid"
        return 0
    fi
""".strip(),
            f'setsid {self._quoted_command()} >> "$resolved_log" 2>&1 < /dev/null &',
            r"""
    pid="$!"
    printf "%s\n" "$pid" > "$pid_path"
    printf "%s\n" "$pid"
}

temporal_status() {
    resolve_runtime_paths >/dev/null 2>&1 || return 0
    resolve_command_path >/dev/null 2>&1 || return 0
    if ! load_valid_pid; then
        return 0
    fi
    printf "%s\n" "$pid"
}
temporal_log_tail() {
    requested_lines="$1"
    if [ -z "$requested_lines" ]; then
        requested_lines="80"
    fi
    resolve_runtime_paths >/dev/null 2>&1 || return 0
    if [ -f "$resolved_log" ]; then
        tail -n "$requested_lines" "$resolved_log"
    fi
}

temporal_run() {
    request_id="$1"
    shift
    stdout_file="$(mktemp)"
    stderr_file="$(mktemp)"
    "$@" >"$stdout_file" 2>"$stderr_file"
    exit_code="$?"
    printf '\036TEMPORAL_BEGIN:%s\036' "$request_id"
    printf '\036TEMPORAL_STDOUT:%s\036' "$request_id"
    cat "$stdout_file"
    printf '\036TEMPORAL_STDERR:%s\036' "$request_id"
    cat "$stderr_file"
    printf '\036TEMPORAL_EXIT:%s:%s\036' "$request_id" "$exit_code"
    printf '\036TEMPORAL_END:%s\036' "$request_id"
    rm -f "$stdout_file" "$stderr_file"
}
""".strip(),
            stop_body,
        )

    def _ensure_control_shell_locked(self) -> None:
        if not self._transport_is_active_locked():
            raise RuntimeError("SSH is not connected")
        if self._shell_is_active_locked():
            return
        assert self._client is not None
        transport = self._client.get_transport()
        if transport is None or not transport.is_active():
            raise RuntimeError("SSH is not connected")
        self._close_shell_locked()
        shell = transport.open_session()
        shell.settimeout(self._SHELL_TIMEOUT_SEC)
        shell.exec_command("sh")
        self._shell = shell
        self._shell_stdout_buffer = ""
        self._shell_stderr_buffer = ""
        time.sleep(self._SHELL_POLL_SEC)
        self._drain_shell_locked()
        self._send_shell_text_locked(self._helper_shell + "\n")
        self._read_until_contains_locked(self._bootstrap_marker())
        self._discard_through_locked(self._bootstrap_marker())

    def _drain_shell_locked(self) -> None:
        if self._shell is None:
            return
        deadline = time.monotonic() + 0.2
        while time.monotonic() < deadline:
            if not self._shell.recv_ready() and not self._shell.recv_stderr_ready():
                time.sleep(self._SHELL_POLL_SEC)
                continue
            self._read_available_locked()

    def _send_shell_text_locked(self, text: str) -> None:
        if not self._shell_is_active_locked() or self._shell is None:
            raise _ControlShellLost("SSH control shell lost", retryable=True)
        self._shell.sendall(text.encode("utf-8"))

    def _read_available_locked(self) -> bool:
        if self._shell is None:
            return False
        saw_activity = False
        while self._shell.recv_ready():
            chunk = self._shell.recv(4096)
            if not chunk:
                raise _ControlShellLost("SSH control shell lost", retryable=False)
            self._shell_stdout_buffer += chunk.decode("utf-8", errors="replace")
            saw_activity = True
        while self._shell.recv_stderr_ready():
            chunk = self._shell.recv_stderr(4096)
            if not chunk:
                raise _ControlShellLost("SSH control shell lost", retryable=False)
            self._shell_stderr_buffer += chunk.decode("utf-8", errors="replace")
            saw_activity = True
        return saw_activity

    def _shell_diagnostic_tail_locked(self) -> str:
        diagnostic = self._shell_stderr_buffer.strip() or self._shell_stdout_buffer.strip()
        if not diagnostic:
            return ""
        lines = diagnostic.splitlines()
        return lines[-1].strip()

    def _read_until_contains_locked(self, token: str) -> None:
        deadline = time.monotonic() + self._SHELL_TIMEOUT_SEC
        saw_activity = False
        while token not in self._shell_stdout_buffer:
            if time.monotonic() >= deadline:
                tail = self._shell_diagnostic_tail_locked()
                if tail:
                    raise RuntimeError(f"SSH control shell timed out: {tail}")
                raise RuntimeError("SSH control shell timed out")
            if not self._shell_is_active_locked() or self._shell is None:
                raise _ControlShellLost("SSH control shell lost", retryable=not saw_activity)
            if not self._shell.recv_ready() and not self._shell.recv_stderr_ready():
                time.sleep(self._SHELL_POLL_SEC)
                continue
            saw_activity = self._read_available_locked() or saw_activity

    def _discard_through_locked(self, token: str) -> None:
        marker_index = self._shell_stdout_buffer.find(token)
        if marker_index < 0:
            return
        self._shell_stdout_buffer = self._shell_stdout_buffer[marker_index + len(token) :]
        self._shell_stderr_buffer = ""

    def _next_request_id_locked(self) -> str:
        self._request_counter += 1
        return str(self._request_counter)

    def _parse_command_result_locked(self, request_id: str) -> CommandResult:
        begin = self._marker("BEGIN", request_id)
        stdout_marker = self._marker("STDOUT", request_id)
        stderr_marker = self._marker("STDERR", request_id)
        exit_prefix = f"{self._MARKER}TEMPORAL_EXIT:{request_id}:"
        end = self._marker("END", request_id)
        self._read_until_contains_locked(end)
        begin_index = self._shell_stdout_buffer.find(begin)
        if begin_index < 0:
            raise RuntimeError("SSH control shell protocol desynced")
        stdout_index = self._shell_stdout_buffer.find(stdout_marker, begin_index + len(begin))
        stderr_index = self._shell_stdout_buffer.find(
            stderr_marker, stdout_index + len(stdout_marker)
        )
        exit_index = self._shell_stdout_buffer.find(exit_prefix, stderr_index + len(stderr_marker))
        exit_end_index = self._shell_stdout_buffer.find(self._MARKER, exit_index + len(exit_prefix))
        end_index = self._shell_stdout_buffer.find(end, exit_end_index)
        if min(stdout_index, stderr_index, exit_index, exit_end_index, end_index) < 0:
            raise RuntimeError("SSH control shell protocol desynced")
        stdout = self._shell_stdout_buffer[stdout_index + len(stdout_marker) : stderr_index]
        stderr = self._shell_stdout_buffer[stderr_index + len(stderr_marker) : exit_index]
        code_text = self._shell_stdout_buffer[exit_index + len(exit_prefix) : exit_end_index]
        try:
            code = int(code_text)
        except ValueError as exc:
            raise RuntimeError("SSH control shell returned invalid exit code") from exc
        self._shell_stdout_buffer = self._shell_stdout_buffer[end_index + len(end) :]
        self._shell_stderr_buffer = ""
        return CommandResult(code=code, stdout=stdout, stderr=stderr)

    def _run_shell_function(self, name: str, *args: str) -> CommandResult:
        with self._lock:
            last_error: RuntimeError | None = None
            for _ in range(2):
                try:
                    self._ensure_control_shell_locked()
                    request_id = self._next_request_id_locked()
                    quoted_args = " ".join(shlex.quote(arg) for arg in args)
                    command = f"temporal_run {shlex.quote(request_id)} {name}"
                    if quoted_args:
                        command = f"{command} {quoted_args}"
                    self._send_shell_text_locked(command + "\n")
                    return self._parse_command_result_locked(request_id)
                except _ControlShellLost as exc:
                    self._close_shell_locked()
                    if not exc.retryable:
                        raise RuntimeError(str(exc)) from exc
                    last_error = RuntimeError(str(exc))
            if last_error is not None:
                raise last_error
            raise RuntimeError("SSH control shell lost")

    def _metadata_result(self) -> CommandResult:
        return self._run_shell_function("temporal_metadata")

    def _parse_metadata(self, stdout: str) -> _PreflightRuntime:
        values: dict[str, str] = {}
        for line in stdout.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key] = value
        return _PreflightRuntime(
            home_dir=values.get("home", ""),
            working_dir=values.get("working_dir", ""),
            resolved_command=values.get("resolved_command", ""),
        )

    def _read_remote_text(self, path: str, missing_reason: str) -> CommandResult:
        result = self._run_shell_function("temporal_cat_file", path, missing_reason)
        if result.code == 0:
            return result
        stderr = result.stderr.strip() or missing_reason
        return CommandResult(code=result.code, stdout=result.stdout, stderr=stderr)

    def _resolve_cfg_path_for_preflight(self, runtime: _PreflightRuntime) -> CommandResult | str:
        raw_cfg_path = self._cfg_arg_path()
        if raw_cfg_path is None:
            wrapper_result = self._read_remote_text(
                runtime.resolved_command,
                "preflight: odas config path missing",
            )
            if wrapper_result.code != 0:
                return self._preflight_failed("preflight: odas config path missing")
            raw_cfg_path = _extract_wrapper_cfg_path(wrapper_result.stdout)
        if not raw_cfg_path:
            return self._preflight_failed("preflight: odas config path missing")
        return _resolve_cfg_path(raw_cfg_path, runtime)

    def _validate_static_preflight(self) -> CommandResult:
        metadata_result = self._metadata_result()
        if metadata_result.code != 0:
            return metadata_result
        runtime = self._parse_metadata(metadata_result.stdout)
        cfg_path = self._resolve_cfg_path_for_preflight(runtime)
        if isinstance(cfg_path, CommandResult):
            return cfg_path
        cfg_result = self._read_remote_text(cfg_path, "preflight: odas config file missing")
        if cfg_result.code != 0:
            return self._preflight_failed("preflight: odas config file missing")
        sink_error = _sink_targets_match(cfg_result.stdout, self._streams)
        if sink_error is not None:
            return self._preflight_failed(sink_error)
        return CommandResult(code=0, stdout="", stderr="")

    def start_odaslive(self) -> CommandResult:
        preflight = self._validate_static_preflight()
        if preflight.code != 0:
            return preflight
        return self._run_shell_function("temporal_start")

    def stop_odaslive(self) -> CommandResult:
        return self._run_shell_function("temporal_stop")

    def status(self) -> CommandResult:
        return self._run_shell_function("temporal_status")

    def read_log_tail(self, lines: int = 80) -> CommandResult:
        safe_lines = str(max(1, min(lines, 200)))
        return self._run_shell_function("temporal_log_tail", safe_lines)
