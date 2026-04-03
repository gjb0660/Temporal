import tempfile
import unittest
import wave
from datetime import datetime
from pathlib import Path

from temporal.app.fake_runtime import FakeClock
from temporal.core.recording.auto_recorder import AutoRecorder


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
            clock = FakeClock(datetime(2026, 3, 18, 12, 0, 0))
            recorder = AutoRecorder(output_dir=temp_dir, now_fn=clock.now)

            recorder.update_active_sources([2])

            self.assertTrue(recorder.is_recording(2, "sp"))
            self.assertTrue(recorder.is_recording(2, "pf"))
            recorder.stop_all()

    def test_sweep_inactive_stops_after_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            clock = FakeClock(datetime(2026, 3, 18, 12, 0, 0))
            recorder = AutoRecorder(
                output_dir=temp_dir,
                inactive_timeout_sec=1.0,
                now_fn=clock.now,
            )
            recorder.update_active_sources([2])
            clock.advance(2.0)

            stopped = recorder.sweep_inactive()

            self.assertIn(2, stopped)
            self.assertEqual(recorder.active_sources(), set())
            self.assertFalse(recorder.is_recording(2, "sp"))
            self.assertFalse(recorder.is_recording(2, "pf"))

    def test_active_sources_tracks_seen_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            clock = FakeClock(datetime(2026, 3, 18, 12, 0, 0))
            recorder = AutoRecorder(output_dir=temp_dir, now_fn=clock.now)

            recorder.update_active_sources([3, 5])

            self.assertEqual(recorder.active_sources(), {3, 5})
            recorder.stop_all()

    def test_push_writes_pcm_frames(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            session = recorder.start(4, "sp")

            recorder.push(4, "sp", b"\x01\x02\x03\x04")
            recorder.stop(4, "sp")

            path = Path(session.filepath)
            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 44)

    def test_set_sample_rates_applies_to_new_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            recorder.set_sample_rates({"sp": 48000, "pf": 44100})

            sp_session = recorder.start(10, "sp")
            pf_session = recorder.start(10, "pf")
            recorder.stop_all()

            with wave.open(str(sp_session.filepath), "rb") as sp_file:
                self.assertEqual(sp_file.getframerate(), 48000)
            with wave.open(str(pf_session.filepath), "rb") as pf_file:
                self.assertEqual(pf_file.getframerate(), 44100)

    def test_sample_rate_change_does_not_rebuild_existing_session(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            first = recorder.start(11, "sp")
            recorder.set_sample_rates({"sp": 48000})
            second = recorder.start(11, "sp")
            recorder.stop_all()

            self.assertEqual(first.filepath, second.filepath)
            with wave.open(str(first.filepath), "rb") as wav_file:
                self.assertEqual(wav_file.getframerate(), 16000)

            third = recorder.start(12, "sp")
            recorder.stop(12, "sp")
            with wave.open(str(third.filepath), "rb") as wav_file:
                self.assertEqual(wav_file.getframerate(), 48000)

    def test_sessions_snapshot_returns_sorted_items(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            clock = FakeClock(datetime(2026, 3, 18, 12, 0, 0))
            recorder = AutoRecorder(output_dir=temp_dir, now_fn=clock.now)

            recorder.start(3, "pf")
            recorder.start(1, "sp")

            sessions = recorder.sessions_snapshot()
            pairs = [(item.source_id, item.mode) for item in sessions]
            self.assertEqual(pairs, [(1, "sp"), (3, "pf")])
            recorder.stop_all()

    def test_timeout_refresh_prevents_jitter_stop(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            clock = FakeClock(datetime(2026, 3, 18, 12, 0, 0))
            recorder = AutoRecorder(
                output_dir=temp_dir,
                inactive_timeout_sec=1.0,
                now_fn=clock.now,
            )

            recorder.update_active_sources([7])
            clock.advance(0.9)
            recorder.update_active_sources([7])
            clock.advance(0.2)

            stopped = recorder.sweep_inactive()

            self.assertEqual(stopped, [])
            self.assertTrue(recorder.is_recording(7, "sp"))
            self.assertTrue(recorder.is_recording(7, "pf"))
            recorder.stop_all()

    def test_timeout_stop_then_reconnect_restarts_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            clock = FakeClock(datetime(2026, 3, 18, 12, 0, 0))
            recorder = AutoRecorder(
                output_dir=temp_dir,
                inactive_timeout_sec=1.0,
                now_fn=clock.now,
            )

            recorder.update_active_sources([9])
            before_paths = [session.filepath for session in recorder.sessions_snapshot()]
            self.assertEqual(len(before_paths), 2)

            clock.advance(1.2)
            stopped = recorder.sweep_inactive()
            self.assertEqual(stopped, [9])
            self.assertEqual(recorder.sessions_snapshot(), [])

            clock.advance(0.1)
            recorder.update_active_sources([9])
            after_paths = [session.filepath for session in recorder.sessions_snapshot()]

            self.assertEqual(len(after_paths), 2)
            self.assertNotEqual(set(before_paths), set(after_paths))
            self.assertTrue(recorder.is_recording(9, "sp"))
            self.assertTrue(recorder.is_recording(9, "pf"))
            recorder.stop_all()


if __name__ == "__main__":
    unittest.main()
