from __future__ import annotations

# pyright: reportMissingImports=false, reportUntypedFunctionDecorator=false
import sys
from pathlib import Path
from typing import Any

from PySide6.QtCore import Property, QObject, QThread, QTimer, Signal, Slot, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from temporal.core.chart_time import build_default_chart_ticks
from temporal.core.config_loader import TemporalConfig, load_config, resolve_default_config_path
from temporal.core.network.odas_client import OdasClient
from temporal.core.network.odas_message_view import (
    build_source_items,
    count_potentials,
    extract_source_ids,
    extract_source_positions,
)
from temporal.core.recording.auto_recorder import AutoRecorder
from temporal.core.source_palette import SourceColorAllocator
from temporal.core.source_tracking import SourceObservation, SpaceTargetSession, TrackingResult
from temporal.core.ssh.remote_odas import RemoteOdasController
from temporal.core.ui_projection import (
    build_chart_series_model,
    build_chart_window_model,
    build_positions_model_items,
    build_rows_model_items,
    compute_sidebar_sources,
    compute_visible_source_ids,
)
from temporal.qml_list_model import QmlListModel
from . import recording_audio, remote_lifecycle, status_state, stream_projection


class AppBridge(QObject):
    _AUDIO_CHANNELS = 4
    _AUDIO_SAMPLE_WIDTH = 2
    _STARTUP_VERIFY_INTERVAL_MS = 200
    _STARTUP_VERIFY_ATTEMPTS = 11
    _RUNTIME_CHART_X_TICKS = build_default_chart_ticks()
    _HEADER_NAV_LABELS = ["配置", "录制", "相机"]
    _EMPTY_REMOTE_LOG = ["等待连接远程 odaslive..."]

    statusChanged = Signal()
    remoteConnectedChanged = Signal()
    odasStartingChanged = Signal()
    odasRunningChanged = Signal()
    streamsActiveChanged = Signal()
    canToggleStreamsChanged = Signal()
    sourceItemsChanged = Signal()
    sourceIdsChanged = Signal()
    sourceCountChanged = Signal()
    sourcePositionsChanged = Signal()
    remoteLogLinesChanged = Signal()
    remoteLogTextChanged = Signal()
    potentialCountChanged = Signal()
    recordingSourceCountChanged = Signal()
    recordingSessionsChanged = Signal()
    sourcesEnabledChanged = Signal()
    potentialsEnabledChanged = Signal()
    potentialRangeChanged = Signal()
    previewStateChanged = Signal()
    _sstIngressRequested = Signal(object)
    _sslIngressRequested = Signal(object)
    _sepAudioIngressRequested = Signal(object)
    _pfAudioIngressRequested = Signal(object)

    def __init__(
        self,
        *,
        cfg: TemporalConfig | None = None,
        remote: Any | None = None,
        client: Any | None = None,
        recorder: Any | None = None,
    ) -> None:
        super().__init__()
        self._status = "Temporal 就绪"
        self._root = Path(__file__).resolve().parents[3]
        self._cfg_path = resolve_default_config_path(self._root)
        self._cfg = cfg or load_config(self._cfg_path)
        self._remote = remote or RemoteOdasController(self._cfg.remote, self._cfg.streams)
        self._client = client or OdasClient(
            config=self._cfg.streams,
            on_sst=self._on_sst,
            on_ssl=self._on_ssl,
            on_sep_audio=self._on_sep_audio,
            on_pf_audio=self._on_pf_audio,
        )
        self._recorder = recorder or AutoRecorder(self._root / "recordings")

        self._last_sst: dict = {}
        self._last_ssl: dict = {}
        self._source_ids: list[int] = []
        self._selected_source_ids: set[int] = set()
        self._source_channel_map: dict[int, int] = {}
        self._channel_source_map: dict[int, int] = {}
        self._source_items: list[str] = []
        self._source_positions: list[dict[str, float | int]] = []
        self._remote_log_lines = list(self._EMPTY_REMOTE_LOG)
        self._recording_sample_rate_warning = ""
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
        self._runtime_chart_messages: list[dict[str, Any]] = []
        self._runtime_chart_frame_sources: dict[int, dict[str, float]] = {}
        self._runtime_tracking_result = TrackingResult(
            visible_targets=[],
            dropped_source_ids=[],
        )
        self._space_target_session = SpaceTargetSession()
        self._source_color_allocator = SourceColorAllocator()

        self._sstIngressRequested.connect(self._handle_sst_ingress, Qt.QueuedConnection)
        self._sslIngressRequested.connect(self._handle_ssl_ingress, Qt.QueuedConnection)
        self._sepAudioIngressRequested.connect(
            self._handle_sep_audio_ingress, Qt.QueuedConnection
        )
        self._pfAudioIngressRequested.connect(self._handle_pf_audio_ingress, Qt.QueuedConnection)

        self._log_timer = QTimer(self)
        self._log_timer.setInterval(1500)
        self._log_timer.timeout.connect(self._poll_remote_log)
        self._startup_timer = QTimer(self)
        self._startup_timer.setInterval(self._STARTUP_VERIFY_INTERVAL_MS)
        self._startup_timer.timeout.connect(self._verify_odas_startup)

        self._source_rows_model = QmlListModel(
            ["sourceId", "label", "checked", "enabled", "badge", "badgeColor"], self
        )
        self._source_positions_model = QmlListModel(["id", "color", "x", "y", "z"], self)
        self._elevation_chart_series_model = QmlListModel(["sourceId", "color", "points"], self)
        self._azimuth_chart_series_model = QmlListModel(["sourceId", "color", "points"], self)
        self._preview_scenario_options_model = QmlListModel(["key", "label"], self)
        self._chart_window_model = QmlListModel(["value"], self)
        self._header_nav_labels_model = QmlListModel(["value"], self)
        self._recording_sessions_model = QmlListModel(["value"], self)

        self._preview_scenario_options_model.replace([])
        self._chart_window_model.replace(self._RUNTIME_CHART_X_TICKS)
        self._header_nav_labels_model.replace(self._HEADER_NAV_LABELS)
        self._recording_sessions_model.replace([])
        self._source_rows_model.replace([])
        self._source_positions_model.replace([])
        self._elevation_chart_series_model.replace([])
        self._azimuth_chart_series_model.replace([])

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

    @Property(bool, notify=canToggleStreamsChanged)  # type: ignore[reportCallIssue]
    def canToggleStreams(self) -> bool:
        return True

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

    @Property(str, notify=remoteLogTextChanged)  # type: ignore[reportCallIssue]
    def remoteLogText(self) -> str:
        return "\n".join(self._remote_log_lines)

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

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def sourceRowsModel(self) -> QmlListModel:
        return self._source_rows_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def sourcePositionsModel(self) -> QmlListModel:
        return self._source_positions_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def elevationChartSeriesModel(self) -> QmlListModel:
        return self._elevation_chart_series_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def azimuthChartSeriesModel(self) -> QmlListModel:
        return self._azimuth_chart_series_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def previewScenarioOptionsModel(self) -> QmlListModel:
        return self._preview_scenario_options_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def chartWindowModel(self) -> QmlListModel:
        return self._chart_window_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def headerNavLabelsModel(self) -> QmlListModel:
        return self._header_nav_labels_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def recordingSessionsModel(self) -> QmlListModel:
        return self._recording_sessions_model

    @Property(bool, notify=previewStateChanged)  # type: ignore[reportCallIssue]
    def previewMode(self) -> bool:
        return False

    @Property(str, notify=previewStateChanged)  # type: ignore[reportCallIssue]
    def previewScenarioKey(self) -> str:
        return ""

    @Property(list, notify=previewStateChanged)  # type: ignore[reportCallIssue]
    def previewScenarioKeys(self) -> list[str]:
        return []

    @Property(bool, notify=previewStateChanged)  # type: ignore[reportCallIssue]
    def showPreviewScenarioSelector(self) -> bool:
        return False

    @Slot(str)
    def setStatus(self, status: str) -> None:
        status_state.set_status(self, status)

    @Slot()
    def connectRemote(self) -> None:
        remote_lifecycle.connect_remote(self)

    @Slot()
    def startRemoteOdas(self) -> None:
        remote_lifecycle.start_remote_odas(self)

    @Slot()
    def stopRemoteOdas(self) -> None:
        remote_lifecycle.stop_remote_odas(self)

    @Slot()
    def toggleRemoteOdas(self) -> None:
        remote_lifecycle.toggle_remote_odas(self)

    @Slot()
    def startStreams(self) -> None:
        stream_projection.start_streams(self)

    @Slot()
    def stopStreams(self) -> None:
        stream_projection.stop_streams(self)

    @Slot()
    def toggleStreams(self) -> None:
        stream_projection.toggle_streams(self)

    @Slot(bool)
    def setSourcesEnabled(self, enabled: bool) -> None:
        stream_projection.set_sources_enabled(self, enabled)

    @Slot(int, bool)
    def setSourceSelected(self, source_id: int, selected: bool) -> None:
        stream_projection.set_source_selected(self, source_id, selected)

    @Slot(int, result=bool)
    def isSourceSelected(self, source_id: int) -> bool:
        return stream_projection.is_source_selected(self, source_id)

    @Slot(bool)
    def setPotentialsEnabled(self, enabled: bool) -> None:
        stream_projection.set_potentials_enabled(self, enabled)

    @Slot(float, float)
    def setPotentialEnergyRange(self, minimum: float, maximum: float) -> None:
        stream_projection.set_potential_energy_range(self, minimum, maximum)

    @Slot(str)
    def setPreviewScenario(self, _key: str) -> None:
        return

    def _on_sst(self, message: dict) -> None:
        if QThread.currentThread() is self.thread():
            self._handle_sst_ingress(message)
            return
        self._sstIngressRequested.emit(message)

    def _on_ssl(self, message: dict) -> None:
        if QThread.currentThread() is self.thread():
            self._handle_ssl_ingress(message)
            return
        self._sslIngressRequested.emit(message)

    def _on_sep_audio(self, chunk: bytes) -> None:
        if QThread.currentThread() is self.thread():
            self._handle_sep_audio_ingress(chunk)
            return
        self._sepAudioIngressRequested.emit(chunk)

    def _on_pf_audio(self, chunk: bytes) -> None:
        if QThread.currentThread() is self.thread():
            self._handle_pf_audio_ingress(chunk)
            return
        self._pfAudioIngressRequested.emit(chunk)

    @Slot(object)
    def _handle_sst_ingress(self, message: object) -> None:
        if isinstance(message, dict):
            stream_projection.on_sst(self, message)

    @Slot(object)
    def _handle_ssl_ingress(self, message: object) -> None:
        if isinstance(message, dict):
            stream_projection.on_ssl(self, message)

    @Slot(object)
    def _handle_sep_audio_ingress(self, chunk: object) -> None:
        if isinstance(chunk, (bytes, bytearray, memoryview)):
            stream_projection.on_sep_audio(self, bytes(chunk))

    @Slot(object)
    def _handle_pf_audio_ingress(self, chunk: object) -> None:
        if isinstance(chunk, (bytes, bytearray, memoryview)):
            stream_projection.on_pf_audio(self, bytes(chunk))

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

    def _apply_state_status(self) -> None:
        if self._odas_starting:
            self.setStatus("远程 odaslive 启动中")
            return
        if self._streams_active:
            self._update_stream_status("正在监听 SST/SSL/SSS 数据流")
            return
        if self._odas_running:
            self.setStatus("SSH 已连接，远程 odaslive 运行中")
            return
        if self._remote_connected:
            self.setStatus("SSH 已连接，远程 odaslive 未运行")
            return
        self.setStatus("Temporal 就绪")

    def _refresh_remote_connection_state(self) -> bool:
        connected = self._remote.is_connected()
        self._set_remote_connected(connected)
        return connected

    def _set_remote_connected(self, connected: bool) -> None:
        if self._remote_connected == connected:
            return
        self._remote_connected = connected
        self.remoteConnectedChanged.emit()
        self.canToggleStreamsChanged.emit()

    def _set_odas_starting(self, starting: bool) -> None:
        if self._odas_starting == starting:
            return
        self._odas_starting = starting
        self.odasStartingChanged.emit()

    def _set_odas_running(self, running: bool) -> None:
        if self._odas_running == running:
            return
        self._odas_running = running
        self.odasRunningChanged.emit()

    def _set_streams_active(self, active: bool) -> None:
        if self._streams_active == active:
            return
        self._streams_active = active
        self.streamsActiveChanged.emit()
        self.canToggleStreamsChanged.emit()

    def _set_recording_source_count(self, value: int) -> None:
        if self._recording_source_count == value:
            return
        self._recording_source_count = value
        self.recordingSourceCountChanged.emit()

    def _set_remote_log_lines(self, lines: list[str]) -> None:
        clean_lines = lines[-120:] if lines else ["远程日志为空，等待 odaslive 输出..."]
        if (
            self._recording_sample_rate_warning
            and self._recording_sample_rate_warning not in clean_lines
        ):
            clean_lines = [*clean_lines, self._recording_sample_rate_warning][-120:]
        if clean_lines == self._remote_log_lines:
            return
        self._remote_log_lines = clean_lines
        self.remoteLogLinesChanged.emit()
        self.remoteLogTextChanged.emit()

    def _set_recording_sessions(self, sessions: list[str]) -> None:
        if self._recording_sessions == sessions:
            return
        self._recording_sessions = sessions
        self.recordingSessionsChanged.emit()
        self._recording_sessions_model.replace(sessions)

    def _set_source_positions(self, positions: list[dict[str, float | int]]) -> None:
        if positions != self._source_positions:
            self._source_positions = positions
            self.sourcePositionsChanged.emit()
        self._source_positions_model.replace(
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

    def _sync_remote_odas_state(self, update_status: bool = False) -> bool | None:
        previous_running = self._odas_running
        if not self._refresh_remote_connection_state():
            self._set_odas_starting(False)
            if update_status:
                self.setStatus("远程控制通道已断开")
            return None

        try:
            result = self._remote.status()
        except Exception as exc:
            self._set_odas_starting(False)
            self._refresh_remote_connection_state()
            if update_status:
                self.setStatus(self._humanize_control_channel_error(str(exc)))
            return None

        running = bool(result.stdout.strip())
        self._set_odas_starting(False)
        self._set_odas_running(running)
        if not update_status or previous_running == running:
            return running
        self._apply_state_status()
        return running

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
        if result is not None:
            stderr = getattr(result, "stderr", "")
            stdout = getattr(result, "stdout", "")
            explicit = stderr.strip() or stdout.strip()
            if explicit.lower().startswith("preflight:"):
                return explicit
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
                return self._humanize_startup_failure_reason(remainder)
        return normalized

    def _humanize_control_channel_error(self, reason: str) -> str:
        normalized = reason.strip()
        lower = normalized.lower()
        if "ssh control shell timed out" in lower:
            return "远程控制通道初始化失败"
        if "ssh control shell lost" in lower or "protocol desynced" in lower:
            return "远程控制通道已断开"
        if "ssh is not connected" in lower:
            return "远程 SSH 连接已断开"
        return normalized

    def _set_startup_failure_status(self, reason: str) -> None:
        humanized = self._humanize_startup_failure_reason(reason)
        if humanized.startswith("启动失败"):
            self.setStatus(humanized)
            return
        self.setStatus(f"启动失败: {humanized}")

    def _verify_odas_startup(self) -> None:
        remote_lifecycle.verify_odas_startup(self)

    def _poll_remote_log(self) -> None:
        remote_lifecycle.poll_remote_log(self)

    def _refresh_recording_sessions(self) -> None:
        recording_audio.refresh_recording_sessions(self)

    def _apply_recording_sample_rates(self) -> None:
        recording_audio.apply_recording_sample_rates(self)

    def _refresh_sources(self, *, refresh_chart: bool = True) -> None:
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

        if self._runtime_tracking_result.visible_targets:
            base_sources = [
                {"id": target.source_id, "color": target.color}
                for target in self._runtime_tracking_result.visible_targets
            ]
        else:
            base_sources = [
                {"id": source_id, "color": self._source_color_allocator.color_for(source_id)}
                for source_id in self._source_ids
            ]
        sidebar_sources = compute_sidebar_sources(
            base_sources,
            sources_enabled=self._sources_enabled,
            potentials_enabled=False,
            potential_min=0.0,
            potential_max=1.0,
        )
        visible_source_ids = compute_visible_source_ids(sidebar_sources, self._selected_source_ids)
        visible_rows = {int(source["id"]): source for source in sidebar_sources}
        current_frame_sources = self._current_runtime_frame_sources()

        positions = build_positions_model_items(
            current_frame_sources,
            visible_rows,
            set(visible_source_ids),
        )
        self._set_source_positions(positions)
        self._source_rows_model.replace(
            build_rows_model_items(sidebar_sources, self._selected_source_ids)
        )
        if refresh_chart:
            self._refresh_chart_models(visible_rows, visible_source_ids)

    def _refresh_chart_models(
        self,
        visible_rows: dict[int, dict[str, Any]],
        visible_source_ids: list[int],
    ) -> None:
        window_model = build_chart_window_model(self._runtime_chart_messages)
        self._chart_window_model.replace(window_model["ticks"])
        self._elevation_chart_series_model.replace(
            self._chart_series_model_items(
                self._runtime_chart_messages,
                visible_rows,
                visible_source_ids,
                axis="elevation",
            )
        )
        self._azimuth_chart_series_model.replace(
            self._chart_series_model_items(
                self._runtime_chart_messages,
                visible_rows,
                visible_source_ids,
                axis="azimuth",
            )
        )

    def _chart_series_model_items(
        self,
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

    def _append_runtime_chart_frame(self, message: dict[str, Any]) -> bool:
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
        self._runtime_chart_frame_sources = {
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
        self._runtime_chart_messages.append({"timeStamp": sample, "src": normalized_sources})
        if len(self._runtime_chart_messages) > 1600:
            self._runtime_chart_messages = self._runtime_chart_messages[-1600:]
        self._runtime_tracking_result = self._space_target_session.step(
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

    def _reset_runtime_chart_clock(self) -> None:
        self._runtime_chart_messages = []
        self._runtime_chart_frame_sources = {}
        self._runtime_tracking_result = TrackingResult(
            visible_targets=[],
            dropped_source_ids=[],
        )
        self._space_target_session = SpaceTargetSession()
        self._source_color_allocator.reset()
        self._chart_window_model.replace(self._RUNTIME_CHART_X_TICKS)
        self._elevation_chart_series_model.replace([])
        self._azimuth_chart_series_model.replace([])

    def _current_runtime_frame_sources(self) -> dict[int, dict[str, float]]:
        return dict(self._runtime_chart_frame_sources)

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


def run_with_bridge(bridge: QObject) -> int:
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    bridge.setParent(engine)
    engine.setInitialProperties({"appBridge": bridge})

    qml_path = Path(__file__).resolve().parents[1] / "qml" / "Main.qml"
    engine.load(str(qml_path))

    if not engine.rootObjects():
        return 1

    return app.exec()


def run() -> int:
    return run_with_bridge(AppBridge())
