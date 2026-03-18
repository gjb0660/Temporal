from __future__ import annotations

import wave
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class RecorderSession:
    source_id: int
    mode: str
    started_at: datetime
    filepath: Path


class AutoRecorder:
    """Source-driven recorder: start on source appear, stop on disappear."""

    def __init__(
        self,
        output_dir: str | Path,
        inactive_timeout_sec: float = 2.0,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._writers: dict[tuple[int, str], wave.Wave_write] = {}
        self._sessions: dict[tuple[int, str], RecorderSession] = {}
        self._last_seen: dict[int, datetime] = {}
        self._inactive_timeout_sec = max(0.1, inactive_timeout_sec)
        self._now_fn = now_fn or datetime.now

    def start(self, source_id: int, mode: str) -> RecorderSession:
        key = (source_id, mode)
        if key in self._sessions:
            return self._sessions[key]

        now = self._now_fn()
        stamp = now.strftime("%Y%m%d_%H%M%S_%f")
        path = self._output_dir / f"ODAS_{source_id}_{stamp}_{mode}.wav"

        writer = wave.open(str(path), "wb")
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(16000)

        session = RecorderSession(source_id=source_id, mode=mode, started_at=now, filepath=path)
        self._writers[key] = writer
        self._sessions[key] = session
        return session

    def update_active_sources(
        self, source_ids: Iterable[int], modes: tuple[str, ...] = ("sp", "pf")
    ) -> None:
        now = self._now_fn()
        for source_id in source_ids:
            if source_id <= 0:
                continue
            self._last_seen[source_id] = now
            for mode in modes:
                self.start(source_id, mode)

    def sweep_inactive(self) -> list[int]:
        now = self._now_fn()
        stopped: list[int] = []
        for source_id, seen_at in list(self._last_seen.items()):
            inactive_seconds = (now - seen_at).total_seconds()
            if inactive_seconds < self._inactive_timeout_sec:
                continue
            self.stop(source_id, "sp")
            self.stop(source_id, "pf")
            self._last_seen.pop(source_id, None)
            stopped.append(source_id)
        return stopped

    def is_recording(self, source_id: int, mode: str) -> bool:
        return (source_id, mode) in self._sessions

    def active_sources(self) -> set[int]:
        return set(self._last_seen.keys())

    def push(self, source_id: int, mode: str, pcm_chunk: bytes) -> None:
        key = (source_id, mode)
        writer = self._writers.get(key)
        if writer is None:
            return
        writer.writeframes(pcm_chunk)

    def stop(self, source_id: int, mode: str) -> None:
        key = (source_id, mode)
        writer = self._writers.pop(key, None)
        if writer is not None:
            writer.close()
        self._sessions.pop(key, None)

    def stop_all(self) -> None:
        for writer in self._writers.values():
            writer.close()
        self._writers.clear()
        self._sessions.clear()
        self._last_seen.clear()
