import unittest

from temporal.core.source_palette import SOURCE_COLOR_PALETTE
from temporal.core.source_tracking import (
    SourceObservation,
    SpaceTargetSession,
    select_top8_observations,
)


class TestSourceTrackingSemantics(unittest.TestCase):
    def test_continuity_keeps_identity_within_window(self) -> None:
        session = SpaceTargetSession(palette=("c0", "c1"))

        first = session.step([SourceObservation(source_id=10, sample=100, x=1.0, y=0.0, z=0.0)])
        second = session.step([SourceObservation(source_id=11, sample=250, x=1.0, y=0.0, z=0.0)])

        self.assertEqual(first.visible_targets[0].target_id, second.visible_targets[0].target_id)
        self.assertEqual(first.visible_targets[0].color, second.visible_targets[0].color)

    def test_large_angle_breaks_continuity_within_window(self) -> None:
        session = SpaceTargetSession(palette=("c0", "c1"))

        first = session.step([SourceObservation(source_id=10, sample=100, x=1.0, y=0.0, z=0.0)])
        second = session.step([SourceObservation(source_id=11, sample=120, x=0.0, y=1.0, z=0.0)])

        self.assertNotEqual(first.visible_targets[0].target_id, second.visible_targets[0].target_id)
        self.assertNotEqual(first.visible_targets[0].color, second.visible_targets[0].color)

    def test_top8_orders_by_recent_sample_then_source_id(self) -> None:
        observations = [
            SourceObservation(source_id=1, sample=100, x=1.0, y=0.0, z=0.0),
            SourceObservation(source_id=3, sample=300, x=1.0, y=0.0, z=0.0),
            SourceObservation(source_id=5, sample=500, x=1.0, y=0.0, z=0.0),
            SourceObservation(source_id=4, sample=500, x=0.0, y=1.0, z=0.0),
            SourceObservation(source_id=6, sample=600, x=1.0, y=0.0, z=0.0),
            SourceObservation(source_id=7, sample=700, x=1.0, y=0.0, z=0.0),
            SourceObservation(source_id=8, sample=800, x=1.0, y=0.0, z=0.0),
            SourceObservation(source_id=9, sample=900, x=1.0, y=0.0, z=0.0),
            SourceObservation(source_id=2, sample=200, x=1.0, y=0.0, z=0.0),
        ]

        ranked = select_top8_observations(observations)

        self.assertEqual(
            [item.source_id for item in ranked],
            [9, 8, 7, 6, 4, 5, 3, 2],
        )

    def test_small_palette_drops_overflow_after_top8_and_warns(self) -> None:
        session = SpaceTargetSession(palette=("c0", "c1"))
        observations = [
            SourceObservation(source_id=index, sample=index * 100, x=1.0, y=0.0, z=0.0)
            for index in range(1, 10)
        ]

        with self.assertLogs("temporal.core.source_tracking", level="WARNING") as captured:
            result = session.step(observations)

        self.assertEqual([item.source_id for item in result.visible_targets], [9, 8])
        self.assertEqual(len(result.dropped_source_ids), 7)
        self.assertTrue(any("palette" in line.lower() for line in captured.output))

    def test_default_palette_supports_visible_upper_bound(self) -> None:
        session = SpaceTargetSession(palette=SOURCE_COLOR_PALETTE)
        observations = [
            SourceObservation(source_id=index, sample=index * 100, x=1.0, y=0.0, z=0.0)
            for index in range(1, 9)
        ]

        result = session.step(observations)

        self.assertEqual(len(result.visible_targets), 8)
        self.assertEqual(len({item.color for item in result.visible_targets}), 8)


if __name__ == "__main__":
    unittest.main()
