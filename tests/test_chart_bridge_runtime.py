from chart_bridge_contract_support import (
    ChartBridgeContractBase,
    _model_items,
    build_chart_window_model,
    cos,
    radians,
    sin,
)


class TestChartBridgeRuntime(ChartBridgeContractBase):
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
