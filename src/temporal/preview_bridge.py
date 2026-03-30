from __future__ import annotations

# pyright: reportMissingImports=false, reportUntypedFunctionDecorator=false

from typing import Any

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot

from temporal.preview_data import (
    DEFAULT_PREVIEW_SCENARIO_KEY,
    get_preview_scenario,
    preview_scenario_keys,
    preview_scenario_options,
)
from temporal.core.ui_projection import (
    build_chart_series,
    build_chart_ticks,
    build_positions_model_items,
    build_rows_model_items,
    compute_sidebar_sources,
    compute_visible_source_ids,
)
from temporal.qml_list_model import QmlListModel


class PreviewBridge(QObject):
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
        self._sources_enabled = True
        self._potentials_enabled = False
        self._potential_min = 0.0
        self._potential_max = 1.0
        self._preview_scenario_keys = preview_scenario_keys()
        self._preview_scenario_key = DEFAULT_PREVIEW_SCENARIO_KEY
        self._scenario = get_preview_scenario(self._preview_scenario_key)
        self._selected_source_ids: set[int] = set()
        self._sample_window_position = 0
        self._preview_chart_sample_step = 200
        self._remote_log_lines = ["等待连接远程 odaslive...", "当前处于预览模式"]

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
        self._preview_tick_timer = QTimer(self)
        self._preview_tick_timer.timeout.connect(self.advancePreviewTick)

        self._preview_scenario_options_model.replace(preview_scenario_options())
        self._chart_x_ticks_model.replace([])
        self._header_nav_labels_model.replace([])
        self._recording_sessions_model.replace([])

        self._reset_selected_sources()
        self._reset_preview_sample_window()
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
        sidebar_sources = self._sidebar_sources()
        return compute_visible_source_ids(sidebar_sources, self._selected_source_ids)

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
                self._stop_preview_streams()
            self._odas_running = False
            self.odasRunningChanged.emit()
            self._set_status("远程 odaslive 已停止")
            self._set_remote_log_lines(["等待连接远程 odaslive...", "远程 odaslive 已停止"])
            return

        if not self._streams_active:
            self._start_preview_streams()
        if not self._remote_connected:
            self._remote_connected = True
            self.remoteConnectedChanged.emit()
        self._odas_running = True
        self.odasRunningChanged.emit()
        self._set_status("远程 odaslive 已启动")
        self._set_remote_log_lines(["远程 odaslive 已启动", "正在监听 SST/SSL/SSS 数据流"])

    @Slot()
    def toggleStreams(self) -> None:
        if self._streams_active:
            self._stop_preview_streams()
            return
        self._start_preview_streams()

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

        was_streaming = self._streams_active
        if was_streaming:
            self._preview_tick_timer.stop()

        self._preview_scenario_key = key
        self._scenario = get_preview_scenario(key)
        self._reset_selected_sources()
        self._reset_preview_sample_window()
        self._apply_scenario_metadata()
        self.previewScenarioKeyChanged.emit()
        self._refresh_preview_models()

        if was_streaming:
            self._preview_tick_timer.setInterval(self._sample_window_config()["timerIntervalMs"])
            self._preview_tick_timer.start()

    @Slot()
    def advancePreviewTick(self) -> None:
        if not self._streams_active:
            return

        frame_count = len(self._tracking_frames())
        if frame_count <= 0:
            return

        advance_per_tick = max(1, int(self._sample_window_config()["advancePerTick"]))
        self._sample_window_position += advance_per_tick
        self._refresh_preview_models()

    def _scenario_sources(self) -> list[dict[str, Any]]:
        return list(self._scenario.get("sources", []))

    def _tracking_frames(self) -> list[dict[str, Any]]:
        frames = self._scenario.get("trackingFrames", [])
        return list(frames) if isinstance(frames, list) else []

    def _sidebar_sources(self) -> list[dict[str, Any]]:
        return compute_sidebar_sources(
            self._scenario_sources(),
            sources_enabled=self._sources_enabled,
            potentials_enabled=self._potentials_enabled,
            potential_min=self._potential_min,
            potential_max=self._potential_max,
        )

    def _visible_source_ids(self) -> list[int]:
        return compute_visible_source_ids(self._sidebar_sources(), self._selected_source_ids)

    def _reset_selected_sources(self) -> None:
        self._selected_source_ids = {int(source["id"]) for source in self._scenario_sources()}

    def _reset_preview_sample_window(self) -> None:
        self._sample_window_position = 0

    def _sample_window_config(self) -> dict[str, int]:
        raw = self._scenario.get("sampleWindow", {})
        if not isinstance(raw, dict):
            raw = {}
        return {
            "sampleStart": int(raw.get("sampleStart", 0)),
            "sampleStep": max(1, int(raw.get("sampleStep", 1))),
            "windowSize": max(1, int(raw.get("windowSize", 1))),
            "tickCount": max(1, int(raw.get("tickCount", 1))),
            "tickStride": max(1, int(raw.get("tickStride", 1))),
            "advancePerTick": max(1, int(raw.get("advancePerTick", 1))),
            "timerIntervalMs": max(50, int(raw.get("timerIntervalMs", 400))),
        }

    def _apply_scenario_metadata(self) -> None:
        self._set_status(str(self._scenario.get("status", "Temporal 就绪")))
        self._set_remote_log_lines(
            list(self._scenario.get("remoteLogLines", ["等待连接远程 odaslive..."]))
        )

    def _start_preview_streams(self) -> None:
        self._reset_preview_sample_window()
        self._streams_active = True
        self.streamsActiveChanged.emit()
        self._preview_tick_timer.setInterval(self._sample_window_config()["timerIntervalMs"])
        self._preview_tick_timer.start()
        if self._odas_running:
            self._set_remote_log_lines(["远程 odaslive 已启动", "正在监听 SST/SSL/SSS 数据流"])
        else:
            self._set_remote_log_lines(["本地 listener 已开启", "等待远程 odaslive 接入"])
        self._set_status("正在监听 SST/SSL/SSS 数据流")
        self._refresh_preview_models()

    def _stop_preview_streams(self) -> None:
        if not self._streams_active:
            return
        self._preview_tick_timer.stop()
        self._streams_active = False
        self.streamsActiveChanged.emit()
        if self._odas_running:
            self._set_remote_log_lines(["远程 odaslive 已启动", "已停止监听 SST/SSL/SSS 数据流"])
        else:
            self._set_remote_log_lines(["本地 listener 已关闭", "等待连接远程 odaslive..."])
        self._set_status("数据流已关闭")

    def _refresh_preview_models(self) -> None:
        sidebar_sources = self._sidebar_sources()
        visible_rows = {int(source["id"]): source for source in sidebar_sources}
        visible_source_ids = self._visible_source_ids()
        current_frame_sources = self._current_frame_sources()

        self._source_rows_model.replace(build_rows_model_items(sidebar_sources, self._selected_source_ids))
        self._source_positions_model.replace(
            build_positions_model_items(current_frame_sources, visible_rows, set(visible_source_ids))
        )
        self._recording_sessions_model.replace([])
        self.sourceIdsChanged.emit()
        self._refresh_chart_models(visible_rows, visible_source_ids)

    def _refresh_chart_models(
        self,
        visible_rows: dict[int, dict[str, Any]],
        visible_source_ids: list[int],
    ) -> None:
        window_frames = self._window_frames()
        config = self._sample_window_config()
        self._chart_x_ticks_model.replace(
            build_chart_ticks(
                window_frames,
                tick_count=config["tickCount"],
                fallback_sample_start=0,
                fallback_sample_step=self._preview_chart_sample_step,
            )
        )
        self._elevation_series_model.replace(
            build_chart_series(window_frames, visible_rows, visible_source_ids, axis="elevation")
        )
        self._azimuth_series_model.replace(
            build_chart_series(window_frames, visible_rows, visible_source_ids, axis="azimuth")
        )

    def _window_frames(self) -> list[dict[str, Any]]:
        frames = self._tracking_frames()
        if not frames:
            return []
        config = self._sample_window_config()
        window_size = max(config["windowSize"], config["tickCount"])
        frame_count = len(frames)
        start_position = self._sample_window_position
        return [
            {
                "sample": (start_position + index) * self._preview_chart_sample_step,
                "sources": list(frames[(start_position + index) % frame_count].get("sources", [])),
            }
            for index in range(window_size)
        ]

    def _current_frame_sources(self) -> dict[int, dict[str, float]]:
        frames = self._tracking_frames()
        if not frames:
            return {}
        frame = frames[self._sample_window_position % len(frames)]
        items: dict[int, dict[str, float]] = {}
        for source in frame.get("sources", []):
            if not isinstance(source, dict):
                continue
            source_id = source.get("id")
            if not isinstance(source_id, int):
                continue
            items[source_id] = {
                "x": float(source.get("x", 0.0)),
                "y": float(source.get("y", 0.0)),
                "z": float(source.get("z", 0.0)),
            }
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
