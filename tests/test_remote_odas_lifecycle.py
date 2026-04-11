from remote_odas_support import (
    CommandResult,
    RemoteOdasController,
    _FakeSSHClient,
    _FakeShellChannel,
    _make_config,
    _make_streams,
    _runtime_metadata_result,
    _valid_cfg,
    patch,
    shlex,
    unittest,
)


class TestRemoteOdasLifecycle(unittest.TestCase):
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
        self.assertEqual(controller.recording_sample_rates(), {"sp": 16000, "pf": 16000})
        self.assertIsNone(controller.recording_sample_rate_warning())
        helper_calls = [shlex.split(item.strip())[2] for item in shell.sent[1:]]
        self.assertEqual(
            helper_calls,
            ["temporal_metadata", "temporal_cat_file", "temporal_cat_file", "temporal_start"],
        )

    def test_start_odaslive_records_sample_rate_warning_without_failing(self) -> None:
        cfg_without_fs = "\n".join(
            [
                'tracked: { interface: { ip = "10.10.0.8"; port = 9000; }; };',
                'potential: { interface: { ip = "10.10.0.8"; port = 9001; }; };',
                'separated: { interface: { ip = "10.10.0.8"; port = 10000; }; };',
                'postfiltered: { interface: { ip = "10.10.0.8"; port = 10010; }; };',
            ]
        )

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
                return CommandResult(code=0, stdout=cfg_without_fs, stderr="")
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
        self.assertEqual(controller.recording_sample_rates(), {"sp": 16000, "pf": 16000})
        warning = controller.recording_sample_rate_warning()
        self.assertIsNotNone(warning)
        assert warning is not None
        self.assertIn("回退 16000Hz", warning)

    def test_start_odaslive_surfaces_pid_persistence_failure(self) -> None:
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
                return CommandResult(
                    code=1,
                    stdout="",
                    stderr="failed to write pid file /home/tester/workspace/ODAS/odas/odaslive.pid\n",
                )
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

        self.assertEqual(result.code, 1)
        self.assertIn("failed to write pid file", result.stderr)

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
