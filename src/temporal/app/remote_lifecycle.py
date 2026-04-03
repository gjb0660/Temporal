from __future__ import annotations

from typing import Any

RemoteLifecycleBridge = Any


__all__ = [
    "RemoteLifecycleBridge",
    "apply_state_status",
    "cancel_odas_startup",
    "connect_remote",
    "humanize_control_channel_error",
    "humanize_startup_failure_reason",
    "latest_remote_log_reason",
    "pick_startup_failure_reason",
    "poll_remote_log",
    "refresh_remote_connection_state",
    "set_startup_failure_status",
    "start_remote_odas",
    "stop_remote_odas",
    "sync_remote_odas_state",
    "toggle_remote_odas",
    "update_stream_status",
    "verify_odas_startup",
]


def update_stream_status(bridge: RemoteLifecycleBridge, prefix: str) -> None:
    bridge.setStatus(
        f"{prefix} | 声源={bridge.sourceCount} 候选={bridge._potential_count} "
        f"录制中={bridge._recording_source_count}"
    )


def apply_state_status(bridge: RemoteLifecycleBridge) -> None:
    if bridge._odas_starting:
        bridge.setStatus("远程 odaslive 启动中")
        return
    if bridge._streams_active:
        update_stream_status(bridge, "正在监听 SST/SSL/SSS 数据流")
        return
    if bridge._odas_running:
        bridge.setStatus("SSH 已连接，远程 odaslive 运行中")
        return
    if bridge._remote_connected:
        bridge.setStatus("SSH 已连接，远程 odaslive 未运行")
        return
    bridge.setStatus("Temporal 就绪")


def refresh_remote_connection_state(bridge: RemoteLifecycleBridge) -> bool:
    connected = bridge._remote.is_connected()
    bridge._set_remote_connected(connected)
    return connected


def connect_remote(bridge: RemoteLifecycleBridge) -> None:
    try:
        bridge._remote.connect()
    except Exception as exc:
        cancel_odas_startup(bridge)
        bridge._set_remote_connected(False)
        bridge._set_odas_running(False)
        reason = humanize_control_channel_error(str(exc))
        bridge.setStatus(reason)
        bridge._set_remote_log_lines([reason])
        return

    refresh_remote_connection_state(bridge)
    if not bridge._log_timer.isActive():
        bridge._log_timer.start()
    poll_remote_log(bridge)
    sync_remote_odas_state(bridge)
    apply_state_status(bridge)


def start_remote_odas(bridge: RemoteLifecycleBridge) -> None:
    if not refresh_remote_connection_state(bridge):
        bridge.setStatus("请先连接远程 SSH")
        return
    if bridge._odas_starting:
        bridge.setStatus("远程 odaslive 启动中")
        return

    if not bridge._remote_connected:
        connect_remote(bridge)
        if not bridge._remote_connected:
            return

    if not bridge._streams_active:
        bridge.startStreams()
        if not bridge._streams_active:
            return

    try:
        result = bridge._remote.start_odaslive()
    except Exception as exc:
        cancel_odas_startup(bridge)
        bridge._set_odas_running(False)
        bridge.setStatus(f"启动失败: {humanize_control_channel_error(str(exc))}")
        return

    poll_remote_log(bridge)
    if result.code != 0:
        cancel_odas_startup(bridge)
        bridge._set_odas_running(False)
        set_startup_failure_status(bridge, pick_startup_failure_reason(bridge, result))
        return

    bridge._apply_recording_sample_rates()
    bridge._startup_failure_hint = result.stderr.strip() or result.stdout.strip()
    bridge._startup_attempts_remaining = bridge._STARTUP_VERIFY_ATTEMPTS
    bridge._set_odas_running(False)
    bridge._set_odas_starting(True)
    bridge.setStatus("远程 odaslive 启动中")
    verify_odas_startup(bridge)


def stop_remote_odas(bridge: RemoteLifecycleBridge) -> None:
    if not refresh_remote_connection_state(bridge):
        bridge.setStatus("SSH 未连接")
        return

    try:
        result = bridge._remote.stop_odaslive()
    except Exception as exc:
        bridge.setStatus(f"停止失败: {humanize_control_channel_error(str(exc))}")
        return

    cancel_odas_startup(bridge)
    if result.code == 0:
        running = sync_remote_odas_state(bridge, update_status=False)
        if running is None:
            bridge.setStatus("停止失败: 远程控制通道已断开")
        elif running:
            bridge.setStatus("远程 odaslive 停止失败")
        else:
            apply_state_status(bridge)
    else:
        sync_remote_odas_state(bridge)
        bridge.setStatus(result.stderr.strip() or "远程 odaslive 停止失败")
    if bridge._remote_connected:
        poll_remote_log(bridge)


def toggle_remote_odas(bridge: RemoteLifecycleBridge) -> None:
    if bridge._odas_starting:
        bridge.setStatus("远程 odaslive 启动中")
        return
    if bridge._odas_running:
        if not refresh_remote_connection_state(bridge):
            connect_remote(bridge)
            if not refresh_remote_connection_state(bridge):
                return
        stop_remote_odas(bridge)
        return
    if not bridge._remote_connected:
        connect_remote(bridge)
        if not bridge._remote_connected:
            return
    start_remote_odas(bridge)


def sync_remote_odas_state(
    bridge: RemoteLifecycleBridge, update_status: bool = False
) -> bool | None:
    previous_running = bridge._odas_running
    if not refresh_remote_connection_state(bridge):
        bridge._set_odas_starting(False)
        if update_status:
            bridge.setStatus("远程控制通道已断开")
        return None

    try:
        result = bridge._remote.status()
    except Exception as exc:
        bridge._set_odas_starting(False)
        refresh_remote_connection_state(bridge)
        if update_status:
            bridge.setStatus(humanize_control_channel_error(str(exc)))
        return None

    running = bool(result.stdout.strip())
    bridge._set_odas_starting(False)
    bridge._set_odas_running(running)
    if not update_status or previous_running == running:
        return running
    apply_state_status(bridge)
    return running


def cancel_odas_startup(bridge: RemoteLifecycleBridge) -> None:
    if bridge._startup_timer.isActive():
        bridge._startup_timer.stop()
    bridge._startup_attempts_remaining = 0
    bridge._startup_failure_hint = ""
    bridge._set_odas_starting(False)


def latest_remote_log_reason(bridge: RemoteLifecycleBridge) -> str:
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


def pick_startup_failure_reason(bridge: RemoteLifecycleBridge, result: object | None = None) -> str:
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


def humanize_startup_failure_reason(reason: str) -> str:
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
            return humanize_startup_failure_reason(remainder)
    return normalized


def humanize_control_channel_error(reason: str) -> str:
    normalized = reason.strip()
    lower = normalized.lower()
    if "ssh control shell timed out" in lower:
        return "远程控制通道初始化失败"
    if "ssh control shell lost" in lower or "protocol desynced" in lower:
        return "远程控制通道已断开"
    if "ssh is not connected" in lower:
        return "远程 SSH 连接已断开"
    return normalized


def set_startup_failure_status(bridge: RemoteLifecycleBridge, reason: str) -> None:
    humanized = humanize_startup_failure_reason(reason)
    if humanized.startswith("启动失败"):
        bridge.setStatus(humanized)
        return
    bridge.setStatus(f"启动失败: {humanized}")


def verify_odas_startup(bridge: RemoteLifecycleBridge) -> None:
    if not bridge._odas_starting:
        return

    try:
        result = bridge._remote.status()
    except Exception as exc:
        cancel_odas_startup(bridge)
        refresh_remote_connection_state(bridge)
        bridge._set_odas_running(False)
        bridge.setStatus(f"启动失败: {humanize_control_channel_error(str(exc))}")
        return

    if result.stdout.strip():
        cancel_odas_startup(bridge)
        bridge._set_odas_running(True)
        apply_state_status(bridge)
        return

    bridge._startup_attempts_remaining -= 1
    poll_remote_log(bridge)
    if bridge._startup_attempts_remaining <= 0:
        reason = pick_startup_failure_reason(bridge)
        cancel_odas_startup(bridge)
        bridge._set_odas_running(False)
        set_startup_failure_status(bridge, reason)
        return

    if not bridge._startup_timer.isActive():
        bridge._startup_timer.start()


def poll_remote_log(bridge: RemoteLifecycleBridge) -> None:
    try:
        result = bridge._remote.read_log_tail(80)
    except Exception as exc:
        message = str(exc)
        if "SSH is not connected" in message or "SSH control shell" in message:
            cancel_odas_startup(bridge)
            refresh_remote_connection_state(bridge)
            if bridge._log_timer.isActive():
                bridge._log_timer.stop()
            reason = humanize_control_channel_error(message)
            bridge._set_remote_log_lines([reason])
            bridge.setStatus(reason)
            return
        bridge._set_remote_log_lines([f"日志读取失败: {message}"])
        if bridge._remote_connected and not bridge._odas_starting:
            sync_remote_odas_state(bridge, update_status=True)
        return

    if result.code != 0 and result.stderr.strip():
        bridge._set_remote_log_lines([f"日志读取失败: {result.stderr.strip()}"])
    else:
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        if not lines:
            bridge._set_remote_log_lines(["远程日志为空，等待 odaslive 输出..."])
        else:
            bridge._set_remote_log_lines(lines)

    if bridge._remote_connected and not bridge._odas_starting:
        sync_remote_odas_state(bridge, update_status=True)
