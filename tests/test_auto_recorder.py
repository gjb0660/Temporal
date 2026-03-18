import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from temporal.core.recording.auto_recorder import AutoRecorder


class _FakeClock:
    def __init__(self, start: datetime) -> None:
        self.current = start

    def now(self) -> datetime:
        return self.current

    def advance(self, seconds: float) -> None:
        self.current = self.current + timedelta(seconds=seconds)


class TestAutoRecorder(unittest.TestCase):
    def test_filename_matches_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            session = recorder.start(7, "sp")
            recorder.stop(7, "sp")

            self.assertRegex(
                session.filepath.name,
                r"^ODAS_7_\d{8}_\d{6}_\d{6}_sp\.wav$",
            )

    def test_update_active_sources_starts_recording(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            clock = _FakeClock(datetime(2026, 3, 18, 12, 0, 0))
            recorder = AutoRecorder(output_dir=temp_dir, now_fn=clock.now)

            recorder.update_active_sources([2])

            self.assertTrue(recorder.is_recording(2, "sp"))
            self.assertTrue(recorder.is_recording(2, "pf"))
            recorder.stop_all()

    def test_sweep_inactive_stops_after_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            clock = _FakeClock(datetime(2026, 3, 18, 12, 0, 0))
            recorder = AutoRecorder(
                output_dir=temp_dir,
                inactive_timeout_sec=1.0,
                now_fn=clock.now,
            )
            recorder.update_active_sources([2])
            clock.advance(2.0)

            stopped = recorder.sweep_inactive()

            self.assertIn(2, stopped)
            self.assertFalse(recorder.is_recording(2, "sp"))
            self.assertFalse(recorder.is_recording(2, "pf"))

    def test_push_writes_pcm_frames(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            session = recorder.start(4, "sp")

            recorder.push(4, "sp", b"\x01\x02\x03\x04")
            recorder.stop(4, "sp")

            path = Path(session.filepath)
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 44)


if __name__ == "__main__":
    unittest.main()
