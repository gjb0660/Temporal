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
from temporal.qml_list_model import QmlListModel


class AppBridge(QObject):
    _AUDIO_CHANNELS = 4
    _AUDIO_SAMPLE_WIDTH = 2
    _RUNTIME_CHART_X_TICKS = ["0", "200", "400", "600", "800", "1000", "1200", "1400", "1600"]
    _HEADER_NAV_LABELS = ["配置", "录制", "相机"]

    statusChanged = Signal()
    remoteConnectedChanged = Signal()
    odasRunningChanged = Signal()
    streamsActiveChanged = Signal()
    sourceItemsChanged = Signal()
    sourceIdsChanged = Signal()
    sourceCountChanged = Signal()
    potentialCountChanged = Signal()
    recordingSourceCountChanged = Signal()
    sourcesEnabledChanged = Signal()
    potentialsEnabledChanged = Signal()
    potentialRangeChanged = Signal()
    previewStateChanged = Signal()
    remoteLogTextChanged = Signal()

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
        self._odas_running = False
        self._streams_active = False
        self._recorder = AutoRecorder(self._root / "recordings")
        self._log_timer = QTimer(self)
        self._log_timer.setInterval(1500)
        self._log_timer.timeout.connect(self._poll_remote_log)
        self._client = OdasClient(
            config=self._cfg.streams,
            on_sst=self._on_sst,
            on_ssl=self._on_ssl,
            on_sep_audio=self._on_sep_audio,
            on_pf_audio=self._on_pf_audio,
        )

        self._source_rows_model = QmlListModel(
            ["sourceId", "label", "checked", "enabled", "badge", "badgeColor"], self
        )
        self._source_positions_model = QmlListModel(["id", "color", "x", "y", "z"], self)
        self._elevation_series_model = QmlListModel(["sourceId", "color", "valuesJson"], self)
        self._azimuth_series_model = QmlListModel(["sourceId", "color", "valuesJson"], self)
        self._preview_scenario_options_model = QmlListModel(["key", "label"], self)
        self._chart_x_ticks_model = QmlListModel(["value"], self)
        self._header_nav_labels_model = QmlListModel(["value"], self)
        self._recording_sessions_model = QmlListModel(["value"], self)

        self._preview_scenario_options_model.replace([])
        self._chart_x_ticks_model.replace(self._RUNTIME_CHART_X_TICKS)
        self._header_nav_labels_model.replace(self._HEADER_NAV_LABELS)
        self._recording_sessions_model.replace([])
        self._source_rows_model.replace([])
        self._source_positions_model.replace([])
        self._elevation_series_model.replace([])
        self._azimuth_series_model.replace([])

    @Property(str, notify=statusChanged)  # type: ignore[reportCallIssue]
    def status(self) -> str:
        return self._status

    @Property(bool, notify=remoteConnectedChanged)  # type: ignore[reportCallIssue]
    def remoteConnected(self) -> bool:
        return self._remote_connected

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

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def sourceRowsModel(self) -> QmlListModel:
        return self._source_rows_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def sourcePositionsModel(self) -> QmlListModel:
        return self._source_positions_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def elevationSeriesModel(self) -> QmlListModel:
        return self._elevation_series_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def azimuthSeriesModel(self) -> QmlListModel:
        return self._azimuth_series_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def previewScenarioOptionsModel(self) -> QmlListModel:
        return self._preview_scenario_options_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def chartXTicksModel(self) -> QmlListModel:
        return self._chart_x_ticks_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def headerNavLabelsModel(self) -> QmlListModel:
        return self._header_nav_labels_model

    @Property(QObject, constant=True)  # type: ignore[reportCallIssue]
    def recordingSessionsModel(self) -> QmlListModel:
        return self._recording_sessions_model

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
        if self._status == status:
            return
        self._status = status
        self.statusChanged.emit()

    @Slot()
    def connectRemote(self) -> None:
        try:
            self._remote.connect()
        except Exception as exc:
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

        try:
            result = self._remote.start_odaslive()
        except Exception as exc:
            self.setStatus(f"启动失败: {exc}")
            return

        if result.code == 0:
            self._set_odas_running(True)
            self.setStatus("远程 odaslive 已启动")
        else:
            self._sync_remote_odas_state()
            self.setStatus(result.stderr.strip() or "远程 odaslive 启动失败")
        self._poll_remote_log()

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

        if result.code == 0:
            self._set_odas_running(False)
            self.setStatus("远程 odaslive 已停止")
        else:
            self._sync_remote_odas_state()
            self.setStatus(result.stderr.strip() or "远程 odaslive 停止失败")
        self._poll_remote_log()

    @Slot()
    def toggleRemoteOdas(self) -> None:
        if self._odas_running:
            if self._streams_active:
                self.stopStreams()
            self.stopRemoteOdas()
            return

        if not self._remote_connected:
            self.connectRemote()
            if not self._remote_connected:
                return
        if not self._streams_active:
            self.startStreams()
        self.startRemoteOdas()

    @Slot()
    def startStreams(self) -> None:
        if self._streams_active:
            self._update_stream_status("正在监听 SST/SSL/SSS 数据流")
            return

        self._client.start()
        self._set_streams_active(True)
        if self._odas_running:
            self._set_remote_log_lines(["远程 odaslive 已启动", "正在监听 SST/SSL/SSS 数据流"])
        else:
            self._set_remote_log_lines(["本地 listener 已开启", "等待远程 odaslive 接入"])
        self._update_stream_status("正在监听 SST/SSL/SSS 数据流")

    @Slot()
    def stopStreams(self) -> None:
        self._client.stop()
        self._recorder.stop_all()
        self._source_channel_map.clear()
        self._channel_source_map.clear()
        self._set_streams_active(False)
        self._set_recording_source_count(0)
        self._set_recording_sessions([])
        if self._odas_running:
            self._set_remote_log_lines(["远程 odaslive 已启动", "已停止监听 SST/SSL/SSS 数据流"])
        else:
            self._set_remote_log_lines(["本地 listener 已关闭", "等待连接远程 odaslive..."])
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
        self._update_stream_status("候选点筛选已更新")

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
            f"{prefix} | 声源={self.sourceCount} 候选={self._potential_count} 录制中={self._recording_source_count}"
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
        self.remoteLogTextChanged.emit()

    def _sync_remote_odas_state(self) -> None:
        if not self._remote_connected:
            self._set_odas_running(False)
            return

        try:
            result = self._remote.status()
        except Exception:
            self._set_odas_running(False)
            return

        self._set_odas_running(bool(result.stdout.strip()))

    def _poll_remote_log(self) -> None:
        try:
            result = self._remote.read_log_tail(80)
        except Exception as exc:
            message = str(exc)
            if "SSH is not connected" in message:
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
            return

        lines = [line for line in result.stdout.splitlines() if line.strip()]
        if not lines:
            self._set_remote_log_lines(["远程日志为空，等待 odaslive 输出..."])
            return
        self._set_remote_log_lines(lines)

    def _set_recording_sessions(self, sessions: list[str]) -> None:
        if self._recording_sessions == sessions:
            return
        self._recording_sessions = sessions
        self._recording_sessions_model.replace(sessions)

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
        self._source_positions = positions
        self._source_positions_model.replace(
            [
                {
                    "id": int(item["id"]),
                    "color": item.get("color", "#cf54ea"),
                    "x": float(item["x"]),
                    "y": float(item["y"]),
                    "z": float(item["z"]),
                }
                for item in positions
            ]
        )
        self._source_rows_model.replace(
            [
                {
                    "sourceId": source_id,
                    "label": "声源",
                    "checked": source_id in self._selected_source_ids,
                    "enabled": True,
                    "badge": str(source_id),
                    "badgeColor": "#cf54ea",
                }
                for source_id in self._source_ids
                if self._sources_enabled
            ]
        )

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

    @Slot(str)
    def setPreviewScenario(self, _key: str) -> None:
        return


def run_with_bridge(bridge: QObject) -> int:
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    bridge.setParent(engine)
    engine.setInitialProperties({"appBridge": bridge})

    qml_path = Path(__file__).resolve().parent / "qml" / "Main.qml"
    engine.load(str(qml_path))

    if not engine.rootObjects():
        return 1

    return app.exec()


def run() -> int:
    return run_with_bridge(AppBridge())
