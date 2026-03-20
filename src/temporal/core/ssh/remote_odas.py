from __future__ import annotations

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

    def _common_shell_prelude(self) -> str:
        cfg_cwd = shlex.quote(self._cfg.odas_cwd or "")
        cfg_log = shlex.quote(self._cfg.odas_log)
        cfg_command = shlex.quote(self._cfg.odas_command)
        cfg_arg_path = shlex.quote(self._cfg_arg_path() or "")
        listen_host = shlex.quote(self._streams.sst.host)
        validate_sink_host = "1" if self._should_validate_sink_host() else "0"
        ports = [
            self._streams.sst.port,
            self._streams.ssl.port,
            self._streams.sss_sep.port,
            self._streams.sss_pf.port,
        ]
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
                f"cfg_arg_path={cfg_arg_path}",
                f"listen_host={listen_host}",
                f"validate_sink_host={validate_sink_host}",
                f"expected_sst_port={ports[0]}",
                f"expected_ssl_port={ports[1]}",
                f"expected_sep_port={ports[2]}",
                f"expected_pf_port={ports[3]}",
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

    if [ -n "$cfg_log" ]; then
        case "$cfg_log" in
            /*)
                resolved_log="$cfg_log"
                ;;
            *)
                resolved_log="$(pwd -P)/$cfg_log"
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

resolve_cfg_path() {
    raw_cfg_path="$cfg_arg_path"
    if [ -z "$raw_cfg_path" ] && [ -f "$resolved_command" ]; then
        raw_cfg_path="$(
            grep -Eo '(^|[[:space:]])(-c|--config|--cfg)([[:space:]]+|=)[^[:space:]]+' "$resolved_command" \
            | head -n 1 \
            | awk '{print $NF}'
        )"
        raw_cfg_path="${raw_cfg_path#*=}"
    fi

    if [ -z "$raw_cfg_path" ]; then
        printf 'preflight: odas config path missing\n' >&2
        return 1
    fi

    case "$raw_cfg_path" in
        /*)
            cfg_path="$raw_cfg_path"
            ;;
        "~"|"~/"*)
            cfg_path="$(resolve_home_relative "$raw_cfg_path")"
            ;;
        *)
            cfg_path="$(pwd -P)/$raw_cfg_path"
            ;;
    esac

    if [ ! -f "$cfg_path" ]; then
        printf 'preflight: odas config file missing\n' >&2
        return 1
    fi
}

ensure_cfg_contains_port() {
    expected_port="$1"
    label="$2"
    if ! grep -Eq "(^|[^0-9])${expected_port}([^0-9]|$)" "$cfg_path"; then
        printf 'preflight: %s sink port mismatch\n' "$label" >&2
        return 1
    fi
}

validate_cfg_sinks() {
    if [ "$validate_sink_host" = "1" ]; then
        if ! grep -Fq "$listen_host" "$cfg_path"; then
            printf 'preflight: sink host mismatch\n' >&2
            return 1
        fi
    fi
    ensure_cfg_contains_port "$expected_sst_port" "tracks" || return 1
    ensure_cfg_contains_port "$expected_ssl_port" "hops" || return 1
    ensure_cfg_contains_port "$expected_sep_port" "audio sep" || return 1
    ensure_cfg_contains_port "$expected_pf_port" "audio pf" || return 1
}

preflight_or_exit() {
    resolve_runtime_paths || return 1
    resolve_command_path || return 1
    resolve_cfg_path || return 1
    validate_cfg_sinks || return 1
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
        return self._exec(self._shell_command(self._start_script()))

    def stop_odaslive(self) -> CommandResult:
        return self._exec(self._shell_command(self._stop_script()))

    def status(self) -> CommandResult:
        return self._exec(self._shell_command(self._status_script()))

    def read_log_tail(self, lines: int = 80) -> CommandResult:
        safe_lines = max(1, min(lines, 200))
        return self._exec(self._shell_command(self._log_script(safe_lines)))
