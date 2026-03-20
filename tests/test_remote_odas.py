import unittest
from unittest.mock import MagicMock, patch

from temporal.core.models import RemoteOdasConfig
from temporal.core.ssh.remote_odas import CommandResult, RemoteOdasController


class FakeRemoteOdasController(RemoteOdasController):
    def __init__(self) -> None:
        cfg = RemoteOdasConfig(
            host="127.0.0.1",
            port=22,
            username="tester",
            private_key="dummy",
            odas_command="odaslive",
            odas_args=["-c", "odas.cfg"],
            odas_cwd="/opt/odas",
            odas_log="/tmp/custom-odas.log",
        )
        super().__init__(cfg)
        self.commands: list[str] = []

    def _exec(self, cmd: str) -> CommandResult:
        self.commands.append(cmd)
        return CommandResult(code=0, stdout="log line", stderr="")


class TestRemoteOdasController(unittest.TestCase):
    def test_start_odaslive_runs_in_background_without_nohup(self) -> None:
        controller = FakeRemoteOdasController()
        controller.start_odaslive()
        command = controller.commands[-1]
        self.assertNotIn("nohup", command)
        self.assertIn("odaslive -c odas.cfg >> /tmp/custom-odas.log 2>&1 < /dev/null", command)
        self.assertIn("/tmp/custom-odas.log", command)
        self.assertIn("& echo $!", command)

    def test_connect_passes_none_for_username_and_key_when_empty(self) -> None:
        cfg = RemoteOdasConfig(
            host="127.0.0.1",
            port=22,
            username=None,
            private_key=None,
            odas_command="odaslive",
            odas_args=["-c", "odas.cfg"],
        )
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

    def test_start_odaslive_uses_configured_command(self) -> None:
        cfg = RemoteOdasConfig(
            host="127.0.0.1",
            port=22,
            username="tester",
            private_key="dummy",
            odas_command="/opt/odas/bin/custom-odas",
            odas_args=["-c", "odas.cfg"],
            odas_cwd="/opt/odas",
            odas_log="/tmp/custom-odas.log",
        )
        controller = RemoteOdasController(cfg)
        controller._exec = MagicMock(return_value=CommandResult(code=0, stdout="123\n", stderr=""))

        controller.start_odaslive()

        issued = controller._exec.call_args.args[0]
        self.assertIn("/opt/odas/bin/custom-odas", issued)

    def test_start_odaslive_applies_configured_working_directory_to_relative_log(self) -> None:
        cfg = RemoteOdasConfig(
            host="127.0.0.1",
            port=22,
            username="tester",
            private_key="dummy",
            odas_command="odaslive",
            odas_args=["-c", "odas.cfg"],
            odas_cwd="/opt/odas",
            odas_log="odaslive.log",
        )
        controller = RemoteOdasController(cfg)
        controller._exec = MagicMock(return_value=CommandResult(code=0, stdout="123\n", stderr=""))

        controller.start_odaslive()

        issued = controller._exec.call_args.args[0]
        self.assertIn("cd /opt/odas || exit 1", issued)
        self.assertIn("odaslive.log", issued)
        self.assertIn("odaslive -c odas.cfg >> odaslive.log 2>&1 < /dev/null", issued)

    def test_read_log_tail_uses_configured_log_path(self) -> None:
        controller = FakeRemoteOdasController()
        result = controller.read_log_tail(50)
        self.assertEqual(result.stdout, "log line")
        self.assertIn("tail -n 50", controller.commands[-1])
        self.assertIn("/tmp/custom-odas.log", controller.commands[-1])

    def test_read_log_tail_clamps_requested_line_count(self) -> None:
        controller = FakeRemoteOdasController()
        controller.read_log_tail(999)
        self.assertIn("tail -n 200", controller.commands[-1])

    def test_status_uses_configured_process_name(self) -> None:
        controller = FakeRemoteOdasController()
        controller.status()
        command = controller.commands[-1]
        self.assertIn("pgrep -af odaslive || true", command)

    def test_stop_odaslive_uses_configured_process_name(self) -> None:
        cfg = RemoteOdasConfig(
            host="127.0.0.1",
            port=22,
            username="tester",
            private_key="dummy",
            odas_command="/opt/odas/bin/custom-odas",
            odas_args=["-c", "odas.cfg"],
        )
        controller = RemoteOdasController(cfg)
        controller._exec = MagicMock(return_value=CommandResult(code=0, stdout="", stderr=""))

        controller.stop_odaslive()

        issued = controller._exec.call_args.args[0]
        self.assertEqual(issued, "pkill -f custom-odas || true")


if __name__ == "__main__":
    unittest.main()
