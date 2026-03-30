import json
import unittest

from temporal.core.ui_projection import (
    build_chart_series,
    build_chart_ticks,
    build_positions_model_items,
    build_rows_model_items,
    compute_sidebar_sources,
    compute_visible_source_ids,
)


class TestUiProjection(unittest.TestCase):
    def test_sidebar_and_visible_filtering(self) -> None:
        sources = [
            {"id": 7, "color": "#111111", "energy": 0.3},
            {"id": 15, "color": "#222222", "energy": 0.9},
        ]

        sidebar_disabled = compute_sidebar_sources(
            sources,
            sources_enabled=False,
            potentials_enabled=False,
            potential_min=0.0,
            potential_max=1.0,
        )
        self.assertEqual(sidebar_disabled, [])

        sidebar_filtered = compute_sidebar_sources(
            sources,
            sources_enabled=True,
            potentials_enabled=True,
            potential_min=0.8,
            potential_max=1.0,
        )
        self.assertEqual([item["id"] for item in sidebar_filtered], [15])

        visible_ids = compute_visible_source_ids(sidebar_filtered, {7, 15})
        self.assertEqual(visible_ids, [15])

    def test_rows_positions_ticks_series(self) -> None:
        sidebar_sources = [
            {"id": 7, "color": "#111111"},
            {"id": 15, "color": "#222222"},
        ]
        selected_ids = {15}
        rows = build_rows_model_items(sidebar_sources, selected_ids)
        self.assertEqual([row["sourceId"] for row in rows], [7, 15])
        self.assertFalse(rows[0]["checked"])
        self.assertTrue(rows[1]["checked"])

        current_frame_sources = {
            7: {"x": 1.0, "y": 0.0, "z": 0.0},
            15: {"x": 0.0, "y": 1.0, "z": 0.0},
        }
        visible_rows = {int(source["id"]): source for source in sidebar_sources}
        positions = build_positions_model_items(current_frame_sources, visible_rows, {15})
        self.assertEqual([item["id"] for item in positions], [15])

        window_frames = [
            {"sample": 100, "sources": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]},
            {"sample": 120, "sources": [{"id": 15, "x": 0.0, "y": 1.0, "z": 0.0}]},
        ]
        ticks = build_chart_ticks(
            window_frames,
            tick_count=2,
            fallback_sample_start=0,
            fallback_sample_step=200,
        )
        self.assertEqual(ticks, ["0", "120"])

        elevation = build_chart_series(window_frames, visible_rows, [15], axis="elevation")
        azimuth = build_chart_series(window_frames, visible_rows, [15], axis="azimuth")
        self.assertEqual(len(elevation), 1)
        self.assertEqual(len(azimuth), 1)
        self.assertEqual(json.loads(elevation[0]["valuesJson"]), [0.5, 0.5])
        self.assertEqual(json.loads(azimuth[0]["valuesJson"]), [0.5, 0.75])

    def test_ticks_fallback(self) -> None:
        ticks = build_chart_ticks(
            [],
            tick_count=4,
            fallback_sample_start=0,
            fallback_sample_step=200,
        )
        self.assertEqual(ticks, ["0", "200", "400", "600"])


if __name__ == "__main__":
    unittest.main()
