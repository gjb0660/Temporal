from __future__ import annotations

from collections import deque
from math import atan2, ceil, degrees, sqrt
from time import monotonic
from typing import Any, Protocol

from temporal.core.network.odas_message_view import (
    count_potentials,
    extract_source_ids,
    extract_source_positions,
)
from temporal.core.source_palette import SOURCE_COLOR_PALETTE
from temporal.core.source_tracking import SourceObservation, SpaceTargetSession, TrackingResult
from temporal.core.ui_projection import (
    build_rows_model_items,
    compute_sidebar_sources,
)

from . import recording_audio, remote_lifecycle, status_state


class StreamProjectionBridge(Protocol):
    _AUDIO_CHANNELS: int
    _AUDIO_SAMPLE_WIDTH: int
    _RUNTIME_CHART_X_TICKS: list[dict[str, Any]]
    _RUNTIME_CHART_COMMIT_INTERVAL_MS: int
    _runtime_chart_samples: deque[int]
    _runtime_chart_frame_sources: dict[int, dict[str, float | int]]
    _runtime_catalog_by_target: dict[int, dict[str, Any]]
    _runtime_series_cache: dict[int, deque[dict[str, float | int | None]]]
    _runtime_series_last_sample: int | None
    _runtime_chart_visible_rows: dict[int, dict[str, Any]]
    _runtime_chart_visible_target_ids: list[int]
    _runtime_target_colors: dict[int, str]
    _runtime_source_target_alias: dict[int, int]
    _chart_commit_dirty: bool
    _chart_next_commit_at: float
    _chart_commit_timer: Any
    _runtime_tracking_result: TrackingResult
    _space_target_session: SpaceTargetSession
    _source_channel_map: dict[int, int]
    _channel_source_map: dict[int, int]
    _last_sst: dict
    _last_ssl: dict
    _source_ids: list[int]
    _selected_source_ids: set[int]
    _source_items: list[str]
    _source_positions: list[dict[str, float | int]]
    _sources_enabled: bool
    _potentials_enabled: bool
    _potential_min: float
    _potential_max: float
    _potential_count: int
    _recording_source_count: int
    _recording_sessions: list[str]
    _recording_sample_rate_warning: str
    _streams_active: bool
    _client: Any
    _recorder: Any
    _source_rows_model: Any
    _source_positions_model: Any
    _elevation_chart_series_model: Any
    _azimuth_chart_series_model: Any
    _chart_window_model: Any
    sourceCount: int

    sourcesEnabledChanged: Any
    potentialsEnabledChanged: Any
    potentialRangeChanged: Any
    sourceIdsChanged: Any
    sourceItemsChanged: Any
    sourceCountChanged: Any
    sourcePositionsChanged: Any
    potentialCountChanged: Any

    def setStatus(self, status: str) -> None: ...
    def startStreams(self) -> None: ...
    def stopStreams(self) -> None: ...

    def _refresh_recording_sessions(self) -> None: ...
    def _apply_recording_sample_rates(self) -> None: ...


__all__ = [
    "StreamProjectionBridge",
    "append_runtime_chart_frame",
    "current_runtime_frame_sources",
    "on_pf_audio",
    "on_sep_audio",
    "on_sst",
    "on_ssl",
    "refresh_chart_models",
    "flush_chart_models_if_due",
    "refresh_potentials",
    "refresh_sources",
    "reset_runtime_chart_clock",
    "set_potential_energy_range",
    "set_potentials_enabled",
    "set_source_selected",
    "set_source_positions",
    "set_sources_enabled",
    "start_streams",
    "stop_streams",
    "toggle_streams",
]

_HISTORY_ROW_LIMIT = len(SOURCE_COLOR_PALETTE)


def start_streams(bridge: StreamProjectionBridge) -> None:
    if bridge._streams_active:
        remote_lifecycle.update_stream_status(bridge, "正在监听 SST/SSL/SSS 数据流")
        return

    try:
        bridge._client.start()
    except Exception as exc:
        status_state.set_streams_active(bridge, False)
        bridge.setStatus(f"本地监听启动失败: {exc}")
        return

    reset_runtime_chart_clock(bridge)
    status_state.set_streams_active(bridge, True)
    bridge._chart_next_commit_at = 0.0
    bridge._chart_commit_timer.start()
    remote_lifecycle.apply_state_status(bridge)


def stop_streams(bridge: StreamProjectionBridge) -> None:
    flush_chart_models_if_due(bridge, force=True)
    bridge._chart_commit_timer.stop()
    bridge._client.stop()
    bridge._recorder.stop_all()
    bridge._source_channel_map.clear()
    bridge._channel_source_map.clear()
    reset_runtime_chart_clock(bridge)
    status_state.set_streams_active(bridge, False)
    status_state.set_recording_source_count(bridge, 0)
    recording_audio.set_recording_sessions(bridge, [])
    remote_lifecycle.apply_state_status(bridge)


def toggle_streams(bridge: StreamProjectionBridge) -> None:
    if bridge._streams_active:
        bridge.stopStreams()
        return
    bridge.startStreams()


def set_sources_enabled(bridge: StreamProjectionBridge, enabled: bool) -> None:
    if bridge._sources_enabled == enabled:
        return
    bridge._sources_enabled = enabled
    bridge.sourcesEnabledChanged.emit()
    refresh_sources(bridge)
    remote_lifecycle.update_stream_status(bridge, "声源筛选已更新")


def set_source_selected(bridge: StreamProjectionBridge, source_id: int, selected: bool) -> None:
    target_id = bridge._runtime_source_target_alias.get(int(source_id))
    if target_id is None:
        return

    changed = False
    if selected and target_id not in bridge._selected_source_ids:
        bridge._selected_source_ids.add(target_id)
        changed = True
    if not selected and target_id in bridge._selected_source_ids:
        bridge._selected_source_ids.remove(target_id)
        changed = True

    if not changed:
        return

    refresh_sources(bridge)
    remote_lifecycle.update_stream_status(bridge, "声源选择已更新")


def set_potentials_enabled(bridge: StreamProjectionBridge, enabled: bool) -> None:
    if bridge._potentials_enabled == enabled:
        return
    bridge._potentials_enabled = enabled
    bridge.potentialsEnabledChanged.emit()
    refresh_potentials(bridge)
    remote_lifecycle.update_stream_status(bridge, "候选点筛选已更新")


def set_potential_energy_range(
    bridge: StreamProjectionBridge, minimum: float, maximum: float
) -> None:
    low = min(minimum, maximum)
    high = max(minimum, maximum)
    if bridge._potential_min == low and bridge._potential_max == high:
        return
    bridge._potential_min = low
    bridge._potential_max = high
    bridge.potentialRangeChanged.emit()
    refresh_potentials(bridge)
    remote_lifecycle.update_stream_status(bridge, "候选能量范围已更新")


def on_sst(bridge: StreamProjectionBridge, message: dict[str, Any]) -> None:
    bridge._last_sst = message
    has_chart_sample = append_runtime_chart_frame(bridge, message)
    refresh_sources(bridge, refresh_chart=False)
    if has_chart_sample:
        _append_chart_series_sample(bridge)
        bridge._chart_commit_dirty = True
        flush_chart_models_if_due(bridge, force=not bridge._streams_active)
    active_source_ids = extract_source_ids(message)
    recording_audio.sync_recording_state_from_sources(bridge, active_source_ids)
    remote_lifecycle.update_stream_status(bridge, "SST 数据已更新")


def on_ssl(bridge: StreamProjectionBridge, message: dict[str, Any]) -> None:
    bridge._last_ssl = message
    refresh_potentials(bridge)
    remote_lifecycle.update_stream_status(bridge, "SSL 数据已更新")


def on_sep_audio(bridge: StreamProjectionBridge, chunk: bytes) -> None:
    recording_audio.route_audio_chunk(bridge, chunk, mode="sp")


def on_pf_audio(bridge: StreamProjectionBridge, chunk: bytes) -> None:
    recording_audio.route_audio_chunk(bridge, chunk, mode="pf")


def set_source_positions(
    bridge: StreamProjectionBridge, positions: list[dict[str, float | int]]
) -> None:
    if positions != bridge._source_positions:
        bridge._source_positions = positions
        bridge.sourcePositionsChanged.emit()
    bridge._source_positions_model.replace(
        [
            {
                "id": int(item["id"]),
                "color": item.get("color", ""),
                "x": float(item["x"]),
                "y": float(item["y"]),
                "z": float(item["z"]),
            }
            for item in positions
        ]
    )


def refresh_sources(bridge: StreamProjectionBridge, *, refresh_chart: bool = True) -> None:
    previous_catalog_target_ids = set(int(value) for value in bridge._runtime_catalog_by_target)
    current_targets = list(bridge._runtime_tracking_result.visible_targets)
    active_target_ids = {int(target.target_id) for target in current_targets}

    catalog_by_target = {
        int(target_id): dict(row) for target_id, row in bridge._runtime_catalog_by_target.items()
    }
    for target in current_targets:
        target_id = int(target.target_id)
        catalog_by_target[target_id] = {
            "targetId": target_id,
            "sourceId": int(target.source_id),
            "lastSample": int(target.sample),
        }
    latest_sample = _latest_chart_sample(bridge)
    if latest_sample is not None:
        catalog_by_target = {
            int(target_id): dict(row)
            for target_id, row in catalog_by_target.items()
            if latest_sample - int(row.get("lastSample", latest_sample)) <= 1600
        }
    catalog_by_target = _trim_catalog_targets(
        catalog_by_target,
        active_target_ids=active_target_ids,
        limit=_HISTORY_ROW_LIMIT,
    )
    bridge._runtime_target_colors = _assign_catalog_colors(
        catalog_by_target,
        bridge._runtime_target_colors,
    )
    for target_id, row in catalog_by_target.items():
        row["color"] = str(bridge._runtime_target_colors.get(int(target_id), ""))

    catalog_rows = sorted(
        catalog_by_target.values(),
        key=lambda row: (int(row["sourceId"]), int(row["targetId"])),
    )
    bridge._runtime_catalog_by_target = {int(row["targetId"]): dict(row) for row in catalog_rows}
    catalog_target_ids = [int(row["targetId"]) for row in catalog_rows]
    catalog_target_id_set = set(catalog_target_ids)
    bridge._runtime_series_cache = {
        int(target_id): cache
        for target_id, cache in bridge._runtime_series_cache.items()
        if int(target_id) in catalog_target_id_set
    }

    bridge._selected_source_ids = {
        target_id for target_id in bridge._selected_source_ids if target_id in catalog_target_id_set
    }
    for target_id in catalog_target_ids:
        if target_id in previous_catalog_target_ids:
            continue
        if target_id not in bridge._selected_source_ids:
            bridge._selected_source_ids.add(target_id)

    display_source_ids = [int(row["sourceId"]) for row in catalog_rows]
    bridge._runtime_source_target_alias = {
        int(row["sourceId"]): int(row["targetId"]) for row in catalog_rows
    }
    if display_source_ids != bridge._source_ids:
        bridge._source_ids = display_source_ids
        bridge.sourceIdsChanged.emit()

    items = [f"Source {source_id}" for source_id in display_source_ids]
    if items != bridge._source_items:
        bridge._source_items = items
        bridge.sourceItemsChanged.emit()
        bridge.sourceCountChanged.emit()

    sidebar_sources = compute_sidebar_sources(
        [
            {
                "id": int(row["sourceId"]),
                "targetId": int(row["targetId"]),
                "color": str(row["color"]),
            }
            for row in catalog_rows
        ],
        sources_enabled=True,
        potentials_enabled=False,
        potential_min=0.0,
        potential_max=1.0,
    )
    visible_target_ids = (
        [
            int(source["targetId"])
            for source in sidebar_sources
            if int(source["targetId"]) in bridge._selected_source_ids
        ]
        if bridge._sources_enabled
        else []
    )
    visible_rows_by_target = {int(source["targetId"]): source for source in sidebar_sources}
    bridge._runtime_chart_visible_rows = {
        int(target_id): dict(row) for target_id, row in visible_rows_by_target.items()
    }
    bridge._runtime_chart_visible_target_ids = list(visible_target_ids)

    current_frame_sources = current_runtime_frame_sources(bridge)
    visible_target_id_set = set(visible_target_ids)
    positions = [
        {
            "id": int(frame_source["sourceId"]),
            "color": str(visible_rows_by_target[target_id]["color"]),
            "x": float(frame_source["x"]),
            "y": float(frame_source["y"]),
            "z": float(frame_source["z"]),
        }
        for target_id, frame_source in current_frame_sources.items()
        if target_id in visible_rows_by_target and target_id in visible_target_id_set
    ]
    set_source_positions(bridge, positions)
    bridge._source_rows_model.replace(
        build_rows_model_items(
            sidebar_sources,
            bridge._selected_source_ids,
            active_source_ids=active_target_ids,
        )
    )
    if refresh_chart:
        _append_chart_series_sample(bridge)
        refresh_chart_models(bridge, visible_rows_by_target, visible_target_ids)


def _latest_chart_sample(bridge: StreamProjectionBridge) -> int | None:
    if not bridge._runtime_chart_samples:
        return None
    return int(bridge._runtime_chart_samples[-1])


def _trim_catalog_targets(
    catalog_by_target: dict[int, dict[str, Any]],
    *,
    active_target_ids: set[int],
    limit: int,
) -> dict[int, dict[str, Any]]:
    if limit <= 0:
        return {}
    if len(catalog_by_target) <= limit:
        return {int(target_id): dict(row) for target_id, row in catalog_by_target.items()}

    rows = [dict(row) for row in catalog_by_target.values()]
    active_rows = [row for row in rows if int(row["targetId"]) in active_target_ids]
    inactive_rows = [row for row in rows if int(row["targetId"]) not in active_target_ids]
    active_rows.sort(key=lambda row: (-int(row["lastSample"]), int(row["targetId"])))
    inactive_rows.sort(key=lambda row: (-int(row["lastSample"]), int(row["targetId"])))
    kept_rows = active_rows[:limit]
    if len(kept_rows) < limit:
        kept_rows.extend(inactive_rows[: limit - len(kept_rows)])
    return {int(row["targetId"]): row for row in kept_rows}


def _assign_catalog_colors(
    catalog_by_target: dict[int, dict[str, Any]],
    previous_colors: dict[int, str],
) -> dict[int, str]:
    palette = tuple(str(color) for color in SOURCE_COLOR_PALETTE) or ("#4bc0c0",)
    rows = [dict(row) for row in catalog_by_target.values()]
    by_target_asc = sorted(rows, key=lambda row: int(row["targetId"]))
    by_recent = sorted(rows, key=lambda row: (-int(row["lastSample"]), int(row["targetId"])))

    assigned: dict[int, str] = {}
    occupied_colors: set[str] = set()
    for row in by_target_asc:
        target_id = int(row["targetId"])
        color = str(previous_colors.get(target_id, ""))
        if color not in palette or color in occupied_colors:
            continue
        assigned[target_id] = color
        occupied_colors.add(color)

    for row in by_recent:
        target_id = int(row["targetId"])
        if target_id in assigned:
            continue
        next_color = next((color for color in palette if color not in occupied_colors), "")
        if not next_color:
            continue
        assigned[target_id] = next_color
        occupied_colors.add(next_color)
    return assigned


def _append_chart_series_sample(bridge: StreamProjectionBridge) -> None:
    sample = _latest_chart_sample(bridge)
    if sample is None:
        return
    if bridge._runtime_series_last_sample is not None and int(
        bridge._runtime_series_last_sample
    ) == int(sample):
        return

    current_frame_sources = current_runtime_frame_sources(bridge)
    for target_id in bridge._runtime_catalog_by_target:
        tid = int(target_id)
        cache = bridge._runtime_series_cache.get(tid)
        if cache is None:
            cache = deque(maxlen=1600)
            bridge._runtime_series_cache[tid] = cache
        source = current_frame_sources.get(tid)
        if source is None:
            cache.append({"x": int(sample), "elevation": None, "azimuth": None})
            continue
        cache.append(
            {
                "x": int(sample),
                "elevation": _axis_value(source, axis="elevation"),
                "azimuth": _axis_value(source, axis="azimuth"),
            }
        )
    bridge._runtime_series_last_sample = int(sample)


def flush_chart_models_if_due(
    bridge: StreamProjectionBridge,
    *,
    force: bool = False,
) -> None:
    if not bridge._chart_commit_dirty:
        return
    now = monotonic()
    if not force and now < bridge._chart_next_commit_at:
        return
    refresh_chart_models(
        bridge,
        bridge._runtime_chart_visible_rows,
        bridge._runtime_chart_visible_target_ids,
    )
    bridge._chart_commit_dirty = False
    interval_ms = max(1, int(bridge._RUNTIME_CHART_COMMIT_INTERVAL_MS))
    bridge._chart_next_commit_at = now + (interval_ms / 1000.0)


def _build_chart_window_ticks(samples: deque[int]) -> list[dict[str, Any]]:
    if not samples:
        return []
    latest = int(samples[-1])
    window_start = latest - 1600
    tick_step = 200
    first_tick = int(ceil(window_start / tick_step) * tick_step)
    ticks = [
        {
            "value": int(value),
            "label": str(int(value)),
            "isMajor": int(value) % tick_step == 0,
            "isLatest": int(value) == latest,
        }
        for value in range(first_tick, latest + 1, tick_step)
        if window_start <= int(value) <= latest
    ]
    if latest % tick_step != 0:
        ticks.append(
            {
                "value": latest,
                "label": str(latest),
                "isMajor": latest % tick_step == 0,
                "isLatest": True,
            }
        )
    return ticks


def refresh_chart_models(
    bridge: StreamProjectionBridge,
    visible_rows: dict[int, dict[str, Any]],
    visible_source_ids: list[int],
) -> None:
    bridge._chart_window_model.replace(_build_chart_window_ticks(bridge._runtime_chart_samples))
    bridge._elevation_chart_series_model.replace(
        chart_series_model_items(
            bridge,
            visible_rows,
            visible_source_ids,
            axis="elevation",
        )
    )
    bridge._azimuth_chart_series_model.replace(
        chart_series_model_items(
            bridge,
            visible_rows,
            visible_source_ids,
            axis="azimuth",
        )
    )


def chart_series_model_items(
    bridge: StreamProjectionBridge,
    visible_rows: dict[int, dict[str, Any]],
    visible_source_ids: list[int],
    *,
    axis: str,
) -> list[dict[str, Any]]:
    if not bridge._runtime_chart_samples:
        return []
    axis_key = "elevation" if axis == "elevation" else "azimuth"
    items: list[dict[str, Any]] = []
    for target_id in visible_source_ids:
        row = visible_rows.get(int(target_id))
        if row is None:
            continue
        cache = bridge._runtime_series_cache.get(int(target_id))
        if not cache:
            continue
        points: list[dict[str, float | int | None]] = []
        for point in cache:
            sample = point.get("x")
            if sample is None:
                continue
            points.append({"x": int(sample), "y": point.get(axis_key)})
        items.append(
            {
                "sourceId": int(row["id"]),
                "color": str(row.get("color", "")),
                "points": points,
            }
        )
    return items


def _axis_value(source: dict[str, Any], *, axis: str) -> float:
    x = float(source.get("x", 0.0))
    y = float(source.get("y", 0.0))
    z = float(source.get("z", 0.0))
    if axis == "elevation":
        return degrees(atan2(z, sqrt(x * x + y * y)))
    return degrees(atan2(y, x))


def append_runtime_chart_frame(bridge: StreamProjectionBridge, message: dict[str, Any]) -> bool:
    positions = extract_source_positions(
        message,
        enabled=True,
        selected_ids=None,
    )
    normalized_sources = [
        {
            "id": int(item["id"]),
            "x": float(item["x"]),
            "y": float(item["y"]),
            "z": float(item["z"]),
        }
        for item in positions
    ]
    sample_raw = message.get("timeStamp")
    has_timestamp = type(sample_raw) is int
    sample = int(sample_raw) if has_timestamp else _next_tracking_sample(bridge)
    bridge._runtime_tracking_result = bridge._space_target_session.step(
        [
            SourceObservation(
                source_id=int(item["id"]),
                sample=sample,
                x=float(item["x"]),
                y=float(item["y"]),
                z=float(item["z"]),
            )
            for item in normalized_sources
        ]
    )
    bridge._runtime_chart_frame_sources = {
        int(target.target_id): {
            "sourceId": int(target.source_id),
            "x": float(target.x),
            "y": float(target.y),
            "z": float(target.z),
        }
        for target in bridge._runtime_tracking_result.visible_targets
    }
    if not has_timestamp:
        return False

    bridge._runtime_chart_samples.append(int(sample))
    return True


def _next_tracking_sample(bridge: StreamProjectionBridge) -> int:
    if bridge._runtime_tracking_result.visible_targets:
        return (
            max(int(target.sample) for target in bridge._runtime_tracking_result.visible_targets)
            + 1
        )
    if bridge._runtime_chart_samples:
        return int(bridge._runtime_chart_samples[-1]) + 1
    return 0


def reset_runtime_chart_clock(bridge: StreamProjectionBridge) -> None:
    bridge._chart_commit_timer.stop()
    bridge._chart_commit_dirty = False
    bridge._chart_next_commit_at = 0.0
    bridge._runtime_chart_samples.clear()
    bridge._runtime_chart_frame_sources = {}
    bridge._runtime_catalog_by_target = {}
    bridge._runtime_series_cache = {}
    bridge._runtime_series_last_sample = None
    bridge._runtime_chart_visible_rows = {}
    bridge._runtime_chart_visible_target_ids = []
    bridge._runtime_target_colors = {}
    bridge._runtime_source_target_alias = {}
    bridge._runtime_tracking_result = TrackingResult(
        visible_targets=[],
        dropped_source_ids=[],
    )
    bridge._space_target_session = SpaceTargetSession()
    bridge._chart_window_model.replace(bridge._RUNTIME_CHART_X_TICKS)
    bridge._elevation_chart_series_model.replace([])
    bridge._azimuth_chart_series_model.replace([])


def current_runtime_frame_sources(
    bridge: StreamProjectionBridge,
) -> dict[int, dict[str, float | int]]:
    return dict(bridge._runtime_chart_frame_sources)


def refresh_potentials(bridge: StreamProjectionBridge) -> None:
    count = count_potentials(
        bridge._last_ssl,
        min_energy=bridge._potential_min,
        max_energy=bridge._potential_max,
        enabled=bridge._potentials_enabled,
    )
    if count != bridge._potential_count:
        bridge._potential_count = count
        bridge.potentialCountChanged.emit()
