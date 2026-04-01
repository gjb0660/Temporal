from __future__ import annotations

import json


class JsonStreamBuffer:
    """Decode object-framed JSON from chunked TCP data."""

    def __init__(self) -> None:
        self._buffer = ""

    def feed(self, chunk: bytes) -> list[dict]:
        text = chunk.decode("utf-8", errors="replace")
        self._buffer += text

        out: list[dict] = []
        while True:
            start = self._buffer.find("{")
            if start < 0:
                self._buffer = ""
                break

            if start > 0:
                self._buffer = self._buffer[start:]
                start = 0

            parsed = self._extract_next_object_text(start)
            if parsed is None:
                break
            raw, end_index = parsed
            self._buffer = self._buffer[end_index:]

            # ODAS JSON sinks render multi-line object payloads.
            if "\n" not in raw:
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                out.append(data)
        return out

    def _extract_next_object_text(self, start: int) -> tuple[str, int] | None:
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(self._buffer)):
            char = self._buffer[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
                continue
            if char == "{":
                depth += 1
                continue
            if char == "}":
                depth -= 1
                if depth == 0:
                    return self._buffer[start : index + 1], index + 1
        return None
