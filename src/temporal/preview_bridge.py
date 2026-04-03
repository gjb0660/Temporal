from __future__ import annotations

# pyright: reportMissingImports=false, reportUntypedFunctionDecorator=false
from PySide6.QtCore import Property, Signal, Slot

from temporal.app.bridge import AppBridge
from temporal.app.preview_runtime import (
    PreviewRuntime,
    _PreviewClient,
    _PreviewRecorder,
    _PreviewRemoteController,
    build_preview_config,
)


class PreviewBridge(AppBridge):
    _PREVIEW_SAMPLE_STRIDE = PreviewRuntime._PREVIEW_SAMPLE_STRIDE
    _PREVIEW_TIMER_INTERVAL_MS = PreviewRuntime._PREVIEW_TIMER_INTERVAL_MS

    previewModeChanged = Signal()
    previewScenarioKeyChanged = Signal()
    previewScenarioKeysChanged = Signal()

    def __init__(self) -> None:
        self._preview_remote = _PreviewRemoteController()
        self._preview_client = _PreviewClient()
        self._preview_recorder = _PreviewRecorder()
        self._preview_runtime = PreviewRuntime(self)
        super().__init__(
            cfg=build_preview_config(),
            remote=self._preview_remote,
            client=self._preview_client,
            recorder=self._preview_recorder,
        )
        self._preview_runtime.initialize()

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
    def startStreams(self) -> None:
        was_active = self._streams_active
        super().startStreams()
        self._preview_runtime.start_streams(was_active)

    @Slot()
    def stopStreams(self) -> None:
        super().stopStreams()
        self._preview_runtime.stop_streams()

    @Slot(str)
    def setPreviewScenario(self, key: str) -> None:
        self._preview_runtime.set_preview_scenario(key)

    @Slot()
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
