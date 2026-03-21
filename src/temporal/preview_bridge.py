from __future__ import annotations

# pyright: reportMissingImports=false, reportUntypedFunctionDecorator=false

import json
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from temporal.preview_data import (
    DEFAULT_PREVIEW_SCENARIO_KEY,
    get_preview_scenario,
    preview_scenario_keys,
    preview_scenario_options,
)
from temporal.qml_list_model import QmlListModel


class PreviewBridge(QObject):
    _PREVIEW_CHART_X_TICKS = [
        "1512",
        "1600",
        "1800",
        "2000",
        "2200",
        "2400",
        "2600",
        "2800",
        "3000",
        "3112",
    ]

    statusChanged = Signal()
    remoteConnectedChanged = Signal()
    odasRunningChanged = Signal()
    streamsActiveChanged = Signal()
    sourceIdsChanged = Signal()
    sourcesEnabledChanged = Signal()
    potentialsEnabledChanged = Signal()
    potentialRangeChanged = Signal()
    previewModeChanged = Signal()
    previewScenarioKeyChanged = Signal()
    previewScenarioKeysChanged = Signal()
    remoteLogTextChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._status = "Temporal 就绪"
        self._remote_connected = False
        self._odas_running = False
        self._streams_active = False
        self._remote_log_lines = ["等待连接远程 odaslive...", "当前处于预览模式"]
        self._sources_enabled = True
        self._potentials_enabled = False
        self._potential_min = 0.0
        self._potential_max = 1.0
        self._preview_scenario_keys = preview_scenario_keys()
        self._preview_scenario_key = DEFAULT_PREVIEW_SCENARIO_KEY
        self._selected_source_ids: set[int] = set()

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

        self._preview_scenario_options_model.replace(preview_scenario_options())
        self._chart_x_ticks_model.replace(self._PREVIEW_CHART_X_TICKS)
        self._header_nav_labels_model.replace([])
        self._recording_sessions_model.replace([])

        self._reset_selected_sources()
        self._apply_scenario_metadata()
        self._refresh_preview_models()

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
        return self._visible_source_ids()

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

    @Property(bool, notify=previewModeChanged)  # type: ignore[reportCallIssue]
    def showPreviewScenarioSelector(self) -> bool:
        return True

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

        self._refresh_preview_models()

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
        self._refresh_preview_models()

    @Slot(bool)
    def setPotentialsEnabled(self, enabled: bool) -> None:
        if self._potentials_enabled == enabled:
            return
        self._potentials_enabled = enabled
        self.potentialsEnabledChanged.emit()
        self._set_status("候选点筛选已更新")
        self._refresh_preview_models()

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
        self._refresh_preview_models()

    @Slot(str)
    def setPreviewScenario(self, key: str) -> None:
        if key not in self._preview_scenario_keys or key == self._preview_scenario_key:
            return
        self._preview_scenario_key = key
        self._reset_selected_sources()
        self._apply_scenario_metadata()
        self.previewScenarioKeyChanged.emit()
        self._refresh_preview_models()

    def _active_scenario(self) -> dict[str, Any]:
        return get_preview_scenario(self._preview_scenario_key)

    def _scenario_sources(self) -> list[dict[str, Any]]:
        scenario = self._active_scenario()
        return list(scenario.get("sources", []))

    def _sidebar_sources(self) -> list[dict[str, Any]]:
        if not self._sources_enabled:
            return []

        if not self._potentials_enabled:
            return self._scenario_sources()

        return [
            source
            for source in self._scenario_sources()
            if self._potential_min <= float(source.get("energy", 0.0)) <= self._potential_max
        ]

    def _visible_sources(self) -> list[dict[str, Any]]:
        return [
            source
            for source in self._sidebar_sources()
            if int(source["id"]) in self._selected_source_ids
        ]

    def _visible_source_ids(self) -> list[int]:
        return [int(source["id"]) for source in self._visible_sources()]

    def _reset_selected_sources(self) -> None:
        self._selected_source_ids = {int(source["id"]) for source in self._scenario_sources()}

    def _apply_scenario_metadata(self) -> None:
        scenario = self._active_scenario()
        self._set_status(str(scenario.get("status", "Temporal 就绪")))
        self._set_remote_log_lines(
            list(scenario.get("remoteLogLines", ["等待连接远程 odaslive..."]))
        )

    def _refresh_preview_models(self) -> None:
        sidebar_sources = self._sidebar_sources()
        visible_sources = self._visible_sources()
        visible_source_ids = {int(source["id"]) for source in visible_sources}
        scenario = self._active_scenario()

        self._source_rows_model.replace(
            [
                {
                    "sourceId": int(source["id"]),
                    "label": "声源",
                    "checked": int(source["id"]) in self._selected_source_ids,
                    "enabled": True,
                    "badge": str(int(source["id"])),
                    "badgeColor": source["color"],
                }
                for source in sidebar_sources
            ]
        )
        self._source_positions_model.replace(
            [
                {
                    "id": int(source["id"]),
                    "color": source["color"],
                    "x": source["x"],
                    "y": source["y"],
                    "z": source["z"],
                }
                for source in visible_sources
            ]
        )
        self._elevation_series_model.replace(
            self._series_items(scenario.get("elevationSeries", []), visible_source_ids)
        )
        self._azimuth_series_model.replace(
            self._series_items(scenario.get("azimuthSeries", []), visible_source_ids)
        )
        self._recording_sessions_model.replace([])
        self.sourceIdsChanged.emit()

    def _series_items(
        self, series_list: list[dict[str, Any]], visible_source_ids: set[int]
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for series in series_list:
            source_id = int(series["sourceId"])
            if source_id not in visible_source_ids:
                continue
            values = [float(value) for value in series.get("values", [])]
            items.append(
                {
                    "sourceId": source_id,
                    "color": series["color"],
                    "valuesJson": json.dumps(values),
                }
            )
        return items

    def _set_status(self, status: str) -> None:
        if self._status == status:
            return
        self._status = status
        self.statusChanged.emit()

    def _set_remote_log_lines(self, lines: list[str]) -> None:
        if self._remote_log_lines == lines:
            return
        self._remote_log_lines = lines
        self.remoteLogTextChanged.emit()
