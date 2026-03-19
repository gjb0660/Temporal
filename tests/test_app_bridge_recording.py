import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from temporal.app import AppBridge


@dataclass
class _Session:
    source_id: int
    mode: str
    filepath: Path


class _FakeRecorder:
    def __init__(self, _output_dir) -> None:
        self._active: set[int] = set()
        self.pushed: list[tuple[int, str, bytes]] = []
        self._sessions: dict[tuple[int, str], _Session] = {}

    def update_active_sources(self, source_ids) -> None:
        self._active = {int(source_id) for source_id in source_ids if int(source_id) > 0}
        for source_id in self._active:
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

    def sweep_inactive(self):
        return []

    def active_sources(self) -> set[int]:
        return set(self._active)

    def push(self, source_id: int, mode: str, pcm_chunk: bytes) -> None:
        self.pushed.append((source_id, mode, pcm_chunk))

    def stop_all(self) -> None:
        self._active.clear()
        self.pushed.clear()
        self._sessions.clear()

    def sessions_snapshot(self):
        sessions = list(self._sessions.values())
        sessions.sort(key=lambda item: (item.source_id, item.mode))
        return sessions


class TestAppBridgeRecording(unittest.TestCase):
    def test_sst_updates_recording_count(self) -> None:
        with patch("temporal.app.AutoRecorder", _FakeRecorder):
            bridge = AppBridge()

            bridge._on_sst({"src": [{"id": 2}, {"id": 0}, {"id": 5}]})

            self.assertEqual(bridge.recordingSourceCount, 2)
            self.assertIn("录制中=2", bridge.status)

    def test_stop_streams_resets_recording_count(self) -> None:
        with patch("temporal.app.AutoRecorder", _FakeRecorder):
            bridge = AppBridge()
            bridge._on_sst({"src": [{"id": 3}]})

            bridge.stopStreams()

            self.assertEqual(bridge.recordingSourceCount, 0)
            self.assertEqual(bridge.status, "数据流已关闭")

    def test_source_channel_map_reuses_existing_channel(self) -> None:
        with patch("temporal.app.AutoRecorder", _FakeRecorder):
            bridge = AppBridge()

            bridge._on_sst({"src": [{"id": 10}, {"id": 20}]})
            self.assertEqual(bridge._source_channel_map, {10: 0, 20: 1})

            bridge._on_sst({"src": [{"id": 20}, {"id": 30}]})
            self.assertEqual(bridge._source_channel_map, {20: 1, 30: 0})

    def test_sep_audio_routes_to_mapped_sources(self) -> None:
        with patch("temporal.app.AutoRecorder", _FakeRecorder):
            bridge = AppBridge()
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
        with patch("temporal.app.AutoRecorder", _FakeRecorder):
            bridge = AppBridge()
            recorder = bridge._recorder
            self.assertIsInstance(recorder, _FakeRecorder)

            bridge._on_sst({"src": [{"id": 1}, {"id": 2}]})

            chunk = b"\x11\x00\x22\x00\x33\x00\x44\x00"
            bridge._on_pf_audio(chunk)

            actual = {(source_id, mode): pcm for source_id, mode, pcm in recorder.pushed}
            self.assertEqual(actual.get((1, "pf")), b"\x11\x00")
            self.assertEqual(actual.get((2, "pf")), b"\x22\x00")

    def test_recording_sessions_updates_on_sst_and_stop(self) -> None:
        with patch("temporal.app.AutoRecorder", _FakeRecorder):
            bridge = AppBridge()

            bridge._on_sst({"src": [{"id": 2}]})

            self.assertEqual(len(bridge.recordingSessions), 2)
            self.assertTrue(any("Source 2 [sp]" in item for item in bridge.recordingSessions))
            self.assertTrue(any("Source 2 [pf]" in item for item in bridge.recordingSessions))

            bridge.stopStreams()

            self.assertEqual(bridge.recordingSessions, [])

    def test_sst_over_capacity_limits_recording_to_mapped_sources(self) -> None:
        with patch("temporal.app.AutoRecorder", _FakeRecorder):
            bridge = AppBridge()

            bridge._on_sst({"src": [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]})

            self.assertEqual(len(bridge._source_channel_map), 4)
            self.assertEqual(bridge.recordingSourceCount, 4)
            self.assertFalse(any("Source 5" in item for item in bridge.recordingSessions))


if __name__ == "__main__":
    unittest.main()
