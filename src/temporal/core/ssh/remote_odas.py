from __future__ import annotations

import posixpath
import shlex
import threading
from dataclasses import dataclass

import paramiko

from temporal.core.models import RemoteOdasConfig


@dataclass(slots=True)
class CommandResult:
    code: int
    stdout: str
    stderr: str


class RemoteOdasController:
    """Manage one odaslive instance on a Linux server over SSH."""

    _STOP_WAIT_ATTEMPTS = 10
    _STOP_WAIT_SEC = 0.1

    def __init__(self, config: RemoteOdasConfig) -> None:
        self._cfg = config
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

    def _wrap_in_cwd(self, shell_script: str) -> str:
        if self._cfg.odas_cwd is None:
            return shell_script
        escaped_cwd = shlex.quote(self._cfg.odas_cwd)
        return f"cd {escaped_cwd} || exit 1\n{shell_script}"

    def _shell_command(self, shell_script: str) -> str:
        return f"sh -lc {shlex.quote(self._wrap_in_cwd(shell_script))}"

    def _log_path(self) -> str:
        return self._cfg.odas_log

    def _pid_path(self) -> str:
        base, extension = posixpath.splitext(self._log_path())
        if extension:
            return f"{base}.pid"
        return f"{self._log_path()}.pid"

    def _quoted_log_path(self) -> str:
        return shlex.quote(self._log_path())

    def _quoted_pid_path(self) -> str:
        return shlex.quote(self._pid_path())

    def _quoted_command(self) -> str:
        return " ".join(
            [
                shlex.quote(self._cfg.odas_command),
                *[shlex.quote(arg) for arg in self._cfg.odas_args],
            ]
        )

    def _expected_cmdline(self) -> str:
        return "".join(f"{part}\n" for part in [self._cfg.odas_command, *self._cfg.odas_args])

    def _identity_validation_function(self) -> str:
        lines = [
            f"pid_path={self._quoted_pid_path()}",
            "cleanup_pid() {",
            '    rm -f "$pid_path"',
            "}",
            "load_valid_pid() {",
            '    pid=""',
            '    if [ ! -f "$pid_path" ]; then',
            "        return 1",
            "    fi",
            "    pid=\"$(tr -d '[:space:]' < \"$pid_path\" 2>/dev/null || printf '')\"",
            '    case "$pid" in',
            "        ''|*[!0-9]*)",
            "            cleanup_pid",
            "            return 1",
            "            ;;",
            "    esac",
            '    if ! kill -0 "$pid" 2>/dev/null; then',
            "        cleanup_pid",
            "        return 1",
            "    fi",
            '    cmdline_path="/proc/$pid/cmdline"',
            '    if [ ! -r "$cmdline_path" ]; then',
            "        cleanup_pid",
            "        return 1",
            "    fi",
            "    actual_cmdline=\"$(tr '\\000' '\\n' < \"$cmdline_path\")\"",
            f"    expected_cmdline={shlex.quote(self._expected_cmdline())}",
            '    if [ "$actual_cmdline" != "$expected_cmdline" ]; then',
            "        cleanup_pid",
            "        return 1",
            "    fi",
        ]
        if self._cfg.odas_cwd is not None:
            lines.extend(
                [
                    '    actual_cwd="$(readlink "/proc/$pid/cwd" 2>/dev/null || printf \'\')"',
                    '    expected_cwd="$(pwd -P)"',
                    '    if [ -z "$actual_cwd" ] || [ "$actual_cwd" != "$expected_cwd" ]; then',
                    "        cleanup_pid",
                    "        return 1",
                    "    fi",
                ]
            )
        lines.extend(["    return 0", "}"])
        return "\n".join(lines)

    def start_odaslive(self) -> CommandResult:
        escaped_log = self._quoted_log_path()
        shell_script = "\n".join(
            [
                self._identity_validation_function(),
                "if load_valid_pid; then",
                "    printf '%s\\n' \"$pid\"",
                "    exit 0",
                "fi",
                f"{self._quoted_command()} >> {escaped_log} 2>&1 < /dev/null &",
                'pid="$!"',
                'printf "%s\\n" "$pid" > "$pid_path"',
                'printf "%s\\n" "$pid"',
            ]
        )
        return self._exec(self._shell_command(shell_script))

    def stop_odaslive(self) -> CommandResult:
        shell_script = "\n".join(
            [
                self._identity_validation_function(),
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
            ]
        )
        return self._exec(self._shell_command(shell_script))

    def status(self) -> CommandResult:
        shell_script = "\n".join(
            [
                self._identity_validation_function(),
                "if ! load_valid_pid; then",
                "    exit 0",
                "fi",
                'printf "%s\\n" "$pid"',
            ]
        )
        return self._exec(self._shell_command(shell_script))

    def read_log_tail(self, lines: int = 80) -> CommandResult:
        safe_lines = max(1, min(lines, 200))
        escaped_log = self._quoted_log_path()
        shell_script = f"if [ -f {escaped_log} ]; then tail -n {safe_lines} {escaped_log}; fi"
        return self._exec(self._shell_command(shell_script))
