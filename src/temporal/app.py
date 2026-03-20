from __future__ import annotations

# pyright: reportMissingImports=false, reportUntypedFunctionDecorator=false

import sys
from pathlib import Path

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from temporal.core.config_loader import load_config
from temporal.core.network.odas_client import OdasClient
from temporal.core.network.odas_message_view import (
    build_source_items,
    count_potentials,
    extract_source_ids,
    extract_source_positions,
)
from temporal.core.recording.auto_recorder import AutoRecorder
from temporal.core.ssh.remote_odas import RemoteOdasController


class AppBridge(QObject):
    _AUDIO_CHANNELS = 4
    _AUDIO_SAMPLE_WIDTH = 2
    _STARTUP_VERIFY_INTERVAL_MS = 200
    _STARTUP_VERIFY_ATTEMPTS = 11

    statusChanged = Signal()
    remoteConnectedChanged = Signal()
    odasStartingChanged = Signal()
    odasRunningChanged = Signal()
    streamsActiveChanged = Signal()
    sourceItemsChanged = Signal()
    sourceIdsChanged = Signal()
    sourceCountChanged = Signal()
    sourcePositionsChanged = Signal()
    remoteLogLinesChanged = Signal()
    potentialCountChanged = Signal()
    recordingSourceCountChanged = Signal()
    recordingSessionsChanged = Signal()
    sourcesEnabledChanged = Signal()
    potentialsEnabledChanged = Signal()
    potentialRangeChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._status = "Temporal 就绪"
        self._root = Path(__file__).resolve().parents[2]
        self._cfg_path = self._root / "config" / "odas.example.toml"
        self._cfg = load_config(self._cfg_path)
        self._remote = RemoteOdasController(self._cfg.remote)
        self._last_sst: dict = {}
        self._last_ssl: dict = {}
        self._source_ids: list[int] = []
        self._selected_source_ids: set[int] = set()
        self._source_channel_map: dict[int, int] = {}
        self._channel_source_map: dict[int, int] = {}
        self._source_items: list[str] = []
        self._source_positions: list[dict[str, float | int]] = []
        self._remote_log_lines = ["等待连接远程 odaslive..."]
        self._potential_count = 0
        self._recording_source_count = 0
        self._recording_sessions: list[str] = []
        self._sources_enabled = True
        self._potentials_enabled = False
        self._potential_min = 0.0
        self._potential_max = 1.0
        self._remote_connected = False
        self._odas_starting = False
        self._odas_running = False
        self._streams_active = False
        self._startup_attempts_remaining = 0
        self._startup_failure_hint = ""
        self._recorder = AutoRecorder(self._root / "recordings")
        self._log_timer = QTimer(self)
        self._log_timer.setInterval(1500)
        self._log_timer.timeout.connect(self._poll_remote_log)
        self._startup_timer = QTimer(self)
        self._startup_timer.setInterval(self._STARTUP_VERIFY_INTERVAL_MS)
        self._startup_timer.timeout.connect(self._verify_odas_startup)
        self._client = OdasClient(
            config=self._cfg.streams,
            on_sst=self._on_sst,
            on_ssl=self._on_ssl,
            on_sep_audio=self._on_sep_audio,
            on_pf_audio=self._on_pf_audio,
        )

    @Property(str, notify=statusChanged)  # type: ignore[reportCallIssue]
    def status(self) -> str:
        return self._status

    @Property(bool, notify=remoteConnectedChanged)  # type: ignore[reportCallIssue]
    def remoteConnected(self) -> bool:
        return self._remote_connected

    @Property(bool, notify=odasStartingChanged)  # type: ignore[reportCallIssue]
    def odasStarting(self) -> bool:
        return self._odas_starting

    @Property(bool, notify=odasRunningChanged)  # type: ignore[reportCallIssue]
    def odasRunning(self) -> bool:
        return self._odas_running

    @Property(bool, notify=streamsActiveChanged)  # type: ignore[reportCallIssue]
    def streamsActive(self) -> bool:
        return self._streams_active

    @Property(list, notify=sourceItemsChanged)  # type: ignore[reportCallIssue]
    def sourceItems(self) -> list[str]:
        return self._source_items

    @Property(list, notify=sourceIdsChanged)  # type: ignore[reportCallIssue]
    def sourceIds(self) -> list[int]:
        return self._source_ids

    @Property(list, notify=sourcePositionsChanged)  # type: ignore[reportCallIssue]
    def sourcePositions(self) -> list[dict[str, float | int]]:
        return self._source_positions

    @Property(list, notify=remoteLogLinesChanged)  # type: ignore[reportCallIssue]
    def remoteLogLines(self) -> list[str]:
        return self._remote_log_lines

    @Property(int, notify=sourceCountChanged)  # type: ignore[reportCallIssue]
    def sourceCount(self) -> int:
        return len(self._source_items)

    @Property(int, notify=potentialCountChanged)  # type: ignore[reportCallIssue]
    def potentialCount(self) -> int:
        return self._potential_count

    @Property(int, notify=recordingSourceCountChanged)  # type: ignore[reportCallIssue]
    def recordingSourceCount(self) -> int:
        return self._recording_source_count

    @Property(list, notify=recordingSessionsChanged)  # type: ignore[reportCallIssue]
    def recordingSessions(self) -> list[str]:
        return self._recording_sessions

    @Property(bool, notify=sourcesEnabledChanged)  # type: ignore[reportCallIssue]
    def sourcesEnabled(self) -> bool:
        return self._sources_enabled

    @Property(bool, notify=potentialsEnabledChanged)  # type: ignore[reportCallIssue]
    def potentialsEnabled(self) -> bool:
        return self._potentials_enabled

    @Property(float, notify=potentialRangeChanged)  # type: ignore[reportCallIssue]
    def potentialEnergyMin(self) -> float:
        return self._potential_min

    @Property(float, notify=potentialRangeChanged)  # type: ignore[reportCallIssue]
    def potentialEnergyMax(self) -> float:
        return self._potential_max

    @Slot(str)
    def setStatus(self, status: str) -> None:
        if self._status == status:
            return
        self._status = status
        self.statusChanged.emit()

    @Slot()
    def connectRemote(self) -> None:
        try:
            self._remote.connect()
        except Exception as exc:
            self._cancel_odas_startup()
            self._set_remote_connected(False)
            self._set_odas_running(False)
            self.setStatus(f"SSH 连接失败: {exc}")
            self._set_remote_log_lines([f"远程连接失败: {exc}"])
            return

        self._set_remote_connected(True)
        if not self._log_timer.isActive():
            self._log_timer.start()
        self._poll_remote_log()
        self._sync_remote_odas_state()
        if self._odas_running:
            self.setStatus("SSH 已连接，远程 odaslive 运行中")
        else:
            self.setStatus("SSH 已连接")

    @Slot()
    def startRemoteOdas(self) -> None:
        if not self._remote_connected:
            self.setStatus("请先连接远程 SSH")
            return

        if self._odas_starting:
            self.setStatus("远程 odaslive 启动中")
            return

        try:
            result = self._remote.start_odaslive()
        except Exception as exc:
            self._cancel_odas_startup()
            self._set_odas_running(False)
            self.setStatus(f"启动失败: {exc}")
            return

        self._poll_remote_log()
        if result.code != 0:
            self._cancel_odas_startup()
            self._set_odas_running(False)
            self._set_startup_failure_status(self._pick_startup_failure_reason(result))
            return

        self._startup_failure_hint = result.stderr.strip() or result.stdout.strip()
        self._startup_attempts_remaining = self._STARTUP_VERIFY_ATTEMPTS
        self._set_odas_running(False)
        self._set_odas_starting(True)
        self.setStatus("远程 odaslive 启动中")
        self._verify_odas_startup()

    @Slot()
    def stopRemoteOdas(self) -> None:
        if not self._remote_connected:
            self.setStatus("SSH 未连接")
            return

        try:
            result = self._remote.stop_odaslive()
        except Exception as exc:
            self.setStatus(f"停止失败: {exc}")
            return

        self._cancel_odas_startup()
        if result.code == 0:
            self._set_odas_running(False)
            self.setStatus("远程 odaslive 已停止")
        else:
            self._sync_remote_odas_state()
            self.setStatus(result.stderr.strip() or "远程 odaslive 停止失败")
        self._poll_remote_log()

    @Slot()
    def toggleRemoteOdas(self) -> None:
        if self._odas_starting:
            self.setStatus("远程 odaslive 启动中")
            return
        if self._odas_running:
            if self._streams_active:
                self.stopStreams()
            self.stopRemoteOdas()
            return

        if not self._remote_connected:
            self.connectRemote()
            if not self._remote_connected:
                return
        self.startRemoteOdas()

    @Slot()
    def startStreams(self) -> None:
        if not self._odas_running:
            self.setStatus("请先启动远程 odaslive")
            return
        if self._streams_active:
            self._update_stream_status("正在监听 SST/SSL/SSS 数据流")
            return

        self._client.start()
        self._set_streams_active(True)
        self._update_stream_status("开始监听 SST/SSL/SSS 数据流")

    @Slot()
    def stopStreams(self) -> None:
        self._client.stop()
        self._recorder.stop_all()
        self._source_channel_map.clear()
        self._channel_source_map.clear()
        self._set_streams_active(False)
        self._set_recording_source_count(0)
        self._set_recording_sessions([])
        self.setStatus("数据流已关闭")

    @Slot()
    def toggleStreams(self) -> None:
        if self._streams_active:
            self.stopStreams()
            return
        self.startStreams()

    @Slot(bool)
    def setSourcesEnabled(self, enabled: bool) -> None:
        if self._sources_enabled == enabled:
            return
        self._sources_enabled = enabled
        self.sourcesEnabledChanged.emit()
        self._refresh_sources()
        self._update_stream_status("声源筛选已更新")

    @Slot(int, bool)
    def setSourceSelected(self, source_id: int, selected: bool) -> None:
        if source_id not in self._source_ids:
            return

        has_changed = False
        if selected and source_id not in self._selected_source_ids:
            self._selected_source_ids.add(source_id)
            has_changed = True
        if not selected and source_id in self._selected_source_ids:
            self._selected_source_ids.remove(source_id)
            has_changed = True

        if not has_changed:
            return

        self._refresh_sources()
        self._update_stream_status("声源选择已更新")

    @Slot(int, result=bool)
    def isSourceSelected(self, source_id: int) -> bool:
        return source_id in self._selected_source_ids

    @Slot(bool)
    def setPotentialsEnabled(self, enabled: bool) -> None:
        if self._potentials_enabled == enabled:
            return
        self._potentials_enabled = enabled
        self.potentialsEnabledChanged.emit()
        self._refresh_potentials()
        self._update_stream_status("候选筛选已更新")

    @Slot(float, float)
    def setPotentialEnergyRange(self, minimum: float, maximum: float) -> None:
        low = min(minimum, maximum)
        high = max(minimum, maximum)
        if self._potential_min == low and self._potential_max == high:
            return
        self._potential_min = low
        self._potential_max = high
        self.potentialRangeChanged.emit()
        self._refresh_potentials()
        self._update_stream_status("候选能量范围已更新")

    def _on_sst(self, message: dict) -> None:
        self._last_sst = message
        self._refresh_sources()
        self._update_source_channel_map(self._source_ids)
        mapped_source_ids = [
            source_id for source_id in self._source_ids if source_id in self._source_channel_map
        ]
        self._recorder.update_active_sources(mapped_source_ids)
        self._recorder.sweep_inactive()
        self._set_recording_source_count(len(self._recorder.active_sources()))
        self._refresh_recording_sessions()
        self._update_stream_status("SST 数据已更新")

    def _on_ssl(self, message: dict) -> None:
        self._last_ssl = message
        self._refresh_potentials()
        self._update_stream_status("SSL 数据已更新")

    def _on_sep_audio(self, chunk: bytes) -> None:
        self._route_audio_chunk(chunk, mode="sp")

    def _on_pf_audio(self, chunk: bytes) -> None:
        self._route_audio_chunk(chunk, mode="pf")

    def _route_audio_chunk(self, chunk: bytes, mode: str) -> None:
        if not self._channel_source_map:
            return

        frame_width = self._AUDIO_CHANNELS * self._AUDIO_SAMPLE_WIDTH
        usable = len(chunk) - (len(chunk) % frame_width)
        if usable <= 0:
            return

        buffers = {
            channel_index: bytearray()
            for channel_index in self._channel_source_map
            if 0 <= channel_index < self._AUDIO_CHANNELS
        }
        if not buffers:
            return

        for offset in range(0, usable, frame_width):
            frame = chunk[offset : offset + frame_width]
            for channel_index in buffers:
                sample_offset = channel_index * self._AUDIO_SAMPLE_WIDTH
                sample = frame[sample_offset : sample_offset + self._AUDIO_SAMPLE_WIDTH]
                buffers[channel_index].extend(sample)

        for channel_index, channel_pcm in buffers.items():
            source_id = self._channel_source_map.get(channel_index)
            if source_id is None or not channel_pcm:
                continue
            self._recorder.push(source_id, mode, bytes(channel_pcm))

    def _update_source_channel_map(self, source_ids: list[int]) -> None:
        next_source_map: dict[int, int] = {}
        used_channels: set[int] = set()

        for source_id in source_ids:
            channel_index = self._source_channel_map.get(source_id)
            if channel_index is None or channel_index in used_channels:
                continue
            if not 0 <= channel_index < self._AUDIO_CHANNELS:
                continue
            next_source_map[source_id] = channel_index
            used_channels.add(channel_index)

        free_channels = [
            channel_index
            for channel_index in range(self._AUDIO_CHANNELS)
            if channel_index not in used_channels
        ]
        for source_id in source_ids:
            if source_id in next_source_map:
                continue
            if not free_channels:
                break
            channel_index = free_channels.pop(0)
            next_source_map[source_id] = channel_index

        self._source_channel_map = next_source_map
        self._channel_source_map = {
            channel_index: source_id
            for source_id, channel_index in self._source_channel_map.items()
        }

    def _update_stream_status(self, prefix: str) -> None:
        self.setStatus(
            f"{prefix} | 声源={self.sourceCount} 候选={self._potential_count} "
            f"录制中={self._recording_source_count}"
        )

    def _set_remote_connected(self, connected: bool) -> None:
        if self._remote_connected == connected:
            return
        self._remote_connected = connected
        self.remoteConnectedChanged.emit()

    def _set_odas_running(self, running: bool) -> None:
        if self._odas_running == running:
            return
        self._odas_running = running
        self.odasRunningChanged.emit()

    def _set_odas_starting(self, starting: bool) -> None:
        if self._odas_starting == starting:
            return
        self._odas_starting = starting
        self.odasStartingChanged.emit()

    def _set_streams_active(self, active: bool) -> None:
        if self._streams_active == active:
            return
        self._streams_active = active
        self.streamsActiveChanged.emit()

    def _set_recording_source_count(self, value: int) -> None:
        if self._recording_source_count == value:
            return
        self._recording_source_count = value
        self.recordingSourceCountChanged.emit()

    def _set_remote_log_lines(self, lines: list[str]) -> None:
        clean_lines = lines[-120:] if lines else ["远程日志为空，等待 odaslive 输出..."]
        if clean_lines == self._remote_log_lines:
            return
        self._remote_log_lines = clean_lines
        self.remoteLogLinesChanged.emit()

    def _sync_remote_odas_state(self, update_status: bool = False) -> None:
        previous_running = self._odas_running
        if not self._remote_connected:
            self._set_odas_starting(False)
            self._set_odas_running(False)
            return

        try:
            result = self._remote.status()
        except Exception:
            self._set_odas_starting(False)
            self._set_odas_running(False)
            return

        running = bool(result.stdout.strip())
        self._set_odas_starting(False)
        self._set_odas_running(running)
        if not update_status or previous_running == running:
            return
        if running:
            self.setStatus("SSH 已连接，远程 odaslive 运行中")
            return
        self.setStatus("SSH 已连接，远程 odaslive 未运行")

    def _cancel_odas_startup(self) -> None:
        if self._startup_timer.isActive():
            self._startup_timer.stop()
        self._startup_attempts_remaining = 0
        self._startup_failure_hint = ""
        self._set_odas_starting(False)

    def _latest_remote_log_reason(self) -> str:
        for line in reversed(self._remote_log_lines):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("等待连接远程 odaslive"):
                continue
            if stripped.startswith("远程日志为空"):
                continue
            return stripped
        return ""

    def _pick_startup_failure_reason(self, result: object | None = None) -> str:
        log_reason = self._latest_remote_log_reason()
        if log_reason:
            return log_reason
        if result is not None:
            stderr = getattr(result, "stderr", "")
            stdout = getattr(result, "stdout", "")
            message = stderr.strip() or stdout.strip()
            if message:
                return message
        if self._startup_failure_hint:
            return self._startup_failure_hint
        return "远程 odaslive 启动失败"

    def _humanize_startup_failure_reason(self, reason: str) -> str:
        normalized = reason.strip()
        lower = normalized.lower()

        if normalized.startswith("日志读取失败"):
            if "cd:" in lower and "no such file or directory" in lower:
                return "远程工作目录不存在或不可访问"
            if "permission denied" in lower:
                return "远程日志路径不可读或不可写"
            return "远程日志读取失败"
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
                return self._humanize_startup_failure_reason(remainder)
        return normalized

    def _set_startup_failure_status(self, reason: str) -> None:
        humanized = self._humanize_startup_failure_reason(reason)
        if humanized.startswith("启动失败"):
            self.setStatus(humanized)
            return
        self.setStatus(f"启动失败: {humanized}")

    def _verify_odas_startup(self) -> None:
        if not self._odas_starting:
            return

        try:
            result = self._remote.status()
        except Exception as exc:
            self._cancel_odas_startup()
            self._set_odas_running(False)
            self.setStatus(f"启动失败: {exc}")
            return

        if result.stdout.strip():
            self._cancel_odas_startup()
            self._set_odas_running(True)
            self.setStatus("远程 odaslive 已启动")
            return

        self._startup_attempts_remaining -= 1
        self._poll_remote_log()
        if self._startup_attempts_remaining <= 0:
            reason = self._pick_startup_failure_reason()
            self._cancel_odas_startup()
            self._set_odas_running(False)
            self._set_startup_failure_status(reason)
            return

        if not self._startup_timer.isActive():
            self._startup_timer.start()

    def _poll_remote_log(self) -> None:
        try:
            result = self._remote.read_log_tail(80)
        except Exception as exc:
            message = str(exc)
            if "SSH is not connected" in message:
                self._cancel_odas_startup()
                self._set_remote_connected(False)
                self._set_odas_running(False)
                if self._log_timer.isActive():
                    self._log_timer.stop()
                self._set_remote_log_lines(["等待连接远程 odaslive..."])
                return
            self._set_remote_log_lines([f"日志读取失败: {message}"])
            return

        if result.code != 0 and result.stderr.strip():
            self._set_remote_log_lines([f"日志读取失败: {result.stderr.strip()}"])
        else:
            lines = [line for line in result.stdout.splitlines() if line.strip()]
            if not lines:
                self._set_remote_log_lines(["远程日志为空，等待 odaslive 输出..."])
            else:
                self._set_remote_log_lines(lines)

        if self._remote_connected and not self._odas_starting:
            self._sync_remote_odas_state(update_status=True)

    def _set_recording_sessions(self, sessions: list[str]) -> None:
        if self._recording_sessions == sessions:
            return
        self._recording_sessions = sessions
        self.recordingSessionsChanged.emit()

    def _refresh_recording_sessions(self) -> None:
        snapshot_fn = getattr(self._recorder, "sessions_snapshot", None)
        if snapshot_fn is None or not callable(snapshot_fn):
            self._set_recording_sessions([])
            return

        sessions = snapshot_fn()
        if not isinstance(sessions, list):
            self._set_recording_sessions([])
            return
        items = [f"Source {item.source_id} [{item.mode}] {item.filepath.name}" for item in sessions]
        self._set_recording_sessions(items)

    def _refresh_sources(self) -> None:
        source_ids = extract_source_ids(self._last_sst)
        if source_ids != self._source_ids:
            current = set(source_ids)
            self._selected_source_ids = {
                source_id for source_id in self._selected_source_ids if source_id in current
            }
            for source_id in source_ids:
                if source_id not in self._selected_source_ids:
                    self._selected_source_ids.add(source_id)
            self._source_ids = source_ids
            self.sourceIdsChanged.emit()

        items = build_source_items(
            self._last_sst,
            enabled=self._sources_enabled,
            selected_ids=self._selected_source_ids,
        )
        if items != self._source_items:
            self._source_items = items
            self.sourceItemsChanged.emit()
            self.sourceCountChanged.emit()

        positions = extract_source_positions(
            self._last_sst,
            enabled=self._sources_enabled,
            selected_ids=self._selected_source_ids,
        )
        if positions != self._source_positions:
            self._source_positions = positions
            self.sourcePositionsChanged.emit()

    def _refresh_potentials(self) -> None:
        count = count_potentials(
            self._last_ssl,
            min_energy=self._potential_min,
            max_energy=self._potential_max,
            enabled=self._potentials_enabled,
        )
        if count != self._potential_count:
            self._potential_count = count
            self.potentialCountChanged.emit()


def run() -> int:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    bridge = AppBridge()
    engine.rootContext().setContextProperty("appBridge", bridge)

    qml_path = Path(__file__).resolve().parent / "qml" / "Main.qml"
    engine.load(str(qml_path))

    if not engine.rootObjects():
        return 1

    return app.exec()
