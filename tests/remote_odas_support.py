# ruff: noqa: F401
import shlex


import unittest


from collections import deque


from typing import cast


from unittest.mock import patch


from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig


from temporal.core.ssh.remote_odas import (
    CommandResult,
    RemoteOdasController,
    _extract_wrapper_cfg_path,
    _sink_targets_match,
)


def _make_streams(listen_host: str = "192.168.1.50") -> OdasStreamConfig:
    return OdasStreamConfig(
        sst=OdasEndpoint(host=listen_host, port=9000),
        ssl=OdasEndpoint(host=listen_host, port=9001),
        sss_sep=OdasEndpoint(host=listen_host, port=10000),
        sss_pf=OdasEndpoint(host=listen_host, port=10010),
    )


def _make_config(**overrides: object) -> RemoteOdasConfig:
    host = cast(str, overrides.get("host", "127.0.0.1"))
    port = cast(int, overrides.get("port", 22))
    username = cast(str | None, overrides.get("username", "tester"))
    private_key = cast(str | None, overrides.get("private_key", "dummy"))
    odas_command = cast(str, overrides.get("odas_command", "./odas_loop.sh"))
    odas_args = cast(list[str], overrides.get("odas_args", []))
    odas_cwd = cast(str | None, overrides.get("odas_cwd", "workspace/ODAS/odas"))
    odas_log = cast(str, overrides.get("odas_log", "odaslive.log"))
    return RemoteOdasConfig(
        host=host,
        port=port,
        username=username,
        private_key=private_key,
        odas_command=odas_command,
        odas_args=odas_args,
        odas_cwd=odas_cwd,
        odas_log=odas_log,
    )


def _runtime_metadata_result(
    *,
    home_dir: str = "/home/tester",
    working_dir: str = "/home/tester/workspace/ODAS/odas",
    resolved_command: str = "/home/tester/workspace/ODAS/odas/odas_loop.sh",
) -> CommandResult:
    return CommandResult(
        code=0,
        stdout="\n".join(
            [
                f"home={home_dir}",
                f"working_dir={working_dir}",
                f"resolved_command={resolved_command}",
            ]
        )
        + "\n",
        stderr="",
    )


def _valid_cfg(host: str = "10.10.0.8", sep_fs: int = 16000, pf_fs: int = 16000) -> str:
    return "\n".join(
        [
            "tracked: {",
            '  format = "json";',
            "  interface: {",
            '    type = "socket";',
            f'    ip = "{host}";',
            "    port = 9000;",
            "  };",
            "};",
            "potential: {",
            '  format = "json";',
            "  interface: {",
            '    type = "socket";',
            f'    ip = "{host}";',
            "    port = 9001;",
            "  };",
            "};",
            "separated: {",
            f"  fS = {sep_fs};",
            "  interface: {",
            '    type = "socket";',
            f'    ip = "{host}";',
            "    port = 10000;",
            "  };",
            "};",
            "postfiltered: {",
            f"  fS = {pf_fs};",
            "  interface: {",
            '    type = "socket";',
            f'    ip = "{host}";',
            "    port = 10010;",
            "  };",
            "};",
        ]
    )


def _render_shell_response(request_id: str, result: CommandResult) -> str:
    return (
        f"\x1eTEMPORAL_BEGIN:{request_id}\x1e"
        f"\x1eTEMPORAL_STDOUT:{request_id}\x1e{result.stdout}"
        f"\x1eTEMPORAL_STDERR:{request_id}\x1e{result.stderr}"
        f"\x1eTEMPORAL_EXIT:{request_id}:{result.code}\x1e"
        f"\x1eTEMPORAL_END:{request_id}\x1e"
    )


class _FakeTransport:
    def __init__(self, shells: list["_FakeShellChannel"]) -> None:
        self.active = True
        self.shells = deque(shells)
        self.open_session_calls = 0

    def is_active(self) -> bool:
        return self.active

    def open_session(self) -> "_FakeShellChannel":
        self.open_session_calls += 1
        if not self.shells:
            raise RuntimeError("no fake shell available")
        return self.shells.popleft()


class _FakeShellChannel:
    def __init__(self, response_fn=None) -> None:
        self.response_fn = response_fn or (lambda _name, _args: CommandResult(0, "", ""))
        self.sent: list[str] = []
        self.closed = False
        self.timeout: float | None = None
        self.exec_commands: list[str] = []
        self._recv_chunks: deque[bytes] = deque()
        self._recv_stderr_chunks: deque[bytes] = deque()

    def settimeout(self, timeout: float) -> None:
        self.timeout = timeout

    def exec_command(self, command: str) -> None:
        self.exec_commands.append(command)

    def sendall(self, data: bytes | str) -> None:
        if self.closed:
            raise OSError("shell is closed")
        if isinstance(data, bytes):
            text = data.decode("utf-8")
        else:
            text = data
        self.sent.append(text)
        if "TEMPORAL_BOOTSTRAP_READY" in text:
            self._recv_chunks.append(b"\x1eTEMPORAL_BOOTSTRAP_READY\x1e")
            return
        stripped = text.strip()
        if not stripped:
            return
        parts = shlex.split(stripped)
        if len(parts) < 3 or parts[0] != "temporal_run":
            return
        request_id = parts[1]
        helper_name = parts[2]
        helper_args = parts[3:]
        result = self.response_fn(helper_name, helper_args)
        self._recv_chunks.append(_render_shell_response(request_id, result).encode("utf-8"))

    def recv_ready(self) -> bool:
        return bool(self._recv_chunks)

    def recv_stderr_ready(self) -> bool:
        return bool(self._recv_stderr_chunks)

    def recv(self, _size: int) -> bytes:
        if not self._recv_chunks:
            return b""
        return self._recv_chunks.popleft()

    def recv_stderr(self, _size: int) -> bytes:
        if not self._recv_stderr_chunks:
            return b""
        return self._recv_stderr_chunks.popleft()

    def exit_status_ready(self) -> bool:
        return self.closed

    def close(self) -> None:
        self.closed = True


class _FakeSSHClient:
    def __init__(self, shells: list[_FakeShellChannel]) -> None:
        self.transport = _FakeTransport(shells)
        self.connect_calls = 0
        self.connect_kwargs: dict[str, object] = {}

    def set_missing_host_key_policy(self, _policy) -> None:
        return None

    def connect(self, **kwargs: object) -> None:
        self.connect_calls += 1
        self.connect_kwargs = kwargs

    def get_transport(self) -> _FakeTransport:
        return self.transport

    def close(self) -> None:
        self.transport.active = False


class _NoBootstrapShellChannel(_FakeShellChannel):
    def sendall(self, data: bytes | str) -> None:
        if self.closed:
            raise OSError("shell is closed")
        if isinstance(data, bytes):
            text = data.decode("utf-8")
        else:
            text = data
        self.sent.append(text)
        stripped = text.strip()
        if not stripped:
            return
        parts = shlex.split(stripped)
        if len(parts) < 3 or parts[0] != "temporal_run":
            return
        request_id = parts[1]
        helper_name = parts[2]
        helper_args = parts[3:]
        result = self.response_fn(helper_name, helper_args)
        self._recv_chunks.append(_render_shell_response(request_id, result).encode("utf-8"))
