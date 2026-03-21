from __future__ import annotations

from copy import deepcopy
from math import cos, pi, sin
from typing import Any


DEFAULT_PREVIEW_SCENARIO_KEY = "referenceSingle"
PREVIEW_SCENARIO_KEYS = (
    "referenceSingle",
    "hemisphereSpread",
    "equatorBoundary",
    "emptyState",
)

_DEFAULT_SAMPLE_WINDOW = {
    "sampleStart": 1512,
    "sampleStep": 16,
    "windowSize": 10,
    "tickCount": 10,
    "tickStride": 1,
    "advancePerTick": 2,
    "timerIntervalMs": 400,
}


def _normalize_vector(x: float, y: float, z: float) -> tuple[float, float, float]:
    length = max(0.0001, (x * x + y * y + z * z) ** 0.5)
    return (x / length, y / length, z / length)


def _build_tracking_frames(
    anchors: list[dict[str, Any]],
    phase_offsets: dict[int, float],
    sample_window: dict[str, int],
) -> list[dict[str, Any]]:
    frame_count = max(24, sample_window["windowSize"] * 2)
    frames: list[dict[str, Any]] = []

    for frame_index in range(frame_count):
        ratio = frame_index / frame_count
        sample = sample_window["sampleStart"] + frame_index * sample_window["sampleStep"]
        sources: list[dict[str, Any]] = []

        for anchor in anchors:
            source_id = int(anchor["id"])
            phase = phase_offsets.get(source_id, 0.0)
            theta = 2 * pi * ratio + phase
            wobble = float(anchor.get("motionScale", 0.0))

            x, y, z = _normalize_vector(
                float(anchor["anchorX"]) + wobble * cos(theta),
                float(anchor["anchorY"]) + wobble * 0.55 * sin(theta * 0.75 + phase * 0.25),
                float(anchor["anchorZ"]) + wobble * sin(theta),
            )
            sources.append({"id": source_id, "x": x, "y": y, "z": z})

        frames.append({"sample": sample, "sources": sources})

    return frames


def _scenario_entry(
    key: str,
    display_name: str,
    remote_log_lines: list[str],
    anchors: list[dict[str, Any]],
    phase_offsets: dict[int, float],
) -> dict[str, Any]:
    sample_window = dict(_DEFAULT_SAMPLE_WINDOW)
    return {
        "key": key,
        "displayName": display_name,
        "status": "Temporal 就绪",
        "remoteLogLines": list(remote_log_lines),
        "sampleWindow": sample_window,
        "sources": [
            {
                "id": int(anchor["id"]),
                "color": str(anchor["color"]),
                "energy": float(anchor["energy"]),
            }
            for anchor in anchors
        ],
        "trackingFrames": _build_tracking_frames(anchors, phase_offsets, sample_window),
    }


_PREVIEW_CATALOG: dict[str, dict[str, Any]] = {
    "referenceSingle": _scenario_entry(
        key="referenceSingle",
        display_name="参考单点",
        remote_log_lines=["等待连接远程 odaslive...", "当前场景：参考单点"],
        anchors=[
            {
                "id": 15,
                "color": "#cf54ea",
                "energy": 0.88,
                "anchorX": -0.42,
                "anchorY": 0.18,
                "anchorZ": 0.64,
                "motionScale": 0.11,
            }
        ],
        phase_offsets={15: 0.2},
    ),
    "hemisphereSpread": _scenario_entry(
        key="hemisphereSpread",
        display_name="半球分布",
        remote_log_lines=["等待连接远程 odaslive...", "当前场景：半球分布"],
        anchors=[
            {
                "id": 7,
                "color": "#4dc6d8",
                "energy": 0.76,
                "anchorX": -0.56,
                "anchorY": 0.28,
                "anchorZ": 0.58,
                "motionScale": 0.09,
            },
            {
                "id": 15,
                "color": "#cf54ea",
                "energy": 0.88,
                "anchorX": 0.46,
                "anchorY": 0.18,
                "anchorZ": 0.62,
                "motionScale": 0.12,
            },
            {
                "id": 21,
                "color": "#5ac97c",
                "energy": 0.42,
                "anchorX": -0.18,
                "anchorY": -0.42,
                "anchorZ": -0.50,
                "motionScale": 0.08,
            },
            {
                "id": 31,
                "color": "#6a88ff",
                "energy": 0.61,
                "anchorX": 0.54,
                "anchorY": -0.36,
                "anchorZ": 0.10,
                "motionScale": 0.10,
            },
        ],
        phase_offsets={7: 0.1, 15: 1.2, 21: 2.4, 31: 3.0},
    ),
    "equatorBoundary": _scenario_entry(
        key="equatorBoundary",
        display_name="赤道边界",
        remote_log_lines=["等待连接远程 odaslive...", "当前场景：赤道边界"],
        anchors=[
            {
                "id": 12,
                "color": "#ff9c47",
                "energy": 0.74,
                "anchorX": 0.98,
                "anchorY": 0.00,
                "anchorZ": 0.02,
                "motionScale": 0.05,
            },
            {
                "id": 15,
                "color": "#cf54ea",
                "energy": 0.82,
                "anchorX": -0.96,
                "anchorY": 0.02,
                "anchorZ": -0.01,
                "motionScale": 0.05,
            },
            {
                "id": 27,
                "color": "#f16f7d",
                "energy": 0.67,
                "anchorX": 0.02,
                "anchorY": 0.00,
                "anchorZ": 0.98,
                "motionScale": 0.04,
            },
            {
                "id": 31,
                "color": "#6a88ff",
                "energy": 0.59,
                "anchorX": 0.04,
                "anchorY": -0.02,
                "anchorZ": -0.96,
                "motionScale": 0.04,
            },
        ],
        phase_offsets={12: 0.5, 15: 1.8, 27: 2.2, 31: 3.4},
    ),
    "emptyState": {
        "key": "emptyState",
        "displayName": "空状态",
        "status": "Temporal 就绪",
        "remoteLogLines": ["等待连接远程 odaslive...", "当前场景：空状态"],
        "sampleWindow": dict(_DEFAULT_SAMPLE_WINDOW),
        "sources": [],
        "trackingFrames": [],
    },
}


def preview_scenario_keys() -> list[str]:
    return list(PREVIEW_SCENARIO_KEYS)


def preview_scenario_options() -> list[dict[str, str]]:
    return [
        {"key": scenario_key, "label": _PREVIEW_CATALOG[scenario_key]["displayName"]}
        for scenario_key in PREVIEW_SCENARIO_KEYS
    ]


def get_preview_scenario(key: str) -> dict[str, Any]:
    selected_key = key if key in _PREVIEW_CATALOG else DEFAULT_PREVIEW_SCENARIO_KEY
    return deepcopy(_PREVIEW_CATALOG[selected_key])
