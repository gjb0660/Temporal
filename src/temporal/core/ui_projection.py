from __future__ import annotations

from typing import Any

from temporal.core.chart_window import build_chart_series_model, build_chart_window_model


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
    return [source for source in sources if low <= float(source.get("energy", 0.0)) <= high]


def compute_visible_source_ids(
    sidebar_sources: list[dict[str, Any]],
    selected_source_ids: set[int],
) -> list[int]:
    return [
        int(source["id"]) for source in sidebar_sources if int(source["id"]) in selected_source_ids
    ]


def build_rows_model_items(
    sidebar_sources: list[dict[str, Any]],
    selected_source_ids: set[int],
    *,
    active_source_ids: set[int] | None = None,
) -> list[dict[str, Any]]:
    active_ids = set(active_source_ids or set())
    rows: list[dict[str, Any]] = []
    for source in sidebar_sources:
        source_id = int(source["id"])
        target_id = int(source.get("targetId", source_id))
        rows.append(
            {
                "sourceId": source_id,
                "label": "声源",
                "checked": target_id in selected_source_ids,
                "enabled": True,
                "active": target_id in active_ids,
                "badge": str(source_id),
                "badgeColor": str(source.get("color", "")),
            }
        )
    return rows


def build_positions_model_items(
    current_frame_sources: dict[int, dict[str, float]],
    visible_rows: dict[int, dict[str, Any]],
    visible_source_ids: set[int],
) -> list[dict[str, Any]]:
    return [
        {
            "id": source_id,
            "color": str(visible_rows[source_id].get("color", "")),
            "x": float(frame_source["x"]),
            "y": float(frame_source["y"]),
            "z": float(frame_source["z"]),
        }
        for source_id, frame_source in current_frame_sources.items()
        if source_id in visible_rows and source_id in visible_source_ids
    ]


def build_chart_ticks(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    messages = list(args[0]) if args else list(kwargs.pop("messages", []))
    return build_chart_window_model(messages)["ticks"]


def build_chart_series(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    messages = list(args[0]) if args else list(kwargs.pop("messages", []))
    visible_rows = dict(args[1]) if len(args) > 1 else dict(kwargs.pop("visible_rows", {}))
    visible_source_ids = (
        list(args[2]) if len(args) > 2 else list(kwargs.pop("visible_source_ids", []))
    )
    axis = str(kwargs.pop("axis", "elevation"))
    return build_chart_series_model(
        messages,
        visible_rows,
        visible_source_ids,
        axis=axis,
    )
