from app_bridge_recording_support import (
    AppBridgeRecordingBase,
    FakeRemote,
    _FakeRecorder,
)


class TestAppBridgeRecordingRemoteControl(AppBridgeRecordingBase):
    def test_toggle_remote_odas_connects_then_starts(self) -> None:
        bridge = self._make_bridge()

        bridge.toggleRemoteOdas()

        self.assertTrue(bridge.remoteConnected)
        self.assertTrue(bridge.odasRunning)
        self.assertTrue(bridge.streamsActive)
        self.assertEqual(bridge._remote.connect_calls, 1)
        self.assertEqual(bridge._remote.start_calls, 1)
        self.assertEqual(bridge._client.start_calls, 1)
        self.assertEqual(bridge._recorder.sample_rates, {"sp": 16000, "pf": 16000})

    def test_remote_start_applies_detected_recording_sample_rates(self) -> None:
        bridge = self._make_bridge()
        remote = bridge._remote
        self.assertIsInstance(remote, FakeRemote)
        remote.sample_rates = {"sp": 48000, "pf": 44100}

        bridge.toggleRemoteOdas()

        recorder = bridge._recorder
        self.assertIsInstance(recorder, _FakeRecorder)
        self.assertEqual(recorder.sample_rates, {"sp": 48000, "pf": 44100})

    def test_remote_start_with_sample_rate_warning_publishes_log_notice(self) -> None:
        bridge = self._make_bridge()
        remote = bridge._remote
        self.assertIsInstance(remote, FakeRemote)
        remote.sample_rate_warning = "录音采样率自动识别失败，已回退 16000Hz"

        bridge.toggleRemoteOdas()

        self.assertIn("回退 16000Hz", "\n".join(bridge._remote_log_lines))

    def test_toggle_remote_odas_stops_remote_only(self) -> None:
        bridge = self._make_bridge()
        bridge.toggleRemoteOdas()

        bridge.toggleRemoteOdas()

        self.assertFalse(bridge.odasRunning)
        self.assertTrue(bridge.streamsActive)
        self.assertEqual(bridge._remote.stop_calls, 1)
        self.assertEqual(bridge._client.stop_calls, 0)
        self.assertEqual(bridge.controlPhase, "streams_listening")
        self.assertEqual(bridge.controlDataState, "listening_remote_not_running")
        self.assertIn("监听", str(bridge.controlSummary))

    def test_toggle_streams_is_independent_from_control_channel(self) -> None:
        bridge = self._make_bridge()

        bridge.toggleStreams()
        self.assertTrue(bridge.streamsActive)
        self.assertEqual(bridge._client.start_calls, 1)
        self.assertTrue(bridge.canToggleStreams)
        self.assertEqual(bridge.controlPhase, "streams_listening")
        self.assertEqual(bridge.controlDataState, "listening_remote_not_running")
        self.assertIn("正在监听", str(bridge.controlSummary))

        bridge._remote.connected = False
        bridge._refresh_remote_connection_state()
        self.assertTrue(bridge.canToggleStreams)
