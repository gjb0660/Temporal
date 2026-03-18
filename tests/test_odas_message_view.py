import unittest

from temporal.core.network.odas_message_view import build_source_items, count_potentials


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

    def test_count_potentials(self) -> None:
        ssl = {"src": [{"E": 0.5}, {"E": 0.7}, {"E": 0.9}]}
        self.assertEqual(count_potentials(ssl), 3)

    def test_count_potentials_handles_invalid_type(self) -> None:
        self.assertEqual(count_potentials({"src": "invalid"}), 0)


if __name__ == "__main__":
    unittest.main()
