import unittest

from temporal.core.models import RemoteOdasConfig
from temporal.core.ssh.remote_odas import CommandResult, RemoteOdasController


class FakeRemoteOdasController(RemoteOdasController):
    def __init__(self) -> None:
        cfg = RemoteOdasConfig(
            host="127.0.0.1",
            port=22,
            username="tester",
            private_key="dummy",
            odas_command="odaslive -c odas.cfg",
        )
        super().__init__(cfg)
        self.commands: list[str] = []

    def _exec(self, cmd: str) -> CommandResult:
        self.commands.append(cmd)
        return CommandResult(code=0, stdout="log line", stderr="")


class TestRemoteOdasController(unittest.TestCase):
    def test_read_log_tail_uses_tail_command(self) -> None:
        controller = FakeRemoteOdasController()
        result = controller.read_log_tail(50)
        self.assertEqual(result.stdout, "log line")
        self.assertEqual(
            controller.commands[-1],
            "sh -lc 'if [ -f /tmp/odaslive.log ]; then tail -n 50 /tmp/odaslive.log; fi'",
        )

    def test_read_log_tail_clamps_requested_line_count(self) -> None:
        controller = FakeRemoteOdasController()
        controller.read_log_tail(999)
        self.assertIn("tail -n 200", controller.commands[-1])


if __name__ == "__main__":
    unittest.main()
