from __future__ import annotations

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

    def start_odaslive(self) -> CommandResult:
        escaped_command = shlex.quote(self._cfg.odas_command)
        escaped_args = " ".join(shlex.quote(arg) for arg in self._cfg.odas_args)
        command = escaped_command
        if escaped_args:
            command = f"{command} {escaped_args}"
        if self._cfg.odas_cwd is not None:
            escaped_cwd = shlex.quote(self._cfg.odas_cwd)
            command = f"cd {escaped_cwd} && {command}"
        escaped_log = shlex.quote(self._cfg.odas_log)
        shell_script = f"{command} >{escaped_log} 2>&1 < /dev/null & echo $!"
        cmd = f"sh -lc {shlex.quote(shell_script)}"
        return self._exec(cmd)

    def stop_odaslive(self) -> CommandResult:
        return self._exec("pkill -f odaslive || true")

    def status(self) -> CommandResult:
        return self._exec("pgrep -af odaslive || true")

    def read_log_tail(self, lines: int = 80) -> CommandResult:
        safe_lines = max(1, min(lines, 200))
        escaped_log = shlex.quote(self._cfg.odas_log)
        shell_script = f"if [ -f {escaped_log} ]; then tail -n {safe_lines} {escaped_log}; fi"
        cmd = f"sh -lc {shlex.quote(shell_script)}"
        return self._exec(cmd)
