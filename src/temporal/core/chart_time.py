from __future__ import annotations

from typing import Any


DEFAULT_CHART_SAMPLE_STEP = 200
DEFAULT_CHART_TICK_COUNT = 10


def build_default_chart_ticks(
    *,
    tick_count: int = DEFAULT_CHART_TICK_COUNT,
    sample_step: int = DEFAULT_CHART_SAMPLE_STEP,
) -> list[str]:
    safe_tick_count = max(1, int(tick_count))
    safe_sample_step = max(1, int(sample_step))
    return [str(index * safe_sample_step) for index in range(safe_tick_count)]


def build_relative_window_frames(
    tracking_frames: list[dict[str, Any]],
    *,
    start_position: int,
    window_size: int,
    sample_step: int = DEFAULT_CHART_SAMPLE_STEP,
) -> list[dict[str, Any]]:
    if not tracking_frames:
        return []

    safe_step = max(1, int(sample_step))
    safe_window_size = max(1, int(window_size))
    safe_start_position = max(0, int(start_position))
    frame_count = len(tracking_frames)
    window_frames: list[dict[str, Any]] = []
    for index in range(safe_window_size):
        frame = tracking_frames[(safe_start_position + index) % frame_count]
        window_frames.append(
            {
                "sample": (safe_start_position + index) * safe_step,
                "sources": list(frame.get("sources", [])),
            }
        )
    return window_frames
