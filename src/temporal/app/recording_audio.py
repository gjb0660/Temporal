from __future__ import annotations

from typing import Any

from .status_state import set_recording_source_count, set_remote_log_lines

_RECENT_CLOSED_LIMIT = 2


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

    active_by_key: dict[tuple[int, str, str], tuple[int, dict[str, Any]]] = {}
    source_target_alias = {
        int(row.get("sourceId", 0)): int(target_id)
        for target_id, row in bridge._runtime_catalog_by_target.items()
    }
    valid_target_ids = {int(target_id) for target_id in bridge._runtime_catalog_by_target}
    for item in sessions:
        key = _session_key(item)
        source_id = int(item.source_id)
        target_id = bridge._recording_session_target_by_key.get(
            key,
            source_target_alias.get(source_id),
        )
        if target_id is None:
            continue
        active_by_key[key] = (int(target_id), _session_detail(item))

    previous_active = dict(bridge._recording_active_sessions_by_key)
    for key in set(previous_active) - set(active_by_key):
        target_id, detail = previous_active[key]
        if int(target_id) not in valid_target_ids:
            continue
        recent = list(bridge._recording_recent_closed_by_target.get(int(target_id), []))
        recent.insert(0, detail)
        bridge._recording_recent_closed_by_target[int(target_id)] = recent[:_RECENT_CLOSED_LIMIT]

    bridge._recording_active_sessions_by_key = active_by_key
    bridge._recording_session_target_by_key = {
        key: int(target_id) for key, (target_id, _detail) in active_by_key.items()
    }
    prune_recording_target_caches(bridge, valid_target_ids)

    grouped_active: dict[int, list[dict[str, Any]]] = {}
    for target_id, detail in active_by_key.values():
        grouped_active.setdefault(int(target_id), []).append(detail)

    items: list[dict[str, Any]] = []
    for target_id in sorted(valid_target_ids):
        active_details = sorted(
            grouped_active.get(target_id, []),
            key=lambda item: (int(item["sourceId"]), str(item["filename"])),
        )
        recent_details = list(bridge._recording_recent_closed_by_target.get(target_id, []))
        if not active_details and not recent_details:
            continue
        details = [*active_details, *recent_details]
        summary_source_id = int(details[0]["sourceId"])
        details_text = "\n".join(str(item["line"]) for item in details)
        items.append(
            {
                "targetId": int(target_id),
                "summary": (
                    f"Target {int(target_id)} | "
                    f"Source {summary_source_id} | "
                    f"files: {len(active_details)}"
                ),
                "details": details_text,
                "hasActive": bool(active_details),
            }
        )
    set_recording_sessions(bridge, items)


def set_recording_sessions(bridge: Any, sessions: list[dict[str, Any]]) -> None:
    if bridge._recording_sessions == sessions:
        return
    bridge._recording_sessions = sessions
    bridge.recordingSessionsChanged.emit()
    bridge._recording_sessions_model.replace(sessions)


def prune_recording_target_caches(bridge: Any, valid_target_ids: set[int]) -> None:
    valid_ids = {int(target_id) for target_id in valid_target_ids}
    bridge._recording_recent_closed_by_target = {
        int(target_id): list(items)[:_RECENT_CLOSED_LIMIT]
        for target_id, items in bridge._recording_recent_closed_by_target.items()
        if int(target_id) in valid_ids
    }
    bridge._recording_active_sessions_by_key = {
        key: (int(target_id), dict(detail))
        for key, (target_id, detail) in bridge._recording_active_sessions_by_key.items()
        if int(target_id) in valid_ids
    }
    bridge._recording_session_target_by_key = {
        key: int(target_id)
        for key, target_id in bridge._recording_session_target_by_key.items()
        if int(target_id) in valid_ids
    }


def reset_recording_runtime_state(bridge: Any) -> None:
    bridge._recording_recent_closed_by_target = {}
    bridge._recording_active_sessions_by_key = {}
    bridge._recording_session_target_by_key = {}


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


def _session_key(item: Any) -> tuple[int, str, str]:
    return (
        int(item.source_id),
        str(item.mode),
        str(item.filepath.name),
    )


def _session_detail(item: Any) -> dict[str, Any]:
    source_id = int(item.source_id)
    filename = str(item.filepath.name)
    return {
        "sourceId": source_id,
        "filename": filename,
        "line": filename,
    }


__all__ = [
    "apply_recording_sample_rates",
    "prune_recording_target_caches",
    "reset_recording_runtime_state",
    "refresh_recording_sessions",
    "route_audio_chunk",
    "set_recording_sessions",
    "sync_recording_state_from_sources",
    "update_source_channel_map",
]
