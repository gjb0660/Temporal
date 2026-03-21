import unittest
from typing import cast
from unittest.mock import MagicMock, patch

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


class SequencedRemoteOdasController(RemoteOdasController):
    def __init__(self, config: RemoteOdasConfig, streams: OdasStreamConfig) -> None:
        super().__init__(config, streams)
        self.commands: list[str] = []
        self.results: list[CommandResult] = []

    def queue_results(self, *results: CommandResult) -> None:
        self.results.extend(results)

    def _exec(self, cmd: str) -> CommandResult:
        self.commands.append(cmd)
        if self.results:
            return self.results.pop(0)
        return CommandResult(code=0, stdout="", stderr="")


class TestRemoteOdasController(unittest.TestCase):
    def test_should_validate_sink_host_is_false_for_wildcard(self) -> None:
        controller = SequencedRemoteOdasController(
            _make_config(),
            _make_streams(listen_host="0.0.0.0"),
        )

        self.assertFalse(controller._should_validate_sink_host())

    def test_should_validate_sink_host_is_true_for_specific_host(self) -> None:
        controller = SequencedRemoteOdasController(
            _make_config(),
            _make_streams(listen_host="192.168.1.50"),
        )

        self.assertTrue(controller._should_validate_sink_host())

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
        controller = SequencedRemoteOdasController(
            _make_config(odas_command="odaslive", odas_args=["-c", "odas.cfg"]),
            _make_streams(listen_host="10.10.0.8"),
        )
        controller.queue_results(
            _runtime_metadata_result(resolved_command="/usr/bin/odaslive"),
            CommandResult(
                code=0,
                stdout=_valid_cfg(host="10.10.0.8").replace("9000", "9100", 1),
                stderr="",
            ),
        )

        result = controller.start_odaslive()

        self.assertEqual(result.code, 1)
        self.assertEqual(result.stderr, "preflight: tracked sink port mismatch")
        self.assertEqual(len(controller.commands), 2)

    def test_start_odaslive_uses_wrapper_cfg_when_args_are_empty(self) -> None:
        controller = SequencedRemoteOdasController(
            _make_config(), _make_streams(listen_host="10.10.0.8")
        )
        controller.queue_results(
            _runtime_metadata_result(),
            CommandResult(
                code=0,
                stdout='#!/bin/sh\nexec odaslive -c "./configs/odas.cfg"\n',
                stderr="",
            ),
            CommandResult(code=0, stdout=_valid_cfg(host="10.10.0.8"), stderr=""),
            CommandResult(code=0, stdout="4242\n", stderr=""),
        )

        result = controller.start_odaslive()

        self.assertEqual(result.code, 0)
        self.assertEqual(len(controller.commands), 4)
        self.assertIn("cfg_cwd=workspace/ODAS/odas", controller.commands[-1])
        self.assertIn(
            './odas_loop.sh >> "$resolved_log" 2>&1 < /dev/null &', controller.commands[-1]
        )

    def test_status_validates_pid_file_instead_of_name_matching(self) -> None:
        controller = SequencedRemoteOdasController(
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
        controller = SequencedRemoteOdasController(_make_config(), _make_streams())

        controller.stop_odaslive()

        command = controller.commands[-1]
        self.assertNotIn("pkill", command)
        self.assertIn('kill "$pid"', command)
        self.assertIn("cleanup_pid", command)

    def test_read_log_tail_uses_resolved_log_path_and_clamps_lines(self) -> None:
        controller = SequencedRemoteOdasController(_make_config(), _make_streams())
        controller.read_log_tail(999)

        command = controller.commands[-1]
        self.assertIn('if [ -f "$resolved_log" ]; then tail -n 200 "$resolved_log"; fi', command)
        self.assertIn("resolve_runtime_paths >/dev/null 2>&1 || exit 0", command)


if __name__ == "__main__":
    unittest.main()
