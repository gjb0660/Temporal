from preview_bridge_support import (
    PreviewBridge,
    PreviewBridgeQtBase,
    QQmlComponent,
    QQmlEngine,
    QUrl,
    _QML_DIR,
    os,
)


class TestPreviewQmlContract(PreviewBridgeQtBase):
    def test_qml_can_read_preview_models_and_remote_log_text(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")
        engine = QQmlEngine()
        engine.rootContext().setContextProperty("bridge", bridge)
        component = QQmlComponent(engine)
        component.setData(
            b"""
import QtQuick
QtObject {
    property int rowCount: bridge.sourceRowsModel.count
    property int pointCount: bridge.sourcePositionsModel.count
    property int optionCount: bridge.previewScenarioOptionsModel.count
    property string firstBadge: bridge.sourceRowsModel.get(0).badge
    property int firstPointId: bridge.sourcePositionsModel.get(0).id
    property bool hasRemoteLog: bridge.remoteLogText.length > 0
    property bool odasStartingDefaultFalse: bridge.odasStarting === false
    property string controlSummary: bridge.controlSummary
    property string controlDataState: bridge.controlDataState
}
""",
            QUrl(),
        )
        obj = component.create()

        self.assertFalse(component.isError(), [error.toString() for error in component.errors()])
        self.assertEqual(obj.property("rowCount"), 4)
        self.assertEqual(obj.property("pointCount"), 4)
        self.assertEqual(obj.property("optionCount"), 4)
        self.assertEqual(obj.property("firstBadge"), "7")
        self.assertEqual(obj.property("firstPointId"), 7)
        self.assertTrue(obj.property("hasRemoteLog"))
        self.assertTrue(obj.property("odasStartingDefaultFalse"))
        self.assertIn("Temporal 就绪", obj.property("controlSummary"))
        self.assertEqual(obj.property("controlDataState"), "inactive")
        obj.deleteLater()
        engine.deleteLater()
        self._app.processEvents()


class TestSourceSphereViewContract(PreviewBridgeQtBase):
    def test_source_sphere_exposes_equator_radius_drag_and_mapping_contract(self) -> None:
        engine = QQmlEngine()
        component = QQmlComponent(engine)
        component.setData(
            """
import QtQuick

Item {
    width: 420
    height: 260

    QtObject {
        id: theme
        property color accentPurple: "#cf54ea"
        property color accentCyan: "#4dc6d8"
        property color axisOrange: "#ff7a29"
        property color axisGreen: "#35b56f"
        property color axisBlue: "#4168ff"
    }

    QtObject {
        id: positionsModel
        property int count: 1

        function get(index) {
            if (index !== 0) {
                return null
            }
            return {
                id: 7,
                x: 0.3,
                y: 0.4,
                z: 0.5,
                color: "#123456"
            }
        }
    }

    SourceSphereView {
        id: sphere
        anchors.fill: parent
        theme: theme
        sourcePositionsModel: positionsModel
    }

    property bool clipped: sphere.clip
    property real equatorRadius: sphere.equatorRadius
    property real coreChipSide: sphere.coreChipSide
    property real coreChipThickness: sphere.coreChipThickness
    property real latitudeGapA: sphere.latitudeAngles[1] - sphere.latitudeAngles[0]
    property real latitudeGapB: sphere.latitudeAngles[2] - sphere.latitudeAngles[1]
    property real meridianGapA: sphere.meridianAngles[1] - sphere.meridianAngles[0]
    property real meridianGapB: sphere.meridianAngles[2] - sphere.meridianAngles[1]
    property real normalizedX: sphere.visibleSources[0].x
    property real normalizedY: sphere.visibleSources[0].y
    property real normalizedZ: sphere.visibleSources[0].z
    property real mappedX: sphere.sourcePositionVector(sphere.visibleSources[0]).x
    property real mappedY: sphere.sourcePositionVector(sphere.visibleSources[0]).y
    property real mappedZ: sphere.sourcePositionVector(sphere.visibleSources[0]).z
    property real pitchAfterFront: sphere.previewPitchAfterDrag(0, 0, -10)
    property real pitchAfterBack: sphere.previewPitchAfterDrag(180, 0, -10)
}
""".encode(),
            QUrl.fromLocalFile(os.path.join(_QML_DIR, "SourceSphereViewContract.qml")),
        )
        obj = component.create()

        self.assertFalse(component.isError(), [error.toString() for error in component.errors()])
        self.assertTrue(obj.property("clipped"))
        self.assertEqual(obj.property("equatorRadius"), 150.0)
        self.assertEqual(obj.property("coreChipSide"), 60.0)
        self.assertEqual(obj.property("coreChipThickness"), 10.0)
        self.assertAlmostEqual(obj.property("latitudeGapA"), obj.property("latitudeGapB"), places=4)
        self.assertAlmostEqual(obj.property("meridianGapA"), obj.property("meridianGapB"), places=4)
        self.assertAlmostEqual(obj.property("normalizedX"), 0.3, places=4)
        self.assertAlmostEqual(obj.property("normalizedY"), 0.4, places=4)
        self.assertAlmostEqual(obj.property("normalizedZ"), 0.5, places=4)
        self.assertAlmostEqual(obj.property("mappedX"), 45.0, places=3)
        self.assertAlmostEqual(obj.property("mappedY"), 75.0, places=3)
        self.assertAlmostEqual(obj.property("mappedZ"), -60.0, places=3)
        self.assertLess(obj.property("pitchAfterFront"), 0.0)
        self.assertEqual(obj.property("pitchAfterFront"), obj.property("pitchAfterBack"))
        obj.deleteLater()
        engine.deleteLater()
        self._app.processEvents()
