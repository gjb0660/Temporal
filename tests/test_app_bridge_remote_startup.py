from app_bridge_integration_support import (
    AppBridgeIntegrationBase,
    AutoRecorder,
    CommandResult,
    FakeClient,
    _BootstrapFailingRemoteOdasController,
    _FailingOdasClient,
    _FakeRemoteOdasController,
    tempfile,
)


class TestAppBridgeRemoteStartup(AppBridgeIntegrationBase):
    def test_start_remote_starts_local_listeners_before_remote_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            client = bridge._client
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            self.assertIsInstance(client, FakeClient)

            bridge.startRemoteOdas()

            self.assertTrue(bridge.streamsActive)
            self.assertEqual(client.start_calls, 1)
            self.assertEqual(remote.start_calls, 1)

    def test_start_streams_does_not_require_ssh_connection(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)

            bridge.startStreams()

            self.assertTrue(bridge.streamsActive)
            self.assertTrue(bridge.canToggleStreams)
            self.assertEqual(bridge.controlPhase, "streams_listening")
            self.assertEqual(bridge.controlDataState, "listening_remote_not_running")
            lines = self._summary_lines(bridge)
            self.assertIn("正在监听", lines[0])
            self.assertIn("监听中，远端未启动", lines[1])

    def test_connect_remote_reports_control_channel_init_failure_without_labeling_ssh_failure(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder, remote_cls=_BootstrapFailingRemoteOdasController)

            bridge.connectRemote()

            self.assertFalse(bridge.remoteConnected)
            self.assertEqual(bridge.controlPhase, "ssh_disconnected")
            self.assertEqual(bridge.controlDataState, "unavailable")
            lines = self._summary_lines(bridge)
            self.assertIn("远程控制通道初始化失败", lines[0])
            self.assertIn("不可用", lines[1])
            self.assertEqual(bridge.remoteLogLines, ["远程控制通道初始化失败"])

    def test_start_streams_keeps_inactive_when_listener_bind_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder, client_cls=_FailingOdasClient)
            bridge.connectRemote()

            bridge.startStreams()

            self.assertFalse(bridge.streamsActive)
            self.assertEqual(bridge.controlPhase, "error")
            self.assertEqual(bridge.controlDataState, "unavailable")
            lines = self._summary_lines(bridge)
            self.assertIn("本地监听启动失败", lines[0])
            self.assertIn("bind failed", lines[0])
            self.assertIn("不可用", lines[1])

    def test_start_remote_does_not_launch_remote_when_listener_start_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder, client_cls=_FailingOdasClient)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)

            bridge.startRemoteOdas()

            self.assertFalse(bridge.streamsActive)
            self.assertFalse(bridge.odasStarting)
            self.assertFalse(bridge.odasRunning)
            self.assertEqual(remote.start_calls, 0)
            self.assertEqual(bridge.controlPhase, "error")
            self.assertEqual(bridge.controlDataState, "unavailable")
            lines = self._summary_lines(bridge)
            self.assertIn("本地监听启动失败", lines[0])

    def test_preflight_failure_uses_humanized_sink_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.log_output = "Sink tracks: Cannot connect to server\n"
            remote.start_result = CommandResult(
                code=1,
                stdout="",
                stderr="preflight: sink host mismatch",
            )

            bridge.startRemoteOdas()

            self.assertFalse(bridge.odasStarting)
            self.assertFalse(bridge.odasRunning)
            self.assertEqual(bridge.controlPhase, "error")
            self.assertEqual(bridge.controlDataState, "unavailable")
            lines = self._summary_lines(bridge)
            self.assertTrue(lines[0].startswith("启动失败:"))
            self.assertIn("Temporal", lines[0])
            self.assertNotIn("preflight:", lines[0])

    def test_start_failure_uses_log_reason_when_process_never_appears(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.log_output = "sh: line 1: odaslive: command not found\n"

            bridge.startRemoteOdas()
            self.assertTrue(bridge.odasStarting)
            self.assertFalse(bridge.odasRunning)

            self._drain_startup(bridge)

            self.assertFalse(bridge.odasStarting)
            self.assertFalse(bridge.odasRunning)
            self.assertEqual(bridge.controlPhase, "error")
            self.assertEqual(bridge.controlDataState, "unavailable")
            self.assertIn("启动失败: 远程命令不存在或未安装", self._summary_lines(bridge)[0])

    def test_start_transitions_from_starting_to_running_after_pid_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.start_status_sequence = ["", "", "4242\n"]

            bridge.startRemoteOdas()
            self.assertTrue(bridge.odasStarting)
            self.assertEqual(bridge.controlPhase, "odas_starting")
            self.assertEqual(bridge.controlDataState, "running_waiting_sst")
            bridge._verify_odas_startup()

            self.assertFalse(bridge.odasStarting)
            self.assertTrue(bridge.odasRunning)
            self.assertTrue(bridge.streamsActive)
            self.assertEqual(bridge.controlPhase, "streams_listening")
            self.assertEqual(bridge.controlDataState, "running_waiting_sst")
            lines = self._summary_lines(bridge)
            self.assertIn("监听", lines[0])
            self.assertIn("等待 SST", lines[1])

    def test_connect_remote_without_pid_file_does_not_adopt_instance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)

            bridge.connectRemote()

            self.assertTrue(bridge.remoteConnected)
            self.assertFalse(bridge.odasRunning)
            self.assertEqual(bridge.controlPhase, "ssh_connected_idle")
            self.assertEqual(bridge.controlDataState, "inactive")
            self.assertIn("未运行", self._summary_lines(bridge)[0])

    def test_connect_remote_adopts_instance_with_valid_pid_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()

            self.assertTrue(bridge.remoteConnected)
            self.assertTrue(bridge.odasRunning)
            self.assertEqual(bridge.controlPhase, "odas_running")
            self.assertEqual(bridge.controlDataState, "inactive")
            self.assertIn("运行中", self._summary_lines(bridge)[0])

    def test_health_sync_marks_remote_not_running_after_instance_exit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()
            self.assertTrue(bridge.odasRunning)

            remote.status_output = ""
            bridge._poll_remote_log()

            self.assertFalse(bridge.odasRunning)
            self.assertEqual(bridge.controlPhase, "ssh_connected_idle")
            self.assertEqual(bridge.controlDataState, "inactive")
            self.assertIn("未运行", self._summary_lines(bridge)[0])
