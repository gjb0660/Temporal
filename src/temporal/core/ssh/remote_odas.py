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
    """Manage odaslive lifecycle on a Linux server over SSH."""

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

    def _quoted_log_path(self) -> str:
        return shlex.quote(self._cfg.odas_log)

    def _quoted_command(self) -> str:
        return " ".join(
            [
                shlex.quote(self._cfg.odas_command),
                *[shlex.quote(arg) for arg in self._cfg.odas_args],
            ]
        )

    def _quoted_process_name(self) -> str:
        return shlex.quote(posixpath.basename(self._cfg.odas_command))

    def start_odaslive(self) -> CommandResult:
        escaped_log = self._quoted_log_path()
        shell_script = f"{self._quoted_command()} >> {escaped_log} 2>&1 < /dev/null & echo $!"
        cmd = f"sh -lc {shlex.quote(self._wrap_in_cwd(shell_script))}"
        return self._exec(cmd)

    def stop_odaslive(self) -> CommandResult:
        return self._exec(f"pkill -f {self._quoted_process_name()} || true")

    def status(self) -> CommandResult:
        return self._exec(f"pgrep -af {self._quoted_process_name()} || true")

    def read_log_tail(self, lines: int = 80) -> CommandResult:
        safe_lines = max(1, min(lines, 200))
        escaped_log = self._quoted_log_path()
        shell_script = f"if [ -f {escaped_log} ]; then tail -n {safe_lines} {escaped_log}; fi"
        cmd = f"sh -lc {shlex.quote(self._wrap_in_cwd(shell_script))}"
        return self._exec(cmd)
