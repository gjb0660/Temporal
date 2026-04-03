from __future__ import annotations

from typing import Any

from .status_state import set_recording_source_count, set_remote_log_lines


def sync_recording_state_from_sources(bridge: Any, source_ids: list[int]) -> None:
    update_source_channel_map(bridge, source_ids)

    mapped_source_ids = [
        source_id for source_id in source_ids if source_id in bridge._source_channel_map
    ]
    bridge._recorder.update_active_sources(mapped_source_ids)
    bridge._recorder.sweep_inactive()
    set_recording_source_count(bridge, len(bridge._recorder.active_sources()))
    refresh_recording_sessions(bridge)


def route_audio_chunk(bridge: Any, chunk: bytes, mode: str) -> None:
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


def update_source_channel_map(bridge: Any, source_ids: list[int]) -> None:
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
        next_source_map[source_id] = free_channels.pop(0)

    bridge._source_channel_map = next_source_map
    bridge._channel_source_map = {
        channel_index: source_id for source_id, channel_index in bridge._source_channel_map.items()
    }


def refresh_recording_sessions(bridge: Any) -> None:
    snapshot_fn = getattr(bridge._recorder, "sessions_snapshot", None)
    if snapshot_fn is None or not callable(snapshot_fn):
        set_recording_sessions(bridge, [])
        return

    sessions = snapshot_fn()
    if not isinstance(sessions, list):
        set_recording_sessions(bridge, [])
        return

    items = [f"Source {item.source_id} [{item.mode}] {item.filepath.name}" for item in sessions]
    set_recording_sessions(bridge, items)


def set_recording_sessions(bridge: Any, sessions: list[str]) -> None:
    if bridge._recording_sessions == sessions:
        return
    bridge._recording_sessions = sessions
    bridge.recordingSessionsChanged.emit()
    bridge._recording_sessions_model.replace(sessions)


def apply_recording_sample_rates(bridge: Any) -> None:
    sample_rates_fn = getattr(bridge._remote, "recording_sample_rates", None)
    warning_fn = getattr(bridge._remote, "recording_sample_rate_warning", None)
    recorder_update_fn = getattr(bridge._recorder, "set_sample_rates", None)

    sample_rates = {"sp": 16000, "pf": 16000}
    if callable(sample_rates_fn):
        remote_rates = sample_rates_fn()
        if isinstance(remote_rates, dict):
            for mode in ("sp", "pf"):
                value = remote_rates.get(mode)
                if isinstance(value, int) and value > 0:
                    sample_rates[mode] = value
    if callable(recorder_update_fn):
        recorder_update_fn(sample_rates)

    warning = warning_fn() if callable(warning_fn) else None
    if isinstance(warning, str) and warning.strip():
        bridge._recording_sample_rate_warning = warning.strip()
        set_remote_log_lines(bridge, bridge._remote_log_lines)
    else:
        bridge._recording_sample_rate_warning = ""


__all__ = [
    "apply_recording_sample_rates",
    "refresh_recording_sessions",
    "route_audio_chunk",
    "set_recording_sessions",
    "sync_recording_state_from_sources",
    "update_source_channel_map",
]
