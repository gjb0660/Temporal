from __future__ import annotations

import logging
from dataclasses import dataclass
from math import acos, degrees, sqrt
from typing import Any, Iterable, Sequence, cast

from temporal.core.source_palette import SOURCE_COLOR_PALETTE

_LOGGER = logging.getLogger(__name__)
DEFAULT_CONTINUITY_WINDOW_SAMPLES = 1600


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


@dataclass(frozen=True, slots=True)
class _AssignmentState:
    matched_count: int
    total_cost: float
    signature: tuple[int, ...]


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
    ranked = _rank_observations(observations)
    return ranked[: max(0, int(limit))]


def _rank_observations(
    observations: Iterable[SourceObservation | dict[str, object]],
) -> list[SourceObservation]:
    ranked = sorted(
        (_coerce_observation(item) for item in observations),
        key=lambda item: (-int(item.sample), int(item.source_id)),
    )
    return ranked


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

    safe_window_samples = int(window_samples)
    safe_threshold_degrees = float(threshold_degrees)
    observation_count = len(observations)
    empty_signature = tuple(-1 for _ in range(observation_count))

    def is_better(
        candidate: _AssignmentState,
        current: _AssignmentState | None,
    ) -> bool:
        if current is None:
            return True
        if candidate.matched_count != current.matched_count:
            return candidate.matched_count > current.matched_count
        if abs(candidate.total_cost - current.total_cost) > 1e-9:
            return candidate.total_cost < current.total_cost
        return candidate.signature < current.signature

    dp: dict[int, _AssignmentState] = {
        0: _AssignmentState(matched_count=0, total_cost=0.0, signature=empty_signature)
    }

    # Objective order (first principles): maximize matched cardinality, then minimize angle cost.
    for target_index, target in enumerate(targets):
        next_dp = dict(dp)
        for observation_mask, state in dp.items():
            for observation_index, observation in enumerate(observations):
                if observation_mask & (1 << observation_index):
                    continue
                if abs(int(observation.sample) - int(target.sample)) > safe_window_samples:
                    continue
                angle = _angular_distance(target, observation)
                if angle > safe_threshold_degrees:
                    continue

                updated_signature = list(state.signature)
                updated_signature[observation_index] = target_index
                updated_state = _AssignmentState(
                    matched_count=state.matched_count + 1,
                    total_cost=state.total_cost + angle,
                    signature=tuple(updated_signature),
                )
                updated_mask = observation_mask | (1 << observation_index)
                current_state = next_dp.get(updated_mask)
                if is_better(updated_state, current_state):
                    next_dp[updated_mask] = updated_state
        dp = next_dp

    best_state: _AssignmentState | None = None
    for state in dp.values():
        if is_better(state, best_state):
            best_state = state

    if best_state is None:
        return {}

    return {
        observation_index: target_index
        for observation_index, target_index in enumerate(best_state.signature)
        if target_index >= 0
    }


class SpaceTargetSession:
    def __init__(
        self,
        *,
        palette: Sequence[str] | None = None,
        continuity_window_samples: int = DEFAULT_CONTINUITY_WINDOW_SAMPLES,
        angular_threshold_degrees: float = 20.0,
    ) -> None:
        provided_palette = tuple(palette or SOURCE_COLOR_PALETTE)
        self._palette = provided_palette or ("#4bc0c0",)
        self._continuity_window_samples = max(0, int(continuity_window_samples))
        self._angular_threshold_degrees = float(angular_threshold_degrees)
        self._targets: dict[int, TrackedTarget] = {}
        self._next_target_id = 1

    def step(self, observations: Iterable[SourceObservation | dict[str, object]]) -> TrackingResult:
        ranked_observations = _rank_observations(observations)
        selected = ranked_observations[:8]
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
            observation.source_id for observation in ranked_observations[len(selected) :]
        ]

        visible_targets: list[TrackedTarget] = []
        matched_target_ids: set[int] = set()
        active_targets = sorted(self._targets.values(), key=lambda target: int(target.target_id))
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
