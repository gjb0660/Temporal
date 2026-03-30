import json
import unittest
from unittest.mock import patch

from temporal.app import AppBridge
from temporal.core.config_loader import TemporalConfig
from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig
from temporal.preview_bridge import PreviewBridge


class _FakeRecorder:
    def __init__(self, _output_dir) -> None:
        pass

    def stop_all(self) -> None:
        return

    def sessions_snapshot(self):
        return []

    def update_active_sources(self, _source_ids) -> None:
        return

    def sweep_inactive(self):
        return []

    def active_sources(self) -> set[int]:
        return set()

    def push(self, _source_id: int, _mode: str, _pcm_chunk: bytes) -> None:
        return


class _FakeClient:
    def __init__(self, **_kwargs) -> None:
        pass

    def start(self) -> None:
        return

    def stop(self) -> None:
        return


class _FakeRemote:
    def __init__(self, _config, _streams) -> None:
        pass


def _fake_config() -> TemporalConfig:
    remote = RemoteOdasConfig(
        host="127.0.0.1",
        port=22,
        username="odas",
        private_key="~/.ssh/id_rsa",
        odas_args=["-c", "/opt/odas/config/odas.cfg"],
        odas_log="/tmp/odaslive.log",
    )
    streams = OdasStreamConfig(
        sst=OdasEndpoint(host="127.0.0.1", port=9000),
        ssl=OdasEndpoint(host="127.0.0.1", port=9001),
        sss_sep=OdasEndpoint(host="127.0.0.1", port=10000),
        sss_pf=OdasEndpoint(host="127.0.0.1", port=10010),
    )
    return TemporalConfig(remote=remote, streams=streams)


def _model_items(model) -> list[dict]:
    return [model.get(index) for index in range(model.count)]


def _series_values_by_source(model) -> dict[int, list[float]]:
    return {
        int(item["sourceId"]): json.loads(item["valuesJson"])
        for item in _model_items(model)
    }


class TestProjectionParity(unittest.TestCase):
    def _make_runtime_bridge(self) -> AppBridge:
        with (
            patch("temporal.app.load_config", return_value=_fake_config()),
            patch("temporal.app.OdasClient", _FakeClient),
            patch("temporal.app.RemoteOdasController", _FakeRemote),
            patch("temporal.app.AutoRecorder", _FakeRecorder),
        ):
            return AppBridge()

    def test_runtime_and_preview_share_projection_outputs_for_isomorphic_frame(self) -> None:
        preview = PreviewBridge()
        preview._scenario = {
            "key": "parity",
            "displayName": "Parity",
            "status": "Temporal 就绪",
            "remoteLogLines": ["等待连接远程 odaslive...", "当前场景：Parity"],
            "sampleWindow": {
                "sampleStart": 0,
                "sampleStep": 200,
                "windowSize": 1,
                "tickCount": 1,
                "tickStride": 1,
                "advancePerTick": 1,
                "timerIntervalMs": 400,
            },
            "sources": [{"id": 15, "color": "#cf54ea", "energy": 0.88}],
            "trackingFrames": [{"sample": 0, "sources": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]}],
        }
        preview._reset_selected_sources()
        preview._reset_preview_sample_window()
        preview._refresh_preview_models()

        runtime = self._make_runtime_bridge()
        runtime._runtime_chart_tick_count = 1
        runtime._runtime_chart_frames = []
        runtime._runtime_chart_next_fallback_sample = 0
        runtime._on_sst({"timeStamp": 1512, "src": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]})

        self.assertEqual(
            [item["sourceId"] for item in _model_items(runtime.sourceRowsModel)],
            [item["sourceId"] for item in _model_items(preview.sourceRowsModel)],
        )
        self.assertEqual(
            [item["id"] for item in _model_items(runtime.sourcePositionsModel)],
            [item["id"] for item in _model_items(preview.sourcePositionsModel)],
        )
        self.assertEqual(
            [item["value"] for item in _model_items(runtime.chartXTicksModel)],
            [item["value"] for item in _model_items(preview.chartXTicksModel)],
        )
        self.assertEqual(
            _series_values_by_source(runtime.elevationSeriesModel),
            _series_values_by_source(preview.elevationSeriesModel),
        )
        self.assertEqual(
            _series_values_by_source(runtime.azimuthSeriesModel),
            _series_values_by_source(preview.azimuthSeriesModel),
        )


if __name__ == "__main__":
    unittest.main()
