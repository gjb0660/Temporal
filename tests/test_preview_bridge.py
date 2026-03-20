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
    def test_defaults_to_preview_reference_single(self) -> None:
        bridge = PreviewBridge()
        source_positions = cast(list[dict[str, Any]], bridge.sourcePositions)

        self.assertTrue(bridge.previewMode)
        self.assertEqual(bridge.previewScenarioKey, DEFAULT_PREVIEW_SCENARIO_KEY)
        self.assertEqual(bridge.previewScenarioKeys, list(PREVIEW_SCENARIO_KEYS))
        self.assertEqual(bridge.sourceIds, [])
        self.assertEqual(bridge.recordingSessions, [])
        self.assertEqual(len(source_positions), 1)
        self.assertEqual(source_positions[0]["id"], 15)

    def test_set_preview_scenario_updates_preview_data(self) -> None:
        bridge = PreviewBridge()

        bridge.setPreviewScenario("hemisphereSpread")

        source_positions = cast(list[dict[str, Any]], bridge.sourcePositions)
        elevation_series = cast(list[dict[str, Any]], bridge.elevationSeries)
        azimuth_series = cast(list[dict[str, Any]], bridge.azimuthSeries)
        self.assertEqual(bridge.previewScenarioKey, "hemisphereSpread")
        self.assertEqual(len(source_positions), 4)
        self.assertEqual(len(elevation_series), 4)
        self.assertEqual(len(azimuth_series), 4)

    def test_unknown_preview_scenario_is_ignored(self) -> None:
        bridge = PreviewBridge()

        bridge.setPreviewScenario("missingScenario")

        self.assertEqual(bridge.previewScenarioKey, DEFAULT_PREVIEW_SCENARIO_KEY)

    def test_toggle_remote_and_streams_only_changes_local_state(self) -> None:
        bridge = PreviewBridge()

        bridge.toggleRemoteOdas()
        self.assertTrue(bridge.remoteConnected)
        self.assertTrue(bridge.odasRunning)

        bridge.toggleStreams()
        self.assertTrue(bridge.streamsActive)

        bridge.toggleRemoteOdas()
        self.assertFalse(bridge.odasRunning)
        self.assertFalse(bridge.streamsActive)

    def test_filter_state_updates_without_changing_preview_data(self) -> None:
        bridge = PreviewBridge()
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
