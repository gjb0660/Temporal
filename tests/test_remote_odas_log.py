from remote_odas_support import (
    CommandResult,
    RemoteOdasController,
    _FakeSSHClient,
    _FakeShellChannel,
    _make_config,
    _make_streams,
    patch,
    unittest,
)


class TestRemoteOdasLog(unittest.TestCase):
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

    def test_clear_log_routes_to_helper_function(self) -> None:
        shell = _FakeShellChannel(
            lambda name, _args: (
                CommandResult(code=0, stdout="", stderr="")
                if name == "temporal_log_clear"
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
            result = controller.clear_log()

        self.assertEqual(result.code, 0)
        self.assertTrue(shell.sent[1].strip().endswith("temporal_log_clear"))

    def test_clear_log_surfaces_shell_error(self) -> None:
        shell = _FakeShellChannel(
            lambda name, _args: (
                CommandResult(
                    code=1, stdout="", stderr="failed to clear log file /tmp/odaslive.log\n"
                )
                if name == "temporal_log_clear"
                else CommandResult(code=0, stdout="", stderr="")
            )
        )
        fake_client = _FakeSSHClient([shell])
        controller = RemoteOdasController(
            _make_config(odas_cwd="tmp", odas_log="odaslive.log"), _make_streams()
        )

        with patch(
            "temporal.core.ssh.remote_odas.paramiko.SSHClient",
            return_value=fake_client,
        ):
            controller.connect()
            result = controller.clear_log()

        self.assertEqual(result.code, 1)
        self.assertIn("failed to clear log file", result.stderr)
