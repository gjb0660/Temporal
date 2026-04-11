from chart_bridge_contract_support import (
    ChartBridgeContractBase,
    QColor,
    _QML_DIR,
    _model_items,
    re,
)


class TestChartBridgePotential(ChartBridgeContractBase):
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
