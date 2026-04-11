import unittest

from temporal.qml_list_model import QmlListModel


class TestQmlListModel(unittest.TestCase):
    def test_replace_skips_reset_when_items_unchanged(self) -> None:
        model = QmlListModel(["id", "checked"])
        reset_count = 0
        count_changed = 0

        def on_model_reset() -> None:
            nonlocal reset_count
            reset_count += 1

        def on_count_changed() -> None:
            nonlocal count_changed
            count_changed += 1

        model.modelReset.connect(on_model_reset)
        model.countChanged.connect(on_count_changed)

        model.replace([{"id": 1, "checked": True}])
        self.assertEqual(reset_count, 1)
        self.assertEqual(count_changed, 1)

        model.replace([{"id": 1, "checked": True}])
        self.assertEqual(reset_count, 1)
        self.assertEqual(count_changed, 1)

        model.replace([{"id": 1, "checked": False}])
        self.assertEqual(reset_count, 2)
        self.assertEqual(count_changed, 1)

        model.replace([])
        self.assertEqual(reset_count, 3)
        self.assertEqual(count_changed, 2)


if __name__ == "__main__":
    unittest.main()
