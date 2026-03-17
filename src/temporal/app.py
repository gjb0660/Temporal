from __future__ import annotations

from pathlib import Path
import sys

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


class AppBridge(QObject):
    statusChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._status = "Temporal ready"

    @Property(str, notify=statusChanged)
    def status(self) -> str:
        return self._status

    @Slot(str)
    def setStatus(self, status: str) -> None:
        if self._status == status:
            return
        self._status = status
        self.statusChanged.emit()


def run() -> int:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    bridge = AppBridge()
    engine.rootContext().setContextProperty("appBridge", bridge)

    qml_path = Path(__file__).resolve().parent / "ui" / "qml" / "Main.qml"
    engine.load(str(qml_path))

    if not engine.rootObjects():
        return 1

    return app.exec()
