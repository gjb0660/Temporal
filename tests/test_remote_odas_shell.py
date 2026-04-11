from remote_odas_support import (
    CommandResult,
    RemoteOdasController,
    _FakeSSHClient,
    _FakeShellChannel,
    _NoBootstrapShellChannel,
    _make_config,
    _make_streams,
    patch,
    unittest,
)


class TestRemoteOdasShell(unittest.TestCase):
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

    def test_helper_shell_uses_pid_only_running_truth_without_proc_identity_checks(self) -> None:
        controller = RemoteOdasController(
            _make_config(odas_command="./build/bin/odaslive", odas_args=["-c", "config/odas.cfg"]),
            _make_streams(),
        )

        helper = controller._helper_shell

        self.assertIn('if [ ! -f "$pid_path" ]; then', helper)
        self.assertIn('case "$pid" in', helper)
        self.assertIn("''|*[!0-9]*)", helper)
        self.assertIn('if ! kill -0 "$pid" 2>/dev/null; then', helper)
        self.assertNotIn("/proc/$pid/cmdline", helper)
        self.assertNotIn("/proc/$pid/cwd", helper)
        self.assertNotIn("/proc/$pid/exe", helper)
        self.assertNotIn("actual_cmdline", helper)
        self.assertIn(
            "temporal_status() {\n"
            "    resolve_runtime_paths >/dev/null 2>&1 || return 0\n"
            "    if ! load_valid_pid; then",
            helper,
        )
        self.assertIn(
            "temporal_stop() {\n"
            "    resolve_runtime_paths >/dev/null 2>&1 || return 0\n"
            "    if ! load_valid_pid; then",
            helper,
        )

    def test_helper_shell_requires_pid_file_write_and_readback_consistency(self) -> None:
        controller = RemoteOdasController(_make_config(), _make_streams())

        helper = controller._helper_shell

        self.assertIn('if ! printf "%s\\n" "$pid" > "$pid_path"; then', helper)
        self.assertIn("failed to write pid file %s\\n", helper)
        self.assertIn(
            "persisted_pid=\"$(tr -d '[:space:]' < \"$pid_path\" 2>/dev/null || printf '')\"",
            helper,
        )
        self.assertIn('if [ "$persisted_pid" != "$pid" ]; then', helper)
        self.assertIn("failed to persist pid file %s\\n", helper)

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
