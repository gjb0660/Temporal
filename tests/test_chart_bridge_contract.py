import os
import unittest
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

# pyright: reportMissingImports=false

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlComponent, QQmlEngine

from temporal.app import AppBridge
from temporal.core.chart_window import build_chart_window_model
from temporal.core.config_loader import TemporalConfig
from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig
from temporal.preview_bridge import PreviewBridge
from temporal.preview_data import get_preview_scenario


_REPO_ROOT = Path(__file__).resolve().parents[1]
_QML_DIR = _REPO_ROOT / "src" / "temporal" / "qml"


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


def _ensure_app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is not None:
        return cast(QGuiApplication, app)
    return QGuiApplication([])


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


def _model_items(model) -> list[dict[str, Any]]:
    return [model.get(index) for index in range(model.count)]


class TestChartBridgeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = _ensure_app()

    def _make_runtime_bridge(self) -> AppBridge:
        with (
            patch("temporal.app.load_config", return_value=_fake_config()),
            patch("temporal.app.OdasClient", _FakeClient),
            patch("temporal.app.RemoteOdasController", _FakeRemote),
            patch("temporal.app.AutoRecorder", _FakeRecorder),
        ):
            return AppBridge()

    def test_runtime_bridge_exposes_new_chart_models(self) -> None:
        bridge = self._make_runtime_bridge()

        bridge._on_sst({"timeStamp": 0, "src": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]})

        self.assertTrue(hasattr(bridge, "chartWindowModel"))
        self.assertTrue(hasattr(bridge, "elevationChartSeriesModel"))
        self.assertTrue(hasattr(bridge, "azimuthChartSeriesModel"))
        self.assertEqual(
            [item["value"] for item in _model_items(bridge.chartWindowModel)],
            [
                tick["value"]
                for tick in build_chart_window_model(bridge._runtime_chart_messages)["ticks"]
            ],
        )
        elevation_series = _model_items(bridge.elevationChartSeriesModel)
        azimuth_series = _model_items(bridge.azimuthChartSeriesModel)
        self.assertGreaterEqual(len(elevation_series), 1)
        self.assertGreaterEqual(len(azimuth_series), 1)
        self.assertIn("points", elevation_series[0])
        self.assertNotIn("values", elevation_series[0])
        self.assertEqual(elevation_series[0]["points"][0]["x"], 0)
        self.assertEqual(azimuth_series[0]["points"][0]["x"], 0)
        self.assertFalse(hasattr(bridge, "chartXTicksModel"))
        self.assertFalse(hasattr(bridge, "elevationSeriesModel"))
        self.assertFalse(hasattr(bridge, "azimuthSeriesModel"))

    def test_missing_timestamp_frame_is_ignored(self) -> None:
        bridge = self._make_runtime_bridge()
        baseline_window = _model_items(bridge.chartWindowModel)
        baseline_elevation = _model_items(bridge.elevationChartSeriesModel)
        baseline_azimuth = _model_items(bridge.azimuthChartSeriesModel)

        bridge._on_sst({"src": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]})

        self.assertEqual(_model_items(bridge.chartWindowModel), baseline_window)
        self.assertEqual(_model_items(bridge.elevationChartSeriesModel), baseline_elevation)
        self.assertEqual(_model_items(bridge.azimuthChartSeriesModel), baseline_azimuth)
        self.assertFalse(hasattr(bridge, "_runtime_chart_next_fallback_sample"))

    def test_runtime_and_preview_chart_models_match_for_same_frame(self) -> None:
        runtime = self._make_runtime_bridge()
        runtime._on_sst({"timeStamp": 0, "src": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]})

        preview = PreviewBridge()
        preview._scenario = {
            "key": "parity",
            "displayName": "Parity",
            "status": "Temporal 就绪",
            "remoteLogLines": ["等待连接远程 odaslive..."],
            "sampleWindow": {
                "advancePerTick": 1,
                "timerIntervalMs": 400,
            },
            "sources": [{"id": 15, "color": "#cf54ea", "energy": 0.88}],
            "trackingFrames": [
                {"sample": 0, "sources": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]}
            ],
        }
        preview._reset_selected_sources()
        preview._reset_preview_sample_window()
        preview._refresh_preview_models(reset_chart=True)

        self.assertEqual(
            _model_items(runtime.chartWindowModel),
            _model_items(preview.chartWindowModel),
        )
        self.assertEqual(
            _model_items(runtime.elevationChartSeriesModel),
            _model_items(preview.elevationChartSeriesModel),
        )
        self.assertEqual(
            _model_items(runtime.azimuthChartSeriesModel),
            _model_items(preview.azimuthChartSeriesModel),
        )

    def test_preview_sample_window_does_not_change_chart_semantics(self) -> None:
        preview = PreviewBridge()
        preview._scenario = {
            "key": "window",
            "displayName": "Window",
            "status": "Temporal 就绪",
            "remoteLogLines": ["等待连接远程 odaslive..."],
            "sampleWindow": {
                "advancePerTick": 1,
                "timerIntervalMs": 400,
            },
            "sources": [{"id": 15, "color": "#cf54ea", "energy": 0.88}],
            "trackingFrames": [
                {"sample": 0, "sources": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]}
            ],
        }
        preview._reset_selected_sources()
        preview._reset_preview_sample_window()
        preview._refresh_preview_models(reset_chart=True)
        baseline_window = _model_items(preview.chartWindowModel)
        baseline_elevation = _model_items(preview.elevationChartSeriesModel)
        baseline_azimuth = _model_items(preview.azimuthChartSeriesModel)

        preview._scenario["sampleWindow"] = {
            "advancePerTick": 3,
            "timerIntervalMs": 250,
        }
        preview._reset_preview_sample_window()
        preview._refresh_preview_models(reset_chart=True)

        self.assertEqual(_model_items(preview.chartWindowModel), baseline_window)
        self.assertEqual(_model_items(preview.elevationChartSeriesModel), baseline_elevation)
        self.assertEqual(_model_items(preview.azimuthChartSeriesModel), baseline_azimuth)

    def test_preview_scenarios_expose_only_clock_sample_window_fields(self) -> None:
        scenario = get_preview_scenario("referenceSingle")

        self.assertEqual(
            scenario["sampleWindow"],
            {
                "advancePerTick": 2,
                "timerIntervalMs": 400,
            },
        )

    def test_chart_canvas_qml_does_not_parse_json_contract(self) -> None:
        qml_text = (_QML_DIR / "ChartCanvas.qml").read_text(encoding="utf-8")

        self.assertNotIn("valuesJson", qml_text)
        self.assertNotIn("JSON.parse", qml_text)

    def test_chart_canvas_handles_array_like_points_from_qml_model(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]})

        engine = QQmlEngine()
        engine.rootContext().setContextProperty("bridge", bridge)
        component = QQmlComponent(engine)
        component.setData(
            b"""
import QtQuick
import "."

Item {
    QtObject {
        id: theme
        property color accentPurple: "#cf54ea"
    }

    ChartCanvas {
        id: chart
        width: 320
        height: 140
        theme: theme
        yTicks: ["90", "60", "30", "0", "-30", "-60", "-90"]
        xTickModel: bridge.chartWindowModel
        seriesModel: bridge.elevationChartSeriesModel
    }

    property int normalizedSeriesCount: chart.normalizedSeries().length
}
""",
            QUrl.fromLocalFile(str(_QML_DIR / "ChartCanvasProbe.qml")),
        )
        obj = component.create()

        self.assertFalse(component.isError(), [error.toString() for error in component.errors()])
        self.assertGreaterEqual(obj.property("normalizedSeriesCount"), 1)
        obj.deleteLater()
        engine.deleteLater()
        self._app.processEvents()

    def test_center_pane_binds_new_chart_models(self) -> None:
        qml_text = (_QML_DIR / "CenterPane.qml").read_text(encoding="utf-8")

        self.assertIn("chartWindowModel", qml_text)
        self.assertIn("elevationChartSeriesModel", qml_text)
        self.assertIn("azimuthChartSeriesModel", qml_text)
        self.assertNotIn("chartXTicksModel", qml_text)
        self.assertNotIn("elevationSeriesModel", qml_text)
        self.assertNotIn("azimuthSeriesModel", qml_text)


if __name__ == "__main__":
    unittest.main()
