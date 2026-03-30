from __future__ import annotations

# pyright: reportMissingImports=false, reportUntypedFunctionDecorator=false

from typing import Any

from PySide6.QtCore import Property, QTimer, Signal, Slot

from temporal.app import AppBridge
from temporal.core.chart_time import DEFAULT_CHART_SAMPLE_STEP
from temporal.core.config_loader import TemporalConfig
from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig
from temporal.core.ssh.remote_odas import CommandResult
from temporal.preview_data import (
    DEFAULT_PREVIEW_SCENARIO_KEY,
    get_preview_scenario,
    preview_scenario_keys,
    preview_scenario_options,
)


class _PreviewRecorder:
    def __init__(self) -> None:
        self._active: set[int] = set()

    def stop_all(self) -> None:
        self._active.clear()

    def sessions_snapshot(self) -> list[Any]:
        return []

    def update_active_sources(self, source_ids: list[int]) -> None:
        self._active = {int(source_id) for source_id in source_ids if int(source_id) > 0}

    def sweep_inactive(self) -> list[int]:
        return []

    def active_sources(self) -> set[int]:
        return set(self._active)

    def push(self, _source_id: int, _mode: str, _pcm_chunk: bytes) -> None:
        return


class _PreviewClient:
    def __init__(self) -> None:
        self.started = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False


class _PreviewRemoteController:
    def __init__(self) -> None:
        self.connected = True
        self.running = False
        self.log_lines = ["等待连接远程 odaslive..."]

    def connect(self) -> None:
        self.connected = True

    def is_connected(self) -> bool:
        return self.connected

    def start_odaslive(self) -> CommandResult:
        self.running = True
        return CommandResult(code=0, stdout="preview\n", stderr="")

    def stop_odaslive(self) -> CommandResult:
        self.running = False
        return CommandResult(code=0, stdout="", stderr="")

    def status(self) -> CommandResult:
        return CommandResult(code=0, stdout="preview\n" if self.running else "", stderr="")

    def read_log_tail(self, _lines: int = 80) -> CommandResult:
        return CommandResult(code=0, stdout="\n".join(self.log_lines), stderr="")


def _preview_config() -> TemporalConfig:
    remote = RemoteOdasConfig(
        host="127.0.0.1",
        port=22,
        username="preview",
        private_key=None,
        odas_command="preview-odaslive",
        odas_args=[],
        odas_cwd=None,
        odas_log="preview.log",
    )
    streams = OdasStreamConfig(
        sst=OdasEndpoint(host="127.0.0.1", port=9000),
        ssl=OdasEndpoint(host="127.0.0.1", port=9001),
        sss_sep=OdasEndpoint(host="127.0.0.1", port=10000),
        sss_pf=OdasEndpoint(host="127.0.0.1", port=10010),
    )
    return TemporalConfig(remote=remote, streams=streams)


class PreviewBridge(AppBridge):
    previewModeChanged = Signal()
    previewScenarioKeyChanged = Signal()
    previewScenarioKeysChanged = Signal()

    def __init__(self) -> None:
        self._preview_remote = _PreviewRemoteController()
        self._preview_client = _PreviewClient()
        self._preview_recorder = _PreviewRecorder()
        super().__init__(
            cfg=_preview_config(),
            remote=self._preview_remote,
            client=self._preview_client,
            recorder=self._preview_recorder,
        )

        self._preview_scenario_keys = preview_scenario_keys()
        self._preview_scenario_key = DEFAULT_PREVIEW_SCENARIO_KEY
        self._scenario = get_preview_scenario(self._preview_scenario_key)
        self._sample_window_position = 0
        self._preview_tick_timer = QTimer(self)
        self._preview_tick_timer.timeout.connect(self.advancePreviewTick)

        self._preview_scenario_options_model.replace(preview_scenario_options())
        self._set_remote_connected(self._preview_remote.is_connected())
        self._reset_selected_sources()
        self._reset_preview_sample_window()
        self._apply_scenario_metadata()
        self._refresh_preview_models(reset_chart=True)
        self.setStatus(str(self._scenario.get("status", "Temporal 就绪")))

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
        if not self._streams_active:
            return
        if not was_active:
            self._reset_preview_sample_window()
            self._refresh_preview_models(reset_chart=True)
        self._preview_tick_timer.setInterval(self._sample_window_config()["timerIntervalMs"])
        if not self._preview_tick_timer.isActive():
            self._preview_tick_timer.start()
        self._apply_state_status()

    @Slot()
    def stopStreams(self) -> None:
        if self._preview_tick_timer.isActive():
            self._preview_tick_timer.stop()
        super().stopStreams()
        self._set_remote_log_lines(self._scenario_remote_lines())

    @Slot(str)
    def setPreviewScenario(self, key: str) -> None:
        if key not in self._preview_scenario_keys or key == self._preview_scenario_key:
            return

        was_streaming = self._streams_active
        if was_streaming and self._preview_tick_timer.isActive():
            self._preview_tick_timer.stop()

        self._preview_scenario_key = key
        self._scenario = get_preview_scenario(key)
        self._reset_selected_sources()
        self._reset_preview_sample_window()
        self._apply_scenario_metadata()
        self.previewScenarioKeyChanged.emit()
        self.previewModeChanged.emit()
        self.previewStateChanged.emit()
        self._refresh_preview_models(reset_chart=True)

        if was_streaming:
            self._preview_tick_timer.setInterval(self._sample_window_config()["timerIntervalMs"])
            self._preview_tick_timer.start()
            self._apply_state_status()
            return

        self.setStatus(str(self._scenario.get("status", "Temporal 就绪")))

    @Slot()
    def advancePreviewTick(self) -> None:
        if not self._streams_active:
            return
        frames = self._tracking_frames()
        if not frames:
            return
        advance_per_tick = max(1, int(self._sample_window_config()["advancePerTick"]))
        self._sample_window_position += advance_per_tick
        self._refresh_preview_models()

    def _scenario_sources(self) -> list[dict[str, Any]]:
        return list(self._scenario.get("sources", []))

    def _tracking_frames(self) -> list[dict[str, Any]]:
        frames = self._scenario.get("trackingFrames", [])
        return list(frames) if isinstance(frames, list) else []

    def _reset_selected_sources(self) -> None:
        self._selected_source_ids = {int(source["id"]) for source in self._scenario_sources()}

    def _reset_preview_sample_window(self) -> None:
        self._sample_window_position = 0

    def _sample_window_config(self) -> dict[str, int]:
        raw = self._scenario.get("sampleWindow", {})
        if not isinstance(raw, dict):
            raw = {}
        return {
            "windowSize": max(1, int(raw.get("windowSize", 1))),
            "tickCount": max(1, int(raw.get("tickCount", 1))),
            "advancePerTick": max(1, int(raw.get("advancePerTick", 1))),
            "timerIntervalMs": max(50, int(raw.get("timerIntervalMs", 400))),
        }

    def _scenario_remote_lines(self) -> list[str]:
        lines = self._scenario.get("remoteLogLines", ["等待连接远程 odaslive..."])
        return list(lines) if isinstance(lines, list) else ["等待连接远程 odaslive..."]

    def _apply_scenario_metadata(self) -> None:
        lines = self._scenario_remote_lines()
        self._preview_remote.log_lines = lines
        self._set_remote_log_lines(lines)

    def _refresh_preview_models(self, *, reset_chart: bool = False) -> None:
        config = self._sample_window_config()
        self._runtime_chart_tick_count = max(1, int(config["tickCount"]))
        self._runtime_chart_sample_step = DEFAULT_CHART_SAMPLE_STEP
        if reset_chart:
            self._reset_runtime_chart_clock()
        sst = self._current_preview_sst_message()
        self._last_sst = sst
        self._append_runtime_chart_frame(sst)
        self._refresh_sources()
        self._last_ssl = self._current_preview_ssl_message()
        self._refresh_potentials()

    def _current_preview_sst_message(self) -> dict[str, Any]:
        frames = self._tracking_frames()
        if not frames:
            return {"timeStamp": self._sample_window_position * DEFAULT_CHART_SAMPLE_STEP, "src": []}
        frame = frames[self._sample_window_position % len(frames)]
        sources = [
            {
                "id": int(source.get("id", 0)),
                "x": float(source.get("x", 0.0)),
                "y": float(source.get("y", 0.0)),
                "z": float(source.get("z", 0.0)),
            }
            for source in frame.get("sources", [])
            if isinstance(source, dict)
        ]
        return {
            "timeStamp": self._sample_window_position * DEFAULT_CHART_SAMPLE_STEP,
            "src": sources,
        }

    def _current_preview_ssl_message(self) -> dict[str, Any]:
        return {
            "src": [{"E": float(source.get("energy", 0.0))} for source in self._scenario_sources()]
        }
