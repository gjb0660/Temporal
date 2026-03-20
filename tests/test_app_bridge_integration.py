import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from temporal.app import AppBridge
from temporal.core.config_loader import TemporalConfig
from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig
from temporal.core.recording.auto_recorder import AutoRecorder
from temporal.core.ssh.remote_odas import CommandResult


class _FakeClock:
    def __init__(self, start: datetime) -> None:
        self.current = start

    def now(self) -> datetime:
        return self.current

    def advance(self, seconds: float) -> None:
        self.current = self.current + timedelta(seconds=seconds)


class _FakeOdasClient:
    def __init__(self, **_kwargs) -> None:
        self.started = False
        self.start_calls = 0
        self.stop_calls = 0

    def start(self) -> None:
        self.started = True
        self.start_calls += 1

    def stop(self) -> None:
        self.started = False
        self.stop_calls += 1


class _FakeRemoteOdasController:
    def __init__(self, _cfg: RemoteOdasConfig, _streams: OdasStreamConfig) -> None:
        self.connected = False
        self.connect_calls = 0
        self.start_calls = 0
        self.stop_calls = 0
        self.start_result = CommandResult(code=0, stdout="4242\n", stderr="")
        self.stop_result = CommandResult(code=0, stdout="", stderr="")
        self.log_output = "startup ok\nready\n"
        self.status_output = ""
        self.status_sequence: list[str] = []
        self.start_status_sequence: list[str] = []

    def connect(self) -> None:
        self.connected = True
        self.connect_calls += 1

    def start_odaslive(self) -> CommandResult:
        self.start_calls += 1
        self.status_sequence = list(self.start_status_sequence)
        return self.start_result

    def stop_odaslive(self) -> CommandResult:
        self.stop_calls += 1
        self.status_output = ""
        self.status_sequence = []
        return self.stop_result

    def status(self) -> CommandResult:
        if self.status_sequence:
            self.status_output = self.status_sequence.pop(0)
        return CommandResult(code=0, stdout=self.status_output, stderr="")

    def read_log_tail(self, _lines: int = 80) -> CommandResult:
        return CommandResult(code=0, stdout=self.log_output, stderr="")


def _fake_config() -> TemporalConfig:
    remote = RemoteOdasConfig(
        host="172.21.16.222",
        port=22,
        username="odas",
        private_key="~/.ssh/id_rsa",
        odas_command="./odas_loop.sh",
        odas_args=[],
        odas_cwd="workspace/ODAS/odas",
        odas_log="odaslive.log",
    )
    streams = OdasStreamConfig(
        sst=OdasEndpoint(host="192.168.1.50", port=9000),
        ssl=OdasEndpoint(host="192.168.1.50", port=9001),
        sss_sep=OdasEndpoint(host="192.168.1.50", port=10000),
        sss_pf=OdasEndpoint(host="192.168.1.50", port=10010),
    )
    return TemporalConfig(remote=remote, streams=streams)


class TestAppBridgeIntegration(unittest.TestCase):
    def _make_bridge(self, recorder: AutoRecorder) -> AppBridge:
        with (
            patch("temporal.app.load_config", return_value=_fake_config()),
            patch("temporal.app.OdasClient", _FakeOdasClient),
            patch("temporal.app.RemoteOdasController", _FakeRemoteOdasController),
            patch("temporal.app.AutoRecorder", return_value=recorder),
        ):
            return AppBridge()

    def _drain_startup(self, bridge: AppBridge) -> None:
        while bridge.odasStarting:
            bridge._verify_odas_startup()

    def test_sst_ssl_sss_flow_updates_status_and_writes_audio(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)

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

    def test_timeout_recovery_creates_new_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            clock = _FakeClock(datetime(2026, 3, 19, 12, 0, 0))
            recorder = AutoRecorder(
                output_dir=temp_dir,
                inactive_timeout_sec=1.0,
                now_fn=clock.now,
            )
            bridge = self._make_bridge(recorder)
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
            self.assertEqual(
                bridge._status,
                "启动失败: 远程 ODAS 配置中的输出地址与 Temporal 监听地址不一致",
            )

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

            self.assertTrue(bridge.odasStarting)
            self.assertFalse(bridge.odasRunning)

            bridge._verify_odas_startup()

            self.assertFalse(bridge.odasStarting)
            self.assertTrue(bridge.odasRunning)

    def test_repeated_start_click_is_ignored_while_starting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.start_status_sequence = [""] * 20

            bridge.startRemoteOdas()
            bridge.startRemoteOdas()

            self.assertTrue(bridge.odasStarting)
            self.assertEqual(remote.start_calls, 1)

    def test_connect_remote_without_pid_file_does_not_adopt_instance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)

            bridge.connectRemote()

            self.assertTrue(bridge.remoteConnected)
            self.assertFalse(bridge.odasRunning)
            self.assertEqual(bridge._status, "SSH 已连接")

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

    def test_stop_remote_odas_is_idempotent_when_pid_has_already_exited(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()
            bridge.stopRemoteOdas()

            self.assertFalse(bridge.odasRunning)
            self.assertEqual(remote.stop_calls, 1)
            self.assertIn("已停止", bridge._status)


if __name__ == "__main__":
    unittest.main()
