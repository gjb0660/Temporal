import unittest
from typing import cast
from unittest.mock import MagicMock, patch

from temporal.core.models import RemoteOdasConfig
from temporal.core.ssh.remote_odas import CommandResult, RemoteOdasController


class RecordingRemoteOdasController(RemoteOdasController):
    def __init__(self, config: RemoteOdasConfig) -> None:
        super().__init__(config)
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
    odas_command = cast(str, overrides.get("odas_command", "odaslive"))
    odas_args = cast(list[str], overrides.get("odas_args", ["-c", "odas.cfg"]))
    odas_cwd = cast(str | None, overrides.get("odas_cwd", "/opt/odas"))
    odas_log = cast(str, overrides.get("odas_log", "/tmp/custom-odas.log"))
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
        controller = RemoteOdasController(cfg)

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

    def test_pid_path_replaces_log_extension(self) -> None:
        controller = RecordingRemoteOdasController(_make_config(odas_log="/tmp/odaslive.log"))
        self.assertEqual(controller._pid_path(), "/tmp/odaslive.pid")

    def test_pid_path_appends_extension_when_log_has_none(self) -> None:
        controller = RecordingRemoteOdasController(_make_config(odas_log="/tmp/odaslive"))
        self.assertEqual(controller._pid_path(), "/tmp/odaslive.pid")

    def test_start_odaslive_writes_pid_to_derived_pid_file(self) -> None:
        controller = RecordingRemoteOdasController(_make_config(odas_log="/tmp/custom-odas.log"))

        controller.start_odaslive()

        command = controller.commands[-1]
        self.assertNotIn("nohup", command)
        self.assertIn("pid_path=/tmp/custom-odas.pid", command)
        self.assertIn('printf "%s\\n" "$pid" > "$pid_path"', command)
        self.assertIn("odaslive -c odas.cfg >> /tmp/custom-odas.log 2>&1 < /dev/null &", command)

    def test_start_odaslive_reuses_existing_valid_pid_file_before_launching(self) -> None:
        controller = RecordingRemoteOdasController(_make_config())

        controller.start_odaslive()

        command = controller.commands[-1]
        self.assertIn("if load_valid_pid; then", command)
        self.assertIn("printf", command)
        self.assertIn("exit 0", command)

    def test_start_odaslive_applies_configured_working_directory_to_relative_paths(self) -> None:
        controller = RecordingRemoteOdasController(
            _make_config(odas_log="odaslive.log", odas_cwd="/opt/odas")
        )

        controller.start_odaslive()

        issued = controller.commands[-1]
        self.assertIn("cd /opt/odas || exit 1", issued)
        self.assertIn("pid_path=odaslive.pid", issued)
        self.assertIn("odaslive.log", issued)

    def test_status_validates_pid_cmdline_and_cwd(self) -> None:
        controller = RecordingRemoteOdasController(
            _make_config(
                odas_command="/opt/odas/bin/custom-odas",
                odas_args=["-c", "/opt/odas/config/odas.cfg", "-v"],
                odas_cwd="/opt/odas",
                odas_log="/tmp/custom-odas.log",
            )
        )

        controller.status()

        command = controller.commands[-1]
        self.assertIn("pid_path=/tmp/custom-odas.pid", command)
        self.assertIn('kill -0 "$pid"', command)
        self.assertIn("/proc/$pid/cmdline", command)
        self.assertIn("/opt/odas/bin/custom-odas", command)
        self.assertIn("/opt/odas/config/odas.cfg", command)
        self.assertIn("/proc/$pid/cwd", command)
        self.assertIn('expected_cwd="$(pwd -P)"', command)
        self.assertIn("cleanup_pid", command)

    def test_status_skips_cwd_validation_when_cwd_is_not_configured(self) -> None:
        controller = RecordingRemoteOdasController(
            _make_config(odas_cwd=None, odas_log="/tmp/custom-odas.log")
        )

        controller.status()

        command = controller.commands[-1]
        self.assertNotIn("/proc/$pid/cwd", command)
        self.assertNotIn("expected_cwd", command)

    def test_stop_odaslive_targets_only_pid_file_instance(self) -> None:
        controller = RecordingRemoteOdasController(_make_config())

        controller.stop_odaslive()

        command = controller.commands[-1]
        self.assertNotIn("pkill", command)
        self.assertIn("if ! load_valid_pid; then", command)
        self.assertIn('kill "$pid"', command)
        self.assertIn("cleanup_pid", command)

    def test_read_log_tail_uses_configured_log_path(self) -> None:
        controller = RecordingRemoteOdasController(_make_config(odas_log="/tmp/custom-odas.log"))
        result = controller.read_log_tail(50)
        self.assertEqual(result.stdout, "4242\n")
        self.assertIn("tail -n 50", controller.commands[-1])
        self.assertIn("/tmp/custom-odas.log", controller.commands[-1])

    def test_read_log_tail_clamps_requested_line_count(self) -> None:
        controller = RecordingRemoteOdasController(_make_config())
        controller.read_log_tail(999)
        self.assertIn("tail -n 200", controller.commands[-1])


if __name__ == "__main__":
    unittest.main()
