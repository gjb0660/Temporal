import unittest

from temporal.core.ui_projection import (
    build_chart_series,
    build_chart_window_model,
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

    def test_rows_and_positions(self) -> None:
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

    def test_chart_projection_uses_structured_models(self) -> None:
        messages = [
            {"timeStamp": 350, "sources": [{"id": 15, "x": 0.0, "y": 1.0, "z": 0.0}]}
        ]

        window = build_chart_window_model(messages)
        series = build_chart_series(messages, {15: {"color": "#123456"}}, [15], axis="azimuth")

        self.assertEqual([tick["value"] for tick in window["ticks"]], [-1200, -1000, -800, -600, -400, -200, 0, 200, 350])
        self.assertTrue(window["ticks"][-1]["isLatest"])
        self.assertEqual(series[0]["points"][0]["y"], 90.0)


if __name__ == "__main__":
    unittest.main()
