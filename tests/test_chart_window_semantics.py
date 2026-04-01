import unittest

from temporal.core.chart_window import (
    build_chart_series_model,
    build_chart_window_model,
    normalize_chart_frames,
)


class TestChartWindowSemantics(unittest.TestCase):
    def test_missing_timestamp_frames_are_dropped_from_window_inputs(self) -> None:
        messages = [
            {
                "timeStamp": 0,
                "sources": [{"id": 15, "x": 0.0, "y": 1.0, "z": 0.0}],
            },
            {"sources": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]},
            {
                "timeStamp": 200,
                "sources": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}],
            },
        ]

        frames = normalize_chart_frames(messages)

        self.assertEqual([frame["sample"] for frame in frames], [0, 200])
        self.assertEqual(len(frames), 2)

    def test_latest_350_renders_negative_ticks_and_unique_latest_label(self) -> None:
        model = build_chart_window_model(
            [{"timeStamp": 350, "sources": [{"id": 15, "x": 0.0, "y": 1.0, "z": 0.0}]}]
        )

        ticks = model["ticks"]

        self.assertEqual(
            [tick["value"] for tick in ticks],
            [-1200, -1000, -800, -600, -400, -200, 0, 200, 350],
        )
        self.assertEqual(sum(1 for tick in ticks if tick["isLatest"]), 1)
        self.assertEqual(ticks[-1]["value"], 350)
        self.assertTrue(ticks[-1]["isLatest"])
        self.assertFalse(ticks[-1]["isMajor"])

    def test_latest_1600_does_not_duplicate_latest_tick(self) -> None:
        model = build_chart_window_model(
            [{"timeStamp": 1600, "sources": [{"id": 15, "x": 0.0, "y": 1.0, "z": 0.0}]}]
        )

        ticks = model["ticks"]

        self.assertEqual(
            [tick["value"] for tick in ticks],
            [0, 200, 400, 600, 800, 1000, 1200, 1400, 1600],
        )
        self.assertEqual(sum(1 for tick in ticks if tick["value"] == 1600), 1)
        self.assertTrue(ticks[-1]["isLatest"])
        self.assertTrue(ticks[-1]["isMajor"])

    def test_latest_1660_keeps_1600_window_and_unique_latest_label(self) -> None:
        model = build_chart_window_model(
            [{"timeStamp": 1660, "sources": [{"id": 15, "x": 0.0, "y": 1.0, "z": 0.0}]}]
        )

        ticks = model["ticks"]

        self.assertEqual(model["windowStart"], 60)
        self.assertEqual(model["windowEnd"], 1660)
        self.assertEqual(
            [tick["value"] for tick in ticks],
            [200, 400, 600, 800, 1000, 1200, 1400, 1600, 1660],
        )
        self.assertEqual(sum(1 for tick in ticks if tick["value"] == 1660), 1)
        self.assertTrue(ticks[-1]["isLatest"])
        self.assertFalse(ticks[-1]["isMajor"])

    def test_gap_preserves_null_points_and_physical_angles(self) -> None:
        messages = [
            {
                "timeStamp": 0,
                "sources": [{"id": 15, "x": 0.0, "y": 1.0, "z": 0.0}],
            },
            {"sources": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]},
            {"timeStamp": 200, "sources": []},
            {
                "timeStamp": 400,
                "sources": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}],
            },
        ]

        series = build_chart_series_model(
            messages,
            {15: {"color": "#123456"}},
            [15],
            axis="azimuth",
        )

        points = series[0]["points"]

        self.assertEqual([point["x"] for point in points], [0, 200, 400])
        self.assertEqual(points[0]["y"], 90.0)
        self.assertIsNone(points[1]["y"])
        self.assertEqual(points[2]["y"], 0.0)

    def test_runtime_src_payload_preserves_gap_semantics(self) -> None:
        messages = [
            {"timeStamp": 0, "src": [{"id": 15, "x": 0.0, "y": 1.0, "z": 0.0}]},
            {"timeStamp": 200, "src": []},
            {"timeStamp": 400, "src": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]},
        ]

        series = build_chart_series_model(
            messages,
            {15: {"color": "#123456"}},
            [15],
            axis="azimuth",
        )

        points = series[0]["points"]

        self.assertEqual([point["x"] for point in points], [0, 200, 400])
        self.assertEqual(points[0]["y"], 90.0)
        self.assertIsNone(points[1]["y"])
        self.assertEqual(points[2]["y"], 0.0)


if __name__ == "__main__":
    unittest.main()
