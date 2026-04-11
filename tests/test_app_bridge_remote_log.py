from app_bridge_integration_support import (
    AppBridgeIntegrationBase,
    AutoRecorder,
    CommandResult,
    _FakeRemoteOdasController,
    patch,
    tempfile,
)


class TestAppBridgeRemoteLog(AppBridgeIntegrationBase):
    def test_remote_log_poll_updates_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()

            bridge._poll_remote_log()

            self.assertEqual(bridge.remoteLogLines, ["startup ok", "ready"])

    def test_clear_remote_log_behaviors(self) -> None:
        warning_text = "录音采样率自动识别失败，已回退 16000Hz"
        for scenario in ("success", "failure", "failure_then_success", "success_clears_warning"):
            with self.subTest(scenario=scenario):
                with tempfile.TemporaryDirectory() as temp_dir:
                    recorder = AutoRecorder(output_dir=temp_dir)
                    bridge = self._make_bridge(recorder)
                    bridge.connectRemote()
                    remote = bridge._remote
                    self.assertIsInstance(remote, _FakeRemoteOdasController)
                    self.assertEqual(bridge.remoteLogLines, ["startup ok", "ready"])

                    if scenario == "success":
                        bridge.clearRemoteLog()
                        self.assertEqual(remote.clear_calls, 1)
                        self.assertEqual(
                            bridge.remoteLogLines, ["远程日志为空，等待 odaslive 输出..."]
                        )
                        continue

                    if scenario == "failure":
                        remote.clear_result = CommandResult(
                            code=1, stdout="", stderr="permission denied"
                        )
                        baseline_lines = list(bridge._remote_log_lines)
                        bridge.clearRemoteLog()
                        self.assertEqual(remote.clear_calls, 1)
                        self.assertEqual(bridge.remoteLogLines, baseline_lines)
                        self.assertEqual(bridge.controlPhase, "error")
                        self.assertEqual(bridge.controlDataState, "unavailable")
                        self.assertIn("清空远程日志失败", self._summary_lines(bridge)[0])
                        continue

                    if scenario == "failure_then_success":
                        remote.clear_result = CommandResult(
                            code=1, stdout="", stderr="permission denied"
                        )
                        bridge.clearRemoteLog()
                        self.assertEqual(bridge.controlPhase, "error")
                        self.assertEqual(bridge.controlDataState, "unavailable")
                        self.assertIn("清空远程日志失败", self._summary_lines(bridge)[0])
                        remote.clear_result = CommandResult(code=0, stdout="", stderr="")
                        bridge.clearRemoteLog()
                        self.assertEqual(remote.clear_calls, 2)
                        self.assertEqual(bridge.controlPhase, "ssh_connected_idle")
                        self.assertEqual(bridge.controlDataState, "inactive")
                        lines = self._summary_lines(bridge)
                        self.assertIn("SSH 已连接，远程 odaslive 未运行", lines[0])
                        self.assertIn("未监听", lines[1])
                        self.assertEqual(
                            bridge.remoteLogLines, ["远程日志为空，等待 odaslive 输出..."]
                        )
                        continue

                    bridge._recording_sample_rate_warning = warning_text
                    bridge._set_remote_log_lines(["startup ok", "ready"])
                    self.assertIn(warning_text, bridge._remote_log_lines)
                    bridge.clearRemoteLog()
                    self.assertEqual(remote.clear_calls, 1)
                    self.assertEqual(bridge.remoteLogLines, ["远程日志为空，等待 odaslive 输出..."])
                    self.assertNotIn(warning_text, bridge._remote_log_lines)

    def test_clear_remote_log_allows_followup_log_updates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)

            bridge.clearRemoteLog()
            self.assertEqual(bridge.remoteLogLines, ["远程日志为空，等待 odaslive 输出..."])

            remote.log_output = "after clear line 1\nafter clear line 2\n"
            bridge._poll_remote_log()

            self.assertEqual(bridge.remoteLogLines, ["after clear line 1", "after clear line 2"])

    def test_clear_remote_log_restarts_log_timer_when_stopped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)

            bridge._log_timer.stop()
            self.assertFalse(bridge._log_timer.isActive())

            with patch.object(
                bridge._log_timer, "start", wraps=bridge._log_timer.start
            ) as start_spy:
                bridge.clearRemoteLog()
                start_spy.assert_called_once_with()

            remote.log_output = "timer restored\n"
            bridge._poll_remote_log()
            self.assertEqual(bridge.remoteLogLines, ["timer restored"])

    def test_log_poll_exception_still_triggers_control_state_sync(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()
            self.assertTrue(bridge.odasRunning)
            bridge._set_odas_running(False)

            baseline_status_calls = remote.status_calls
            remote.log_exception = RuntimeError("temporary log read failure")
            bridge._poll_remote_log()

            self.assertGreaterEqual(remote.status_calls, baseline_status_calls + 1)
            self.assertTrue(bridge.odasRunning)
            self.assertEqual(bridge.controlPhase, "odas_running")
            self.assertEqual(bridge.controlDataState, "inactive")
            self.assertIn("运行中", self._summary_lines(bridge)[0])
