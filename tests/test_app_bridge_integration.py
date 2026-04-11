import tempfile
import unittest
import wave
from datetime import datetime
from pathlib import Path
from time import monotonic
from unittest.mock import patch

from temporal.app.bridge import AppBridge
from temporal.app.fake_runtime import FakeClient, FakeClock, FakeRemote, fake_app_bridge
from temporal.core.recording.auto_recorder import AutoRecorder
from temporal.core.ssh.remote_odas import CommandResult


class _FakeOdasClient(FakeClient):
    pass


class _FailingOdasClient(_FakeOdasClient):
    def start(self) -> None:
        self.start_calls += 1
        raise OSError("bind failed")


class _FakeRemoteOdasController(FakeRemote):
    def __init__(self, cfg: object, streams: object) -> None:
        super().__init__(cfg, streams)
        self.start_result = CommandResult(code=0, stdout="4242\n", stderr="")
        self.stop_result = CommandResult(code=0, stdout="", stderr="")
        self.log_output = "startup ok\nready\n"
        self.status_output = ""
        self.status_sequence: list[str] = []
        self.start_status_sequence: list[str] = []
        self.keep_running_after_stop = False
        self.status_exception: Exception | None = None
        self.log_exception: Exception | None = None
        self.status_calls = 0
        self.clear_calls = 0
        self.clear_result = CommandResult(code=0, stdout="", stderr="")

    def start_odaslive(self) -> CommandResult:
        super().start_odaslive()
        self.status_sequence = list(self.start_status_sequence)
        return self.start_result

    def stop_odaslive(self) -> CommandResult:
        self.stop_calls += 1
        if not self.keep_running_after_stop:
            self.running = False
            self.status_output = ""
            self.status_sequence = []
        return self.stop_result

    def status(self) -> CommandResult:
        self.status_calls += 1
        if self.status_exception is not None:
            self.connected = False
            raise self.status_exception
        if self.status_sequence:
            self.status_output = self.status_sequence.pop(0)
        return CommandResult(code=0, stdout=self.status_output, stderr="")

    def read_log_tail(self, _lines: int = 80) -> CommandResult:
        if not self.connected:
            raise RuntimeError("SSH is not connected")
        if self.log_exception is not None:
            raise self.log_exception
        return CommandResult(code=0, stdout=self.log_output, stderr="")

    def clear_log(self) -> CommandResult:
        if not self.connected:
            raise RuntimeError("SSH is not connected")
        self.clear_calls += 1
        if self.clear_result.code == 0:
            self.log_output = ""
        return self.clear_result


class _BootstrapFailingRemoteOdasController(_FakeRemoteOdasController):
    def connect(self) -> None:
        self.connect_calls += 1
        raise RuntimeError("SSH control shell timed out")


class TestAppBridgeIntegration(unittest.TestCase):
    def _make_bridge(
        self,
        recorder: AutoRecorder,
        *,
        client_cls: type[_FakeOdasClient] = _FakeOdasClient,
        remote_cls: type[_FakeRemoteOdasController] = _FakeRemoteOdasController,
    ) -> AppBridge:
        return fake_app_bridge(
            client_cls=client_cls,
            remote_cls=remote_cls,
            recorder_instance=recorder,
        )

    def _drain_startup(self, bridge: AppBridge) -> None:
        while bridge.odasStarting:
            bridge._verify_odas_startup()

    def _summary_lines(self, bridge: AppBridge) -> list[str]:
        lines = str(bridge.controlSummary).splitlines()
        self.assertEqual(len(lines), 3)
        return lines

    def test_sst_ssl_sss_flow_updates_status_and_writes_audio(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()

            bridge.startStreams()
            lines_before = self._summary_lines(bridge)
            bridge._on_sst({"src": [{"id": 2}, {"id": 4}]})
            bridge.setPotentialsEnabled(True)
            bridge._on_ssl({"src": [{"E": 0.3}, {"E": 0.7}]})
            lines_after = self._summary_lines(bridge)
            self.assertEqual(lines_before[0], lines_after[0])
            self.assertEqual(lines_before[1], lines_after[1])
            self.assertEqual(bridge.controlPhase, "streams_listening")
            self.assertEqual(bridge.controlDataState, "listening_remote_not_running")

            chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00"
            bridge._on_sep_audio(chunk)
            bridge._on_pf_audio(chunk)

            bridge.stopStreams()

            files = sorted(Path(temp_dir).glob("ODAS_*_*.wav"))
            self.assertGreaterEqual(len(files), 4)
            self.assertEqual(bridge.potentialCount, 2)
            self.assertEqual(bridge.recordingSourceCount, 0)
            self.assertEqual(bridge.controlPhase, "ssh_connected_idle")
            self.assertEqual(bridge.controlDataState, "inactive")
            lines_final = self._summary_lines(bridge)
            self.assertIn("SSH 已连接，远程 odaslive 未运行", lines_final[0])
            self.assertIn("未监听", lines_final[1])

    def test_remote_start_applies_sample_rates_to_new_wav_headers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.sample_rates = {"sp": 48000, "pf": 44100}

            bridge.startRemoteOdas()
            self._drain_startup(bridge)
            bridge._on_sst({"src": [{"id": 2}]})
            chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00"
            bridge._on_sep_audio(chunk)
            bridge._on_pf_audio(chunk)
            bridge.stopStreams()

            sp_files = sorted(Path(temp_dir).glob("ODAS_*_sp.wav"))
            pf_files = sorted(Path(temp_dir).glob("ODAS_*_pf.wav"))
            self.assertTrue(sp_files)
            self.assertTrue(pf_files)
            with wave.open(str(sp_files[0]), "rb") as sp_wav:
                self.assertEqual(sp_wav.getframerate(), 48000)
            with wave.open(str(pf_files[0]), "rb") as pf_wav:
                self.assertEqual(pf_wav.getframerate(), 44100)

    def test_remote_start_sample_rate_warning_keeps_fallback_rate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.sample_rate_warning = "录音采样率自动识别失败，已回退 16000Hz"

            bridge.startRemoteOdas()
            self.assertIn("回退 16000Hz", "\n".join(bridge._remote_log_lines))
            self._drain_startup(bridge)
            bridge._on_sst({"src": [{"id": 4}]})
            chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00"
            bridge._on_sep_audio(chunk)
            bridge.stopStreams()

            sp_files = sorted(Path(temp_dir).glob("ODAS_*_sp.wav"))
            self.assertTrue(sp_files)
            with wave.open(str(sp_files[0]), "rb") as sp_wav:
                self.assertEqual(sp_wav.getframerate(), 16000)

    def test_timeout_recovery_creates_new_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            clock = FakeClock(datetime(2026, 3, 19, 12, 0, 0))
            recorder = AutoRecorder(
                output_dir=temp_dir,
                inactive_timeout_sec=1.0,
                now_fn=clock.now,
            )
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            bridge.startStreams()
            bridge._on_sst({"src": [{"id": 7}]})
            first_session = sorted(recorder.sessions_snapshot(), key=lambda item: item.mode)
            self.assertEqual(len(first_session), 2)

            clock.advance(1.2)
            bridge._on_sst({"src": []})
            self.assertEqual(recorder.sessions_snapshot(), [])

            clock.advance(0.1)
            bridge._on_sst({"src": [{"id": 7}]})
            second_session = sorted(recorder.sessions_snapshot(), key=lambda item: item.mode)
            self.assertEqual(len(second_session), 2)

            first_paths = {session.filepath.name for session in first_session}
            second_paths = {session.filepath.name for session in second_session}
            self.assertNotEqual(first_paths, second_paths)
            bridge.stopStreams()

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

    def test_clear_recording_files_cleans_local_outputs_and_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            try:
                bridge._on_sst({"timeStamp": 0, "src": [{"id": 2, "x": 1.0, "y": 0.0, "z": 0.0}]})
                initial_phase = bridge.controlPhase

                files_before = sorted(Path(temp_dir).glob("ODAS_*_*.wav"))
                self.assertEqual(len(files_before), 2)
                self.assertEqual(bridge.recordingSourceCount, 1)
                self.assertTrue(bridge._recording_sessions)

                bridge.clearRecordingFiles()

                self.assertEqual(sorted(Path(temp_dir).glob("ODAS_*_*.wav")), [])
                self.assertEqual(bridge.recordingSourceCount, 0)
                self.assertEqual(bridge._recording_sessions, [])
                self.assertEqual(bridge.controlPhase, initial_phase)
            finally:
                recorder.stop_all()

    def test_start_remote_starts_local_listeners_before_remote_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            client = bridge._client
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            self.assertIsInstance(client, _FakeOdasClient)

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

    def test_streams_running_sst_timeout_falls_back_to_waiting_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()
            bridge.startStreams()
            bridge._on_sst({"src": [{"id": 2}], "timeStamp": 1})
            self.assertEqual(bridge.controlDataState, "receiving_sst")

            bridge._last_sst_monotonic = monotonic() - 3.0
            bridge._apply_state_status()

            self.assertEqual(bridge.controlDataState, "running_waiting_sst")
            self.assertIn("等待 SST", self._summary_lines(bridge)[1])
            bridge.stopStreams()

    def test_on_sst_emits_receiving_state_before_metrics_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()
            bridge.startStreams()
            self.assertEqual(bridge.controlDataState, "running_waiting_sst")

            emitted_summaries: list[str] = []
            bridge.controlSummaryChanged.connect(
                lambda: emitted_summaries.append(str(bridge.controlSummary))
            )

            bridge._on_sst({"src": [{"id": 2}], "timeStamp": 1})

            self.assertGreaterEqual(len(emitted_summaries), 1)
            first_lines = emitted_summaries[0].splitlines()
            self.assertEqual(len(first_lines), 3)
            self.assertIn("正在接收 SST", first_lines[1])
            self.assertEqual(bridge.controlDataState, "receiving_sst")
            bridge.stopStreams()


if __name__ == "__main__":
    unittest.main()
