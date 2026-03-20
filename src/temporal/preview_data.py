from __future__ import annotations

from copy import deepcopy
from typing import Any


DEFAULT_PREVIEW_SCENARIO_KEY = "referenceSingle"
PREVIEW_SCENARIO_KEYS = (
    "referenceSingle",
    "hemisphereSpread",
    "equatorBoundary",
    "emptyState",
)

_PREVIEW_CATALOG: dict[str, dict[str, Any]] = {
    "referenceSingle": {
        "key": "referenceSingle",
        "sourcePositions": [
            {"id": 15, "color": "#cf54ea", "x": -0.42, "y": 0.18, "z": 0.64},
        ],
        "elevationSeries": [
            {
                "sourceId": 15,
                "color": "#cf54ea",
                "values": [0.40, 0.44, 0.49, 0.54, 0.58, 0.60, 0.61, 0.60, 0.59, 0.58],
            },
        ],
        "azimuthSeries": [
            {
                "sourceId": 15,
                "color": "#cf54ea",
                "values": [0.88, 0.88, 0.87, 0.86, 0.85, 0.84, 0.82, 0.81, 0.82, 0.83],
            },
        ],
    },
    "hemisphereSpread": {
        "key": "hemisphereSpread",
        "sourcePositions": [
            {"id": 7, "color": "#4dc6d8", "x": -0.56, "y": 0.28, "z": 0.58},
            {"id": 15, "color": "#cf54ea", "x": 0.46, "y": 0.18, "z": 0.62},
            {"id": 21, "color": "#5ac97c", "x": -0.18, "y": -0.42, "z": -0.50},
            {"id": 31, "color": "#6a88ff", "x": 0.54, "y": -0.36, "z": 0.10},
        ],
        "elevationSeries": [
            {
                "sourceId": 7,
                "color": "#4dc6d8",
                "values": [0.56, 0.57, 0.57, 0.56, 0.55, 0.54, 0.54, 0.54, 0.53, 0.53],
            },
            {
                "sourceId": 15,
                "color": "#cf54ea",
                "values": [0.34, 0.36, 0.40, 0.45, 0.50, 0.55, 0.57, 0.58, 0.59, 0.60],
            },
            {
                "sourceId": 21,
                "color": "#5ac97c",
                "values": [0.18, 0.17, 0.16, 0.14, 0.13, 0.11, 0.10, 0.10, 0.09, 0.08],
            },
            {
                "sourceId": 31,
                "color": "#6a88ff",
                "values": [0.48, 0.47, 0.46, 0.44, 0.42, 0.41, 0.39, 0.38, 0.37, 0.36],
            },
        ],
        "azimuthSeries": [
            {
                "sourceId": 7,
                "color": "#4dc6d8",
                "values": [0.12, 0.12, 0.13, 0.14, 0.14, 0.14, 0.15, 0.15, 0.15, 0.16],
            },
            {
                "sourceId": 15,
                "color": "#cf54ea",
                "values": [0.84, 0.84, 0.83, 0.82, 0.81, 0.80, 0.79, 0.78, 0.78, 0.77],
            },
            {
                "sourceId": 21,
                "color": "#5ac97c",
                "values": [0.62, 0.61, 0.60, 0.58, 0.57, 0.55, 0.54, 0.53, 0.52, 0.50],
            },
            {
                "sourceId": 31,
                "color": "#6a88ff",
                "values": [0.34, 0.35, 0.37, 0.39, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46],
            },
        ],
    },
    "equatorBoundary": {
        "key": "equatorBoundary",
        "sourcePositions": [
            {"id": 12, "color": "#ff9c47", "x": 0.98, "y": 0.00, "z": 0.02},
            {"id": 15, "color": "#cf54ea", "x": -0.96, "y": 0.02, "z": -0.01},
            {"id": 27, "color": "#f16f7d", "x": 0.02, "y": 0.00, "z": 0.98},
            {"id": 31, "color": "#6a88ff", "x": 0.04, "y": -0.02, "z": -0.96},
        ],
        "elevationSeries": [
            {
                "sourceId": 12,
                "color": "#ff9c47",
                "values": [0.51, 0.50, 0.50, 0.49, 0.49, 0.48, 0.48, 0.48, 0.47, 0.47],
            },
            {
                "sourceId": 15,
                "color": "#cf54ea",
                "values": [0.49, 0.49, 0.50, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53, 0.53],
            },
            {
                "sourceId": 27,
                "color": "#f16f7d",
                "values": [0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89, 0.89, 0.90, 0.90],
            },
            {
                "sourceId": 31,
                "color": "#6a88ff",
                "values": [0.17, 0.16, 0.16, 0.15, 0.14, 0.14, 0.13, 0.12, 0.11, 0.10],
            },
        ],
        "azimuthSeries": [
            {
                "sourceId": 12,
                "color": "#ff9c47",
                "values": [0.51, 0.52, 0.52, 0.53, 0.53, 0.54, 0.54, 0.55, 0.55, 0.56],
            },
            {
                "sourceId": 15,
                "color": "#cf54ea",
                "values": [0.49, 0.48, 0.48, 0.47, 0.47, 0.46, 0.46, 0.45, 0.45, 0.44],
            },
            {
                "sourceId": 27,
                "color": "#f16f7d",
                "values": [0.74, 0.74, 0.74, 0.75, 0.75, 0.76, 0.76, 0.77, 0.77, 0.78],
            },
            {
                "sourceId": 31,
                "color": "#6a88ff",
                "values": [0.24, 0.24, 0.23, 0.23, 0.22, 0.22, 0.21, 0.21, 0.20, 0.20],
            },
        ],
    },
    "emptyState": {
        "key": "emptyState",
        "sourcePositions": [],
        "elevationSeries": [],
        "azimuthSeries": [],
    },
}


def preview_scenario_keys() -> list[str]:
    return list(PREVIEW_SCENARIO_KEYS)


def get_preview_scenario(key: str) -> dict[str, Any]:
    selected_key = key if key in _PREVIEW_CATALOG else DEFAULT_PREVIEW_SCENARIO_KEY
    return deepcopy(_PREVIEW_CATALOG[selected_key])
