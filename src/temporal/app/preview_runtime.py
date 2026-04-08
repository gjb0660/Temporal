from __future__ import annotations

from time import monotonic
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QTimer

from temporal.core.config_loader import TemporalConfig
from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig
from temporal.core.ssh.remote_odas import CommandResult
from temporal.preview_data import (
    DEFAULT_PREVIEW_SCENARIO_KEY,
    get_preview_scenario,
    preview_scenario_keys,
    preview_scenario_options,
)

if TYPE_CHECKING:
    from temporal.preview_bridge import PreviewBridge


class PreviewRecorder:
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


class PreviewClient:
    def __init__(self) -> None:
        self.started = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False


class PreviewRemoteController:
    def __init__(self) -> None:
        self.connected = False
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

    def clear_log(self) -> CommandResult:
        self.log_lines = []
        return CommandResult(code=0, stdout="", stderr="")


def build_preview_config() -> TemporalConfig:
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


class PreviewRuntime:
    _PREVIEW_SAMPLE_STRIDE = 19
    _PREVIEW_TIMER_INTERVAL_MS = 190

    def __init__(self, bridge: "PreviewBridge") -> None:
        self._bridge = bridge

    def initialize(self) -> None:
        bridge = self._bridge
        bridge._preview_scenario_keys = preview_scenario_keys()
        bridge._preview_scenario_key = DEFAULT_PREVIEW_SCENARIO_KEY
        bridge._scenario = get_preview_scenario(bridge._preview_scenario_key)
        bridge._preview_sample_cursor = 0
        bridge._preview_frame_cursor = 0
        bridge._preview_tick_timer = QTimer(bridge)
        bridge._preview_tick_timer.timeout.connect(bridge.advancePreviewTick)

        bridge._preview_scenario_options_model.replace(preview_scenario_options())
        bridge._set_remote_connected(bridge._preview_remote.is_connected())
        self.reset_selected_sources()
        self.reset_preview_sample_window()
        self.apply_scenario_metadata()
        self.refresh_preview_models(reset_chart=True)
        bridge._apply_state_status()

    def start_streams(self, was_active: bool) -> None:
        bridge = self._bridge
        if not bridge._streams_active:
            return
        if not was_active:
            self.reset_preview_sample_window()
            self.refresh_preview_models(reset_chart=True)
        bridge._preview_tick_timer.setInterval(self._PREVIEW_TIMER_INTERVAL_MS)
        if not bridge._preview_tick_timer.isActive():
            bridge._preview_tick_timer.start()
        bridge._apply_state_status()

    def stop_streams(self) -> None:
        bridge = self._bridge
        if bridge._preview_tick_timer.isActive():
            bridge._preview_tick_timer.stop()
        bridge._set_remote_log_lines(self.scenario_remote_lines())

    def set_preview_scenario(self, key: str) -> None:
        bridge = self._bridge
        if key not in bridge._preview_scenario_keys or key == bridge._preview_scenario_key:
            return

        was_streaming = bridge._streams_active
        if was_streaming and bridge._preview_tick_timer.isActive():
            bridge._preview_tick_timer.stop()

        bridge._preview_scenario_key = key
        bridge._scenario = get_preview_scenario(key)
        self.reset_selected_sources()
        self.reset_preview_sample_window()
        self.apply_scenario_metadata()
        bridge.previewScenarioKeyChanged.emit()
        bridge.previewModeChanged.emit()
        bridge.previewStateChanged.emit()
        self.refresh_preview_models(reset_chart=True)

        if was_streaming:
            bridge._preview_tick_timer.setInterval(self._PREVIEW_TIMER_INTERVAL_MS)
            bridge._preview_tick_timer.start()
            bridge._apply_state_status()
            return

        bridge._apply_state_status()

    def advance_preview_tick(self) -> None:
        bridge = self._bridge
        if not bridge._streams_active:
            return
        frames = self.tracking_frames()
        if not frames:
            return
        bridge._preview_frame_cursor += 1
        bridge._preview_sample_cursor += self._PREVIEW_SAMPLE_STRIDE
        self.refresh_preview_models()

    def scenario_sources(self) -> list[dict[str, Any]]:
        return list(self._bridge._scenario.get("sources", []))

    def tracking_frames(self) -> list[dict[str, Any]]:
        frames = self._bridge._scenario.get("trackingFrames", [])
        return list(frames) if isinstance(frames, list) else []

    def reset_selected_sources(self) -> None:
        self._bridge._selected_source_ids = {
            int(source["id"]) for source in self.scenario_sources()
        }

    def reset_preview_sample_window(self) -> None:
        self._bridge._preview_sample_cursor = 0
        self._bridge._preview_frame_cursor = 0

    def scenario_remote_lines(self) -> list[str]:
        lines = self._bridge._scenario.get("remoteLogLines", ["等待连接远程 odaslive..."])
        return list(lines) if isinstance(lines, list) else ["等待连接远程 odaslive..."]

    def apply_scenario_metadata(self) -> None:
        lines = self.scenario_remote_lines()
        self._bridge._preview_remote.log_lines = lines
        self._bridge._set_remote_log_lines(lines)

    def refresh_preview_models(self, *, reset_chart: bool = False) -> None:
        bridge = self._bridge
        if reset_chart:
            bridge._reset_runtime_chart_clock()
        sst = self.current_preview_sst_message()
        if not bridge._append_runtime_chart_frame(sst):
            return
        bridge._last_sst_monotonic = monotonic()
        bridge._last_sst = sst
        bridge._refresh_sources()
        bridge._last_ssl = self.current_preview_ssl_message()
        bridge._refresh_potentials()
        bridge._apply_state_status()

    def current_preview_sst_message(self) -> dict[str, Any]:
        bridge = self._bridge
        frames = self.tracking_frames()
        if not frames:
            return {
                "timeStamp": bridge._preview_sample_cursor,
                "src": [],
            }
        frame = frames[bridge._preview_frame_cursor % len(frames)]
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
            "timeStamp": bridge._preview_sample_cursor,
            "src": sources,
        }

    def current_preview_ssl_message(self) -> dict[str, Any]:
        return {
            "src": [{"E": float(source.get("energy", 0.0))} for source in self.scenario_sources()]
        }
