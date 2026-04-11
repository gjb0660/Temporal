import unittest
from dataclasses import dataclass
from pathlib import Path

from temporal.app.bridge import AppBridge
from temporal.app.fake_runtime import FakeRecorder, FakeRemote, fake_app_bridge
from temporal.core.config_loader import TemporalConfig
from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig


@dataclass
class _Session:
    source_id: int
    mode: str
    filepath: Path


class _FakeRecorder(FakeRecorder):
    def __init__(self, _output_dir) -> None:
        super().__init__(_output_dir)
        self._active: set[int] = set()
        self.pushed: list[tuple[int, str, bytes]] = []
        self._sessions: dict[tuple[int, str], _Session] = {}
        self.sample_rates: dict[str, int] = {"sp": 16000, "pf": 16000}

    def update_active_sources(self, source_ids) -> None:
        next_active = {int(source_id) for source_id in source_ids if int(source_id) > 0}
        for source_id in next_active:
            self._sessions[(source_id, "sp")] = _Session(
                source_id=source_id,
                mode="sp",
                filepath=Path(f"ODAS_{source_id}_sp.wav"),
            )
            self._sessions[(source_id, "pf")] = _Session(
                source_id=source_id,
                mode="pf",
                filepath=Path(f"ODAS_{source_id}_pf.wav"),
            )
        for source_id in list(self._active):
            if source_id in next_active:
                continue
            self._sessions.pop((source_id, "sp"), None)
            self._sessions.pop((source_id, "pf"), None)
        self._active = next_active

    def sweep_inactive(self):
        return []

    def active_sources(self) -> set[int]:
        return set(self._active)

    def push(self, source_id: int, mode: str, pcm_chunk: bytes) -> None:
        if (int(source_id), str(mode)) not in self._sessions:
            return
        self.pushed.append((source_id, mode, pcm_chunk))

    def stop_all(self) -> None:
        self._active.clear()
        self.pushed.clear()
        self._sessions.clear()

    def sessions_snapshot(self):
        sessions = list(self._sessions.values())
        sessions.sort(key=lambda item: (item.source_id, item.mode))
        return sessions

    def set_sample_rates(self, sample_rates: dict[str, int]) -> None:
        self.sample_rates = dict(sample_rates)


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


class TestAppBridgeRecording(unittest.TestCase):
    def _make_bridge(self) -> AppBridge:
        return fake_app_bridge(
            cfg=_fake_config(),
            remote_cls=FakeRemote,
            recorder_cls=_FakeRecorder,
        )

    def _target_id_for_source(self, bridge: AppBridge, source_id: int) -> int:
        fallback_target_id = 0
        for index in range(bridge.sourceRowsModel.count):
            row = bridge.sourceRowsModel.get(index)
            if int(row.get("sourceId", 0)) != int(source_id):
                continue
            target_id = int(row.get("targetId", 0))
            if bool(row.get("active")):
                return target_id
            fallback_target_id = target_id
        return fallback_target_id

    def test_sst_updates_recording_count(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst({"src": [{"id": 2}, {"id": 0}, {"id": 5}]})

        self.assertEqual(bridge.recordingSourceCount, 2)
        self.assertEqual(bridge.controlPhase, "idle")
        self.assertEqual(bridge.controlDataState, "inactive")
        self.assertIn("Temporal 就绪", str(bridge.controlSummary))
        self.assertIn("数据状态: 未监听", str(bridge.controlSummary))
        self.assertIn("录制中=2", str(bridge.controlSummary))
        self.assertEqual(str(bridge.status), str(bridge.controlSummary))

    def test_stop_streams_resets_recording_count(self) -> None:
        bridge = self._make_bridge()
        bridge._on_sst({"src": [{"id": 3}]})

        bridge.stopStreams()

        self.assertEqual(bridge.recordingSourceCount, 0)
        self.assertIn("Temporal 就绪", str(bridge.controlSummary))

    def test_sep_audio_routes_to_mapped_sources(self) -> None:
        bridge = self._make_bridge()
        recorder = bridge._recorder
        self.assertIsInstance(recorder, _FakeRecorder)

        bridge._on_sst({"src": [{"id": 101}, {"id": 202}, {"id": 303}, {"id": 404}]})

        chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00\x0b\x00\x0c\x00\x0d\x00\x0e\x00"
        bridge._on_sep_audio(chunk)

        self.assertEqual(len(recorder.pushed), 4)
        expected = {
            (101, "sp"): b"\x01\x00\x0b\x00",
            (202, "sp"): b"\x02\x00\x0c\x00",
            (303, "sp"): b"\x03\x00\x0d\x00",
            (404, "sp"): b"\x04\x00\x0e\x00",
        }
        actual = {(source_id, mode): pcm for source_id, mode, pcm in recorder.pushed}
        self.assertEqual(actual, expected)

    def test_pf_audio_routes_to_mapped_sources(self) -> None:
        bridge = self._make_bridge()
        recorder = bridge._recorder
        self.assertIsInstance(recorder, _FakeRecorder)

        bridge._on_sst({"src": [{"id": 1}, {"id": 2}]})

        chunk = b"\x11\x00\x22\x00\x33\x00\x44\x00"
        bridge._on_pf_audio(chunk)

        actual = {(source_id, mode): pcm for source_id, mode, pcm in recorder.pushed}
        self.assertEqual(actual.get((1, "pf")), b"\x11\x00")
        self.assertEqual(actual.get((2, "pf")), b"\x22\x00")

    def test_recording_sessions_updates_on_sst_and_stop(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst({"timeStamp": 0, "src": [{"id": 2, "x": 1.0, "y": 0.0, "z": 0.0}]})

        self.assertEqual(len(bridge._recording_sessions), 1)
        session_row = bridge._recording_sessions[0]
        target_id = int(session_row.get("targetId", 0))
        self.assertGreater(target_id, 0)
        self.assertEqual(
            str(session_row.get("summary", "")),
            f"Target {target_id} | Source 2 | files: 2",
        )
        details = str(session_row.get("details", ""))
        self.assertNotIn("Source ", details)
        self.assertIn("ODAS_2_sp.wav", details)
        self.assertIn("ODAS_2_pf.wav", details)
        self.assertTrue(bool(session_row.get("hasActive")))

        bridge._on_sst({"timeStamp": 19, "src": []})
        self.assertEqual(len(bridge._recording_sessions), 1)
        recent_only = bridge._recording_sessions[0]
        self.assertEqual(
            str(recent_only.get("summary", "")),
            f"Target {target_id} | Source 2 | files: 0",
        )
        recent_details = str(recent_only.get("details", ""))
        self.assertNotIn("Source ", recent_details)
        self.assertIn("ODAS_2_sp.wav", recent_details)
        self.assertIn("ODAS_2_pf.wav", recent_details)
        self.assertFalse(bool(recent_only.get("hasActive")))

        bridge.stopStreams()

        self.assertEqual(bridge._recording_sessions, [])

    def test_source_id_drift_keeps_target_grouped_recording_sessions(self) -> None:
        bridge = self._make_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        first_target_id = self._target_id_for_source(bridge, 7)
        self.assertGreater(first_target_id, 0)

        bridge._on_sst({"timeStamp": 19, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge._on_sst({"timeStamp": 38, "src": [{"id": 17, "x": 1.0, "y": 0.0, "z": 0.0}]})

        self.assertEqual(len(bridge._recording_sessions), 1)
        session_row = bridge._recording_sessions[0]
        self.assertEqual(int(session_row.get("targetId", 0)), first_target_id)
        self.assertEqual(
            str(session_row.get("summary", "")),
            f"Target {first_target_id} | Source 17 | files: 2",
        )
        details = str(session_row.get("details", ""))
        self.assertIn("ODAS_17_sp.wav", details)
        self.assertIn("ODAS_7_sp.wav", details)

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

    def test_sst_over_capacity_limits_recording_to_mapped_sources(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst({"src": [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]})

        self.assertEqual(len(bridge._source_channel_map), 4)
        self.assertEqual(bridge.recordingSourceCount, 4)
        details_blob = "\n".join(
            str(item.get("details", "")) for item in bridge._recording_sessions
        )
        self.assertNotIn("ODAS_5_", details_blob)

    def test_unchecked_last_source_keeps_rows_but_clears_visible_outputs(self) -> None:
        bridge = self._make_bridge()
        bridge._on_sst(
            {
                "src": [
                    {"id": 2, "x": 1.0, "y": 0.0, "z": 0.0},
                    {"id": 5, "x": 0.0, "y": 1.0, "z": 0.0},
                ]
            }
        )

        bridge.setTargetSelected(self._target_id_for_source(bridge, 2), False)
        self.assertEqual(bridge.sourcePositionsModel.count, 1)

        bridge.setTargetSelected(self._target_id_for_source(bridge, 5), False)

        self.assertEqual(bridge.sourceRowsModel.count, 2)
        self.assertEqual(bridge.sourcePositionsModel.count, 0)


if __name__ == "__main__":
    unittest.main()
