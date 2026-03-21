import json
import os
import unittest
from typing import Any
from unittest.mock import patch

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlComponent, QQmlEngine

from temporal.app import AppBridge
from temporal.core.config_loader import TemporalConfig
from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig
from temporal.preview_bridge import PreviewBridge
from temporal.preview_data import DEFAULT_PREVIEW_SCENARIO_KEY, PREVIEW_SCENARIO_KEYS
from temporal.preview_main import main as preview_main


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
    def __init__(self, _config) -> None:
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


def _series_items(model) -> list[dict[str, Any]]:
    return [
        {
            "sourceId": item["sourceId"],
            "color": item["color"],
            "values": json.loads(item["valuesJson"]),
        }
        for item in _model_items(model)
    ]


class TestPreviewBridge(unittest.TestCase):
    def test_defaults_to_preview_reference_single_with_source_rows(self) -> None:
        bridge = PreviewBridge()
        source_rows = _model_items(bridge.sourceRowsModel)
        source_positions = _model_items(bridge.sourcePositionsModel)

        self.assertTrue(bridge.previewMode)
        self.assertEqual(bridge.previewScenarioKey, DEFAULT_PREVIEW_SCENARIO_KEY)
        self.assertEqual(bridge.previewScenarioKeys, list(PREVIEW_SCENARIO_KEYS))
        self.assertEqual(len(source_rows), 1)
        self.assertEqual(source_rows[0]["sourceId"], 15)
        self.assertEqual(source_rows[0]["label"], "声源")
        self.assertTrue(source_rows[0]["checked"])
        self.assertEqual(bridge.sourceIds, [15])
        self.assertEqual(len(source_positions), 1)
        self.assertEqual(source_positions[0]["id"], 15)
        self.assertEqual(bridge.recordingSessionsModel.count, 0)
        self.assertEqual(bridge.status, "Temporal 就绪")
        self.assertEqual(bridge.remoteLogText, "等待连接远程 odaslive...\n当前场景：参考单点")
        self.assertTrue(bridge.showPreviewScenarioSelector)
        self.assertEqual(bridge.headerNavLabelsModel.count, 0)
        self.assertEqual(
            _scalar_values(bridge.chartXTicksModel),
            ["1512", "1600", "1800", "2000", "2200", "2400", "2600", "2800", "3000", "3112"],
        )

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
            elevation_series = _series_items(bridge.elevationSeriesModel)
            azimuth_series = _series_items(bridge.azimuthSeriesModel)

            self.assertEqual(len(source_rows), expected_count)
            self.assertEqual(len(bridge.sourceIds), expected_count)
            self.assertEqual(len(source_positions), expected_count)
            self.assertEqual(len(elevation_series), expected_count)
            self.assertEqual(len(azimuth_series), expected_count)
            self.assertEqual(
                {row["sourceId"] for row in source_rows if row["checked"]}, set(bridge.sourceIds)
            )
            self.assertEqual({item["id"] for item in source_positions}, set(bridge.sourceIds))
            self.assertEqual({item["sourceId"] for item in elevation_series}, set(bridge.sourceIds))
            self.assertEqual({item["sourceId"] for item in azimuth_series}, set(bridge.sourceIds))

    def test_preview_scenario_options_are_exposed_in_chinese(self) -> None:
        bridge = PreviewBridge()

        options = _model_items(bridge.previewScenarioOptionsModel)

        self.assertEqual([item["key"] for item in options], list(PREVIEW_SCENARIO_KEYS))
        self.assertEqual(options[0]["label"], "参考单点")
        self.assertEqual(options[-1]["label"], "空状态")

    def test_scenario_switch_resets_all_sources_to_selected(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")
        bridge.setSourceSelected(7, False)
        self.assertNotIn(7, bridge.sourceIds)

        bridge.setPreviewScenario("equatorBoundary")

        self.assertEqual(sorted(bridge.sourceIds), [12, 15, 27, 31])
        self.assertTrue(all(row["checked"] for row in _model_items(bridge.sourceRowsModel)))
        self.assertEqual(bridge.remoteLogText, "等待连接远程 odaslive...\n当前场景：赤道边界")

    def test_unknown_preview_scenario_is_ignored(self) -> None:
        bridge = PreviewBridge()

        bridge.setPreviewScenario("missingScenario")

        self.assertEqual(bridge.previewScenarioKey, DEFAULT_PREVIEW_SCENARIO_KEY)

    def test_set_source_selected_keeps_row_but_removes_series_and_positions(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")

        bridge.setSourceSelected(21, False)

        row_by_id = {item["sourceId"]: item for item in _model_items(bridge.sourceRowsModel)}
        self.assertIn(21, row_by_id)
        self.assertFalse(row_by_id[21]["checked"])
        self.assertNotIn(21, bridge.sourceIds)
        self.assertNotIn(21, [item["id"] for item in _model_items(bridge.sourcePositionsModel)])
        self.assertNotIn(
            21, [item["sourceId"] for item in _series_items(bridge.elevationSeriesModel)]
        )
        self.assertNotIn(
            21, [item["sourceId"] for item in _series_items(bridge.azimuthSeriesModel)]
        )

        bridge.setSourceSelected(21, True)

        self.assertTrue(
            {item["sourceId"]: item for item in _model_items(bridge.sourceRowsModel)}[21]["checked"]
        )
        self.assertIn(21, bridge.sourceIds)
        self.assertIn(21, [item["sourceId"] for item in _series_items(bridge.elevationSeriesModel)])

    def test_empty_state_yields_no_fake_sources(self) -> None:
        bridge = PreviewBridge()

        bridge.setPreviewScenario("emptyState")

        self.assertEqual(bridge.sourceRowsModel.count, 0)
        self.assertEqual(bridge.sourceIds, [])
        self.assertEqual(bridge.sourcePositionsModel.count, 0)
        self.assertEqual(bridge.elevationSeriesModel.count, 0)
        self.assertEqual(bridge.azimuthSeriesModel.count, 0)
        self.assertEqual(bridge.remoteLogText, "等待连接远程 odaslive...\n当前场景：空状态")

    def test_toggle_remote_and_streams_only_changes_local_state(self) -> None:
        bridge = PreviewBridge()

        bridge.toggleRemoteOdas()
        self.assertTrue(bridge.remoteConnected)
        self.assertTrue(bridge.odasRunning)
        self.assertEqual(bridge.status, "远程 odaslive 已启动")

        bridge.toggleStreams()
        self.assertTrue(bridge.streamsActive)
        self.assertEqual(bridge.status, "正在监听 SST/SSL/SSS 数据流")

        bridge.toggleRemoteOdas()
        self.assertFalse(bridge.odasRunning)
        self.assertFalse(bridge.streamsActive)
        self.assertEqual(bridge.status, "远程 odaslive 已停止")

    def test_global_filters_update_sidebar_and_visible_outputs(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")

        bridge.setSourcesEnabled(False)

        self.assertFalse(bridge.sourcesEnabled)
        self.assertEqual(bridge.sourceRowsModel.count, 0)
        self.assertEqual(bridge.sourcePositionsModel.count, 0)
        self.assertEqual(bridge.elevationSeriesModel.count, 0)
        self.assertEqual(bridge.azimuthSeriesModel.count, 0)

        bridge.setSourcesEnabled(True)
        bridge.setPotentialsEnabled(True)
        bridge.setPotentialEnergyRange(0.8, 1.0)

        self.assertTrue(bridge.potentialsEnabled)
        self.assertEqual(bridge.potentialEnergyMin, 0.8)
        self.assertEqual(bridge.potentialEnergyMax, 1.0)
        self.assertEqual([item["sourceId"] for item in _model_items(bridge.sourceRowsModel)], [15])
        self.assertEqual(bridge.sourceIds, [15])


class TestPreviewQmlContract(unittest.TestCase):
    def test_qml_can_read_preview_models_and_remote_log_text(self) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        app = QGuiApplication.instance() or QGuiApplication([])
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
    property int seriesCount: bridge.elevationSeriesModel.count
    property int optionCount: bridge.previewScenarioOptionsModel.count
    property int tickCount: bridge.chartXTicksModel.count
    property string firstBadge: bridge.sourceRowsModel.get(0).badge
    property int firstPointId: bridge.sourcePositionsModel.get(0).id
    property int firstSeriesValueCount: JSON.parse(bridge.elevationSeriesModel.get(0).valuesJson).length
    property bool hasRemoteLog: bridge.remoteLogText.length > 0
}
""",
            QUrl(),
        )
        obj = component.create()

        self.assertFalse(component.isError(), [error.toString() for error in component.errors()])
        self.assertEqual(obj.property("rowCount"), 4)
        self.assertEqual(obj.property("pointCount"), 4)
        self.assertEqual(obj.property("seriesCount"), 4)
        self.assertEqual(obj.property("optionCount"), 4)
        self.assertEqual(obj.property("tickCount"), 10)
        self.assertEqual(obj.property("firstBadge"), "7")
        self.assertEqual(obj.property("firstPointId"), 7)
        self.assertEqual(obj.property("firstSeriesValueCount"), 10)
        self.assertTrue(obj.property("hasRemoteLog"))
        obj.deleteLater()
        engine.deleteLater()
        app.processEvents()


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
        self.assertEqual(
            _scalar_values(bridge.chartXTicksModel),
            ["0", "200", "400", "600", "800", "1000", "1200", "1400", "1600"],
        )
        self.assertEqual(_model_items(bridge.sourceRowsModel), [])
        self.assertEqual(_model_items(bridge.elevationSeriesModel), [])
        self.assertEqual(_model_items(bridge.azimuthSeriesModel), [])
        bridge.setPreviewScenario("referenceSingle")
        self.assertEqual(bridge.previewScenarioKey, "")


class TestPreviewEntrypoint(unittest.TestCase):
    def test_preview_main_uses_preview_bridge(self) -> None:
        sentinel_bridge = object()
        with (
            patch(
                "temporal.preview_main.PreviewBridge", return_value=sentinel_bridge
            ) as bridge_cls,
            patch("temporal.preview_main.run_with_bridge", return_value=7) as run_with_bridge,
        ):
            result = preview_main()

        self.assertEqual(result, 7)
        bridge_cls.assert_called_once_with()
        run_with_bridge.assert_called_once_with(sentinel_bridge)


if __name__ == "__main__":
    unittest.main()
