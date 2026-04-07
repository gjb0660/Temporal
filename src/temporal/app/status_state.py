from __future__ import annotations

from typing import Any


def set_status(bridge: Any, status: str) -> None:
    if bridge._status == status:
        return
    bridge._status = status
    bridge.statusChanged.emit()


def set_remote_connected(bridge: Any, connected: bool) -> None:
    if bridge._remote_connected == connected:
        return
    bridge._remote_connected = connected
    bridge.remoteConnectedChanged.emit()
    bridge.canToggleStreamsChanged.emit()


def set_odas_starting(bridge: Any, starting: bool) -> None:
    if bridge._odas_starting == starting:
        return
    bridge._odas_starting = starting
    bridge.odasStartingChanged.emit()


def set_odas_running(bridge: Any, running: bool) -> None:
    if bridge._odas_running == running:
        return
    bridge._odas_running = running
    bridge.odasRunningChanged.emit()


def set_streams_active(bridge: Any, active: bool) -> None:
    if bridge._streams_active == active:
        return
    bridge._streams_active = active
    bridge.streamsActiveChanged.emit()
    bridge.canToggleStreamsChanged.emit()


def set_recording_source_count(bridge: Any, value: int) -> None:
    if bridge._recording_source_count == value:
        return
    bridge._recording_source_count = value
    bridge.recordingSourceCountChanged.emit()


def set_remote_log_lines(bridge: Any, lines: list[str]) -> None:
    clean_lines = lines[-120:] if lines else ["远程日志为空，等待 odaslive 输出..."]
    if (
        bridge._recording_sample_rate_warning
        and bridge._recording_sample_rate_warning not in clean_lines
    ):
        clean_lines = [*clean_lines, bridge._recording_sample_rate_warning][-120:]
    if clean_lines == bridge._remote_log_lines:
        return
    bridge._remote_log_lines = clean_lines
    bridge.remoteLogLinesChanged.emit()
    bridge.remoteLogTextChanged.emit()


__all__ = [
    "set_odas_running",
    "set_odas_starting",
    "set_recording_source_count",
    "set_remote_connected",
    "set_remote_log_lines",
    "set_status",
    "set_streams_active",
]
