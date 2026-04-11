from app_bridge_integration_support import (
    AppBridgeIntegrationBase,
    AutoRecorder,
    _FakeRemoteOdasController,
    tempfile,
)


class TestAppBridgeRemoteStop(AppBridgeIntegrationBase):
    def test_stop_remote_odas_keeps_listener_active(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()
            bridge.startStreams()
            bridge.stopRemoteOdas()

            self.assertFalse(bridge.odasRunning)
            self.assertTrue(bridge.streamsActive)
            self.assertEqual(remote.stop_calls, 1)
            self.assertEqual(bridge.controlPhase, "streams_listening")
            self.assertEqual(bridge.controlDataState, "listening_remote_not_running")
            self.assertIn("监听", self._summary_lines(bridge)[0])

    def test_stop_remote_failure_does_not_clear_running_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"
            remote.keep_running_after_stop = True

            bridge.connectRemote()
            bridge.stopRemoteOdas()

            self.assertTrue(bridge.odasRunning)
            self.assertEqual(bridge.controlPhase, "error")
            self.assertEqual(bridge.controlDataState, "unavailable")
            self.assertIn("远程 odaslive 停止失败", self._summary_lines(bridge)[0])

    def test_stop_remote_keeps_running_when_status_check_loses_control_channel(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()
            remote.status_exception = RuntimeError("SSH control shell lost")

            bridge.stopRemoteOdas()

            self.assertTrue(bridge.odasRunning)
            self.assertFalse(bridge.remoteConnected)
            self.assertTrue(bridge.canToggleStreams)
            self.assertEqual(bridge.controlPhase, "error")
            self.assertEqual(bridge.controlDataState, "unavailable")
            self.assertIn("停止失败: 远程控制通道已断开", self._summary_lines(bridge)[0])

    def test_toggle_remote_reconnects_control_channel_before_stopping_running_remote(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()
            self.assertTrue(bridge.odasRunning)

            remote.connected = False
            bridge._refresh_remote_connection_state()
            self.assertFalse(bridge.remoteConnected)
            self.assertTrue(bridge.odasRunning)

            bridge.toggleRemoteOdas()

            self.assertEqual(remote.connect_calls, 2)
            self.assertEqual(remote.stop_calls, 1)
            self.assertFalse(bridge.odasRunning)

    def test_stop_streams_keeps_remote_running(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()
            bridge.startStreams()
            bridge.stopStreams()

            self.assertTrue(bridge.odasRunning)
            self.assertFalse(bridge.streamsActive)
            self.assertEqual(bridge.controlPhase, "odas_running")
            self.assertEqual(bridge.controlDataState, "inactive")
            self.assertIn("运行中", self._summary_lines(bridge)[0])

    def test_can_toggle_streams_stays_true_when_control_channel_disconnects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            bridge.startStreams()

            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.connected = False
            bridge._refresh_remote_connection_state()

            self.assertTrue(bridge.streamsActive)
            self.assertTrue(bridge.canToggleStreams)
