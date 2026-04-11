from chart_bridge_contract_support import (
    ChartBridgeContractBase,
    QQmlComponent,
    QQmlEngine,
    QUrl,
    _QML_DIR,
    get_preview_scenario,
)


class TestChartBridgeQmlContract(ChartBridgeContractBase):
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
