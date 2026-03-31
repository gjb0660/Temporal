from __future__ import annotations

import logging
from dataclasses import dataclass
from itertools import permutations
from math import acos, degrees, sqrt
from typing import Any, Iterable, Sequence, cast

from temporal.core.source_palette import SOURCE_COLOR_PALETTE

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SourceObservation:
    source_id: int
    sample: int
    x: float
    y: float
    z: float


@dataclass(frozen=True, slots=True)
class TrackedTarget:
    target_id: int
    source_id: int
    sample: int
    color: str
    x: float
    y: float
    z: float


@dataclass(frozen=True, slots=True)
class TrackingResult:
    visible_targets: list[TrackedTarget]
    dropped_source_ids: list[int]


def _coerce_observation(item: SourceObservation | dict[str, object]) -> SourceObservation:
    if isinstance(item, SourceObservation):
        return item
    return SourceObservation(
        source_id=int(cast(Any, item["source_id"])),
        sample=int(cast(Any, item["sample"])),
        x=float(cast(Any, item["x"])),
        y=float(cast(Any, item["y"])),
        z=float(cast(Any, item["z"])),
    )


def select_top8_observations(
    observations: Iterable[SourceObservation | dict[str, object]],
    *,
    limit: int = 8,
) -> list[SourceObservation]:
    ranked = sorted(
        (_coerce_observation(item) for item in observations),
        key=lambda item: (-int(item.sample), int(item.source_id)),
    )
    return ranked[: max(0, int(limit))]


def _vector_norm(x: float, y: float, z: float) -> float:
    return sqrt(x * x + y * y + z * z)


def _angular_distance(first: TrackedTarget, second: SourceObservation) -> float:
    first_norm = _vector_norm(first.x, first.y, first.z)
    second_norm = _vector_norm(second.x, second.y, second.z)
    if first_norm == 0.0 or second_norm == 0.0:
        return 0.0
    dot = ((first.x * second.x) + (first.y * second.y) + (first.z * second.z)) / (
        first_norm * second_norm
    )
    dot = max(-1.0, min(1.0, dot))
    return degrees(acos(dot))


def _best_visible_assignment(
    targets: Sequence[TrackedTarget],
    observations: Sequence[SourceObservation],
    *,
    threshold_degrees: float,
    window_samples: int,
) -> dict[int, int]:
    if not targets or not observations:
        return {}

    target_indices = list(range(len(targets)))
    observation_indices = list(range(len(observations)))
    best_assignment: dict[int, int] = {}
    best_cost = float("inf")

    for target_count in range(1, min(len(target_indices), len(observation_indices)) + 1):
        for target_perm in permutations(target_indices, target_count):
            for obs_perm in permutations(observation_indices, target_count):
                used_targets = set()
                total_cost = 0.0
                valid = True
                assignment: dict[int, int] = {}

                for target_index, observation_index in zip(target_perm, obs_perm, strict=True):
                    if target_index in used_targets:
                        valid = False
                        break
                    target = targets[target_index]
                    observation = observations[observation_index]
                    if abs(int(observation.sample) - int(target.sample)) > int(window_samples):
                        valid = False
                        break
                    angle = _angular_distance(target, observation)
                    if angle > float(threshold_degrees):
                        valid = False
                        break
                    used_targets.add(target_index)
                    assignment[observation_index] = target_index
                    total_cost += angle

                if valid and total_cost < best_cost:
                    best_cost = total_cost
                    best_assignment = assignment

    return best_assignment


class SpaceTargetSession:
    def __init__(
        self,
        *,
        palette: Sequence[str] | None = None,
        continuity_window_samples: int = 200,
        angular_threshold_degrees: float = 20.0,
    ) -> None:
        provided_palette = tuple(palette or SOURCE_COLOR_PALETTE)
        self._palette = provided_palette or ("#4bc0c0",)
        self._continuity_window_samples = max(0, int(continuity_window_samples))
        self._angular_threshold_degrees = float(angular_threshold_degrees)
        self._targets: dict[int, TrackedTarget] = {}
        self._next_target_id = 1

    def step(self, observations: Iterable[SourceObservation | dict[str, object]]) -> TrackingResult:
        selected = select_top8_observations(observations)
        if not selected:
            return TrackingResult(visible_targets=[], dropped_source_ids=[])

        latest_sample = max(int(item.sample) for item in selected)
        expired_target_ids = [
            target_id
            for target_id, target in self._targets.items()
            if latest_sample - int(target.sample) > self._continuity_window_samples
        ]
        for target_id in expired_target_ids:
            self._targets.pop(target_id, None)

        dropped_source_ids = [
            observation.source_id
            for observation in sorted(
                (_coerce_observation(item) for item in observations),
                key=lambda item: (-int(item.sample), int(item.source_id)),
            )[len(selected) :]
        ]

        visible_targets: list[TrackedTarget] = []
        matched_target_ids: set[int] = set()
        active_targets = list(self._targets.values())
        active_colors = {target.color for target in active_targets}
        available_colors = [color for color in self._palette if color not in active_colors]
        overflow_dropped = 0

        assignment = _best_visible_assignment(
            active_targets,
            selected,
            threshold_degrees=self._angular_threshold_degrees,
            window_samples=self._continuity_window_samples,
        )

        for observation_index, observation in enumerate(selected):
            matched_target_index = assignment.get(observation_index)
            if matched_target_index is not None:
                matched_target = active_targets[matched_target_index]
                updated = TrackedTarget(
                    target_id=matched_target.target_id,
                    source_id=observation.source_id,
                    sample=observation.sample,
                    color=matched_target.color,
                    x=observation.x,
                    y=observation.y,
                    z=observation.z,
                )
                self._targets[updated.target_id] = updated
                matched_target_ids.add(updated.target_id)
                visible_targets.append(updated)
                continue

            if available_colors:
                color = available_colors.pop(0)
                active_colors.add(color)
                target = TrackedTarget(
                    target_id=self._next_target_id,
                    source_id=observation.source_id,
                    sample=observation.sample,
                    color=color,
                    x=observation.x,
                    y=observation.y,
                    z=observation.z,
                )
                self._targets[target.target_id] = target
                self._next_target_id += 1
                visible_targets.append(target)
                continue

            dropped_source_ids.append(observation.source_id)
            overflow_dropped += 1

        if overflow_dropped:
            _LOGGER.warning(
                "Source color palette exhausted; dropped %d observation(s) after Top8 selection",
                overflow_dropped,
            )

        stale_target_ids = [
            target_id
            for target_id in list(self._targets)
            if target_id not in matched_target_ids
            and self._targets[target_id].sample < latest_sample - self._continuity_window_samples
        ]
        for target_id in stale_target_ids:
            self._targets.pop(target_id, None)

        return TrackingResult(
            visible_targets=visible_targets,
            dropped_source_ids=dropped_source_ids,
        )
