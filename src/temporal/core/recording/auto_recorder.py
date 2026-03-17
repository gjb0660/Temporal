from __future__ import annotations

import wave
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

    def __init__(self, output_dir: str | Path) -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._writers: dict[tuple[int, str], wave.Wave_write] = {}
        self._sessions: dict[tuple[int, str], RecorderSession] = {}

    def start(self, source_id: int, mode: str) -> RecorderSession:
        key = (source_id, mode)
        if key in self._sessions:
            return self._sessions[key]

        now = datetime.now()
        stamp = now.strftime("%Y-%m-%d_%H-%M-%S-%f")
        path = self._output_dir / f"ODAS_{source_id}_{stamp}_{mode}.wav"

        writer = wave.open(str(path), "wb")
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.setframerate(16000)

        session = RecorderSession(source_id=source_id, mode=mode, started_at=now, filepath=path)
        self._writers[key] = writer
        self._sessions[key] = session
        return session

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
