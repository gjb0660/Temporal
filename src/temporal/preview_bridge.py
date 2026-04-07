from __future__ import annotations

from typing import Any

from PySide6.QtCore import Signal

from temporal.app.bridge import AppBridge
from temporal.app.preview_runtime import (
    PreviewClient,
    PreviewRecorder,
    PreviewRemoteController,
    PreviewRuntime,
    build_preview_config,
)
from temporal.qt_decorators import qt_property, qt_slot


class PreviewBridge(AppBridge):
    _PREVIEW_SAMPLE_STRIDE = PreviewRuntime._PREVIEW_SAMPLE_STRIDE
    _PREVIEW_TIMER_INTERVAL_MS = PreviewRuntime._PREVIEW_TIMER_INTERVAL_MS
    _preview_scenario_key: str
    _preview_scenario_keys: list[str]
    _scenario: dict[str, Any]
    _preview_sample_cursor: int
    _preview_frame_cursor: int
    _preview_tick_timer: Any

    previewModeChanged = Signal()
    previewScenarioKeyChanged = Signal()
    previewScenarioKeysChanged = Signal()

    def __init__(self) -> None:
        self._preview_scenario_key = ""
        self._preview_scenario_keys = []
        self._scenario = {}
        self._preview_sample_cursor = 0
        self._preview_frame_cursor = 0
        self._preview_tick_timer = None
        self._preview_remote = PreviewRemoteController()
        self._preview_client = PreviewClient()
        self._preview_recorder = PreviewRecorder()
        self._preview_runtime = PreviewRuntime(self)
        super().__init__(
            cfg=build_preview_config(),
            remote=self._preview_remote,
            client=self._preview_client,
            recorder=self._preview_recorder,
        )
        self._preview_runtime.initialize()

    @qt_property(bool, notify=previewModeChanged)
    def previewMode(self) -> bool:
        return True

    @qt_property(str, notify=previewScenarioKeyChanged)
    def previewScenarioKey(self) -> str:
        return self._preview_scenario_key

    @qt_property(list, notify=previewScenarioKeysChanged)
    def previewScenarioKeys(self) -> list[str]:
        return list(self._preview_scenario_keys)

    @qt_property(bool, notify=previewModeChanged)
    def showPreviewScenarioSelector(self) -> bool:
        return True

    @qt_slot()
    def startStreams(self) -> None:
        was_active = self._streams_active
        super().startStreams()
        self._preview_runtime.start_streams(was_active)

    @qt_slot()
    def stopStreams(self) -> None:
        super().stopStreams()
        self._preview_runtime.stop_streams()

    @qt_slot(str)
    def setPreviewScenario(self, key: str) -> None:
        self._preview_runtime.set_preview_scenario(key)

    @qt_slot()
    def advancePreviewTick(self) -> None:
        self._preview_runtime.advance_preview_tick()

    def _scenario_sources(self) -> list[dict]:
        return self._preview_runtime.scenario_sources()

    def _tracking_frames(self) -> list[dict]:
        return self._preview_runtime.tracking_frames()

    def _reset_selected_sources(self) -> None:
        self._preview_runtime.reset_selected_sources()

    def _reset_preview_sample_window(self) -> None:
        self._preview_runtime.reset_preview_sample_window()

    def _scenario_remote_lines(self) -> list[str]:
        return self._preview_runtime.scenario_remote_lines()

    def _apply_scenario_metadata(self) -> None:
        self._preview_runtime.apply_scenario_metadata()

    def _refresh_preview_models(self, *, reset_chart: bool = False) -> None:
        self._preview_runtime.refresh_preview_models(reset_chart=reset_chart)

    def _current_preview_sst_message(self) -> dict:
        return self._preview_runtime.current_preview_sst_message()

    def _current_preview_ssl_message(self) -> dict:
        return self._preview_runtime.current_preview_ssl_message()
