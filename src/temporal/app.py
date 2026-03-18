from __future__ import annotations

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
    statusChanged = Signal()
    sourceItemsChanged = Signal()
    sourceIdsChanged = Signal()
    sourceCountChanged = Signal()
    sourcePositionsChanged = Signal()
    remoteLogLinesChanged = Signal()
    potentialCountChanged = Signal()
    recordingSourceCountChanged = Signal()
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
        self._source_items: list[str] = []
        self._source_positions: list[dict[str, float | int]] = []
        self._remote_log_lines = ["等待连接远程 odaslive..."]
        self._potential_count = 0
        self._recording_source_count = 0
        self._sources_enabled = True
        self._potentials_enabled = False
        self._potential_min = 0.0
        self._potential_max = 1.0
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

    @Property(str, notify=statusChanged)  # type: ignore[reportCallIssue]
    def status(self) -> str:
        return self._status

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
            self.setStatus("SSH 已连接")
            self._set_remote_log_lines(["已连接远程主机，正在读取 odaslive 日志..."])
            if not self._log_timer.isActive():
                self._log_timer.start()
            self._poll_remote_log()
        except Exception as exc:
            self.setStatus(f"SSH 连接失败: {exc}")
            self._set_remote_log_lines([f"远程连接失败: {exc}"])

    @Slot()
    def startRemoteOdas(self) -> None:
        try:
            result = self._remote.start_odaslive()
            if result.code == 0:
                self.setStatus("远程 odaslive 已启动")
            else:
                self.setStatus(result.stderr.strip() or "远程 odaslive 启动失败")
            self._poll_remote_log()
        except Exception as exc:
            self.setStatus(f"启动失败: {exc}")

    @Slot()
    def stopRemoteOdas(self) -> None:
        try:
            result = self._remote.stop_odaslive()
            if result.code == 0:
                self.setStatus("远程 odaslive 已停止")
            else:
                self.setStatus(result.stderr.strip() or "远程 odaslive 停止失败")
            self._poll_remote_log()
        except Exception as exc:
            self.setStatus(f"停止失败: {exc}")

    @Slot()
    def startStreams(self) -> None:
        self._client.start()
        self._update_stream_status("开始监听 SST/SSL/SSS 数据流")

    @Slot()
    def stopStreams(self) -> None:
        self._client.stop()
        self._recorder.stop_all()
        self._set_recording_source_count(0)
        self.setStatus("数据流已关闭")

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
        self._recorder.update_active_sources(self._source_ids)
        self._recorder.sweep_inactive()
        self._set_recording_source_count(len(self._recorder.active_sources()))
        self._update_stream_status("SST 数据已更新")

    def _on_ssl(self, message: dict) -> None:
        self._last_ssl = message
        self._refresh_potentials()
        self._update_stream_status("SSL 数据已更新")

    def _on_sep_audio(self, _chunk: bytes) -> None:
        return

    def _on_pf_audio(self, _chunk: bytes) -> None:
        return

    def _update_stream_status(self, prefix: str) -> None:
        self.setStatus(
            f"{prefix} | 声源={self.sourceCount} 候选={self._potential_count} "
            f"录制中={self._recording_source_count}"
        )

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

    def _poll_remote_log(self) -> None:
        try:
            result = self._remote.read_log_tail(80)
        except Exception as exc:
            message = str(exc)
            if "SSH is not connected" in message:
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
