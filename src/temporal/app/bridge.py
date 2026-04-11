from __future__ import annotations

import sys
from collections import deque
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from temporal.core.chart_time import build_default_chart_ticks
from temporal.core.config_loader import TemporalConfig, load_config, resolve_default_config_path
from temporal.core.network.odas_client import OdasClient
from temporal.core.recording.auto_recorder import AutoRecorder
from temporal.core.source_tracking import SpaceTargetSession, TrackingResult
from temporal.core.ssh.remote_odas import RemoteOdasController
from temporal.qml_list_model import QmlListModel
from temporal.qt_decorators import qt_property, qt_slot

from . import recording_audio, remote_lifecycle, status_state, stream_projection


class AppBridge(QObject):
    _AUDIO_CHANNELS = 4
    _AUDIO_SAMPLE_WIDTH = 2
    _STARTUP_VERIFY_INTERVAL_MS = 200
    _STARTUP_VERIFY_ATTEMPTS = 11
    _RUNTIME_CHART_X_TICKS = build_default_chart_ticks()
    _RUNTIME_CHART_COMMIT_INTERVAL_MS = 50
    _HEADER_NAV_LABELS = ["配置", "录制", "相机"]
    _EMPTY_REMOTE_LOG = ["等待连接远程 odaslive..."]

    statusChanged = Signal()
    controlPhaseChanged = Signal()
    controlDataStateChanged = Signal()
    controlSummaryChanged = Signal()
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
        self._control_phase = "idle"
        self._control_data_state = "inactive"
        self._control_phase_summary_override: str | None = None
        self._control_summary = ""
        self._last_sst_monotonic: float | None = None
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
        self._recording_sessions: list[dict[str, Any]] = []
        self._recording_recent_closed_by_target: dict[int, list[dict[str, Any]]] = {}
        self._recording_active_sessions_by_key: dict[
            tuple[int, str, str], tuple[int, dict[str, Any]]
        ] = {}
        self._recording_session_target_by_key: dict[tuple[int, str, str], int] = {}
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
        self._runtime_chart_samples: deque[int] = deque(maxlen=1600)
        self._runtime_chart_frame_sources: dict[int, dict[str, float | int]] = {}
        self._runtime_catalog_by_target: dict[int, dict[str, Any]] = {}
        self._runtime_series_cache: dict[int, deque[dict[str, float | int | None]]] = {}
        self._runtime_series_last_sample: int | None = None
        self._runtime_chart_visible_rows: dict[int, dict[str, Any]] = {}
        self._runtime_chart_visible_target_ids: list[int] = []
        self._runtime_target_colors: dict[int, str] = {}
        self._chart_commit_dirty = False
        self._chart_next_commit_at = 0.0
        self._runtime_tracking_result = TrackingResult(
            visible_targets=[],
            dropped_source_ids=[],
        )
        self._space_target_session = SpaceTargetSession()
        self._SST_DATA_TIMEOUT_SEC = 2.0

        self._sstIngressRequested.connect(
            self._handle_sst_ingress, Qt.ConnectionType.QueuedConnection
        )
        self._sslIngressRequested.connect(
            self._handle_ssl_ingress, Qt.ConnectionType.QueuedConnection
        )
        self._sepAudioIngressRequested.connect(
            self._handle_sep_audio_ingress, Qt.ConnectionType.QueuedConnection
        )
        self._pfAudioIngressRequested.connect(
            self._handle_pf_audio_ingress, Qt.ConnectionType.QueuedConnection
        )

        self._log_timer = QTimer(self)
        self._log_timer.setInterval(1500)
        self._log_timer.timeout.connect(self._poll_remote_log)
        self._startup_timer = QTimer(self)
        self._startup_timer.setInterval(self._STARTUP_VERIFY_INTERVAL_MS)
        self._startup_timer.timeout.connect(self._verify_odas_startup)
        self._chart_commit_timer = QTimer(self)
        self._chart_commit_timer.setInterval(self._RUNTIME_CHART_COMMIT_INTERVAL_MS)
        self._chart_commit_timer.timeout.connect(self._on_chart_commit_timeout)

        self._source_rows_model = QmlListModel(
            [
                "targetId",
                "sourceId",
                "label",
                "checked",
                "enabled",
                "active",
                "badge",
                "badgeColor",
            ],
            self,
        )
        self._source_positions_model = QmlListModel(["id", "color", "x", "y", "z"], self)
        self._elevation_chart_series_model = QmlListModel(["sourceId", "color", "points"], self)
        self._azimuth_chart_series_model = QmlListModel(["sourceId", "color", "points"], self)
        self._preview_scenario_options_model = QmlListModel(["key", "label"], self)
        self._chart_window_model = QmlListModel(["value"], self)
        self._header_nav_labels_model = QmlListModel(["value"], self)
        self._recording_sessions_model = QmlListModel(
            ["targetId", "summary", "details", "hasActive"], self
        )

        self._preview_scenario_options_model.replace([])
        self._chart_window_model.replace(self._RUNTIME_CHART_X_TICKS)
        self._header_nav_labels_model.replace(self._HEADER_NAV_LABELS)
        self._recording_sessions_model.replace([])
        self._source_rows_model.replace([])
        self._source_positions_model.replace([])
        self._elevation_chart_series_model.replace([])
        self._azimuth_chart_series_model.replace([])
        status_state.refresh_control_summary(self)

    @qt_property(str, notify=statusChanged)
    def status(self) -> str:
        return self._control_summary

    @qt_property(str, notify=controlPhaseChanged)
    def controlPhase(self) -> str:
        return self._control_phase

    @qt_property(str, notify=controlDataStateChanged)
    def controlDataState(self) -> str:
        return self._control_data_state

    @qt_property(str, notify=controlSummaryChanged)
    def controlSummary(self) -> str:
        return self._control_summary

    @qt_property(bool, notify=remoteConnectedChanged)
    def remoteConnected(self) -> bool:
        return self._remote_connected

    @qt_property(bool, notify=odasStartingChanged)
    def odasStarting(self) -> bool:
        return self._odas_starting

    @qt_property(bool, notify=odasRunningChanged)
    def odasRunning(self) -> bool:
        return self._odas_running

    @qt_property(bool, notify=streamsActiveChanged)
    def streamsActive(self) -> bool:
        return self._streams_active

    @qt_property(bool, notify=canToggleStreamsChanged)
    def canToggleStreams(self) -> bool:
        return True

    @qt_property(list, notify=sourceIdsChanged)
    def sourceIds(self) -> list[int]:
        return self._source_ids

    @qt_property(list, notify=remoteLogLinesChanged)
    def remoteLogLines(self) -> list[str]:
        return self._remote_log_lines

    @qt_property(str, notify=remoteLogTextChanged)
    def remoteLogText(self) -> str:
        return "\n".join(self._remote_log_lines)

    @qt_property(int, notify=sourceCountChanged)
    def sourceCount(self) -> int:
        return len(self._source_items)

    @qt_property(int, notify=potentialCountChanged)
    def potentialCount(self) -> int:
        return self._potential_count

    @qt_property(int, notify=recordingSourceCountChanged)
    def recordingSourceCount(self) -> int:
        return self._recording_source_count

    @qt_property(bool, notify=sourcesEnabledChanged)
    def sourcesEnabled(self) -> bool:
        return self._sources_enabled

    @qt_property(bool, notify=potentialsEnabledChanged)
    def potentialsEnabled(self) -> bool:
        return self._potentials_enabled

    @qt_property(float, notify=potentialRangeChanged)
    def potentialEnergyMin(self) -> float:
        return self._potential_min

    @qt_property(float, notify=potentialRangeChanged)
    def potentialEnergyMax(self) -> float:
        return self._potential_max

    @qt_property(QObject, constant=True)
    def sourceRowsModel(self) -> QmlListModel:
        return self._source_rows_model

    @qt_property(QObject, constant=True)
    def sourcePositionsModel(self) -> QmlListModel:
        return self._source_positions_model

    @qt_property(QObject, constant=True)
    def elevationChartSeriesModel(self) -> QmlListModel:
        return self._elevation_chart_series_model

    @qt_property(QObject, constant=True)
    def azimuthChartSeriesModel(self) -> QmlListModel:
        return self._azimuth_chart_series_model

    @qt_property(QObject, constant=True)
    def previewScenarioOptionsModel(self) -> QmlListModel:
        return self._preview_scenario_options_model

    @qt_property(QObject, constant=True)
    def chartWindowModel(self) -> QmlListModel:
        return self._chart_window_model

    @qt_property(QObject, constant=True)
    def headerNavLabelsModel(self) -> QmlListModel:
        return self._header_nav_labels_model

    @qt_property(QObject, constant=True)
    def recordingSessionsModel(self) -> QmlListModel:
        return self._recording_sessions_model

    @qt_property(bool, notify=previewStateChanged)
    def previewMode(self) -> bool:
        return False

    @qt_property(str, notify=previewStateChanged)
    def previewScenarioKey(self) -> str:
        return ""

    @qt_property(list, notify=previewStateChanged)
    def previewScenarioKeys(self) -> list[str]:
        return []

    @qt_property(bool, notify=previewStateChanged)
    def showPreviewScenarioSelector(self) -> bool:
        return False

    @qt_slot(str)
    def setStatus(self, status: str) -> None:
        status_state.set_status(self, status)

    @qt_slot()
    def connectRemote(self) -> None:
        remote_lifecycle.connect_remote(self)

    @qt_slot()
    def startRemoteOdas(self) -> None:
        remote_lifecycle.start_remote_odas(self)

    @qt_slot()
    def stopRemoteOdas(self) -> None:
        remote_lifecycle.stop_remote_odas(self)

    @qt_slot()
    def toggleRemoteOdas(self) -> None:
        remote_lifecycle.toggle_remote_odas(self)

    @qt_slot()
    def clearRemoteLog(self) -> None:
        remote_lifecycle.clear_remote_log(self)

    @qt_slot()
    def clearRecordingFiles(self) -> None:
        recording_audio.clear_recording_files(self)

    @qt_slot()
    def startStreams(self) -> None:
        stream_projection.start_streams(self)

    @qt_slot()
    def stopStreams(self) -> None:
        stream_projection.stop_streams(self)

    @qt_slot()
    def toggleStreams(self) -> None:
        stream_projection.toggle_streams(self)

    @qt_slot(bool)
    def setSourcesEnabled(self, enabled: bool) -> None:
        stream_projection.set_sources_enabled(self, enabled)

    @qt_slot(int, bool)
    def setTargetSelected(self, target_id: int, selected: bool) -> None:
        stream_projection.set_target_selected(self, target_id, selected)

    @qt_slot(bool)
    def setPotentialsEnabled(self, enabled: bool) -> None:
        stream_projection.set_potentials_enabled(self, enabled)

    @qt_slot(float, float)
    def setPotentialEnergyRange(self, minimum: float, maximum: float) -> None:
        stream_projection.set_potential_energy_range(self, minimum, maximum)

    @qt_slot(str)
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

    @qt_slot(object)
    def _handle_sst_ingress(self, message: object) -> None:
        if isinstance(message, dict):
            stream_projection.on_sst(self, message)

    @qt_slot(object)
    def _handle_ssl_ingress(self, message: object) -> None:
        if isinstance(message, dict):
            stream_projection.on_ssl(self, message)

    @qt_slot(object)
    def _handle_sep_audio_ingress(self, chunk: object) -> None:
        if isinstance(chunk, (bytes, bytearray, memoryview)):
            stream_projection.on_sep_audio(self, bytes(chunk))

    @qt_slot(object)
    def _handle_pf_audio_ingress(self, chunk: object) -> None:
        if isinstance(chunk, (bytes, bytearray, memoryview)):
            stream_projection.on_pf_audio(self, bytes(chunk))

    def _route_audio_chunk(self, chunk: bytes, mode: str) -> None:
        recording_audio.route_audio_chunk(self, chunk, mode)

    def _update_source_channel_map(self, source_ids: list[int]) -> None:
        recording_audio.update_source_channel_map(self, source_ids)

    def _apply_state_status(self) -> None:
        remote_lifecycle.apply_state_status(self)

    def _refresh_remote_connection_state(self) -> bool:
        return remote_lifecycle.refresh_remote_connection_state(self)

    def _set_remote_connected(self, connected: bool) -> None:
        status_state.set_remote_connected(self, connected)

    def _set_control_state(
        self, phase: str, data_state: str, summary_override: str | None = None
    ) -> None:
        status_state.set_control_state(
            self,
            phase,
            data_state,
            summary_override=summary_override,
        )

    def _set_odas_starting(self, starting: bool) -> None:
        status_state.set_odas_starting(self, starting)

    def _set_odas_running(self, running: bool) -> None:
        status_state.set_odas_running(self, running)

    def _set_streams_active(self, active: bool) -> None:
        status_state.set_streams_active(self, active)

    def _set_recording_source_count(self, value: int) -> None:
        status_state.set_recording_source_count(self, value)

    def _set_remote_log_lines(self, lines: list[str], *, include_warning: bool = True) -> None:
        status_state.set_remote_log_lines(self, lines, include_warning=include_warning)

    def _set_recording_sessions(self, sessions: list[dict[str, Any]]) -> None:
        recording_audio.set_recording_sessions(self, sessions)

    def _set_source_positions(self, positions: list[dict[str, float | int]]) -> None:
        stream_projection.set_source_positions(self, positions)

    def _sync_remote_odas_state(self, update_status: bool = False) -> bool | None:
        return remote_lifecycle.sync_remote_odas_state(self, update_status=update_status)

    def _cancel_odas_startup(self) -> None:
        remote_lifecycle.cancel_odas_startup(self)

    def _latest_remote_log_reason(self) -> str:
        return remote_lifecycle.latest_remote_log_reason(self)

    def _pick_startup_failure_reason(self, result: object | None = None) -> str:
        return remote_lifecycle.pick_startup_failure_reason(self, result)

    def _humanize_startup_failure_reason(self, reason: str) -> str:
        return remote_lifecycle.humanize_startup_failure_reason(reason)

    def _humanize_control_channel_error(self, reason: str) -> str:
        return remote_lifecycle.humanize_control_channel_error(reason)

    def _set_startup_failure_status(self, reason: str) -> None:
        remote_lifecycle.set_startup_failure_status(self, reason)

    def _verify_odas_startup(self) -> None:
        remote_lifecycle.verify_odas_startup(self)

    def _poll_remote_log(self) -> None:
        remote_lifecycle.poll_remote_log(self)

    def _refresh_recording_sessions(self) -> None:
        recording_audio.refresh_recording_sessions(self)

    def _apply_recording_sample_rates(self) -> None:
        recording_audio.apply_recording_sample_rates(self)

    def _on_chart_commit_timeout(self) -> None:
        stream_projection.flush_chart_models_if_due(self, force=False)

    def _refresh_sources(self, *, refresh_chart: bool = True) -> None:
        stream_projection.refresh_sources(self, refresh_chart=refresh_chart)

    def _append_runtime_chart_frame(self, message: dict[str, Any]) -> bool:
        return stream_projection.append_runtime_chart_frame(self, message)

    def _reset_runtime_chart_clock(self) -> None:
        stream_projection.reset_runtime_chart_clock(self)

    def _current_runtime_frame_sources(self) -> dict[int, dict[str, float | int]]:
        return stream_projection.current_runtime_frame_sources(self)

    def _refresh_potentials(self) -> None:
        stream_projection.refresh_potentials(self)


def run_with_bridge(bridge: QObject) -> int:
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication(sys.argv)

    cleaned_up = False

    def _cleanup_local_streams_on_quit() -> None:
        nonlocal cleaned_up
        if cleaned_up:
            return
        cleaned_up = True
        stop_streams = getattr(bridge, "stopStreams", None)
        if callable(stop_streams):
            stop_streams()

    app.aboutToQuit.connect(_cleanup_local_streams_on_quit)

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
