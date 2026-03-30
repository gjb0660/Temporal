from __future__ import annotations

import json
from math import acos, atan2, degrees, sqrt
from typing import Any


def compute_sidebar_sources(
    sources: list[dict[str, Any]],
    *,
    sources_enabled: bool,
    potentials_enabled: bool,
    potential_min: float,
    potential_max: float,
) -> list[dict[str, Any]]:
    if not sources_enabled:
        return []
    if not potentials_enabled:
        return list(sources)
    low = min(potential_min, potential_max)
    high = max(potential_min, potential_max)
    return [
        source
        for source in sources
        if low <= float(source.get("energy", 0.0)) <= high
    ]


def compute_visible_source_ids(
    sidebar_sources: list[dict[str, Any]],
    selected_source_ids: set[int],
) -> list[int]:
    return [
        int(source["id"])
        for source in sidebar_sources
        if int(source["id"]) in selected_source_ids
    ]


def build_rows_model_items(
    sidebar_sources: list[dict[str, Any]],
    selected_source_ids: set[int],
) -> list[dict[str, Any]]:
    return [
        {
            "sourceId": int(source["id"]),
            "label": "声源",
            "checked": int(source["id"]) in selected_source_ids,
            "enabled": True,
            "badge": str(int(source["id"])),
            "badgeColor": str(source.get("color", "#cf54ea")),
        }
        for source in sidebar_sources
    ]


def build_positions_model_items(
    current_frame_sources: dict[int, dict[str, float]],
    visible_rows: dict[int, dict[str, Any]],
    visible_source_ids: set[int],
) -> list[dict[str, Any]]:
    return [
        {
            "id": source_id,
            "color": str(visible_rows[source_id].get("color", "#cf54ea")),
            "x": float(frame_source["x"]),
            "y": float(frame_source["y"]),
            "z": float(frame_source["z"]),
        }
        for source_id, frame_source in current_frame_sources.items()
        if source_id in visible_rows and source_id in visible_source_ids
    ]


def build_chart_ticks(
    window_frames: list[dict[str, Any]],
    *,
    tick_count: int,
    fallback_sample_start: int,
    fallback_sample_step: int,
) -> list[str]:
    safe_tick_count = max(1, int(tick_count))
    if not window_frames:
        return [
            str(int(fallback_sample_start) + int(fallback_sample_step) * index)
            for index in range(safe_tick_count)
        ]
    return [str(int(frame.get("sample", 0))) for frame in window_frames[:safe_tick_count]]


def build_chart_series(
    window_frames: list[dict[str, Any]],
    visible_rows: dict[int, dict[str, Any]],
    visible_source_ids: list[int],
    *,
    axis: str,
) -> list[dict[str, Any]]:
    if not window_frames:
        return []

    values_by_source: dict[int, list[float]] = {source_id: [] for source_id in visible_source_ids}
    for frame in window_frames:
        frame_sources = {
            int(source["id"]): source
            for source in frame.get("sources", [])
            if isinstance(source, dict) and isinstance(source.get("id"), int)
        }
        for source_id in visible_source_ids:
            source = frame_sources.get(source_id)
            if source is None:
                continue
            values_by_source[source_id].append(normalized_axis_value(source, axis=axis))

    return [
        {
            "sourceId": source_id,
            "color": str(visible_rows[source_id].get("color", "#cf54ea")),
            "valuesJson": json.dumps(values),
        }
        for source_id, values in values_by_source.items()
        if values
    ]


def normalized_axis_value(source: dict[str, Any], *, axis: str) -> float:
    x = float(source.get("x", 0.0))
    y = float(source.get("y", 0.0))
    z = float(source.get("z", 0.0))
    length = max(0.0001, sqrt(x * x + y * y + z * z))
    if axis == "elevation":
        elevation_deg = 90.0 - degrees(acos(max(-1.0, min(1.0, z / length))))
        return (elevation_deg + 90.0) / 180.0
    azimuth_deg = degrees(atan2(y, x))
    return (azimuth_deg + 180.0) / 360.0
