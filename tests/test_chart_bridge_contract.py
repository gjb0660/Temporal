import queue
import os
import re
import threading
import time
import unittest
from math import cos, radians, sin
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtQml import QQmlComponent, QQmlEngine

from temporal.app.bridge import AppBridge
from temporal.app.fake_runtime import fake_app_bridge
from temporal.core.chart_window import build_chart_window_model
from temporal.preview_bridge import PreviewBridge
from temporal.preview_data import get_preview_scenario

_REPO_ROOT = Path(__file__).resolve().parents[1]
_QML_DIR = _REPO_ROOT / "src" / "temporal" / "qml"


def _ensure_app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is not None:
        return cast(QGuiApplication, app)
    return QGuiApplication([])


def _model_items(model) -> list[dict[str, Any]]:
    return [model.get(index) for index in range(model.count)]


class TestChartBridgeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = _ensure_app()

    def _make_runtime_bridge(self) -> AppBridge:
        return fake_app_bridge()

    def test_runtime_bridge_exposes_new_chart_models(self) -> None:
        bridge = self._make_runtime_bridge()

        bridge._on_sst({"timeStamp": 0, "src": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]})

        self.assertTrue(hasattr(bridge, "chartWindowModel"))
        self.assertTrue(hasattr(bridge, "elevationChartSeriesModel"))
        self.assertTrue(hasattr(bridge, "azimuthChartSeriesModel"))
        self.assertTrue(hasattr(bridge, "potentialPositionsModel"))
        self.assertEqual(
            [item["value"] for item in _model_items(bridge.chartWindowModel)],
            [tick["value"] for tick in build_chart_window_model([{"timeStamp": 0}])["ticks"]],
        )
        elevation_series = _model_items(bridge.elevationChartSeriesModel)
        azimuth_series = _model_items(bridge.azimuthChartSeriesModel)
        self.assertGreaterEqual(len(elevation_series), 1)
        self.assertGreaterEqual(len(azimuth_series), 1)
        self.assertIn("points", elevation_series[0])
        self.assertIn("layer", elevation_series[0])
        self.assertIn("showLine", elevation_series[0])
        self.assertIn("pointRadius", elevation_series[0])
        self.assertNotIn("values", elevation_series[0])
        self.assertEqual(elevation_series[0]["points"][0]["x"], 0)
        self.assertEqual(azimuth_series[0]["points"][0]["x"], 0)
        self.assertFalse(hasattr(bridge, "chartXTicksModel"))
        self.assertFalse(hasattr(bridge, "elevationSeriesModel"))
        self.assertFalse(hasattr(bridge, "azimuthSeriesModel"))

    def test_runtime_keeps_disappeared_source_rows_and_series_until_window_expires(self) -> None:
        bridge = self._make_runtime_bridge()

        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge._on_sst({"timeStamp": 19, "src": []})

        self.assertEqual(bridge.sourceRowsModel.count, 1)
        self.assertEqual(bridge.sourceRowsModel.get(0)["sourceId"], 7)
        self.assertFalse(bridge.sourceRowsModel.get(0)["active"])
        self.assertEqual(bridge.elevationChartSeriesModel.count, 1)
        points = bridge.elevationChartSeriesModel.get(0)["points"]
        self.assertEqual(len(points), 2)
        self.assertIsNone(points[-1]["y"])

        bridge._on_sst({"timeStamp": 1700, "src": []})

        self.assertEqual(bridge.sourceRowsModel.count, 0)
        self.assertEqual(bridge.elevationChartSeriesModel.count, 0)
        self.assertEqual(bridge.azimuthChartSeriesModel.count, 0)

    def test_sources_toggle_hides_visible_outputs_but_keeps_rows(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst(
            {
                "timeStamp": 0,
                "src": [
                    {"id": 7, "x": 1.0, "y": 0.0, "z": 0.0},
                    {"id": 15, "x": 0.0, "y": 1.0, "z": 0.0},
                ],
            }
        )

        bridge.setSourcesEnabled(False)

        self.assertEqual(bridge.sourceRowsModel.count, 2)
        self.assertEqual([bridge.sourceRowsModel.get(i)["sourceId"] for i in range(2)], [7, 15])
        self.assertEqual(bridge.sourcePositionsModel.count, 0)
        self.assertEqual(bridge.elevationChartSeriesModel.count, 0)
        self.assertEqual(bridge.azimuthChartSeriesModel.count, 0)

    def test_potential_overlay_respects_independent_source_and_potential_toggles(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge.setPotentialsEnabled(True)
        bridge._on_ssl({"timeStamp": 0, "src": [{"x": 0.0, "y": 1.0, "z": 0.0, "E": 0.9}]})

        self.assertEqual(bridge.sourcePositionsModel.count, 1)
        self.assertGreaterEqual(bridge.potentialPositionsModel.count, 1)
        baseline_layers = {item["layer"] for item in _model_items(bridge.elevationChartSeriesModel)}
        self.assertIn("tracked", baseline_layers)
        self.assertIn("potential", baseline_layers)

        bridge.setSourcesEnabled(False)

        self.assertEqual(bridge.sourcePositionsModel.count, 0)
        self.assertGreaterEqual(bridge.potentialPositionsModel.count, 1)
        layers_after_source_off = {
            item["layer"] for item in _model_items(bridge.elevationChartSeriesModel)
        }
        self.assertNotIn("tracked", layers_after_source_off)
        self.assertIn("potential", layers_after_source_off)

        bridge.setPotentialsEnabled(False)

        self.assertEqual(bridge.potentialPositionsModel.count, 0)
        layers_after_potential_off = {
            item["layer"] for item in _model_items(bridge.elevationChartSeriesModel)
        }
        self.assertNotIn("potential", layers_after_potential_off)

    def test_potential_energy_range_filters_only_potential_layer(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge.setPotentialsEnabled(True)
        bridge._on_ssl(
            {
                "timeStamp": 0,
                "src": [
                    {"x": 0.0, "y": 1.0, "z": 0.0, "E": 0.9},
                    {"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.4},
                ],
            }
        )
        self.assertEqual(bridge.sourcePositionsModel.count, 1)
        self.assertEqual(bridge.potentialPositionsModel.count, 2)

        bridge.setPotentialEnergyRange(0.8, 1.0)

        self.assertEqual(bridge.sourcePositionsModel.count, 1)
        self.assertEqual(bridge.potentialPositionsModel.count, 1)
        layers = {item["layer"] for item in _model_items(bridge.elevationChartSeriesModel)}
        self.assertIn("tracked", layers)
        self.assertIn("potential", layers)

    def test_potential_overlay_does_not_apply_hard_cap(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge.setPotentialsEnabled(True)
        potentials = [
            {"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.5 + ((index % 11) / 100.0)}
            for index in range(200)
        ]
        bridge._on_ssl({"timeStamp": 0, "src": potentials})

        self.assertEqual(bridge.potentialPositionsModel.count, 200)
        potential_series = [
            item
            for item in _model_items(bridge.elevationChartSeriesModel)
            if item["layer"] == "potential"
        ]
        self.assertEqual(
            sum(len(item["points"]) for item in potential_series),
            200,
        )

    def test_potential_overlay_throttles_chart_points_by_ssl_stride(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge.setPotentialsEnabled(True)
        for sample in range(200):
            bridge._on_ssl(
                {"timeStamp": sample, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]}
            )

        potential_series = [
            item
            for item in _model_items(bridge.elevationChartSeriesModel)
            if item["layer"] == "potential"
        ]
        self.assertEqual(sum(len(item["points"]) for item in potential_series), 10)

    def test_potential_overlay_stride_keeps_window_alignment(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge.setPotentialsEnabled(True)
        for sample in range(2001):
            bridge._on_ssl(
                {"timeStamp": sample, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]}
            )

        potential_series = [
            item
            for item in _model_items(bridge.elevationChartSeriesModel)
            if item["layer"] == "potential"
        ]
        all_points = [
            point
            for item in potential_series
            for point in item["points"]
            if isinstance(point, dict)
        ]
        self.assertEqual(len(all_points), 81)
        self.assertEqual(min(float(point["x"]) for point in all_points), 400.0)
        self.assertEqual(max(float(point["x"]) for point in all_points), 2000.0)

    def test_potential_overlay_uses_odas_web_scatter_radius(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge.setPotentialsEnabled(True)
        bridge._on_ssl({"timeStamp": 0, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]})

        potential_series = [
            item
            for item in _model_items(bridge.elevationChartSeriesModel)
            if item["layer"] == "potential"
        ]
        self.assertGreaterEqual(len(potential_series), 1)
        self.assertEqual(float(potential_series[0]["pointRadius"]), 3.0)

    def test_potential_overlay_colors_are_qt_parseable(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge.setPotentialsEnabled(True)
        bridge._on_ssl(
            {
                "timeStamp": 0,
                "src": [
                    {"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88},
                    {"x": 0.0, "y": 1.0, "z": 0.0, "E": 0.52},
                ],
            }
        )

        for item in _model_items(bridge.potentialPositionsModel):
            self.assertTrue(QColor(str(item["color"])).isValid())

        potential_series = [
            item
            for item in _model_items(bridge.elevationChartSeriesModel)
            if item["layer"] == "potential"
        ]
        self.assertGreaterEqual(len(potential_series), 1)
        for item in potential_series:
            self.assertTrue(QColor(str(item["color"])).isValid())

    def test_runtime_inactive_history_row_keeps_stable_color(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        baseline_color = str(bridge.sourceRowsModel.get(0)["badgeColor"])

        bridge._on_sst({"timeStamp": 19, "src": []})
        bridge._on_sst({"timeStamp": 38, "src": []})

        self.assertEqual(bridge.sourceRowsModel.count, 1)
        self.assertEqual(bridge.sourceRowsModel.get(0)["sourceId"], 7)
        self.assertFalse(bridge.sourceRowsModel.get(0)["active"])
        self.assertEqual(str(bridge.sourceRowsModel.get(0)["badgeColor"]), baseline_color)

    def test_runtime_merges_source_id_drift_into_single_row_with_stable_color(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst(
            {
                "timeStamp": 0,
                "src": [
                    {"id": 7, "x": 1.0, "y": 0.0, "z": 0.0},
                    {"id": 15, "x": 0.0, "y": 1.0, "z": 0.0},
                ],
            }
        )
        color_7 = next(
            str(item["badgeColor"])
            for item in _model_items(bridge.sourceRowsModel)
            if int(item["sourceId"]) == 7
        )

        bridge._on_sst(
            {
                "timeStamp": 19,
                "src": [
                    {"id": 17, "x": 1.0, "y": 0.0, "z": 0.0},
                    {"id": 15, "x": 0.0, "y": 1.0, "z": 0.0},
                ],
            }
        )

        rows = _model_items(bridge.sourceRowsModel)
        self.assertEqual([int(item["sourceId"]) for item in rows], [15, 17])
        self.assertTrue(all(int(item["sourceId"]) != 7 for item in rows))
        color_17 = next(str(item["badgeColor"]) for item in rows if int(item["sourceId"]) == 17)
        self.assertEqual(color_17, color_7)

    def test_runtime_selection_follows_target_id_across_source_id_drift(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        target_id = int(bridge.sourceRowsModel.get(0)["targetId"])
        self.assertGreater(target_id, 0)

        bridge.setTargetSelected(target_id, False)
        bridge._on_sst({"timeStamp": 19, "src": [{"id": 17, "x": 1.0, "y": 0.0, "z": 0.0}]})

        row = next(
            item for item in _model_items(bridge.sourceRowsModel) if int(item["sourceId"]) == 17
        )
        self.assertEqual(int(row["targetId"]), target_id)
        self.assertFalse(bool(row["checked"]))

    def test_runtime_keeps_history_window_colors_unique_for_old_and_new_targets(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 3, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge._on_sst({"timeStamp": 220, "src": [{"id": 4, "x": 0.0, "y": 1.0, "z": 0.0}]})

        rows = _model_items(bridge.sourceRowsModel)
        self.assertEqual([int(item["sourceId"]) for item in rows], [3, 4])
        self.assertEqual(len({str(item["badgeColor"]) for item in rows}), len(rows))
        self.assertEqual([bool(item["active"]) for item in rows], [False, True])

    def test_runtime_active_flag_uses_target_identity_when_source_id_reused(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge._on_sst({"timeStamp": 220, "src": [{"id": 7, "x": 0.0, "y": 1.0, "z": 0.0}]})

        rows = _model_items(bridge.sourceRowsModel)
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(int(item["sourceId"]) == 7 for item in rows))
        self.assertEqual(sum(1 for item in rows if bool(item["active"])), 1)

    def test_runtime_history_rows_are_capped_to_palette_size_without_color_conflicts(self) -> None:
        bridge = self._make_runtime_bridge()
        for index in range(13):
            angle = radians(float(index * 30))
            bridge._on_sst(
                {
                    "timeStamp": index * 19,
                    "src": [
                        {
                            "id": index + 1,
                            "x": cos(angle),
                            "y": sin(angle),
                            "z": 0.0,
                        }
                    ],
                }
            )

        rows = _model_items(bridge.sourceRowsModel)
        self.assertEqual(len(rows), 12)
        self.assertNotIn(1, {int(item["sourceId"]) for item in rows})
        self.assertEqual(len({str(item["badgeColor"]) for item in rows}), 12)
        self.assertEqual(sum(1 for item in rows if bool(item["active"])), 1)

    def test_runtime_preview_parity_for_source_id_drift_and_color_stability(self) -> None:
        runtime = self._make_runtime_bridge()
        runtime._on_sst(
            {
                "timeStamp": 0,
                "src": [
                    {"id": 7, "x": 1.0, "y": 0.0, "z": 0.0},
                    {"id": 15, "x": 0.0, "y": 1.0, "z": 0.0},
                ],
            }
        )
        runtime._on_sst(
            {
                "timeStamp": 19,
                "src": [
                    {"id": 17, "x": 1.0, "y": 0.0, "z": 0.0},
                    {"id": 15, "x": 0.0, "y": 1.0, "z": 0.0},
                ],
            }
        )

        preview = PreviewBridge()
        preview._scenario = {
            "key": "idDriftParity",
            "displayName": "idDriftParity",
            "status": "Temporal 就绪",
            "remoteLogLines": ["等待连接远程 odaslive..."],
            "sources": [
                {"id": 7, "color": "#cf54ea", "energy": 0.9},
                {"id": 15, "color": "#4dc6d8", "energy": 0.9},
            ],
            "trackingFrames": [
                {
                    "sample": 0,
                    "sources": [
                        {"id": 7, "x": 1.0, "y": 0.0, "z": 0.0},
                        {"id": 15, "x": 0.0, "y": 1.0, "z": 0.0},
                    ],
                },
                {
                    "sample": 19,
                    "sources": [
                        {"id": 17, "x": 1.0, "y": 0.0, "z": 0.0},
                        {"id": 15, "x": 0.0, "y": 1.0, "z": 0.0},
                    ],
                },
            ],
        }
        preview._reset_selected_sources()
        preview._reset_preview_sample_window()
        preview.toggleStreams()
        preview.advancePreviewTick()

        runtime_rows = [
            (int(item["sourceId"]), str(item["badgeColor"]), bool(item["active"]))
            for item in _model_items(runtime.sourceRowsModel)
        ]
        preview_rows = [
            (int(item["sourceId"]), str(item["badgeColor"]), bool(item["active"]))
            for item in _model_items(preview.sourceRowsModel)
        ]
        self.assertEqual(runtime_rows, preview_rows)

    def test_runtime_preview_parity_for_history_window_color_uniqueness(self) -> None:
        runtime = self._make_runtime_bridge()
        runtime._on_sst({"timeStamp": 0, "src": [{"id": 3, "x": 1.0, "y": 0.0, "z": 0.0}]})
        runtime._on_sst({"timeStamp": 220, "src": [{"id": 4, "x": 0.0, "y": 1.0, "z": 0.0}]})

        preview = PreviewBridge()
        preview._scenario = {
            "key": "historyColorUniqueness",
            "displayName": "historyColorUniqueness",
            "status": "Temporal 就绪",
            "remoteLogLines": ["等待连接远程 odaslive..."],
            "sources": [
                {"id": 3, "color": "#cf54ea", "energy": 0.9},
                {"id": 4, "color": "#4dc6d8", "energy": 0.9},
            ],
            "trackingFrames": [
                {"sample": 0, "sources": [{"id": 3, "x": 1.0, "y": 0.0, "z": 0.0}]},
                {"sample": 220, "sources": [{"id": 4, "x": 0.0, "y": 1.0, "z": 0.0}]},
            ],
        }
        preview._reset_selected_sources()
        preview._reset_preview_sample_window()
        preview.toggleStreams()
        preview.advancePreviewTick()

        runtime_rows = [
            (int(item["sourceId"]), str(item["badgeColor"]), bool(item["active"]))
            for item in _model_items(runtime.sourceRowsModel)
        ]
        preview_rows = [
            (int(item["sourceId"]), str(item["badgeColor"]), bool(item["active"]))
            for item in _model_items(preview.sourceRowsModel)
        ]
        self.assertEqual(runtime_rows, preview_rows)
        self.assertEqual(len({row[1] for row in runtime_rows}), len(runtime_rows))

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

    def test_runtime_chart_commit_is_throttled_to_interval(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._set_streams_active(True)
        messages = [
            {"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]},
            {"timeStamp": 19, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]},
            {"timeStamp": 38, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]},
            {"timeStamp": 57, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]},
        ]
        with (
            patch("temporal.app.stream_projection.refresh_chart_models") as refresh_mock,
            patch(
                "temporal.app.stream_projection.monotonic",
                side_effect=[1.00, 1.00, 1.01, 1.01, 1.02, 1.02, 1.07, 1.07],
            ),
        ):
            for message in messages:
                bridge._on_sst(message)

        self.assertEqual(refresh_mock.call_count, 2)

    def test_ssl_ingress_queue_is_bounded_and_applies_backpressure(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge.setPotentialsEnabled(True)
        bridge._ssl_ingress_queue = queue.Queue(maxsize=1)
        bridge._set_ssl_ingress_accepting(True)
        done = threading.Event()

        def _producer() -> None:
            bridge._on_ssl({"timeStamp": 0, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]})
            bridge._on_ssl({"timeStamp": 1, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]})
            done.set()

        worker = threading.Thread(target=_producer, daemon=True)
        worker.start()
        time.sleep(0.15)

        self.assertLessEqual(bridge._ssl_ingress_queue.qsize(), 1)
        self.assertGreater(bridge._ssl_ingress_blocked_count, 0)
        self.assertFalse(done.is_set())

        bridge._drain_ssl_ingress_batch(flush_all=True)
        worker.join(timeout=1.0)
        self.assertFalse(worker.is_alive())
        bridge._set_ssl_ingress_accepting(False)

    def test_ssl_ingress_tick_batches_messages_before_projection(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge.setPotentialsEnabled(True)
        bridge._set_ssl_ingress_accepting(True)
        now = time.monotonic()
        for sample in range(5):
            bridge._ssl_ingress_queue.put(
                (
                    {"timeStamp": sample, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]},
                    now,
                )
            )

        with patch("temporal.app.stream_projection.on_ssl_batch") as batch_mock:
            bridge._on_ssl_ingress_timeout()

        self.assertEqual(batch_mock.call_count, 1)
        self.assertEqual(len(batch_mock.call_args.args[1]), 5)
        self.assertEqual(bridge._ssl_ingress_queue.qsize(), 0)
        bridge._set_ssl_ingress_accepting(False)

    def test_ssl_ingress_backpressure_path_keeps_full_frame_sequence(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge.setPotentialsEnabled(True)
        bridge._ssl_ingress_queue = queue.Queue(maxsize=8)
        bridge._set_ssl_ingress_accepting(True)
        frame_total = 200

        def _producer() -> None:
            for sample in range(frame_total):
                bridge._on_ssl(
                    {"timeStamp": sample, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]}
                )

        worker = threading.Thread(target=_producer, daemon=True)
        worker.start()
        while worker.is_alive():
            bridge._drain_ssl_ingress_batch()
            time.sleep(0.001)
        bridge._drain_ssl_ingress_batch(flush_all=True)

        self.assertEqual(bridge._runtime_last_ssl_sample, frame_total - 1)
        bridge._set_ssl_ingress_accepting(False)

    def test_ssl_chart_commit_uses_dirty_gate_and_interval_throttle(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge.setPotentialsEnabled(True)
        bridge._set_streams_active(True)
        bridge._chart_next_commit_at = 0.0
        with (
            patch("temporal.app.stream_projection.refresh_chart_models") as refresh_mock,
            patch("temporal.app.stream_projection.monotonic", side_effect=[1.00, 1.01, 1.02]),
        ):
            for sample in range(60):
                bridge._on_ssl(
                    {"timeStamp": sample, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]}
                )

        self.assertEqual(refresh_mock.call_count, 0)
        self.assertTrue(bridge._chart_commit_dirty)

    def test_potential_trail_keeps_only_latest_50_samples(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge.setPotentialsEnabled(True)
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        for sample in range(200):
            bridge._on_ssl(
                {
                    "timeStamp": sample,
                    "src": [
                        {"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88},
                        {"x": 0.0, "y": 1.0, "z": 0.0, "E": 0.66},
                    ],
                }
            )

        items = _model_items(bridge.potentialPositionsModel)
        self.assertEqual(len(items), 100)
        samples = [int(item["sample"]) for item in items]
        self.assertEqual(min(samples), 150)
        self.assertEqual(max(samples), 199)

    def test_runtime_and_preview_chart_models_match_for_same_frame(self) -> None:
        runtime = self._make_runtime_bridge()
        runtime._on_sst({"timeStamp": 0, "src": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]})

        preview = PreviewBridge()
        preview._scenario = {
            "key": "parity",
            "displayName": "Parity",
            "status": "Temporal 就绪",
            "remoteLogLines": ["等待连接远程 odaslive..."],
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

    def test_runtime_preview_parity_for_potential_overlay(self) -> None:
        runtime = self._make_runtime_bridge()
        runtime._on_sst({"timeStamp": 0, "src": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]})
        runtime.setPotentialsEnabled(True)
        runtime._on_ssl({"timeStamp": 0, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]})

        preview = PreviewBridge()
        preview._scenario = {
            "key": "potentialParity",
            "displayName": "PotentialParity",
            "status": "Temporal 就绪",
            "remoteLogLines": ["等待连接远程 odaslive..."],
            "sources": [{"id": 15, "color": "#cf54ea", "energy": 0.88}],
            "trackingFrames": [
                {"sample": 0, "sources": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]}
            ],
        }
        preview._reset_selected_sources()
        preview._reset_preview_sample_window()
        preview.setPotentialsEnabled(True)
        preview._refresh_preview_models(reset_chart=True)

        self.assertEqual(
            _model_items(runtime.potentialPositionsModel),
            _model_items(preview.potentialPositionsModel),
        )
        runtime_potential = [
            item
            for item in _model_items(runtime.elevationChartSeriesModel)
            if item["layer"] == "potential"
        ]
        preview_potential = [
            item
            for item in _model_items(preview.elevationChartSeriesModel)
            if item["layer"] == "potential"
        ]
        self.assertEqual(runtime_potential, preview_potential)

    def test_runtime_preview_parity_for_potential_stride_sampling(self) -> None:
        runtime = self._make_runtime_bridge()
        runtime._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        runtime.setPotentialsEnabled(True)

        preview = PreviewBridge()
        preview._reset_runtime_chart_clock()
        preview._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        preview.setPotentialsEnabled(True)

        for sample in range(40):
            message = {
                "timeStamp": sample,
                "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}],
            }
            runtime._on_ssl(message)
            preview._on_ssl(message)

        runtime_potential = [
            item
            for item in _model_items(runtime.elevationChartSeriesModel)
            if item["layer"] == "potential"
        ]
        preview_potential = [
            item
            for item in _model_items(preview.elevationChartSeriesModel)
            if item["layer"] == "potential"
        ]
        self.assertEqual(runtime_potential, preview_potential)
        self.assertEqual(sum(len(item["points"]) for item in runtime_potential), 2)

    def test_preview_scenarios_do_not_expose_sample_window_field(self) -> None:
        scenario = get_preview_scenario("referenceSingle")

        self.assertNotIn("sampleWindow", scenario)

    def test_chart_canvas_qml_does_not_parse_json_contract(self) -> None:
        qml_text = (_QML_DIR / "ChartCanvas.qml").read_text(encoding="utf-8")

        self.assertNotIn("valuesJson", qml_text)
        self.assertNotIn("JSON.parse", qml_text)
        self.assertNotIn("item.values", qml_text)

    def test_chart_canvas_supports_mixed_line_and_scatter_series(self) -> None:
        qml_text = (_QML_DIR / "ChartCanvas.qml").read_text(encoding="utf-8")

        self.assertIn("item.showLine", qml_text)
        self.assertIn("item.pointRadius", qml_text)
        self.assertIn("drawScatter", qml_text)
        self.assertIn("function schedulePaint()", qml_text)
        self.assertIn("Qt.callLater", qml_text)
        self.assertIn("onWidthChanged: schedulePaint()", qml_text)

    def test_source_sphere_potential_marker_scale_matches_odas_ratio(self) -> None:
        qml_text = (_QML_DIR / "SourceSphereView.qml").read_text(encoding="utf-8")

        self.assertIn("potentialMarkerScale: sourceMarkerScale * 0.625", qml_text)

    def test_source_sphere_potential_marker_is_opaque(self) -> None:
        qml_text = (_QML_DIR / "SourceSphereView.qml").read_text(encoding="utf-8")

        self.assertIn("model: root.visiblePotentials", qml_text)
        self.assertIn("opacity: 1.0", qml_text)
        self.assertNotIn("potentialBaseOpacity", qml_text)
        self.assertNotIn("potentialExtraOpacity", qml_text)

    def test_source_sphere_renders_potentials_below_tracked_sources(self) -> None:
        qml_text = (_QML_DIR / "SourceSphereView.qml").read_text(encoding="utf-8")

        potential_index = qml_text.index("model: root.visiblePotentials")
        source_index = qml_text.index("model: root.visibleSources")
        self.assertLess(potential_index, source_index)

    def test_source_sphere_potential_uses_square_marker_with_rotation_compensation(self) -> None:
        qml_text = (_QML_DIR / "SourceSphereView.qml").read_text(encoding="utf-8")

        self.assertRegex(
            qml_text,
            re.compile(
                r"model:\s*root\.visiblePotentials[\s\S]*?"
                r"eulerRotation:\s*Qt\.vector3d\(0,\s*-root\.sphereYaw,\s*0\)[\s\S]*?"
                r"eulerRotation:\s*Qt\.vector3d\(-root\.spherePitch,\s*0,\s*0\)[\s\S]*?"
                r'source:\s*"#Rectangle"',
            ),
        )

    def test_source_sphere_axis_overlay_repaint_only_on_pose_changes(self) -> None:
        qml_text = (_QML_DIR / "SourceSphereView.qml").read_text(encoding="utf-8")

        self.assertNotIn("onVisibleSourcesChanged: axisOverlay.requestPaint()", qml_text)
        self.assertNotIn("onVisiblePotentialsChanged: axisOverlay.requestPaint()", qml_text)
        self.assertNotIn(
            "onModelReset() {\n            root.sourceModelRevision += 1\n            axisOverlay.requestPaint()",
            qml_text,
        )
        self.assertNotIn(
            "onModelReset() {\n            root.potentialModelRevision += 1\n            axisOverlay.requestPaint()",
            qml_text,
        )

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
        self.assertIn("potentialPositionsModel", qml_text)
        self.assertNotIn("chartXTicksModel", qml_text)
        self.assertNotIn("elevationSeriesModel", qml_text)
        self.assertNotIn("azimuthSeriesModel", qml_text)


if __name__ == "__main__":
    unittest.main()
