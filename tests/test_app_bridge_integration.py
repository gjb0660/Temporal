import tempfile
import unittest
import wave
from datetime import datetime
from pathlib import Path

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

    def test_sst_ssl_sss_flow_updates_status_and_writes_audio(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()

            bridge.startStreams()
            bridge._on_sst({"src": [{"id": 2}, {"id": 4}]})
            bridge.setPotentialsEnabled(True)
            bridge._on_ssl({"src": [{"E": 0.3}, {"E": 0.7}]})

            chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00"
            bridge._on_sep_audio(chunk)
            bridge._on_pf_audio(chunk)

            bridge.stopStreams()

            files = sorted(Path(temp_dir).glob("ODAS_*_*.wav"))
            self.assertGreaterEqual(len(files), 4)
            self.assertEqual(bridge.potentialCount, 2)
            self.assertEqual(bridge.recordingSourceCount, 0)

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
            self.assertIn("正在监听", bridge._status)

    def test_connect_remote_reports_control_channel_init_failure_without_labeling_ssh_failure(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder, remote_cls=_BootstrapFailingRemoteOdasController)

            bridge.connectRemote()

            self.assertFalse(bridge.remoteConnected)
            self.assertEqual(bridge._status, "远程控制通道初始化失败")
            self.assertEqual(bridge.remoteLogLines, ["远程控制通道初始化失败"])

    def test_start_streams_keeps_inactive_when_listener_bind_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder, client_cls=_FailingOdasClient)
            bridge.connectRemote()

            bridge.startStreams()

            self.assertFalse(bridge.streamsActive)
            self.assertIn("本地监听启动失败", bridge._status)
            self.assertIn("bind failed", bridge._status)

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
            self.assertIn("本地监听启动失败", bridge._status)

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
            self.assertTrue(bridge._status.startswith("启动失败:"))
            self.assertIn("Temporal", bridge._status)
            self.assertNotIn("preflight:", bridge._status)

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
            self.assertEqual(bridge._status, "启动失败: 远程命令不存在或未安装")

    def test_start_transitions_from_starting_to_running_after_pid_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.start_status_sequence = ["", "", "4242\n"]

            bridge.startRemoteOdas()
            bridge._verify_odas_startup()

            self.assertFalse(bridge.odasStarting)
            self.assertTrue(bridge.odasRunning)
            self.assertTrue(bridge.streamsActive)
            self.assertIn("监听", bridge._status)

    def test_connect_remote_without_pid_file_does_not_adopt_instance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)

            bridge.connectRemote()

            self.assertTrue(bridge.remoteConnected)
            self.assertFalse(bridge.odasRunning)
            self.assertEqual(bridge._status, "SSH 已连接，远程 odaslive 未运行")

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
            self.assertIn("运行中", bridge._status)

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
            self.assertEqual(bridge._status, "SSH 已连接，远程 odaslive 未运行")

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
            self.assertEqual(bridge._status, "SSH 已连接，远程 odaslive 运行中")

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
            self.assertIn("监听", bridge._status)

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
            self.assertEqual(bridge._status, "远程 odaslive 停止失败")

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
            self.assertEqual(bridge._status, "停止失败: 远程控制通道已断开")

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
            self.assertEqual(bridge._status, "SSH 已连接，远程 odaslive 运行中")

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


if __name__ == "__main__":
    unittest.main()
