from chart_bridge_contract_support import (
    ChartBridgeContractBase,
    PreviewBridge,
    _model_items,
)


class TestChartBridgeParity(ChartBridgeContractBase):
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
