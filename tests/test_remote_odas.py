import unittest
from typing import cast
from unittest.mock import MagicMock, patch

from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig
from temporal.core.ssh.remote_odas import CommandResult, RemoteOdasController


def _make_streams(listen_host: str = "192.168.1.50") -> OdasStreamConfig:
    return OdasStreamConfig(
        sst=OdasEndpoint(host=listen_host, port=9000),
        ssl=OdasEndpoint(host=listen_host, port=9001),
        sss_sep=OdasEndpoint(host=listen_host, port=10000),
        sss_pf=OdasEndpoint(host=listen_host, port=10010),
    )


class RecordingRemoteOdasController(RemoteOdasController):
    def __init__(self, config: RemoteOdasConfig, streams: OdasStreamConfig) -> None:
        super().__init__(config, streams)
        self.commands: list[str] = []
        self.result = CommandResult(code=0, stdout="4242\n", stderr="")

    def _exec(self, cmd: str) -> CommandResult:
        self.commands.append(cmd)
        return self.result


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


class TestRemoteOdasController(unittest.TestCase):
    def test_connect_passes_none_for_username_and_key_when_empty(self) -> None:
        cfg = _make_config(username=None, private_key=None)
        controller = RemoteOdasController(cfg, _make_streams())

        with patch("temporal.core.ssh.remote_odas.paramiko.SSHClient") as ssh_client_cls:
            ssh_client = MagicMock()
            ssh_client_cls.return_value = ssh_client

            controller.connect()

            kwargs = ssh_client.connect.call_args.kwargs
            self.assertEqual(kwargs["hostname"], "127.0.0.1")
            self.assertEqual(kwargs["port"], 22)
            self.assertEqual(kwargs["timeout"], 8)
            self.assertIsNone(kwargs["username"])
            self.assertIsNone(kwargs["key_filename"])

    def test_start_odaslive_resolves_relative_cwd_from_home_and_derives_pid_path(self) -> None:
        controller = RecordingRemoteOdasController(_make_config(), _make_streams())

        controller.start_odaslive()

        command = controller.commands[-1]
        self.assertIn("cfg_cwd=workspace/ODAS/odas", command)
        self.assertIn("$HOME/$path_input", command)
        self.assertIn('pid_file="${log_file%.*}.pid"', command)
        self.assertIn('./odas_loop.sh >> "$resolved_log" 2>&1 < /dev/null &', command)

    def test_start_odaslive_validates_sink_host_and_ports_before_launch(self) -> None:
        controller = RecordingRemoteOdasController(
            _make_config(odas_command="odaslive", odas_args=["-c", "odas.cfg"]),
            _make_streams(listen_host="10.10.0.8"),
        )

        controller.start_odaslive()

        command = controller.commands[-1]
        self.assertIn("preflight_or_exit || exit 1", command)
        self.assertIn("listen_host=10.10.0.8", command)
        self.assertIn("expected_sst_port=9000", command)
        self.assertIn("expected_ssl_port=9001", command)
        self.assertIn("expected_sep_port=10000", command)
        self.assertIn("expected_pf_port=10010", command)
        self.assertIn("preflight: sink host mismatch", command)
        self.assertIn("preflight: %s sink port mismatch", command)
        self.assertIn("cfg_arg_path=odas.cfg", command)

    def test_start_odaslive_extracts_cfg_path_from_wrapper_when_args_are_empty(self) -> None:
        controller = RecordingRemoteOdasController(_make_config(), _make_streams())

        controller.start_odaslive()

        command = controller.commands[-1]
        self.assertIn("grep -Eo", command)
        self.assertIn("preflight: odas config path missing", command)
        self.assertIn("preflight: odas config file missing", command)

    def test_status_validates_pid_file_instead_of_name_matching(self) -> None:
        controller = RecordingRemoteOdasController(
            _make_config(odas_command="odaslive", odas_args=["-c", "/opt/odas/odas.cfg"]),
            _make_streams(),
        )

        controller.status()

        command = controller.commands[-1]
        self.assertNotIn("pgrep", command)
        self.assertIn('if [ ! -f "$pid_path" ]; then', command)
        self.assertIn('kill -0 "$pid"', command)
        self.assertIn("/proc/$pid/cmdline", command)
        self.assertIn('grep -Fxq -- "$cfg_command"', command)

    def test_stop_odaslive_targets_pid_file_identity_only(self) -> None:
        controller = RecordingRemoteOdasController(_make_config(), _make_streams())

        controller.stop_odaslive()

        command = controller.commands[-1]
        self.assertNotIn("pkill", command)
        self.assertIn('kill "$pid"', command)
        self.assertIn("cleanup_pid", command)

    def test_read_log_tail_uses_resolved_log_path_and_clamps_lines(self) -> None:
        controller = RecordingRemoteOdasController(_make_config(), _make_streams())
        controller.read_log_tail(999)

        command = controller.commands[-1]
        self.assertIn('if [ -f "$resolved_log" ]; then tail -n 200 "$resolved_log"; fi', command)
        self.assertIn("resolve_runtime_paths >/dev/null 2>&1 || exit 0", command)


if __name__ == "__main__":
    unittest.main()
