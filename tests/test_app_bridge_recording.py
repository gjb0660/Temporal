import json
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from temporal.app import AppBridge
from temporal.core.config_loader import TemporalConfig
from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig
from temporal.core.source_palette import SOURCE_COLOR_PALETTE
from temporal.core.ssh.remote_odas import CommandResult


@dataclass
class _Session:
    source_id: int
    mode: str
    filepath: Path


class _FakeRecorder:
    def __init__(self, _output_dir) -> None:
        self._active: set[int] = set()
        self.pushed: list[tuple[int, str, bytes]] = []
        self._sessions: dict[tuple[int, str], _Session] = {}
        self.sample_rates: dict[str, int] = {"sp": 16000, "pf": 16000}

    def update_active_sources(self, source_ids) -> None:
        self._active = {int(source_id) for source_id in source_ids if int(source_id) > 0}
        for source_id in self._active:
            self._sessions[(source_id, "sp")] = _Session(
                source_id=source_id,
                mode="sp",
                filepath=Path(f"ODAS_{source_id}_sp.wav"),
            )
            self._sessions[(source_id, "pf")] = _Session(
                source_id=source_id,
                mode="pf",
                filepath=Path(f"ODAS_{source_id}_pf.wav"),
            )

    def sweep_inactive(self):
        return []

    def active_sources(self) -> set[int]:
        return set(self._active)

    def push(self, source_id: int, mode: str, pcm_chunk: bytes) -> None:
        self.pushed.append((source_id, mode, pcm_chunk))

    def stop_all(self) -> None:
        self._active.clear()
        self.pushed.clear()
        self._sessions.clear()

    def sessions_snapshot(self):
        sessions = list(self._sessions.values())
        sessions.sort(key=lambda item: (item.source_id, item.mode))
        return sessions

    def set_sample_rates(self, sample_rates: dict[str, int]) -> None:
        self.sample_rates = dict(sample_rates)


class _FakeClient:
    def __init__(self, **_kwargs) -> None:
        self.start_calls = 0
        self.stop_calls = 0

    def start(self) -> None:
        self.start_calls += 1

    def stop(self) -> None:
        self.stop_calls += 1


class _FakeRemote:
    def __init__(self, _config, _streams) -> None:
        self.connected = False
        self.running = False
        self.connect_calls = 0
        self.start_calls = 0
        self.stop_calls = 0
        self.sample_rates = {"sp": 16000, "pf": 16000}
        self.sample_rate_warning: str | None = None

    def connect(self) -> None:
        self.connected = True
        self.connect_calls += 1

    def is_connected(self) -> bool:
        return self.connected

    def start_odaslive(self) -> CommandResult:
        self.running = True
        self.start_calls += 1
        return CommandResult(code=0, stdout="123\n", stderr="")

    def stop_odaslive(self) -> CommandResult:
        self.running = False
        self.stop_calls += 1
        return CommandResult(code=0, stdout="", stderr="")

    def status(self) -> CommandResult:
        stdout = "123\n" if self.running else ""
        return CommandResult(code=0, stdout=stdout, stderr="")

    def read_log_tail(self, _lines: int = 80) -> CommandResult:
        if not self.connected:
            raise RuntimeError("SSH is not connected")
        stdout = "odaslive ready\n" if self.running else "connected\n"
        return CommandResult(code=0, stdout=stdout, stderr="")

    def recording_sample_rates(self) -> dict[str, int]:
        return dict(self.sample_rates)

    def recording_sample_rate_warning(self) -> str | None:
        return self.sample_rate_warning


def _fake_config() -> tuple[RemoteOdasConfig, OdasStreamConfig]:
    remote = RemoteOdasConfig(
        host="172.21.16.222",
        port=22,
        username="odas",
        private_key="~/.ssh/id_rsa",
        odas_command="./odas_loop.sh",
        odas_args=[],
        odas_cwd="workspace/ODAS/odas",
        odas_log="odaslive.log",
    )
    streams = OdasStreamConfig(
        sst=OdasEndpoint(host="192.168.1.50", port=9000),
        ssl=OdasEndpoint(host="192.168.1.50", port=9001),
        sss_sep=OdasEndpoint(host="192.168.1.50", port=10000),
        sss_pf=OdasEndpoint(host="192.168.1.50", port=10010),
    )
    return remote, streams


class TestAppBridgeRecording(unittest.TestCase):
    def _make_bridge(self) -> AppBridge:
        remote, streams = _fake_config()
        with (
            patch("temporal.app.AutoRecorder", _FakeRecorder),
            patch(
                "temporal.app.load_config",
                return_value=TemporalConfig(remote=remote, streams=streams),
            ),
            patch("temporal.app.OdasClient", _FakeClient),
            patch("temporal.app.RemoteOdasController", _FakeRemote),
        ):
            return AppBridge()

    def test_sst_updates_recording_count(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst({"src": [{"id": 2}, {"id": 0}, {"id": 5}]})

        self.assertEqual(bridge.recordingSourceCount, 2)
        self.assertIn("录制中=2", bridge._status)

    def test_stop_streams_resets_recording_count(self) -> None:
        bridge = self._make_bridge()
        bridge._on_sst({"src": [{"id": 3}]})

        bridge.stopStreams()

        self.assertEqual(bridge.recordingSourceCount, 0)
        self.assertEqual(bridge._status, "Temporal 就绪")

    def test_source_channel_map_reuses_existing_channel(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst({"src": [{"id": 10}, {"id": 20}]})
        self.assertEqual(bridge._source_channel_map, {10: 0, 20: 1})
        color_by_source = {
            row["sourceId"]: row["badgeColor"]
            for row in [
                bridge.sourceRowsModel.get(index) for index in range(bridge.sourceRowsModel.count)
            ]
        }
        self.assertEqual(color_by_source[10], SOURCE_COLOR_PALETTE[0])
        self.assertEqual(color_by_source[20], SOURCE_COLOR_PALETTE[1])

        bridge._on_sst({"src": [{"id": 20}, {"id": 30}]})
        self.assertEqual(bridge._source_channel_map, {20: 1, 30: 0})
        color_by_source = {
            row["sourceId"]: row["badgeColor"]
            for row in [
                bridge.sourceRowsModel.get(index) for index in range(bridge.sourceRowsModel.count)
            ]
        }
        self.assertEqual(color_by_source[20], SOURCE_COLOR_PALETTE[1])
        self.assertEqual(color_by_source[30], SOURCE_COLOR_PALETTE[2])

        bridge._on_sst({"src": [{"id": 10}]})
        color_by_source = {
            row["sourceId"]: row["badgeColor"]
            for row in [
                bridge.sourceRowsModel.get(index) for index in range(bridge.sourceRowsModel.count)
            ]
        }
        self.assertEqual(color_by_source[10], SOURCE_COLOR_PALETTE[0])

    def test_sep_audio_routes_to_mapped_sources(self) -> None:
        bridge = self._make_bridge()
        recorder = bridge._recorder
        self.assertIsInstance(recorder, _FakeRecorder)

        bridge._on_sst({"src": [{"id": 101}, {"id": 202}, {"id": 303}, {"id": 404}]})

        chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00\x0b\x00\x0c\x00\x0d\x00\x0e\x00"
        bridge._on_sep_audio(chunk)

        self.assertEqual(len(recorder.pushed), 4)
        expected = {
            (101, "sp"): b"\x01\x00\x0b\x00",
            (202, "sp"): b"\x02\x00\x0c\x00",
            (303, "sp"): b"\x03\x00\x0d\x00",
            (404, "sp"): b"\x04\x00\x0e\x00",
        }
        actual = {(source_id, mode): pcm for source_id, mode, pcm in recorder.pushed}
        self.assertEqual(actual, expected)

    def test_pf_audio_routes_to_mapped_sources(self) -> None:
        bridge = self._make_bridge()
        recorder = bridge._recorder
        self.assertIsInstance(recorder, _FakeRecorder)

        bridge._on_sst({"src": [{"id": 1}, {"id": 2}]})

        chunk = b"\x11\x00\x22\x00\x33\x00\x44\x00"
        bridge._on_pf_audio(chunk)

        actual = {(source_id, mode): pcm for source_id, mode, pcm in recorder.pushed}
        self.assertEqual(actual.get((1, "pf")), b"\x11\x00")
        self.assertEqual(actual.get((2, "pf")), b"\x22\x00")

    def test_recording_sessions_updates_on_sst_and_stop(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst({"src": [{"id": 2}]})

        self.assertEqual(len(bridge._recording_sessions), 2)
        self.assertTrue(any("Source 2 [sp]" in item for item in bridge._recording_sessions))
        self.assertTrue(any("Source 2 [pf]" in item for item in bridge._recording_sessions))

        bridge.stopStreams()

        self.assertEqual(bridge._recording_sessions, [])

    def test_toggle_remote_odas_connects_then_starts(self) -> None:
        bridge = self._make_bridge()

        bridge.toggleRemoteOdas()

        self.assertTrue(bridge.remoteConnected)
        self.assertTrue(bridge.odasRunning)
        self.assertTrue(bridge.streamsActive)
        self.assertEqual(bridge._remote.connect_calls, 1)
        self.assertEqual(bridge._remote.start_calls, 1)
        self.assertEqual(bridge._client.start_calls, 1)
        self.assertEqual(bridge._recorder.sample_rates, {"sp": 16000, "pf": 16000})

    def test_remote_start_applies_detected_recording_sample_rates(self) -> None:
        bridge = self._make_bridge()
        remote = bridge._remote
        self.assertIsInstance(remote, _FakeRemote)
        remote.sample_rates = {"sp": 48000, "pf": 44100}

        bridge.toggleRemoteOdas()

        recorder = bridge._recorder
        self.assertIsInstance(recorder, _FakeRecorder)
        self.assertEqual(recorder.sample_rates, {"sp": 48000, "pf": 44100})

    def test_remote_start_with_sample_rate_warning_publishes_log_notice(self) -> None:
        bridge = self._make_bridge()
        remote = bridge._remote
        self.assertIsInstance(remote, _FakeRemote)
        remote.sample_rate_warning = "录音采样率自动识别失败，已回退 16000Hz"

        bridge.toggleRemoteOdas()

        self.assertIn("回退 16000Hz", "\n".join(bridge._remote_log_lines))

    def test_toggle_remote_odas_stops_remote_only(self) -> None:
        bridge = self._make_bridge()
        bridge.toggleRemoteOdas()

        bridge.toggleRemoteOdas()

        self.assertFalse(bridge.odasRunning)
        self.assertTrue(bridge.streamsActive)
        self.assertEqual(bridge._remote.stop_calls, 1)
        self.assertEqual(bridge._client.stop_calls, 0)
        self.assertIn("监听", bridge._status)

    def test_toggle_streams_is_independent_from_control_channel(self) -> None:
        bridge = self._make_bridge()

        bridge.toggleStreams()
        self.assertTrue(bridge.streamsActive)
        self.assertEqual(bridge._client.start_calls, 1)
        self.assertTrue(bridge.canToggleStreams)
        self.assertIn("正在监听", bridge._status)

        bridge._remote.connected = False
        bridge._refresh_remote_connection_state()
        self.assertTrue(bridge.canToggleStreams)

    def test_sst_over_capacity_limits_recording_to_mapped_sources(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst({"src": [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]})

        self.assertEqual(len(bridge._source_channel_map), 4)
        self.assertEqual(bridge.recordingSourceCount, 4)
        self.assertFalse(any("Source 5" in item for item in bridge._recording_sessions))

    def test_sst_refreshes_runtime_chart_series(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst(
            {
                "src": [
                    {"id": 2, "x": 1.0, "y": 0.0, "z": 0.0},
                    {"id": 5, "x": 0.0, "y": 1.0, "z": 0.0},
                ]
            }
        )

        self.assertEqual(bridge.elevationSeriesModel.count, 2)
        self.assertEqual(bridge.azimuthSeriesModel.count, 2)

        elevation_first = json.loads(bridge.elevationSeriesModel.get(0)["valuesJson"])
        azimuth_first = json.loads(bridge.azimuthSeriesModel.get(0)["valuesJson"])
        azimuth_second = json.loads(bridge.azimuthSeriesModel.get(1)["valuesJson"])

        self.assertEqual(elevation_first, [0.5])
        self.assertEqual(azimuth_first, [0.5])
        self.assertEqual(azimuth_second, [0.75])
        row_colors = {
            bridge.sourceRowsModel.get(index)["badgeColor"]
            for index in range(bridge.sourceRowsModel.count)
        }
        self.assertGreater(len(row_colors), 1)
        self.assertEqual(
            [
                bridge.sourceRowsModel.get(index)["badgeColor"]
                for index in range(bridge.sourceRowsModel.count)
            ],
            [SOURCE_COLOR_PALETTE[0], SOURCE_COLOR_PALETTE[1]],
        )

    def test_unchecked_last_source_keeps_rows_but_clears_runtime_chart_and_positions(self) -> None:
        bridge = self._make_bridge()
        bridge._on_sst(
            {
                "src": [
                    {"id": 2, "x": 1.0, "y": 0.0, "z": 0.0},
                    {"id": 5, "x": 0.0, "y": 1.0, "z": 0.0},
                ]
            }
        )

        bridge.setSourceSelected(2, False)
        self.assertEqual(bridge.elevationSeriesModel.count, 1)
        self.assertEqual(bridge.azimuthSeriesModel.count, 1)
        self.assertEqual(bridge.sourcePositionsModel.count, 1)
        self.assertEqual(bridge.elevationSeriesModel.get(0)["sourceId"], 5)

        bridge.setSourceSelected(5, False)

        self.assertEqual(bridge.sourceRowsModel.count, 2)
        self.assertEqual(bridge.sourcePositionsModel.count, 0)
        self.assertEqual(bridge.elevationSeriesModel.count, 0)
        self.assertEqual(bridge.azimuthSeriesModel.count, 0)

    def test_runtime_chart_window_rolls_with_zero_based_time_and_latest_tick(self) -> None:
        bridge = self._make_bridge()

        for index in range(12):
            bridge._on_sst(
                {
                    "timeStamp": 1000 + index * 16,
                    "src": [{"id": 2, "x": 1.0, "y": 0.0, "z": 0.0}],
                }
            )

        ticks = [
            bridge.chartXTicksModel.get(i)["value"] for i in range(bridge.chartXTicksModel.count)
        ]
        self.assertEqual(
            ticks,
            ["0", "200", "400", "600", "800", "1000", "1200", "1400", "1600", "176"],
        )
        values = json.loads(bridge.elevationSeriesModel.get(0)["valuesJson"])
        self.assertEqual(len(values), 10)

    def test_runtime_chart_timestamp_rollback_resets_origin(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst({"timeStamp": 1000, "src": [{"id": 2, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge._on_sst({"timeStamp": 1016, "src": [{"id": 2, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge._on_sst({"timeStamp": 900, "src": [{"id": 5, "x": 1.0, "y": 0.0, "z": 0.0}]})

        self.assertEqual(len(bridge._runtime_chart_frames), 1)
        self.assertEqual(bridge._runtime_chart_frames[0]["sample"], 0)
        self.assertEqual(bridge._runtime_chart_time_origin, 900)
        ticks = [
            bridge.chartXTicksModel.get(i)["value"] for i in range(bridge.chartXTicksModel.count)
        ]
        self.assertEqual(ticks[-1], "0")
        self.assertEqual(bridge.sourceRowsModel.get(0)["sourceId"], 5)
        self.assertEqual(bridge.sourceRowsModel.get(0)["badgeColor"], SOURCE_COLOR_PALETTE[1])

    def test_stop_streams_clears_runtime_chart_clock_and_window(self) -> None:
        bridge = self._make_bridge()
        bridge._on_sst(
            {
                "timeStamp": 1000,
                "src": [
                    {"id": 2, "x": 1.0, "y": 0.0, "z": 0.0},
                    {"id": 5, "x": 0.0, "y": 1.0, "z": 0.0},
                ],
            }
        )
        bridge._on_sst({"timeStamp": 1016, "src": [{"id": 2, "x": 1.0, "y": 0.0, "z": 0.0}]})
        self.assertEqual(bridge.sourceRowsModel.get(0)["badgeColor"], SOURCE_COLOR_PALETTE[0])

        bridge.stopStreams()

        self.assertEqual(bridge._runtime_chart_frames, [])
        self.assertIsNone(bridge._runtime_chart_time_origin)
        self.assertIsNone(bridge._runtime_chart_last_timestamp)
        ticks = [
            bridge.chartXTicksModel.get(i)["value"] for i in range(bridge.chartXTicksModel.count)
        ]
        self.assertEqual(
            ticks, ["0", "200", "400", "600", "800", "1000", "1200", "1400", "1600", "1800"]
        )
        self.assertEqual(bridge.elevationSeriesModel.count, 0)
        self.assertEqual(bridge.azimuthSeriesModel.count, 0)

        bridge._on_sst({"timeStamp": 2000, "src": [{"id": 99, "x": 1.0, "y": 0.0, "z": 0.0}]})
        self.assertEqual(bridge.sourceRowsModel.get(0)["sourceId"], 99)
        self.assertEqual(bridge.sourceRowsModel.get(0)["badgeColor"], SOURCE_COLOR_PALETTE[0])

    def test_runtime_chart_tick_fallback_is_monotonic_without_timestamp(self) -> None:
        bridge = self._make_bridge()

        for _ in range(3):
            bridge._on_sst({"src": [{"id": 2, "x": 1.0, "y": 0.0, "z": 0.0}]})

        ticks = [
            bridge.chartXTicksModel.get(i)["value"] for i in range(bridge.chartXTicksModel.count)
        ]
        self.assertEqual(ticks[:3], ["0", "200", "400"])


if __name__ == "__main__":
    unittest.main()
