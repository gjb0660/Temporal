import os
import sys
import unittest
from typing import Any, cast
from unittest.mock import patch

# pyright: reportMissingImports=false

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlComponent, QQmlEngine

from temporal.app import AppBridge
from temporal.core.config_loader import TemporalConfig
from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig
from temporal.main import preview_main
from temporal.preview_bridge import PreviewBridge
from temporal.preview_data import DEFAULT_PREVIEW_SCENARIO_KEY, PREVIEW_SCENARIO_KEYS


_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_QML_DIR = os.path.join(_REPO_ROOT, "src", "temporal", "qml")


def _ensure_app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is not None:
        return cast(QGuiApplication, app)
    return QGuiApplication([])


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


def _model_items(model) -> list[dict[str, Any]]:
    return [model.get(index) for index in range(model.count)]


def _scalar_values(model) -> list[Any]:
    return [item["value"] for item in _model_items(model)]


def _source_ids(bridge: PreviewBridge) -> list[int]:
    return cast(list[int], getattr(bridge, "sourceIds"))


class TestPreviewBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = _ensure_app()

    def test_defaults_to_preview_reference_single_with_static_first_frame(self) -> None:
        bridge = PreviewBridge()
        source_rows = _model_items(bridge.sourceRowsModel)
        source_positions = _model_items(bridge.sourcePositionsModel)

        self.assertTrue(bridge.previewMode)
        self.assertEqual(bridge.previewScenarioKey, DEFAULT_PREVIEW_SCENARIO_KEY)
        self.assertEqual(bridge.previewScenarioKeys, list(PREVIEW_SCENARIO_KEYS))
        self.assertFalse(bridge.odasStarting)
        self.assertEqual(len(source_rows), 1)
        self.assertEqual(source_rows[0]["sourceId"], 15)
        self.assertEqual(source_rows[0]["label"], "声源")
        self.assertTrue(source_rows[0]["checked"])
        self.assertEqual(_source_ids(bridge), [15])
        self.assertEqual(len(source_positions), 1)
        self.assertEqual(source_positions[0]["id"], 15)
        self.assertEqual(bridge.recordingSessionsModel.count, 0)
        self.assertEqual(bridge.status, "Temporal 就绪")
        self.assertEqual(bridge.remoteLogText, "等待连接远程 odaslive...\n当前场景：参考单点")
        self.assertTrue(bridge.showPreviewScenarioSelector)
        self.assertEqual(bridge.headerNavLabelsModel.count, 3)

    def test_scenarios_keep_models_in_sync(self) -> None:
        expectations = {
            "referenceSingle": 1,
            "hemisphereSpread": 4,
            "equatorBoundary": 4,
            "emptyState": 0,
        }
        bridge = PreviewBridge()

        for scenario_key, expected_count in expectations.items():
            bridge.setPreviewScenario(scenario_key)

            source_rows = _model_items(bridge.sourceRowsModel)
            source_positions = _model_items(bridge.sourcePositionsModel)

            self.assertEqual(len(source_rows), expected_count)
            self.assertEqual(len(_source_ids(bridge)), expected_count)
            self.assertEqual(len(source_positions), expected_count)
            self.assertEqual(
                {row["sourceId"] for row in source_rows if row["checked"]},
                set(_source_ids(bridge)),
            )
            self.assertEqual({item["id"] for item in source_positions}, set(_source_ids(bridge)))
            if expected_count > 1:
                self.assertGreater(
                    len({row["badgeColor"] for row in source_rows}),
                    1,
                )

    def test_preview_scenario_options_are_exposed_in_chinese(self) -> None:
        bridge = PreviewBridge()

        options = _model_items(bridge.previewScenarioOptionsModel)

        self.assertEqual([item["key"] for item in options], list(PREVIEW_SCENARIO_KEYS))
        self.assertEqual(options[0]["label"], "参考单点")
        self.assertEqual(options[-1]["label"], "空状态")

    def test_scenario_switch_resets_selection_and_state(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")
        bridge.toggleStreams()
        bridge.advancePreviewTick()
        bridge.setSourceSelected(7, False)

        self.assertTrue(any(item["sourceId"] == 7 for item in _model_items(bridge.sourceRowsModel)))
        self.assertFalse(
            any(
                item["sourceId"] == 7 and item["checked"]
                for item in _model_items(bridge.sourceRowsModel)
            )
        )

        bridge.setPreviewScenario("equatorBoundary")

        self.assertEqual(sorted(_source_ids(bridge)), [12, 15, 27, 31])
        self.assertTrue(all(row["checked"] for row in _model_items(bridge.sourceRowsModel)))
        self.assertEqual(bridge.remoteLogText, "等待连接远程 odaslive...\n当前场景：赤道边界")

    def test_unknown_preview_scenario_is_ignored(self) -> None:
        bridge = PreviewBridge()

        bridge.setPreviewScenario("missingScenario")

        self.assertEqual(bridge.previewScenarioKey, DEFAULT_PREVIEW_SCENARIO_KEY)

    def test_unchecked_last_source_keeps_rows_but_clears_visible_outputs(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")

        for source_id in [7, 15, 21, 31]:
            bridge.setSourceSelected(source_id, False)

        self.assertEqual(bridge.sourceRowsModel.count, 4)
        self.assertTrue(all(not item["checked"] for item in _model_items(bridge.sourceRowsModel)))
        self.assertEqual(_source_ids(bridge), [7, 15, 21, 31])
        self.assertEqual(bridge.sourcePositionsModel.count, 0)

    def test_empty_state_yields_no_fake_sources(self) -> None:
        bridge = PreviewBridge()

        bridge.setPreviewScenario("emptyState")

        self.assertEqual(bridge.sourceRowsModel.count, 0)
        self.assertEqual(_source_ids(bridge), [])
        self.assertEqual(bridge.sourcePositionsModel.count, 0)
        self.assertEqual(bridge.remoteLogText, "等待连接远程 odaslive...\n当前场景：空状态")

    def test_toggle_remote_auto_starts_streams_and_stop_clears_both(self) -> None:
        bridge = PreviewBridge()

        bridge.toggleRemoteOdas()

        self.assertTrue(bridge.remoteConnected)
        self.assertTrue(bridge.odasRunning)
        self.assertTrue(bridge.streamsActive)
        self.assertIn("正在监听 SST/SSL/SSS 数据流", str(bridge.status))

        bridge.toggleRemoteOdas()

        self.assertTrue(bridge.remoteConnected)
        self.assertFalse(bridge.odasRunning)
        self.assertTrue(bridge.streamsActive)
        self.assertIn("正在监听 SST/SSL/SSS 数据流", str(bridge.status))

    def test_toggle_streams_is_independent_and_restart_resets_positions(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")

        initial_positions = _model_items(bridge.sourcePositionsModel)

        bridge.toggleStreams()
        self.assertTrue(bridge.streamsActive)
        self.assertFalse(bridge.odasRunning)
        self.assertIn("正在监听 SST/SSL/SSS 数据流", str(bridge.status))

        bridge.advancePreviewTick()
        moved_positions = _model_items(bridge.sourcePositionsModel)

        self.assertNotEqual(moved_positions, initial_positions)

        bridge.toggleStreams()
        self.assertFalse(bridge.streamsActive)
        self.assertEqual(bridge.status, "SSH 已连接，远程 odaslive 未运行")

        bridge.toggleStreams()
        self.assertEqual(_model_items(bridge.sourcePositionsModel), initial_positions)

    def test_advance_preview_tick_updates_positions(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")
        bridge.toggleStreams()

        before_positions = _model_items(bridge.sourcePositionsModel)

        bridge.advancePreviewTick()

        self.assertNotEqual(_model_items(bridge.sourcePositionsModel), before_positions)

    def test_global_filters_update_sidebar_and_visible_outputs(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")

        bridge.setSourcesEnabled(False)

        self.assertFalse(bridge.sourcesEnabled)
        self.assertEqual(bridge.sourceRowsModel.count, 0)
        self.assertEqual(bridge.sourcePositionsModel.count, 0)

        bridge.setSourcesEnabled(True)
        bridge.setPotentialsEnabled(True)
        bridge.setPotentialEnergyRange(0.8, 1.0)

        self.assertTrue(bridge.potentialsEnabled)
        self.assertEqual(bridge.potentialEnergyMin, 0.8)
        self.assertEqual(bridge.potentialEnergyMax, 1.0)
        self.assertEqual(
            [item["sourceId"] for item in _model_items(bridge.sourceRowsModel)], [7, 15, 21, 31]
        )
        self.assertEqual(_source_ids(bridge), [7, 15, 21, 31])


class TestPreviewQmlContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = _ensure_app()

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
        obj.deleteLater()
        engine.deleteLater()
        self._app.processEvents()


class TestSourceSphereViewContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = _ensure_app()

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


class TestAppBridgePreviewDefaults(unittest.TestCase):
    def test_preview_defaults_are_safe_in_production_bridge(self) -> None:
        with (
            patch("temporal.app.load_config", return_value=_fake_config()),
            patch("temporal.app.OdasClient", _FakeClient),
            patch("temporal.app.RemoteOdasController", _FakeRemote),
            patch("temporal.app.AutoRecorder", _FakeRecorder),
        ):
            bridge = AppBridge()

        self.assertFalse(bridge.previewMode)
        self.assertEqual(bridge.previewScenarioKey, "")
        self.assertEqual(bridge.previewScenarioKeys, [])
        self.assertFalse(bridge.showPreviewScenarioSelector)
        self.assertEqual(_model_items(bridge.previewScenarioOptionsModel), [])
        self.assertEqual(_scalar_values(bridge.headerNavLabelsModel), ["配置", "录制", "相机"])
        self.assertEqual(_model_items(bridge.sourceRowsModel), [])
        bridge.setPreviewScenario("referenceSingle")
        self.assertEqual(bridge.previewScenarioKey, "")


class TestPreviewEntrypoint(unittest.TestCase):
    def test_preview_main_creates_qgui_application_before_bridge(self) -> None:
        sentinel_bridge = object()
        sentinel_app = object()
        events: list[str] = []

        with (
            patch("temporal.main.QGuiApplication") as qapp_cls,
            patch("temporal.main.PreviewBridge", return_value=sentinel_bridge) as bridge_cls,
            patch("temporal.main.run_with_bridge", return_value=7) as run_with_bridge,
        ):
            qapp_cls.instance.side_effect = lambda: None
            qapp_cls.side_effect = lambda argv: events.append("app") or sentinel_app
            bridge_cls.side_effect = lambda: events.append("bridge") or sentinel_bridge
            run_with_bridge.side_effect = lambda bridge: events.append("run") or 7

            result = preview_main()

        self.assertEqual(result, 7)
        self.assertEqual(events, ["app", "bridge", "run"])
        qapp_cls.assert_called_once_with(sys.argv)
        bridge_cls.assert_called_once_with()
        run_with_bridge.assert_called_once_with(sentinel_bridge)


if __name__ == "__main__":
    unittest.main()
