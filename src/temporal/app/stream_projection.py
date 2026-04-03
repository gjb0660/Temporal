from __future__ import annotations

from math import atan2, degrees, sqrt
from typing import Any, Protocol

from temporal.core.network.odas_message_view import (
    count_potentials,
    extract_source_ids,
    extract_source_positions,
)
from temporal.core.source_tracking import SourceObservation, SpaceTargetSession, TrackingResult
from temporal.core.source_palette import SOURCE_COLOR_PALETTE
from temporal.core.ui_projection import (
    build_chart_window_model,
    build_rows_model_items,
    compute_sidebar_sources,
)

from .remote_lifecycle import apply_state_status, update_stream_status


class StreamProjectionBridge(Protocol):
    _AUDIO_CHANNELS: int
    _AUDIO_SAMPLE_WIDTH: int
    _RUNTIME_CHART_X_TICKS: list[dict[str, Any]]
    _runtime_chart_messages: list[dict[str, Any]]
    _runtime_chart_frame_sources: dict[int, dict[str, float | int]]
    _runtime_target_colors: dict[int, str]
    _runtime_source_target_alias: dict[int, int]
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

    def _set_streams_active(self, active: bool) -> None: ...
    def _set_recording_source_count(self, value: int) -> None: ...
    def _set_recording_sessions(self, sessions: list[str]) -> None: ...
    def _set_source_positions(self, positions: list[dict[str, float | int]]) -> None: ...
    def _refresh_recording_sessions(self) -> None: ...
    def _update_source_channel_map(self, source_ids: list[int]) -> None: ...
    def _refresh_chart_models(
        self,
        visible_rows: dict[int, dict[str, Any]],
        visible_source_ids: list[int],
    ) -> None: ...
    def _refresh_potentials(self) -> None: ...
    def _apply_recording_sample_rates(self) -> None: ...
    def _current_runtime_frame_sources(self) -> dict[int, dict[str, float | int]]: ...
    def _reset_runtime_chart_clock(self) -> None: ...


__all__ = [
    "StreamProjectionBridge",
    "append_runtime_chart_frame",
    "current_runtime_frame_sources",
    "on_pf_audio",
    "on_sep_audio",
    "on_sst",
    "on_ssl",
    "refresh_chart_models",
    "refresh_potentials",
    "refresh_sources",
    "reset_runtime_chart_clock",
    "route_audio_chunk",
    "set_potential_energy_range",
    "set_potentials_enabled",
    "set_source_selected",
    "set_sources_enabled",
    "start_streams",
    "stop_streams",
    "toggle_streams",
    "update_source_channel_map",
]

_HISTORY_ROW_LIMIT = len(SOURCE_COLOR_PALETTE)


def start_streams(bridge: StreamProjectionBridge) -> None:
    if bridge._streams_active:
        update_stream_status(bridge, "正在监听 SST/SSL/SSS 数据流")
        return

    try:
        bridge._client.start()
    except Exception as exc:
        bridge._set_streams_active(False)
        bridge.setStatus(f"本地监听启动失败: {exc}")
        return

    bridge._reset_runtime_chart_clock()
    bridge._set_streams_active(True)
    apply_state_status(bridge)


def stop_streams(bridge: StreamProjectionBridge) -> None:
    bridge._client.stop()
    bridge._recorder.stop_all()
    bridge._source_channel_map.clear()
    bridge._channel_source_map.clear()
    bridge._reset_runtime_chart_clock()
    bridge._set_streams_active(False)
    bridge._set_recording_source_count(0)
    bridge._set_recording_sessions([])
    apply_state_status(bridge)


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
    update_stream_status(bridge, "声源筛选已更新")


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
    update_stream_status(bridge, "声源选择已更新")


def set_potentials_enabled(bridge: StreamProjectionBridge, enabled: bool) -> None:
    if bridge._potentials_enabled == enabled:
        return
    bridge._potentials_enabled = enabled
    bridge.potentialsEnabledChanged.emit()
    refresh_potentials(bridge)
    update_stream_status(bridge, "候选点筛选已更新")


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
    update_stream_status(bridge, "候选能量范围已更新")


def on_sst(bridge: StreamProjectionBridge, message: dict[str, Any]) -> None:
    bridge._last_sst = message
    refresh_chart = append_runtime_chart_frame(bridge, message)
    refresh_sources(bridge, refresh_chart=refresh_chart)
    active_source_ids = extract_source_ids(message)
    update_source_channel_map(bridge, active_source_ids)
    mapped_source_ids = [
        source_id for source_id in active_source_ids if source_id in bridge._source_channel_map
    ]
    bridge._recorder.update_active_sources(mapped_source_ids)
    bridge._recorder.sweep_inactive()
    bridge._set_recording_source_count(len(bridge._recorder.active_sources()))
    bridge._refresh_recording_sessions()
    update_stream_status(bridge, "SST 数据已更新")


def on_ssl(bridge: StreamProjectionBridge, message: dict[str, Any]) -> None:
    bridge._last_ssl = message
    refresh_potentials(bridge)
    update_stream_status(bridge, "SSL 数据已更新")


def on_sep_audio(bridge: StreamProjectionBridge, chunk: bytes) -> None:
    route_audio_chunk(bridge, chunk, mode="sp")


def on_pf_audio(bridge: StreamProjectionBridge, chunk: bytes) -> None:
    route_audio_chunk(bridge, chunk, mode="pf")


def route_audio_chunk(bridge: StreamProjectionBridge, chunk: bytes, mode: str) -> None:
    if not bridge._channel_source_map:
        return

    frame_width = bridge._AUDIO_CHANNELS * bridge._AUDIO_SAMPLE_WIDTH
    usable = len(chunk) - (len(chunk) % frame_width)
    if usable <= 0:
        return

    buffers = {
        channel_index: bytearray()
        for channel_index in bridge._channel_source_map
        if 0 <= channel_index < bridge._AUDIO_CHANNELS
    }
    if not buffers:
        return

    for offset in range(0, usable, frame_width):
        frame = chunk[offset : offset + frame_width]
        for channel_index in buffers:
            sample_offset = channel_index * bridge._AUDIO_SAMPLE_WIDTH
            sample = frame[sample_offset : sample_offset + bridge._AUDIO_SAMPLE_WIDTH]
            buffers[channel_index].extend(sample)

    for channel_index, channel_pcm in buffers.items():
        source_id = bridge._channel_source_map.get(channel_index)
        if source_id is None or not channel_pcm:
            continue
        bridge._recorder.push(source_id, mode, bytes(channel_pcm))


def update_source_channel_map(bridge: StreamProjectionBridge, source_ids: list[int]) -> None:
    next_source_map: dict[int, int] = {}
    used_channels: set[int] = set()

    for source_id in source_ids:
        channel_index = bridge._source_channel_map.get(source_id)
        if channel_index is None or channel_index in used_channels:
            continue
        if not 0 <= channel_index < bridge._AUDIO_CHANNELS:
            continue
        next_source_map[source_id] = channel_index
        used_channels.add(channel_index)

    free_channels = [
        channel_index
        for channel_index in range(bridge._AUDIO_CHANNELS)
        if channel_index not in used_channels
    ]
    for source_id in source_ids:
        if source_id in next_source_map:
            continue
        if not free_channels:
            break
        channel_index = free_channels.pop(0)
        next_source_map[source_id] = channel_index

    bridge._source_channel_map = next_source_map
    bridge._channel_source_map = {
        channel_index: source_id for source_id, channel_index in bridge._source_channel_map.items()
    }


def refresh_sources(bridge: StreamProjectionBridge, *, refresh_chart: bool = True) -> None:
    previous_catalog_target_ids = {
        int(value) for value in bridge._runtime_source_target_alias.values()
    }
    current_targets = list(bridge._runtime_tracking_result.visible_targets)
    active_target_ids = {int(target.target_id) for target in current_targets}

    catalog_by_target = _window_catalog_by_target(
        bridge._runtime_chart_messages,
    )
    for target in current_targets:
        target_id = int(target.target_id)
        catalog_by_target[target_id] = {
            "targetId": target_id,
            "sourceId": int(target.source_id),
            "lastSample": int(target.sample),
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
    catalog_target_ids = [int(row["targetId"]) for row in catalog_rows]
    catalog_target_id_set = set(catalog_target_ids)

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
    bridge._set_source_positions(positions)
    bridge._source_rows_model.replace(
        build_rows_model_items(
            sidebar_sources,
            bridge._selected_source_ids,
            active_source_ids=active_target_ids,
        )
    )
    if refresh_chart:
        refresh_chart_models(bridge, visible_rows_by_target, visible_target_ids)


def _window_catalog_by_target(
    messages: list[dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    window_model = build_chart_window_model(messages)
    window_start = window_model.get("windowStart")
    window_end = window_model.get("windowEnd")
    if not isinstance(window_start, int) or not isinstance(window_end, int):
        return {}

    catalog: dict[int, dict[str, Any]] = {}
    for frame in messages:
        sample_raw = frame.get("timeStamp")
        if type(sample_raw) is not int:
            continue
        sample = int(sample_raw)
        if sample < window_start or sample > window_end:
            continue
        frame_sources = frame.get("src")
        if not isinstance(frame_sources, list):
            continue
        for source in frame_sources:
            if not isinstance(source, dict):
                continue
            target_id = source.get("targetId")
            source_id = source.get("id")
            if not isinstance(target_id, int) or not isinstance(source_id, int):
                continue
            previous = catalog.get(target_id)
            if previous is None or int(previous["lastSample"]) <= sample:
                catalog[target_id] = {
                    "targetId": target_id,
                    "sourceId": source_id,
                    "lastSample": sample,
                }
    return catalog


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


def refresh_chart_models(
    bridge: StreamProjectionBridge,
    visible_rows: dict[int, dict[str, Any]],
    visible_source_ids: list[int],
) -> None:
    window_model = build_chart_window_model(bridge._runtime_chart_messages)
    bridge._chart_window_model.replace(window_model["ticks"])
    bridge._elevation_chart_series_model.replace(
        chart_series_model_items(
            bridge,
            bridge._runtime_chart_messages,
            visible_rows,
            visible_source_ids,
            axis="elevation",
        )
    )
    bridge._azimuth_chart_series_model.replace(
        chart_series_model_items(
            bridge,
            bridge._runtime_chart_messages,
            visible_rows,
            visible_source_ids,
            axis="azimuth",
        )
    )


def chart_series_model_items(
    bridge: StreamProjectionBridge,
    messages: list[dict[str, Any]],
    visible_rows: dict[int, dict[str, Any]],
    visible_source_ids: list[int],
    *,
    axis: str,
) -> list[dict[str, Any]]:
    window_model = build_chart_window_model(messages)
    window_start = window_model.get("windowStart")
    window_end = window_model.get("windowEnd")
    if not isinstance(window_start, int) or not isinstance(window_end, int):
        return []

    frame_samples: list[int] = []
    for message in messages:
        sample_raw = message.get("timeStamp")
        if type(sample_raw) is not int:
            continue
        sample_value = int(sample_raw)
        if window_start <= sample_value <= window_end:
            frame_samples.append(sample_value)
    frame_samples.sort()
    if not frame_samples:
        return []

    frame_by_sample = {
        int(message["timeStamp"]): message
        for message in messages
        if type(message.get("timeStamp")) is int
        and window_start <= int(message["timeStamp"]) <= window_end
    }
    items: list[dict[str, Any]] = []
    for target_id in visible_source_ids:
        row = visible_rows.get(int(target_id))
        if row is None:
            continue
        points: list[dict[str, float | int | None]] = []
        for sample in frame_samples:
            frame = frame_by_sample.get(sample, {})
            frame_sources = frame.get("src", [])
            source = _find_target_source(frame_sources, int(target_id))
            points.append(
                {
                    "x": int(sample),
                    "y": None if source is None else _axis_value(source, axis=axis),
                }
            )
        items.append(
            {
                "sourceId": int(row["id"]),
                "color": str(row.get("color", "")),
                "points": points,
            }
        )
    return items


def _find_target_source(
    frame_sources: Any,
    target_id: int,
) -> dict[str, Any] | None:
    if not isinstance(frame_sources, list):
        return None
    for source in frame_sources:
        if not isinstance(source, dict):
            continue
        if int(source.get("targetId", -1)) != int(target_id):
            continue
        return source
    return None


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
    target_by_source = {
        int(target.source_id): int(target.target_id)
        for target in bridge._runtime_tracking_result.visible_targets
    }
    bridge._runtime_chart_frame_sources = {
        int(target.target_id): {
            "sourceId": int(target.source_id),
            "x": float(target.x),
            "y": float(target.y),
            "z": float(target.z),
        }
        for target in bridge._runtime_tracking_result.visible_targets
    }
    frame_sources = [
        {
            "id": int(item["id"]),
            "targetId": target_by_source.get(int(item["id"])),
            "x": float(item["x"]),
            "y": float(item["y"]),
            "z": float(item["z"]),
        }
        for item in normalized_sources
        if target_by_source.get(int(item["id"])) is not None
    ]
    if not has_timestamp:
        return False

    bridge._runtime_chart_messages.append({"timeStamp": sample, "src": frame_sources})
    if len(bridge._runtime_chart_messages) > 1600:
        bridge._runtime_chart_messages = bridge._runtime_chart_messages[-1600:]
    return True


def _next_tracking_sample(bridge: StreamProjectionBridge) -> int:
    if bridge._runtime_tracking_result.visible_targets:
        return (
            max(int(target.sample) for target in bridge._runtime_tracking_result.visible_targets)
            + 1
        )
    valid_samples: list[int] = []
    for message in bridge._runtime_chart_messages:
        sample_raw = message.get("timeStamp")
        if type(sample_raw) is int:
            valid_samples.append(int(sample_raw))
    if valid_samples:
        return max(valid_samples) + 1
    return 0


def reset_runtime_chart_clock(bridge: StreamProjectionBridge) -> None:
    bridge._runtime_chart_messages = []
    bridge._runtime_chart_frame_sources = {}
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
