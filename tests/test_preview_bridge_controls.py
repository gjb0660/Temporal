from preview_bridge_support import (
    PreviewBridge,
    PreviewBridgeQtBase,
    _model_items,
    _scalar_values,
    fake_app_bridge,
    unittest,
)


class TestPreviewBridgeControls(PreviewBridgeQtBase):
    def test_clear_remote_log_keeps_polling_and_receives_new_preview_logs(self) -> None:
        bridge = PreviewBridge()
        bridge.connectRemote()

        bridge.clearRemoteLog()
        self.assertEqual(bridge.remoteLogText, "远程日志为空，等待 odaslive 输出...")

        bridge._preview_remote.log_lines = ["preview new log"]
        bridge._poll_remote_log()

        self.assertEqual(bridge.remoteLogText, "preview new log")

    def test_toggle_remote_auto_starts_streams_and_stop_clears_both(self) -> None:
        bridge = PreviewBridge()

        bridge.toggleRemoteOdas()

        self.assertTrue(bridge.remoteConnected)
        self.assertTrue(bridge.odasRunning)
        self.assertTrue(bridge.streamsActive)
        self.assertEqual(bridge.controlPhase, "streams_listening")
        self.assertEqual(bridge.controlDataState, "receiving_sst")
        self.assertIn("正在监听 SST/SSL/SSS 数据流", str(bridge.status))

        bridge.toggleRemoteOdas()

        self.assertTrue(bridge.remoteConnected)
        self.assertFalse(bridge.odasRunning)
        self.assertTrue(bridge.streamsActive)
        self.assertEqual(bridge.controlPhase, "streams_listening")
        self.assertEqual(bridge.controlDataState, "listening_remote_not_running")
        self.assertIn("正在监听 SST/SSL/SSS 数据流", str(bridge.status))

    def test_toggle_streams_is_independent_and_restart_resets_positions(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")

        initial_positions = _model_items(bridge.sourcePositionsModel)

        bridge.toggleStreams()
        self.assertTrue(bridge.streamsActive)
        self.assertFalse(bridge.odasRunning)
        self.assertEqual(bridge.controlPhase, "streams_listening")
        self.assertEqual(bridge.controlDataState, "listening_remote_not_running")
        self.assertIn("正在监听 SST/SSL/SSS 数据流", str(bridge.status))

        bridge.advancePreviewTick()
        moved_positions = _model_items(bridge.sourcePositionsModel)

        self.assertNotEqual(moved_positions, initial_positions)

        bridge.toggleStreams()
        self.assertFalse(bridge.streamsActive)
        self.assertEqual(bridge.controlPhase, "idle")
        self.assertEqual(bridge.controlDataState, "inactive")
        self.assertIn("Temporal 就绪", str(bridge.status))

        bridge.toggleStreams()
        self.assertEqual(_model_items(bridge.sourcePositionsModel), initial_positions)


class TestAppBridgePreviewDefaults(unittest.TestCase):
    def test_preview_defaults_are_safe_in_production_bridge(self) -> None:
        bridge = fake_app_bridge()

        self.assertFalse(bridge.previewMode)
        self.assertEqual(bridge.previewScenarioKey, "")
        self.assertEqual(bridge.previewScenarioKeys, [])
        self.assertFalse(bridge.showPreviewScenarioSelector)
        self.assertEqual(_model_items(bridge.previewScenarioOptionsModel), [])
        self.assertEqual(_scalar_values(bridge.headerNavLabelsModel), ["配置", "录制", "相机"])
        self.assertEqual(_model_items(bridge.sourceRowsModel), [])
        bridge.setPreviewScenario("referenceSingle")
        self.assertEqual(bridge.previewScenarioKey, "")
