from __future__ import annotations

from math import atan2, ceil, degrees, sqrt
from typing import Any


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _frame_sample(frame: dict[str, Any]) -> int | None:
    sample = _coerce_int(frame.get("sample"))
    if sample is not None:
        return sample
    return _coerce_int(frame.get("timeStamp"))


def _normalize_sources(frame: dict[str, Any]) -> list[dict[str, float | int]]:
    sources: list[dict[str, float | int]] = []
    for source in frame.get("sources", []):
        if not isinstance(source, dict):
            continue
        source_id = _coerce_int(source.get("id"))
        if source_id is None:
            continue
        sources.append(
            {
                "id": source_id,
                "x": _coerce_float(source.get("x")),
                "y": _coerce_float(source.get("y")),
                "z": _coerce_float(source.get("z")),
            }
        )
    return sources


def normalize_chart_frames(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    for frame in messages:
        if not isinstance(frame, dict):
            continue
        sample = _frame_sample(frame)
        if sample is None:
            continue
        frames.append(
            {
                "sample": sample,
                "sources": _normalize_sources(frame),
            }
        )
    frames.sort(key=lambda item: int(item["sample"]))
    return frames


def _visible_window_frames(
    messages: list[dict[str, Any]],
    *,
    window_size: int,
) -> tuple[list[dict[str, Any]], int, int]:
    frames = normalize_chart_frames(messages)
    if not frames:
        return [], 0, 0
    latest = int(frames[-1]["sample"])
    window_start = latest - max(0, int(window_size))
    return [
        frame for frame in frames if window_start <= int(frame["sample"]) <= latest
    ], window_start, latest


def _build_tick(value: int, latest: int, tick_step: int) -> dict[str, Any]:
    return {
        "value": int(value),
        "label": str(int(value)),
        "isMajor": int(value) % tick_step == 0,
        "isLatest": int(value) == int(latest),
    }


def build_chart_window_model(
    messages: list[dict[str, Any]],
    *,
    window_size: int = 1600,
    tick_step: int = 200,
) -> dict[str, Any]:
    window_frames, window_start, latest = _visible_window_frames(
        messages,
        window_size=window_size,
    )
    if not window_frames:
        return {
            "windowStart": None,
            "windowEnd": None,
            "latest": None,
            "windowSize": int(window_size),
            "tickStep": int(max(1, tick_step)),
            "ticks": [],
        }

    safe_step = max(1, int(tick_step))
    first_major_tick = int(ceil(window_start / safe_step) * safe_step)
    ticks = [
        _build_tick(value, latest, safe_step)
        for value in range(first_major_tick, latest + 1, safe_step)
        if window_start <= value <= latest
    ]
    if latest % safe_step != 0:
        ticks.append(_build_tick(latest, latest, safe_step))

    return {
        "windowStart": window_start,
        "windowEnd": latest,
        "latest": latest,
        "windowSize": int(window_size),
        "tickStep": safe_step,
        "ticks": ticks,
    }


def _axis_value(source: dict[str, float | int], *, axis: str) -> float:
    x = _coerce_float(source.get("x"))
    y = _coerce_float(source.get("y"))
    z = _coerce_float(source.get("z"))
    if axis == "elevation":
        return degrees(atan2(z, sqrt(x * x + y * y)))
    return degrees(atan2(y, x))


def build_chart_series_model(
    messages: list[dict[str, Any]],
    visible_rows: dict[int, dict[str, Any]],
    visible_source_ids: list[int],
    *,
    axis: str,
    window_size: int = 1600,
) -> list[dict[str, Any]]:
    window_frames, _, _ = _visible_window_frames(messages, window_size=window_size)
    if not window_frames:
        return []

    source_lookup = {
        int(source_id): dict(row)
        for source_id, row in visible_rows.items()
        if isinstance(source_id, int)
    }
    visible_ids = [int(source_id) for source_id in visible_source_ids if int(source_id) in source_lookup]
    if not visible_ids:
        return []

    series: list[dict[str, Any]] = []
    for source_id in visible_ids:
        row = source_lookup[source_id]
        points: list[dict[str, float | int | None]] = []
        for frame in window_frames:
            frame_sources = {
                int(source["id"]): source
                for source in frame.get("sources", [])
                if isinstance(source, dict) and isinstance(source.get("id"), int)
            }
            source = frame_sources.get(source_id)
            points.append(
                {
                    "x": int(frame["sample"]),
                    "y": None if source is None else _axis_value(source, axis=axis),
                }
            )
        series.append(
            {
                "sourceId": source_id,
                "color": str(row.get("color", "")),
                "points": points,
            }
        )
    return series
