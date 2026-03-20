from __future__ import annotations

# pyright: reportMissingImports=false, reportUntypedFunctionDecorator=false

from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from temporal.preview_data import (
    DEFAULT_PREVIEW_SCENARIO_KEY,
    get_preview_scenario,
    preview_scenario_keys,
)


class PreviewBridge(QObject):
    statusChanged = Signal()
    remoteConnectedChanged = Signal()
    odasRunningChanged = Signal()
    streamsActiveChanged = Signal()
    sourceIdsChanged = Signal()
    sourcePositionsChanged = Signal()
    remoteLogLinesChanged = Signal()
    recordingSessionsChanged = Signal()
    sourcesEnabledChanged = Signal()
    potentialsEnabledChanged = Signal()
    potentialRangeChanged = Signal()
    previewModeChanged = Signal()
    previewScenarioKeyChanged = Signal()
    previewScenarioKeysChanged = Signal()
    elevationSeriesChanged = Signal()
    azimuthSeriesChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._status = "Preview ready"
        self._remote_connected = False
        self._odas_running = False
        self._streams_active = False
        self._remote_log_lines = ["Preview mode active", "No live backend connections"]
        self._source_ids: list[int] = []
        self._selected_source_ids: set[int] = set()
        self._recording_sessions: list[str] = []
        self._sources_enabled = True
        self._potentials_enabled = False
        self._potential_min = 0.0
        self._potential_max = 1.0
        self._preview_scenario_keys = preview_scenario_keys()
        self._preview_scenario_key = DEFAULT_PREVIEW_SCENARIO_KEY

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
        return self._source_ids

    @Property(list, notify=sourcePositionsChanged)  # type: ignore[reportCallIssue]
    def sourcePositions(self) -> list[dict[str, Any]]:
        return self._active_scenario()["sourcePositions"]

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

    @Property(list, notify=elevationSeriesChanged)  # type: ignore[reportCallIssue]
    def elevationSeries(self) -> list[dict[str, Any]]:
        return self._active_scenario()["elevationSeries"]

    @Property(list, notify=azimuthSeriesChanged)  # type: ignore[reportCallIssue]
    def azimuthSeries(self) -> list[dict[str, Any]]:
        return self._active_scenario()["azimuthSeries"]

    @Slot()
    def toggleRemoteOdas(self) -> None:
        if self._odas_running:
            if self._streams_active:
                self._streams_active = False
                self.streamsActiveChanged.emit()
            self._odas_running = False
            self.odasRunningChanged.emit()
            self._set_status("Preview remote odaslive stopped")
            self._set_remote_log_lines(["Preview mode active", "Remote odaslive stopped"])
            return

        if not self._remote_connected:
            self._remote_connected = True
            self.remoteConnectedChanged.emit()
        self._odas_running = True
        self.odasRunningChanged.emit()
        self._set_status("Preview remote odaslive running")
        self._set_remote_log_lines(["Preview mode active", "Remote odaslive running"])

    @Slot()
    def toggleStreams(self) -> None:
        if self._streams_active:
            self._streams_active = False
            self.streamsActiveChanged.emit()
            self._set_status("Preview streams stopped")
            self._set_remote_log_lines(["Preview mode active", "Streams stopped"])
            return

        if not self._odas_running:
            self._set_status("Preview requires remote odaslive")
            return

        self._streams_active = True
        self.streamsActiveChanged.emit()
        self._set_status("Preview streams running")
        self._set_remote_log_lines(["Preview mode active", "Streams running"])

    @Slot(int, bool)
    def setSourceSelected(self, source_id: int, selected: bool) -> None:
        if source_id <= 0:
            return
        if selected:
            self._selected_source_ids.add(source_id)
        else:
            self._selected_source_ids.discard(source_id)

    @Slot(int, result=bool)
    def isSourceSelected(self, source_id: int) -> bool:
        return source_id in self._selected_source_ids

    @Slot(bool)
    def setSourcesEnabled(self, enabled: bool) -> None:
        if self._sources_enabled == enabled:
            return
        self._sources_enabled = enabled
        self.sourcesEnabledChanged.emit()
        self._set_status("Preview source visibility updated")

    @Slot(bool)
    def setPotentialsEnabled(self, enabled: bool) -> None:
        if self._potentials_enabled == enabled:
            return
        self._potentials_enabled = enabled
        self.potentialsEnabledChanged.emit()
        self._set_status("Preview potential filter updated")

    @Slot(float, float)
    def setPotentialEnergyRange(self, minimum: float, maximum: float) -> None:
        low = min(minimum, maximum)
        high = max(minimum, maximum)
        if self._potential_min == low and self._potential_max == high:
            return
        self._potential_min = low
        self._potential_max = high
        self.potentialRangeChanged.emit()
        self._set_status("Preview energy range updated")

    @Slot(str)
    def setPreviewScenario(self, key: str) -> None:
        if key not in self._preview_scenario_keys or key == self._preview_scenario_key:
            return
        self._preview_scenario_key = key
        self.previewScenarioKeyChanged.emit()
        self.sourcePositionsChanged.emit()
        self.elevationSeriesChanged.emit()
        self.azimuthSeriesChanged.emit()
        self._set_status(f"Preview scenario: {key}")
        self._set_remote_log_lines(["Preview mode active", f"Scenario set to {key}"])

    def _active_scenario(self) -> dict[str, Any]:
        return get_preview_scenario(self._preview_scenario_key)

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
