# ruff: noqa: F401
import queue


import os


import re


import threading


import time


import unittest


from math import cos, radians, sin


from pathlib import Path


from typing import Any, cast


from unittest.mock import patch


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


from PySide6.QtCore import QUrl


from PySide6.QtGui import QColor, QGuiApplication


from PySide6.QtQml import QQmlComponent, QQmlEngine


from temporal.app.bridge import AppBridge


from temporal.app.fake_runtime import fake_app_bridge


from temporal.core.chart_window import build_chart_window_model


from temporal.preview_bridge import PreviewBridge


from temporal.preview_data import get_preview_scenario


_REPO_ROOT = Path(__file__).resolve().parents[1]


_QML_DIR = _REPO_ROOT / "src" / "temporal" / "qml"


def _ensure_app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is not None:
        return cast(QGuiApplication, app)
    return QGuiApplication([])


def _model_items(model) -> list[dict[str, Any]]:
    return [model.get(index) for index in range(model.count)]


class ChartBridgeContractBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = _ensure_app()

    def _make_runtime_bridge(self) -> AppBridge:
        return fake_app_bridge()
