from __future__ import annotations

from typing import Any, Protocol

from temporal.core.network.odas_message_view import (
    build_source_items,
    count_potentials,
    extract_source_ids,
    extract_source_positions,
)
from temporal.core.source_tracking import SourceObservation, SpaceTargetSession, TrackingResult
from temporal.core.ui_projection import (
    build_chart_series_model,
    build_chart_window_model,
    build_positions_model_items,
    build_rows_model_items,
    compute_sidebar_sources,
    compute_visible_source_ids,
)

from .remote_lifecycle import apply_state_status, update_stream_status


class StreamProjectionBridge(Protocol):
    _AUDIO_CHANNELS: int
    _AUDIO_SAMPLE_WIDTH: int
    _runtime_chart_messages: list[dict[str, Any]]
    _runtime_chart_frame_sources: dict[int, dict[str, float]]
    _runtime_tracking_result: TrackingResult
    _space_target_session: SpaceTargetSession
    _source_color_allocator: Any
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
    def _current_runtime_frame_sources(self) -> dict[int, dict[str, float]]: ...
    def _reset_runtime_chart_clock(self) -> None: ...


__all__ = [
    "StreamProjectionBridge",
    "append_runtime_chart_frame",
    "current_runtime_frame_sources",
    "is_source_selected",
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
    if source_id not in bridge._source_ids:
        return

    changed = False
    if selected and source_id not in bridge._selected_source_ids:
        bridge._selected_source_ids.add(source_id)
        changed = True
    if not selected and source_id in bridge._selected_source_ids:
        bridge._selected_source_ids.remove(source_id)
        changed = True

    if not changed:
        return

    refresh_sources(bridge)
    update_stream_status(bridge, "声源选择已更新")


def is_source_selected(bridge: StreamProjectionBridge, source_id: int) -> bool:
    return source_id in bridge._selected_source_ids


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
    update_source_channel_map(bridge, bridge._source_ids)
    mapped_source_ids = [
        source_id for source_id in bridge._source_ids if source_id in bridge._source_channel_map
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
    source_ids = extract_source_ids(bridge._last_sst)
    if source_ids != bridge._source_ids:
        current = set(source_ids)
        bridge._selected_source_ids = {
            source_id for source_id in bridge._selected_source_ids if source_id in current
        }
        for source_id in source_ids:
            if source_id not in bridge._selected_source_ids:
                bridge._selected_source_ids.add(source_id)
        bridge._source_ids = source_ids
        bridge.sourceIdsChanged.emit()

    items = build_source_items(
        bridge._last_sst,
        enabled=bridge._sources_enabled,
        selected_ids=bridge._selected_source_ids,
    )
    if items != bridge._source_items:
        bridge._source_items = items
        bridge.sourceItemsChanged.emit()
        bridge.sourceCountChanged.emit()

    if bridge._runtime_tracking_result.visible_targets:
        base_sources = [
            {"id": target.source_id, "color": target.color}
            for target in bridge._runtime_tracking_result.visible_targets
        ]
    else:
        base_sources = [
            {"id": source_id, "color": bridge._source_color_allocator.color_for(source_id)}
            for source_id in bridge._source_ids
        ]
    sidebar_sources = compute_sidebar_sources(
        base_sources,
        sources_enabled=bridge._sources_enabled,
        potentials_enabled=False,
        potential_min=0.0,
        potential_max=1.0,
    )
    visible_source_ids = compute_visible_source_ids(sidebar_sources, bridge._selected_source_ids)
    visible_rows = {int(source["id"]): source for source in sidebar_sources}
    current_frame_sources = current_runtime_frame_sources(bridge)

    positions = build_positions_model_items(
        current_frame_sources,
        visible_rows,
        set(visible_source_ids),
    )
    bridge._set_source_positions(positions)
    bridge._source_rows_model.replace(
        build_rows_model_items(sidebar_sources, bridge._selected_source_ids)
    )
    if refresh_chart:
        refresh_chart_models(bridge, visible_rows, visible_source_ids)


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
    items = build_chart_series_model(messages, visible_rows, visible_source_ids, axis=axis)
    return [
        {
            "sourceId": int(item["sourceId"]),
            "color": str(item["color"]),
            "points": list(item.get("points", [])),
        }
        for item in items
    ]


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
    bridge._runtime_chart_frame_sources = {
        int(item["id"]): {
            "x": float(item["x"]),
            "y": float(item["y"]),
            "z": float(item["z"]),
        }
        for item in normalized_sources
    }
    sample_raw = message.get("timeStamp")
    if type(sample_raw) is not int:
        return False

    sample = int(sample_raw)
    bridge._runtime_chart_messages.append({"timeStamp": sample, "src": normalized_sources})
    if len(bridge._runtime_chart_messages) > 1600:
        bridge._runtime_chart_messages = bridge._runtime_chart_messages[-1600:]
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
    return True


def reset_runtime_chart_clock(bridge: StreamProjectionBridge) -> None:
    bridge._runtime_chart_messages = []
    bridge._runtime_chart_frame_sources = {}
    bridge._runtime_tracking_result = TrackingResult(
        visible_targets=[],
        dropped_source_ids=[],
    )
    bridge._space_target_session = SpaceTargetSession()
    bridge._source_color_allocator.reset()
    bridge._chart_window_model.replace(bridge._RUNTIME_CHART_X_TICKS)
    bridge._elevation_chart_series_model.replace([])
    bridge._azimuth_chart_series_model.replace([])


def current_runtime_frame_sources(
    bridge: StreamProjectionBridge,
) -> dict[int, dict[str, float]]:
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
