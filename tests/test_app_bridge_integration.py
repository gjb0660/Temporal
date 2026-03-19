import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from temporal.app import AppBridge
from temporal.core.config_loader import TemporalConfig
from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig
from temporal.core.recording.auto_recorder import AutoRecorder


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

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False


class _FakeRemoteOdasController:
    def __init__(self, _cfg: RemoteOdasConfig) -> None:
        self.connected = False

    def connect(self) -> None:
        self.connected = True


def _fake_config() -> TemporalConfig:
    remote = RemoteOdasConfig(
        host="127.0.0.1",
        port=22,
        username="odas",
        private_key="~/.ssh/id_rsa",
        odas_args=["-c", "/opt/odas/config/odas.cfg", "-v"],
        odas_log="/tmp/odaslive.log",
    )
    streams = OdasStreamConfig(
        sst=OdasEndpoint(host="127.0.0.1", port=9000),
        ssl=OdasEndpoint(host="127.0.0.1", port=9001),
        sss_sep=OdasEndpoint(host="127.0.0.1", port=10000),
        sss_pf=OdasEndpoint(host="127.0.0.1", port=10010),
    )
    return TemporalConfig(remote=remote, streams=streams)


class TestAppBridgeIntegration(unittest.TestCase):
    def test_sst_ssl_sss_flow_updates_status_and_writes_audio(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            with (
                patch("temporal.app.load_config", return_value=_fake_config()),
                patch("temporal.app.OdasClient", _FakeOdasClient),
                patch("temporal.app.RemoteOdasController", _FakeRemoteOdasController),
                patch("temporal.app.AutoRecorder", return_value=recorder),
            ):
                bridge = AppBridge()

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
            with (
                patch("temporal.app.load_config", return_value=_fake_config()),
                patch("temporal.app.OdasClient", _FakeOdasClient),
                patch("temporal.app.RemoteOdasController", _FakeRemoteOdasController),
                patch("temporal.app.AutoRecorder", return_value=recorder),
            ):
                bridge = AppBridge()
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

    def test_filename_contract_kept_in_integration_flow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            with (
                patch("temporal.app.load_config", return_value=_fake_config()),
                patch("temporal.app.OdasClient", _FakeOdasClient),
                patch("temporal.app.RemoteOdasController", _FakeRemoteOdasController),
                patch("temporal.app.AutoRecorder", return_value=recorder),
            ):
                bridge = AppBridge()
                bridge._on_sst({"src": [{"id": 3}]})
                bridge._on_sep_audio(b"\x01\x00\x02\x00\x03\x00\x04\x00")
                bridge.stopStreams()

            names = [path.name for path in Path(temp_dir).glob("ODAS_3_*_*.wav")]
            self.assertTrue(any(name.endswith("_sp.wav") for name in names))
            self.assertTrue(any(name.endswith("_pf.wav") for name in names))
            for name in names:
                self.assertRegex(name, r"^ODAS_3_\d{8}_\d{6}_\d{6}_(sp|pf)\.wav$")


if __name__ == "__main__":
    unittest.main()
