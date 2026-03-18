import unittest
from unittest.mock import patch

from temporal.app import AppBridge


class _FakeRecorder:
    def __init__(self, _output_dir) -> None:
        self._active: set[int] = set()

    def update_active_sources(self, source_ids) -> None:
        self._active = {int(source_id) for source_id in source_ids if int(source_id) > 0}

    def sweep_inactive(self):
        return []

    def active_sources(self) -> set[int]:
        return set(self._active)

    def stop_all(self) -> None:
        self._active.clear()


class TestAppBridgeRecording(unittest.TestCase):
    def test_sst_updates_recording_count(self) -> None:
        with patch("temporal.app.AutoRecorder", _FakeRecorder):
            bridge = AppBridge()

            bridge._on_sst({"src": [{"id": 2}, {"id": 0}, {"id": 5}]})

            self.assertEqual(bridge.recordingSourceCount, 2)
            self.assertIn("recording=2", bridge.status)

    def test_stop_streams_resets_recording_count(self) -> None:
        with patch("temporal.app.AutoRecorder", _FakeRecorder):
            bridge = AppBridge()
            bridge._on_sst({"src": [{"id": 3}]})

            bridge.stopStreams()

            self.assertEqual(bridge.recordingSourceCount, 0)
            self.assertEqual(bridge.status, "Streams stopped")


if __name__ == "__main__":
    unittest.main()
