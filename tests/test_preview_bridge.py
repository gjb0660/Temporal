import unittest
from typing import Any, cast
from unittest.mock import patch

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


class TestPreviewBridge(unittest.TestCase):
    def test_defaults_to_preview_reference_single_with_source_rows(self) -> None:
        bridge = PreviewBridge()
        source_rows = cast(list[dict[str, Any]], bridge.sourceRows)
        source_positions = cast(list[dict[str, Any]], bridge.sourcePositions)

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
        self.assertEqual(bridge.recordingSessions, [])
        self.assertEqual(bridge.status, "Temporal 就绪")
        self.assertEqual(bridge.remoteLogLines, ["等待连接远程 odaslive...", "当前场景：参考单点"])
        self.assertTrue(bridge.showPreviewScenarioSelector)
        self.assertEqual(bridge.headerNavLabels, [])
        self.assertEqual(
            bridge.chartXTicks,
            ["1512", "1600", "1800", "2000", "2200", "2400", "2600", "2800", "3000", "3112"],
        )

    def test_scenarios_keep_rows_positions_and_series_in_sync(self) -> None:
        expectations = {
            "referenceSingle": 1,
            "hemisphereSpread": 4,
            "equatorBoundary": 4,
            "emptyState": 0,
        }
        bridge = PreviewBridge()

        for scenario_key, expected_count in expectations.items():
            bridge.setPreviewScenario(scenario_key)

            source_rows = cast(list[dict[str, Any]], bridge.sourceRows)
            source_positions = cast(list[dict[str, Any]], bridge.sourcePositions)
            elevation_series = cast(list[dict[str, Any]], bridge.elevationSeries)
            azimuth_series = cast(list[dict[str, Any]], bridge.azimuthSeries)

            self.assertEqual(len(source_rows), expected_count)
            self.assertEqual(len(bridge.sourceIds), expected_count)
            self.assertEqual(len(source_positions), expected_count)
            self.assertEqual(len(elevation_series), expected_count)
            self.assertEqual(len(azimuth_series), expected_count)

    def test_preview_scenario_options_are_exposed_in_chinese(self) -> None:
        bridge = PreviewBridge()

        options = cast(list[dict[str, str]], bridge.previewScenarioOptions)

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
        self.assertTrue(all(row["checked"] for row in bridge.sourceRows))
        self.assertEqual(bridge.remoteLogLines, ["等待连接远程 odaslive...", "当前场景：赤道边界"])

    def test_unknown_preview_scenario_is_ignored(self) -> None:
        bridge = PreviewBridge()

        bridge.setPreviewScenario("missingScenario")

        self.assertEqual(bridge.previewScenarioKey, DEFAULT_PREVIEW_SCENARIO_KEY)

    def test_set_source_selected_updates_sidebar_charts_and_positions(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")

        bridge.setSourceSelected(21, False)

        self.assertNotIn(21, bridge.sourceIds)
        self.assertNotIn(21, [item["sourceId"] for item in bridge.sourceRows if item["checked"]])
        self.assertNotIn(21, [item["id"] for item in bridge.sourcePositions])
        self.assertNotIn(21, [item["sourceId"] for item in bridge.elevationSeries])
        self.assertNotIn(21, [item["sourceId"] for item in bridge.azimuthSeries])

        bridge.setSourceSelected(21, True)

        self.assertIn(21, bridge.sourceIds)
        self.assertIn(21, [item["sourceId"] for item in bridge.elevationSeries])

    def test_empty_state_yields_no_fake_sources(self) -> None:
        bridge = PreviewBridge()

        bridge.setPreviewScenario("emptyState")

        self.assertEqual(bridge.sourceRows, [])
        self.assertEqual(bridge.sourceIds, [])
        self.assertEqual(bridge.sourcePositions, [])
        self.assertEqual(bridge.elevationSeries, [])
        self.assertEqual(bridge.azimuthSeries, [])
        self.assertEqual(bridge.remoteLogLines, ["等待连接远程 odaslive...", "当前场景：空状态"])

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

    def test_filter_state_updates_without_changing_preview_data(self) -> None:
        bridge = PreviewBridge()
        original_rows = bridge.sourceRows
        original_positions = bridge.sourcePositions
        original_elevation = bridge.elevationSeries
        original_azimuth = bridge.azimuthSeries

        bridge.setSourcesEnabled(False)
        bridge.setPotentialsEnabled(True)
        bridge.setPotentialEnergyRange(0.8, 0.2)

        self.assertFalse(bridge.sourcesEnabled)
        self.assertTrue(bridge.potentialsEnabled)
        self.assertEqual(bridge.potentialEnergyMin, 0.2)
        self.assertEqual(bridge.potentialEnergyMax, 0.8)
        self.assertEqual(bridge.sourceRows, original_rows)
        self.assertEqual(bridge.sourcePositions, original_positions)
        self.assertEqual(bridge.elevationSeries, original_elevation)
        self.assertEqual(bridge.azimuthSeries, original_azimuth)


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
        self.assertEqual(bridge.previewScenarioOptions, [])
        self.assertFalse(bridge.showPreviewScenarioSelector)
        self.assertEqual(bridge.headerNavLabels, ["配置", "录制", "相机"])
        self.assertEqual(
            bridge.chartXTicks,
            ["0", "200", "400", "600", "800", "1000", "1200", "1400", "1600"],
        )
        self.assertEqual(bridge.sourceRows, [])
        self.assertEqual(bridge.elevationSeries, [])
        self.assertEqual(bridge.azimuthSeries, [])
        bridge.setPreviewScenario("referenceSingle")
        self.assertEqual(bridge.previewScenarioKey, "")


class TestPreviewEntrypoint(unittest.TestCase):
    def test_preview_main_uses_preview_bridge(self) -> None:
        sentinel_bridge = object()
        with (
            patch("temporal.preview_main.PreviewBridge", return_value=sentinel_bridge) as bridge_cls,
            patch("temporal.preview_main.run_with_bridge", return_value=7) as run_with_bridge,
        ):
            result = preview_main()

        self.assertEqual(result, 7)
        bridge_cls.assert_called_once_with()
        run_with_bridge.assert_called_once_with(sentinel_bridge)


if __name__ == "__main__":
    unittest.main()
