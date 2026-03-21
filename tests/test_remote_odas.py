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


def _valid_cfg(host: str = "10.10.0.8") -> str:
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
            "  interface: {",
            '    type = "socket";',
            f'    ip = "{host}";',
            "    port = 10000;",
            "  };",
            "};",
            "postfiltered: {",
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


class TestRemoteOdasController(unittest.TestCase):
    def test_should_validate_sink_host_is_false_for_wildcard(self) -> None:
        controller = RemoteOdasController(_make_config(), _make_streams(listen_host="0.0.0.0"))
        self.assertFalse(controller._should_validate_sink_host())

    def test_should_validate_sink_host_is_true_for_specific_host(self) -> None:
        controller = RemoteOdasController(
            _make_config(),
            _make_streams(listen_host="192.168.1.50"),
        )
        self.assertTrue(controller._should_validate_sink_host())

    def test_connect_passes_none_for_username_and_key_when_empty(self) -> None:
        fake_shell = _FakeShellChannel()
        fake_client = _FakeSSHClient([fake_shell])
        cfg = _make_config(username=None, private_key=None)
        controller = RemoteOdasController(cfg, _make_streams())

        with patch(
            "temporal.core.ssh.remote_odas.paramiko.SSHClient",
            return_value=fake_client,
        ):
            controller.connect()

        self.assertEqual(fake_client.connect_calls, 1)
        self.assertEqual(fake_client.connect_kwargs["hostname"], "127.0.0.1")
        self.assertEqual(fake_client.connect_kwargs["port"], 22)
        self.assertEqual(fake_client.connect_kwargs["timeout"], 8)
        self.assertIsNone(fake_client.connect_kwargs["username"])
        self.assertIsNone(fake_client.connect_kwargs["key_filename"])
        self.assertEqual(fake_client.transport.open_session_calls, 1)
        self.assertEqual(fake_shell.exec_commands, ["sh"])
        self.assertIn("temporal_run()", fake_shell.sent[0])

    def test_connect_bootstraps_control_shell_once_and_reuses_it(self) -> None:
        shell = _FakeShellChannel(lambda _name, _args: CommandResult(0, "4242\n", ""))
        fake_client = _FakeSSHClient([shell])
        controller = RemoteOdasController(_make_config(), _make_streams())

        with patch(
            "temporal.core.ssh.remote_odas.paramiko.SSHClient",
            return_value=fake_client,
        ):
            controller.connect()
            controller.status()
            controller.read_log_tail(80)

        self.assertEqual(fake_client.transport.open_session_calls, 1)
        self.assertEqual(shell.exec_commands, ["sh"])
        self.assertIn("resolve_runtime_paths()", shell.sent[0])
        self.assertTrue(shell.sent[1].strip().startswith("temporal_run "))
        self.assertTrue(shell.sent[2].strip().startswith("temporal_run "))
        self.assertNotIn("resolve_runtime_paths()", shell.sent[1])
        self.assertNotIn("resolve_runtime_paths()", shell.sent[2])

    def test_helper_shell_renders_stop_body_without_python_concat_fragments(self) -> None:
        controller = RemoteOdasController(_make_config(), _make_streams())

        helper = controller._helper_shell

        self.assertIn('if [ "$attempt" -ge 10 ]; then', helper)
        self.assertIn("sleep 0.1", helper)
        self.assertIn("TEMPORAL_BOOTSTRAP_READY", helper)
        self.assertNotIn("+ str(self._STOP_WAIT_ATTEMPTS)", helper)
        self.assertNotIn("+ str(self._STOP_WAIT_SEC)", helper)
        self.assertNotIn("__ARG_CHECKS__", helper)

    def test_helper_shell_launches_remote_command_in_dedicated_process_group(self) -> None:
        controller = RemoteOdasController(_make_config(), _make_streams())

        helper = controller._helper_shell

        self.assertIn('setsid ./odas_loop.sh >> "$resolved_log" 2>&1 < /dev/null &', helper)
        self.assertIn('kill -TERM -- "-$pid"', helper)
        self.assertIn(
            'while kill -0 -- "-$pid" 2>/dev/null || kill -0 "$pid" 2>/dev/null; do', helper
        )

    def test_control_shell_rebootstraps_after_shell_loss(self) -> None:
        first_shell = _FakeShellChannel()
        second_shell = _FakeShellChannel(lambda _name, _args: CommandResult(0, "4242\n", ""))
        fake_client = _FakeSSHClient([first_shell, second_shell])
        controller = RemoteOdasController(_make_config(), _make_streams())

        with patch(
            "temporal.core.ssh.remote_odas.paramiko.SSHClient",
            return_value=fake_client,
        ):
            controller.connect()
            first_shell.closed = True
            result = controller.status()

        self.assertEqual(result.stdout, "4242\n")
        self.assertEqual(fake_client.transport.open_session_calls, 2)
        self.assertEqual(second_shell.exec_commands, ["sh"])
        self.assertIn("temporal_run()", second_shell.sent[0])
        self.assertTrue(second_shell.sent[1].strip().startswith("temporal_run "))

    def test_connect_reports_bootstrap_timeout_from_noninteractive_sh_session(self) -> None:
        shell = _NoBootstrapShellChannel()
        fake_client = _FakeSSHClient([shell])
        controller = RemoteOdasController(_make_config(), _make_streams())

        with patch(
            "temporal.core.ssh.remote_odas.paramiko.SSHClient",
            return_value=fake_client,
        ):
            with self.assertRaisesRegex(RuntimeError, "SSH control shell timed out"):
                controller.connect()

        self.assertEqual(fake_client.transport.open_session_calls, 1)
        self.assertEqual(shell.exec_commands, ["sh"])

    def test_sink_targets_reject_comment_only_port_matches(self) -> None:
        cfg_text = "\n".join(
            [
                '# tracked: { interface: { ip = "10.10.0.8"; port = 9000; }; };',
                '# potential: { interface: { ip = "10.10.0.8"; port = 9001; }; };',
                '# separated: { interface: { ip = "10.10.0.8"; port = 10000; }; };',
                '# postfiltered: { interface: { ip = "10.10.0.8"; port = 10010; }; };',
                'tracked: { interface: { ip = "10.10.0.8"; port = 9100; }; };',
                'potential: { interface: { ip = "10.10.0.8"; port = 9101; }; };',
                'separated: { interface: { ip = "10.10.0.8"; port = 10100; }; };',
                'postfiltered: { interface: { ip = "10.10.0.8"; port = 10110; }; };',
            ]
        )

        self.assertEqual(
            _sink_targets_match(cfg_text, _make_streams(listen_host="10.10.0.8")),
            "preflight: tracked sink port mismatch",
        )

    def test_sink_targets_skip_host_match_for_wildcard_but_keep_port_checks(self) -> None:
        cfg_text = _valid_cfg(host="127.0.0.1")
        self.assertIsNone(_sink_targets_match(cfg_text, _make_streams(listen_host="0.0.0.0")))

    def test_sink_targets_require_matching_ports_for_wildcard_bind(self) -> None:
        cfg_text = "\n".join(
            [
                'tracked: { interface: { ip = "127.0.0.1"; port = 9100; }; };',
                'potential: { interface: { ip = "127.0.0.1"; port = 9001; }; };',
                'separated: { interface: { ip = "127.0.0.1"; port = 10000; }; };',
                'postfiltered: { interface: { ip = "127.0.0.1"; port = 10010; }; };',
            ]
        )

        self.assertEqual(
            _sink_targets_match(cfg_text, _make_streams(listen_host="0.0.0.0")),
            "preflight: tracked sink port mismatch",
        )

    def test_sink_targets_require_real_block_names(self) -> None:
        cfg_text = "\n".join(
            [
                'tracks: { interface: { ip = "10.10.0.8"; port = 9000; }; };',
                'hops: { interface: { ip = "10.10.0.8"; port = 9001; }; };',
                'audio_sep: { interface: { ip = "10.10.0.8"; port = 10000; }; };',
                'audio_pf: { interface: { ip = "10.10.0.8"; port = 10010; }; };',
            ]
        )

        self.assertEqual(
            _sink_targets_match(cfg_text, _make_streams(listen_host="10.10.0.8")),
            "preflight: tracked sink missing",
        )

    def test_extract_wrapper_cfg_path(self) -> None:
        wrapper_text = '#!/bin/sh\nexec odaslive -v -c "./configs/odas.cfg"\n'
        self.assertEqual(_extract_wrapper_cfg_path(wrapper_text), "./configs/odas.cfg")

    def test_start_odaslive_returns_preflight_failure_without_launch(self) -> None:
        def response_fn(name: str, args: list[str]) -> CommandResult:
            if name == "temporal_metadata":
                return _runtime_metadata_result(resolved_command="/usr/bin/odaslive")
            if name == "temporal_cat_file":
                return CommandResult(
                    code=0,
                    stdout=_valid_cfg(host="10.10.0.8").replace("9000", "9100", 1),
                    stderr="",
                )
            if name == "temporal_start":
                return CommandResult(code=0, stdout="4242\n", stderr="")
            return CommandResult(code=0, stdout="", stderr="")

        shell = _FakeShellChannel(response_fn)
        fake_client = _FakeSSHClient([shell])
        controller = RemoteOdasController(
            _make_config(odas_command="odaslive", odas_args=["-c", "odas.cfg"]),
            _make_streams(listen_host="10.10.0.8"),
        )

        with patch(
            "temporal.core.ssh.remote_odas.paramiko.SSHClient",
            return_value=fake_client,
        ):
            controller.connect()
            result = controller.start_odaslive()

        self.assertEqual(result.code, 1)
        self.assertEqual(result.stderr, "preflight: tracked sink port mismatch")
        self.assertEqual(
            [shlex.split(item.strip())[2] for item in shell.sent[1:]],
            ["temporal_metadata", "temporal_cat_file"],
        )

    def test_start_odaslive_uses_wrapper_cfg_when_args_are_empty(self) -> None:
        def response_fn(name: str, args: list[str]) -> CommandResult:
            if name == "temporal_metadata":
                return _runtime_metadata_result()
            if name == "temporal_cat_file" and args[0].endswith("odas_loop.sh"):
                return CommandResult(
                    code=0,
                    stdout='#!/bin/sh\nexec odaslive -c "./configs/odas.cfg"\n',
                    stderr="",
                )
            if name == "temporal_cat_file" and args[0].endswith("configs/odas.cfg"):
                return CommandResult(code=0, stdout=_valid_cfg(host="10.10.0.8"), stderr="")
            if name == "temporal_start":
                return CommandResult(code=0, stdout="4242\n", stderr="")
            return CommandResult(code=1, stdout="", stderr="unexpected helper")

        shell = _FakeShellChannel(response_fn)
        fake_client = _FakeSSHClient([shell])
        controller = RemoteOdasController(_make_config(), _make_streams(listen_host="10.10.0.8"))

        with patch(
            "temporal.core.ssh.remote_odas.paramiko.SSHClient",
            return_value=fake_client,
        ):
            controller.connect()
            result = controller.start_odaslive()

        self.assertEqual(result.code, 0)
        helper_calls = [shlex.split(item.strip())[2] for item in shell.sent[1:]]
        self.assertEqual(
            helper_calls,
            ["temporal_metadata", "temporal_cat_file", "temporal_cat_file", "temporal_start"],
        )

    def test_stop_odaslive_returns_shell_failure_as_is(self) -> None:
        shell = _FakeShellChannel(
            lambda name, _args: (
                CommandResult(code=1, stdout="", stderr="failed to stop pid 4242\n")
                if name == "temporal_stop"
                else CommandResult(code=0, stdout="", stderr="")
            )
        )
        fake_client = _FakeSSHClient([shell])
        controller = RemoteOdasController(_make_config(), _make_streams())

        with patch(
            "temporal.core.ssh.remote_odas.paramiko.SSHClient",
            return_value=fake_client,
        ):
            controller.connect()
            result = controller.stop_odaslive()

        self.assertEqual(result.code, 1)
        self.assertIn("failed to stop pid 4242", result.stderr)

    def test_read_log_tail_uses_clamped_lines_without_resending_helper_body(self) -> None:
        shell = _FakeShellChannel(
            lambda name, args: (
                CommandResult(code=0, stdout="line\n", stderr="")
                if name == "temporal_log_tail" and args == ["200"]
                else CommandResult(code=0, stdout="", stderr="")
            )
        )
        fake_client = _FakeSSHClient([shell])
        controller = RemoteOdasController(_make_config(), _make_streams())

        with patch(
            "temporal.core.ssh.remote_odas.paramiko.SSHClient",
            return_value=fake_client,
        ):
            controller.connect()
            result = controller.read_log_tail(999)

        self.assertEqual(result.stdout, "line\n")
        self.assertTrue(shell.sent[1].strip().endswith("temporal_log_tail 200"))
        self.assertNotIn("resolve_runtime_paths()", shell.sent[1])


if __name__ == "__main__":
    unittest.main()
