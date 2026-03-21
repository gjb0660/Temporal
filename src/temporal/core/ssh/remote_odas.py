from __future__ import annotations

import re
import shlex
import threading
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


def _extract_cfg_assignment_body(cfg_text: str, name: str) -> str | None:
    pattern = re.compile(rf"(?ms)^\s*{re.escape(name)}\s*=\s*\{{(?P<body>.*?)\}}")
    match = pattern.search(cfg_text)
    if match is None:
        return None
    return match.group("body")


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
        ("tracks", "tracks", streams.sst.host, streams.sst.port),
        ("hops", "hops", streams.ssl.host, streams.ssl.port),
        ("audio_sep", "audio sep", streams.sss_sep.host, streams.sss_sep.port),
        ("audio_pf", "audio pf", streams.sss_pf.host, streams.sss_pf.port),
    )
    for sink_name, label, expected_host, expected_port in sink_specs:
        body = _extract_cfg_assignment_body(cleaned_cfg, sink_name)
        if body is None:
            return f"preflight: {label} sink missing"
        actual_host = _extract_cfg_string(body, "ip", "host")
        actual_port = _extract_cfg_port(body)
        if validate_host and actual_host != expected_host:
            return "preflight: sink host mismatch"
        if actual_port != expected_port:
            return f"preflight: {label} sink port mismatch"
    return None


class RemoteOdasController:
    """Manage one odaslive instance on a Linux server over SSH."""

    _STOP_WAIT_ATTEMPTS = 10
    _STOP_WAIT_SEC = 0.1

    def __init__(self, config: RemoteOdasConfig, streams: OdasStreamConfig) -> None:
        self._cfg = config
        self._streams = streams
        self._client: paramiko.SSHClient | None = None
        self._lock = threading.Lock()

    def connect(self) -> None:
        with self._lock:
            if self._client is not None:
                return

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

    def close(self) -> None:
        with self._lock:
            if self._client is not None:
                self._client.close()
                self._client = None

    def _exec(self, cmd: str) -> CommandResult:
        if self._client is None:
            raise RuntimeError("SSH is not connected")
        _, stdout, stderr = self._client.exec_command(cmd)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        code = stdout.channel.recv_exit_status()
        return CommandResult(code=code, stdout=out, stderr=err)

    def _shell_command(self, shell_script: str) -> str:
        return f"sh -lc {shlex.quote(shell_script)}"

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

    def _metadata_script(self) -> str:
        return "\n".join(
            [
                self._common_shell_prelude(),
                "resolve_runtime_paths || exit 1",
                "resolve_command_path || exit 1",
                'printf "home=%s\\n" "$HOME"',
                'printf "working_dir=%s\\n" "$working_dir"',
                'printf "resolved_command=%s\\n" "$resolved_command"',
            ]
        )

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
        file_path = shlex.quote(path)
        result = self._exec(
            self._shell_command(
                "\n".join(
                    [
                        f"file_path={file_path}",
                        'if [ ! -f "$file_path" ]; then',
                        f"    printf {shlex.quote(missing_reason + chr(10))} >&2",
                        "    exit 1",
                        "fi",
                        'cat -- "$file_path"',
                    ]
                )
            )
        )
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
        metadata_result = self._exec(self._shell_command(self._metadata_script()))
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

    def _common_shell_prelude(self) -> str:
        cfg_cwd = shlex.quote(self._cfg.odas_cwd or "")
        cfg_log = shlex.quote(self._cfg.odas_log)
        cfg_command = shlex.quote(self._cfg.odas_command)
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
        return "\n".join(
            [
                f"cfg_cwd={cfg_cwd}",
                f"cfg_log={cfg_log}",
                f"cfg_command={cfg_command}",
                r"""
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
""".replace("__ARG_CHECKS__", flattened_arg_checks).strip(),
            ]
        )

    def _start_script(self) -> str:
        return "\n".join(
            [
                self._common_shell_prelude(),
                "preflight_or_exit || exit 1",
                "if load_valid_pid; then",
                "    printf '%s\\n' \"$pid\"",
                "    exit 0",
                "fi",
                f'{self._quoted_command()} >> "$resolved_log" 2>&1 < /dev/null &',
                'pid="$!"',
                'printf "%s\\n" "$pid" > "$pid_path"',
                'printf "%s\\n" "$pid"',
            ]
        )

    def _runtime_script(self, *lines: str, needs_command_path: bool = False) -> str:
        script_lines = [
            self._common_shell_prelude(),
            "resolve_runtime_paths >/dev/null 2>&1 || exit 0",
        ]
        if needs_command_path:
            script_lines.append("resolve_command_path >/dev/null 2>&1 || exit 0")
        script_lines.extend(lines)
        return "\n".join(script_lines)

    def _status_script(self) -> str:
        return self._runtime_script(
            "if ! load_valid_pid; then",
            "    exit 0",
            "fi",
            'printf "%s\\n" "$pid"',
            needs_command_path=True,
        )

    def _stop_script(self) -> str:
        return self._runtime_script(
            "if ! load_valid_pid; then",
            "    exit 0",
            "fi",
            'if ! kill "$pid" 2>/dev/null; then',
            '    if ! kill -0 "$pid" 2>/dev/null; then',
            "        cleanup_pid",
            "        exit 0",
            "    fi",
            '    printf "failed to stop pid %s\\n" "$pid" >&2',
            "    exit 1",
            "fi",
            "attempt=0",
            'while kill -0 "$pid" 2>/dev/null; do',
            "    attempt=$((attempt + 1))",
            f'    if [ "$attempt" -ge {self._STOP_WAIT_ATTEMPTS} ]; then',
            '        printf "failed to stop pid %s\\n" "$pid" >&2',
            "        exit 1",
            "    fi",
            f"    sleep {self._STOP_WAIT_SEC}",
            "done",
            "cleanup_pid",
            needs_command_path=True,
        )

    def _log_script(self, lines: int) -> str:
        return self._runtime_script(
            f'if [ -f "$resolved_log" ]; then tail -n {lines} "$resolved_log"; fi'
        )

    def start_odaslive(self) -> CommandResult:
        preflight = self._validate_static_preflight()
        if preflight.code != 0:
            return preflight
        return self._exec(self._shell_command(self._start_script()))

    def stop_odaslive(self) -> CommandResult:
        return self._exec(self._shell_command(self._stop_script()))

    def status(self) -> CommandResult:
        return self._exec(self._shell_command(self._status_script()))

    def read_log_tail(self, lines: int = 80) -> CommandResult:
        safe_lines = max(1, min(lines, 200))
        return self._exec(self._shell_command(self._log_script(safe_lines)))
