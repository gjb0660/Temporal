# ruff: noqa: F401
import os


import sys


import unittest


from collections.abc import Callable


from typing import Any, cast


from unittest.mock import MagicMock, patch


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


from PySide6.QtCore import QUrl


from PySide6.QtGui import QGuiApplication


from PySide6.QtQml import QQmlComponent, QQmlEngine


from temporal.app.bridge import run_with_bridge


from temporal.app.fake_runtime import fake_app_bridge


from temporal.main import preview_main


from temporal.preview_bridge import PreviewBridge


from temporal.preview_data import DEFAULT_PREVIEW_SCENARIO_KEY, PREVIEW_SCENARIO_KEYS


_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


_QML_DIR = os.path.join(_REPO_ROOT, "src", "temporal", "qml")


def _ensure_app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is not None:
        return cast(QGuiApplication, app)
    return QGuiApplication([])


def _model_items(model) -> list[dict[str, Any]]:
    return [model.get(index) for index in range(model.count)]


def _scalar_values(model) -> list[Any]:
    return [item["value"] for item in _model_items(model)]


def _source_ids(bridge: PreviewBridge) -> list[int]:
    return cast(list[int], getattr(bridge, "sourceIds"))


def _target_id_for_source(bridge: PreviewBridge, source_id: int) -> int:
    for row in _model_items(bridge.sourceRowsModel):
        if int(row.get("sourceId", 0)) != int(source_id):
            continue
        return int(row.get("targetId", 0))
    return 0


class _FakeSignal:
    def __init__(self) -> None:
        self._callbacks: list[Callable[[], None]] = []

    def connect(self, callback: Callable[[], None]) -> None:
        self._callbacks.append(callback)

    def emit(self) -> None:
        for callback in list(self._callbacks):
            callback()


class _FakeQuitApp:
    def __init__(self, *, return_code: int = 0) -> None:
        self.aboutToQuit = _FakeSignal()
        self._return_code = int(return_code)
        self.exec_calls = 0

    def exec(self) -> int:
        self.exec_calls += 1
        self.aboutToQuit.emit()
        return self._return_code


class _FakeQmlEngine:
    def __init__(self) -> None:
        self.initial_properties: dict[str, object] = {}
        self.loaded_path = ""
        self._roots = [object()]

    def setInitialProperties(self, properties: dict[str, object]) -> None:
        self.initial_properties = dict(properties)

    def load(self, path: str) -> None:
        self.loaded_path = str(path)

    def rootObjects(self) -> list[object]:
        return list(self._roots)


class PreviewBridgeQtBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = _ensure_app()
