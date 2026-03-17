from __future__ import annotations

import json


class JsonStreamBuffer:
    """Decode line-delimited JSON from chunked TCP data."""

    def __init__(self) -> None:
        self._buffer = ""

    def feed(self, chunk: bytes) -> list[dict]:
        text = chunk.decode("utf-8", errors="replace")
        self._buffer += text

        out: list[dict] = []
        while True:
            idx = self._buffer.find("\n")
            if idx < 0:
                break
            raw = self._buffer[:idx].strip()
            self._buffer = self._buffer[idx + 1 :]
            if not raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                out.append(data)
        return out
