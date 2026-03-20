from __future__ import annotations

# pyright: reportMissingImports=false, reportUntypedFunctionDecorator=false

from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from temporal.preview_data import (
    DEFAULT_PREVIEW_SCENARIO_KEY,
    get_preview_scenario,
    preview_scenario_keys,
    preview_scenario_options,
)


class PreviewBridge(QObject):
    _PREVIEW_CHART_X_TICKS = ["1512", "1600", "1800", "2000", "2200", "2400", "2600", "2800", "3000", "3112"]

    statusChanged = Signal()
    remoteConnectedChanged = Signal()
    odasRunningChanged = Signal()
    streamsActiveChanged = Signal()
    sourceIdsChanged = Signal()
    sourcePositionsChanged = Signal()
    sourceRowsChanged = Signal()
    remoteLogLinesChanged = Signal()
    recordingSessionsChanged = Signal()
    sourcesEnabledChanged = Signal()
    potentialsEnabledChanged = Signal()
    potentialRangeChanged = Signal()
    previewModeChanged = Signal()
    previewScenarioKeyChanged = Signal()
    previewScenarioKeysChanged = Signal()
    previewScenarioOptionsChanged = Signal()
    elevationSeriesChanged = Signal()
    azimuthSeriesChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._status = "Temporal 就绪"
        self._remote_connected = False
        self._odas_running = False
        self._streams_active = False
        self._remote_log_lines = ["等待连接远程 odaslive...", "当前处于预览模式"]
        self._recording_sessions: list[str] = []
        self._sources_enabled = True
        self._potentials_enabled = False
        self._potential_min = 0.0
        self._potential_max = 1.0
        self._preview_scenario_keys = preview_scenario_keys()
        self._preview_scenario_options = preview_scenario_options()
        self._preview_scenario_key = DEFAULT_PREVIEW_SCENARIO_KEY
        self._selected_source_ids: set[int] = set()
        self._reset_selected_sources()
        self._apply_scenario_metadata()

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

    @Property(list, notify=sourceIdsChanged)  # type: ignore[reportCallIssue]
    def sourceIds(self) -> list[int]:
        return [int(source["id"]) for source in self._selected_sources()]

    @Property(list, notify=sourcePositionsChanged)  # type: ignore[reportCallIssue]
    def sourcePositions(self) -> list[dict[str, Any]]:
        return [
            {
                "id": int(source["id"]),
                "color": source["color"],
                "x": source["x"],
                "y": source["y"],
                "z": source["z"],
            }
            for source in self._selected_sources()
        ]

    @Property(list, notify=sourceRowsChanged)  # type: ignore[reportCallIssue]
    def sourceRows(self) -> list[dict[str, Any]]:
        return [
            {
                "sourceId": int(source["id"]),
                "label": "声源",
                "checked": int(source["id"]) in self._selected_source_ids,
                "enabled": True,
                "badge": str(int(source["id"])),
                "badgeColor": source["color"],
            }
            for source in self._scenario_sources()
        ]

    @Property(list, notify=remoteLogLinesChanged)  # type: ignore[reportCallIssue]
    def remoteLogLines(self) -> list[str]:
        return self._remote_log_lines

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

    @Property(bool, notify=previewModeChanged)  # type: ignore[reportCallIssue]
    def previewMode(self) -> bool:
        return True

    @Property(str, notify=previewScenarioKeyChanged)  # type: ignore[reportCallIssue]
    def previewScenarioKey(self) -> str:
        return self._preview_scenario_key

    @Property(list, notify=previewScenarioKeysChanged)  # type: ignore[reportCallIssue]
    def previewScenarioKeys(self) -> list[str]:
        return list(self._preview_scenario_keys)

    @Property(list, notify=previewScenarioOptionsChanged)  # type: ignore[reportCallIssue]
    def previewScenarioOptions(self) -> list[dict[str, str]]:
        return list(self._preview_scenario_options)

    @Property(list, notify=elevationSeriesChanged)  # type: ignore[reportCallIssue]
    def elevationSeries(self) -> list[dict[str, Any]]:
        selected_ids = set(self.sourceIds)
        return [
            series
            for series in self._active_scenario()["elevationSeries"]
            if int(series["sourceId"]) in selected_ids
        ]

    @Property(list, notify=azimuthSeriesChanged)  # type: ignore[reportCallIssue]
    def azimuthSeries(self) -> list[dict[str, Any]]:
        selected_ids = set(self.sourceIds)
        return [
            series
            for series in self._active_scenario()["azimuthSeries"]
            if int(series["sourceId"]) in selected_ids
        ]

    @Property(bool, notify=previewModeChanged)  # type: ignore[reportCallIssue]
    def showPreviewScenarioSelector(self) -> bool:
        return True

    @Property(list, notify=previewModeChanged)  # type: ignore[reportCallIssue]
    def headerNavLabels(self) -> list[str]:
        return []

    @Property(list, notify=previewModeChanged)  # type: ignore[reportCallIssue]
    def chartXTicks(self) -> list[str]:
        return list(self._PREVIEW_CHART_X_TICKS)

    @Slot()
    def toggleRemoteOdas(self) -> None:
        if self._odas_running:
            if self._streams_active:
                self._streams_active = False
                self.streamsActiveChanged.emit()
            self._odas_running = False
            self.odasRunningChanged.emit()
            self._set_status("远程 odaslive 已停止")
            self._set_remote_log_lines(["等待连接远程 odaslive...", "远程 odaslive 已停止"])
            return

        if not self._remote_connected:
            self._remote_connected = True
            self.remoteConnectedChanged.emit()
        self._odas_running = True
        self.odasRunningChanged.emit()
        self._set_status("远程 odaslive 已启动")
        self._set_remote_log_lines(["远程 odaslive 已启动", "当前处于预览模式"])

    @Slot()
    def toggleStreams(self) -> None:
        if self._streams_active:
            self._streams_active = False
            self.streamsActiveChanged.emit()
            self._set_status("数据流已关闭")
            self._set_remote_log_lines(["远程 odaslive 已启动", "已停止监听 SST/SSL/SSS 数据流"])
            return

        if not self._odas_running:
            self._set_status("请先启动远程 odaslive")
            return

        self._streams_active = True
        self.streamsActiveChanged.emit()
        self._set_status("正在监听 SST/SSL/SSS 数据流")
        self._set_remote_log_lines(["远程 odaslive 已启动", "正在监听 SST/SSL/SSS 数据流"])

    @Slot(int, bool)
    def setSourceSelected(self, source_id: int, selected: bool) -> None:
        valid_source_ids = {int(source["id"]) for source in self._scenario_sources()}
        if source_id not in valid_source_ids:
            return

        if selected:
            if source_id in self._selected_source_ids:
                return
            self._selected_source_ids.add(source_id)
        else:
            if source_id not in self._selected_source_ids:
                return
            self._selected_source_ids.remove(source_id)

        self._emit_preview_data_changed()

    @Slot(int, result=bool)
    def isSourceSelected(self, source_id: int) -> bool:
        return source_id in self._selected_source_ids

    @Slot(bool)
    def setSourcesEnabled(self, enabled: bool) -> None:
        if self._sources_enabled == enabled:
            return
        self._sources_enabled = enabled
        self.sourcesEnabledChanged.emit()
        self._set_status("声源筛选已更新")

    @Slot(bool)
    def setPotentialsEnabled(self, enabled: bool) -> None:
        if self._potentials_enabled == enabled:
            return
        self._potentials_enabled = enabled
        self.potentialsEnabledChanged.emit()
        self._set_status("候选点筛选已更新")

    @Slot(float, float)
    def setPotentialEnergyRange(self, minimum: float, maximum: float) -> None:
        low = min(minimum, maximum)
        high = max(minimum, maximum)
        if self._potential_min == low and self._potential_max == high:
            return
        self._potential_min = low
        self._potential_max = high
        self.potentialRangeChanged.emit()
        self._set_status("候选声源能量范围已更新")

    @Slot(str)
    def setPreviewScenario(self, key: str) -> None:
        if key not in self._preview_scenario_keys or key == self._preview_scenario_key:
            return
        self._preview_scenario_key = key
        self._reset_selected_sources()
        self._apply_scenario_metadata()
        self.previewScenarioKeyChanged.emit()
        self._emit_preview_data_changed()

    def _active_scenario(self) -> dict[str, Any]:
        return get_preview_scenario(self._preview_scenario_key)

    def _scenario_sources(self) -> list[dict[str, Any]]:
        scenario = self._active_scenario()
        return list(scenario.get("sources", []))

    def _selected_sources(self) -> list[dict[str, Any]]:
        return [
            source
            for source in self._scenario_sources()
            if int(source["id"]) in self._selected_source_ids
        ]

    def _reset_selected_sources(self) -> None:
        self._selected_source_ids = {int(source["id"]) for source in self._scenario_sources()}

    def _apply_scenario_metadata(self) -> None:
        scenario = self._active_scenario()
        self._set_status(str(scenario.get("status", "Temporal 就绪")))
        self._set_remote_log_lines(list(scenario.get("remoteLogLines", ["等待连接远程 odaslive..."])))

    def _emit_preview_data_changed(self) -> None:
        self.sourceIdsChanged.emit()
        self.sourcePositionsChanged.emit()
        self.sourceRowsChanged.emit()
        self.elevationSeriesChanged.emit()
        self.azimuthSeriesChanged.emit()

    def _set_status(self, status: str) -> None:
        if self._status == status:
            return
        self._status = status
        self.statusChanged.emit()

    def _set_remote_log_lines(self, lines: list[str]) -> None:
        if self._remote_log_lines == lines:
            return
        self._remote_log_lines = lines
        self.remoteLogLinesChanged.emit()
