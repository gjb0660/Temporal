import unittest

from temporal.core.network.odas_message_view import (
    build_source_items,
    count_potentials,
    extract_source_ids,
)


class TestOdasMessageView(unittest.TestCase):
    def test_build_source_items_filters_zero_id(self) -> None:
        sst = {
            "src": [
                {"id": 0, "x": 0.0, "y": 0.0, "z": 0.0},
                {"id": 2, "x": 0.1, "y": 0.2, "z": 0.3},
            ]
        }
        items = build_source_items(sst)
        self.assertEqual(items, ["Source 2"])

    def test_build_source_items_handles_missing_src(self) -> None:
        self.assertEqual(build_source_items({}), [])

    def test_build_source_items_returns_empty_when_disabled(self) -> None:
        sst = {"src": [{"id": 1}, {"id": 2}]}
        self.assertEqual(build_source_items(sst, enabled=False), [])

    def test_extract_source_ids_deduplicates_and_skips_invalid(self) -> None:
        sst = {
            "src": [
                {"id": 0},
                {"id": 2},
                {"id": 2},
                {"id": "bad"},
                {"id": 5},
            ]
        }
        self.assertEqual(extract_source_ids(sst), [2, 5])

    def test_build_source_items_applies_selected_ids(self) -> None:
        sst = {"src": [{"id": 1}, {"id": 2}, {"id": 3}]}
        self.assertEqual(
            build_source_items(sst, enabled=True, selected_ids={2, 3}),
            ["Source 2", "Source 3"],
        )

    def test_count_potentials(self) -> None:
        ssl = {"src": [{"E": 0.5}, {"E": 0.7}, {"E": 0.9}]}
        self.assertEqual(count_potentials(ssl), 3)

    def test_count_potentials_handles_invalid_type(self) -> None:
        self.assertEqual(count_potentials({"src": "invalid"}), 0)

    def test_count_potentials_applies_energy_range(self) -> None:
        ssl = {"src": [{"E": 0.2}, {"E": 0.55}, {"E": 0.85}, {"energy": 0.6}]}
        self.assertEqual(count_potentials(ssl, min_energy=0.5, max_energy=0.8), 2)

    def test_count_potentials_returns_zero_when_disabled(self) -> None:
        ssl = {"src": [{"E": 0.4}, {"E": 0.9}]}
        self.assertEqual(count_potentials(ssl, enabled=False), 0)


if __name__ == "__main__":
    unittest.main()
