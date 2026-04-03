from __future__ import annotations

from typing import Any


def set_status(bridge: Any, status: str) -> None:
    if bridge._status == status:
        return
    bridge._status = status
    bridge.statusChanged.emit()


def update_stream_status(bridge: Any, prefix: str) -> None:
    set_status(
        bridge,
        f"{prefix} | 声源={bridge.sourceCount} 候选={bridge._potential_count} "
        f"录制中={bridge._recording_source_count}",
    )


def apply_state_status(bridge: Any) -> None:
    if bridge._odas_starting:
        set_status(bridge, "远程 odaslive 启动中")
        return
    if bridge._streams_active:
        update_stream_status(bridge, "正在监听 SST/SSL/SSS 数据流")
        return
    if bridge._odas_running:
        set_status(bridge, "SSH 已连接，远程 odaslive 运行中")
        return
    if bridge._remote_connected:
        set_status(bridge, "SSH 已连接，远程 odaslive 未运行")
        return
    set_status(bridge, "Temporal 就绪")


def refresh_remote_connection_state(bridge: Any) -> bool:
    connected = bridge._remote.is_connected()
    set_remote_connected(bridge, connected)
    return connected


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


def sync_remote_odas_state(bridge: Any, update_status: bool = False) -> bool | None:
    previous_running = bridge._odas_running
    if not refresh_remote_connection_state(bridge):
        set_odas_starting(bridge, False)
        if update_status:
            set_status(bridge, "远程控制通道已断开")
        return None

    try:
        result = bridge._remote.status()
    except Exception as exc:
        set_odas_starting(bridge, False)
        refresh_remote_connection_state(bridge)
        if update_status:
            set_status(bridge, humanize_control_channel_error(bridge, str(exc)))
        return None

    running = bool(result.stdout.strip())
    set_odas_starting(bridge, False)
    set_odas_running(bridge, running)
    if not update_status or previous_running == running:
        return running
    apply_state_status(bridge)
    return running


def cancel_odas_startup(bridge: Any) -> None:
    if bridge._startup_timer.isActive():
        bridge._startup_timer.stop()
    bridge._startup_attempts_remaining = 0
    bridge._startup_failure_hint = ""
    set_odas_starting(bridge, False)


def latest_remote_log_reason(bridge: Any) -> str:
    for line in reversed(bridge._remote_log_lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("等待连接远程 odaslive"):
            continue
        if stripped.startswith("远程日志为空"):
            continue
        return stripped
    return ""


def pick_startup_failure_reason(bridge: Any, result: object | None = None) -> str:
    if result is not None:
        stderr = getattr(result, "stderr", "")
        stdout = getattr(result, "stdout", "")
        explicit = stderr.strip() or stdout.strip()
        if explicit.lower().startswith("preflight:"):
            return explicit
    log_reason = latest_remote_log_reason(bridge)
    if log_reason:
        return log_reason
    if result is not None:
        stderr = getattr(result, "stderr", "")
        stdout = getattr(result, "stdout", "")
        message = stderr.strip() or stdout.strip()
        if message:
            return message
    if bridge._startup_failure_hint:
        return bridge._startup_failure_hint
    return "远程 odaslive 启动失败"


def humanize_startup_failure_reason(bridge: Any, reason: str) -> str:
    normalized = reason.strip()
    lower = normalized.lower()

    if normalized.startswith("日志读取失败"):
        if "cd:" in lower and "no such file or directory" in lower:
            return "远程工作目录不存在或不可访问"
        if "permission denied" in lower:
            return "远程日志路径不可读或不可写"
        return "远程日志读取失败"
    if "preflight: remote working directory" in lower:
        return "远程工作目录不存在或不可访问"
    if "preflight: remote command missing" in lower:
        return "远程命令不存在或未安装"
    if "preflight: remote command not executable" in lower:
        return "远程命令或目录权限不足"
    if "preflight: odas config path missing" in lower:
        return "远程 ODAS 配置文件未声明或无法解析"
    if "preflight: odas config file missing" in lower:
        return "远程 ODAS 配置文件不存在"
    if "preflight: sink host mismatch" in lower:
        return "远程 ODAS 配置中的输出地址与 Temporal 监听地址不一致"
    if "preflight: tracked sink missing" in lower:
        return "远程 ODAS 配置缺少 tracked 输出定义"
    if "preflight: potential sink missing" in lower:
        return "远程 ODAS 配置缺少 potential 输出定义"
    if "preflight: separated sink missing" in lower:
        return "远程 ODAS 配置缺少 separated 输出定义"
    if "preflight: postfiltered sink missing" in lower:
        return "远程 ODAS 配置缺少 postfiltered 输出定义"
    if "preflight: tracked sink port mismatch" in lower:
        return "远程 ODAS 配置中的 tracked 输出端口与 Temporal 不一致"
    if "preflight: potential sink port mismatch" in lower:
        return "远程 ODAS 配置中的 potential 输出端口与 Temporal 不一致"
    if "preflight: separated sink port mismatch" in lower:
        return "远程 ODAS 配置中的 separated 输出端口与 Temporal 不一致"
    if "preflight: postfiltered sink port mismatch" in lower:
        return "远程 ODAS 配置中的 postfiltered 输出端口与 Temporal 不一致"
    if "command not found" in lower:
        return "远程命令不存在或未安装"
    if "permission denied" in lower:
        return "远程命令或目录权限不足"
    if "no such file or directory" in lower:
        return "远程文件或目录不存在"
    if "not connected" in lower:
        return "远程 SSH 连接已断开"
    if "timed out" in lower:
        return "远程连接超时"
    if normalized.startswith("启动失败:"):
        remainder = normalized.split(":", 1)[1].strip()
        if remainder:
            return humanize_startup_failure_reason(bridge, remainder)
    return normalized


def humanize_control_channel_error(bridge: Any, reason: str) -> str:
    normalized = reason.strip()
    lower = normalized.lower()
    if "ssh control shell timed out" in lower:
        return "远程控制通道初始化失败"
    if "ssh control shell lost" in lower or "protocol desynced" in lower:
        return "远程控制通道已断开"
    if "ssh is not connected" in lower:
        return "远程 SSH 连接已断开"
    return normalized


def set_startup_failure_status(bridge: Any, reason: str) -> None:
    humanized = humanize_startup_failure_reason(bridge, reason)
    if humanized.startswith("启动失败"):
        set_status(bridge, humanized)
        return
    set_status(bridge, f"启动失败: {humanized}")


def verify_odas_startup(bridge: Any) -> None:
    if not bridge._odas_starting:
        return

    try:
        result = bridge._remote.status()
    except Exception as exc:
        cancel_odas_startup(bridge)
        refresh_remote_connection_state(bridge)
        set_odas_running(bridge, False)
        set_status(bridge, f"启动失败: {humanize_control_channel_error(bridge, str(exc))}")
        return

    if result.stdout.strip():
        cancel_odas_startup(bridge)
        set_odas_running(bridge, True)
        apply_state_status(bridge)
        return

    bridge._startup_attempts_remaining -= 1
    poll_remote_log(bridge)
    if bridge._startup_attempts_remaining <= 0:
        reason = pick_startup_failure_reason(bridge)
        cancel_odas_startup(bridge)
        set_odas_running(bridge, False)
        set_startup_failure_status(bridge, reason)
        return

    if not bridge._startup_timer.isActive():
        bridge._startup_timer.start()


def poll_remote_log(bridge: Any) -> None:
    try:
        result = bridge._remote.read_log_tail(80)
    except Exception as exc:
        message = str(exc)
        if "SSH is not connected" in message or "SSH control shell" in message:
            cancel_odas_startup(bridge)
            refresh_remote_connection_state(bridge)
            if bridge._log_timer.isActive():
                bridge._log_timer.stop()
            reason = humanize_control_channel_error(bridge, message)
            set_remote_log_lines(bridge, [reason])
            set_status(bridge, reason)
            return
        set_remote_log_lines(bridge, [f"日志读取失败: {message}"])
        if bridge._remote_connected and not bridge._odas_starting:
            sync_remote_odas_state(bridge, update_status=True)
        return

    if result.code != 0 and result.stderr.strip():
        set_remote_log_lines(bridge, [f"日志读取失败: {result.stderr.strip()}"])
    else:
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        if not lines:
            set_remote_log_lines(bridge, ["远程日志为空，等待 odaslive 输出..."])
        else:
            set_remote_log_lines(bridge, lines)

    if bridge._remote_connected and not bridge._odas_starting:
        sync_remote_odas_state(bridge, update_status=True)


__all__ = [
    "apply_state_status",
    "cancel_odas_startup",
    "humanize_control_channel_error",
    "humanize_startup_failure_reason",
    "latest_remote_log_reason",
    "pick_startup_failure_reason",
    "poll_remote_log",
    "refresh_remote_connection_state",
    "set_odas_running",
    "set_odas_starting",
    "set_recording_source_count",
    "set_remote_connected",
    "set_remote_log_lines",
    "set_status",
    "set_streams_active",
    "set_startup_failure_status",
    "sync_remote_odas_state",
    "update_stream_status",
    "verify_odas_startup",
]
