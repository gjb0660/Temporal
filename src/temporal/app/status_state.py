from __future__ import annotations

from typing import Any

_PHASE_TEXT = {
    "idle": "Temporal 就绪",
    "ssh_disconnected": "远程控制通道已断开",
    "ssh_connected_idle": "SSH 已连接，远程 odaslive 未运行",
    "odas_starting": "远程 odaslive 启动中",
    "odas_running": "SSH 已连接，远程 odaslive 运行中",
    "streams_listening": "正在监听 SST/SSL/SSS 数据流",
    "error": "异常",
}

_DATA_TEXT = {
    "inactive": "未监听",
    "listening_remote_not_running": "监听中，远端未启动",
    "running_waiting_sst": "已启动，等待 SST",
    "receiving_sst": "正在接收 SST",
    "unavailable": "不可用",
}


def _build_control_summary(bridge: Any) -> str:
    phase_text_raw = bridge._control_phase_summary_override or _PHASE_TEXT.get(
        bridge._control_phase, "未知状态"
    )
    data_text_raw = _DATA_TEXT.get(bridge._control_data_state, "未知")
    metrics_line = (
        f"计数: 声源={bridge.sourceCount} 候选={bridge._potential_count} "
        f"录制中={bridge._recording_source_count}"
    )
    return f"{phase_text_raw}\n数据状态: {data_text_raw}\n{metrics_line}"


def refresh_control_summary(bridge: Any) -> None:
    summary = _build_control_summary(bridge)
    if bridge._control_summary == summary:
        return
    bridge._control_summary = summary
    bridge._status = summary
    bridge.controlSummaryChanged.emit()
    bridge.statusChanged.emit()


def set_control_state(
    bridge: Any,
    phase: str,
    data_state: str,
    *,
    summary_override: str | None = None,
) -> None:
    phase_changed = bridge._control_phase != phase
    data_state_changed = bridge._control_data_state != data_state
    override_changed = bridge._control_phase_summary_override != summary_override
    if not phase_changed and not data_state_changed and not override_changed:
        return
    bridge._control_phase = phase
    bridge._control_data_state = data_state
    bridge._control_phase_summary_override = summary_override
    if phase_changed:
        bridge.controlPhaseChanged.emit()
    if data_state_changed:
        bridge.controlDataStateChanged.emit()
    refresh_control_summary(bridge)


def set_status(bridge: Any, status: str) -> None:
    set_control_state(
        bridge,
        bridge._control_phase,
        bridge._control_data_state,
        summary_override=status,
    )


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
    refresh_control_summary(bridge)


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
    "refresh_control_summary",
    "set_control_state",
    "set_odas_running",
    "set_odas_starting",
    "set_recording_source_count",
    "set_remote_connected",
    "set_remote_log_lines",
    "set_status",
    "set_streams_active",
]
