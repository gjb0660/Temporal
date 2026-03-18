from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from temporal.core.config_loader import load_config
from temporal.core.network.odas_client import OdasClient
from temporal.core.ssh.remote_odas import RemoteOdasController


class AppBridge(QObject):
    statusChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._status = "Temporal ready"
        self._root = Path(__file__).resolve().parents[2]
        self._cfg_path = self._root / "config" / "odas.example.toml"
        self._cfg = load_config(self._cfg_path)
        self._remote = RemoteOdasController(self._cfg.remote)
        self._client = OdasClient(
            config=self._cfg.streams,
            on_sst=self._on_sst,
            on_ssl=self._on_ssl,
            on_sep_audio=self._on_sep_audio,
            on_pf_audio=self._on_pf_audio,
        )

    @Property(str, notify=statusChanged)  # type: ignore[reportCallIssue]
    def status(self) -> str:
        return self._status

    @Slot(str)
    def setStatus(self, status: str) -> None:
        if self._status == status:
            return
        self._status = status
        self.statusChanged.emit()

    @Slot()
    def connectRemote(self) -> None:
        try:
            self._remote.connect()
            self.setStatus("SSH connected")
        except Exception as exc:
            self.setStatus(f"SSH connect failed: {exc}")

    @Slot()
    def startRemoteOdas(self) -> None:
        try:
            result = self._remote.start_odaslive()
            self.setStatus("Remote odaslive started" if result.code == 0 else result.stderr.strip())
        except Exception as exc:
            self.setStatus(f"Start failed: {exc}")

    @Slot()
    def stopRemoteOdas(self) -> None:
        try:
            result = self._remote.stop_odaslive()
            self.setStatus("Remote odaslive stopped" if result.code == 0 else result.stderr.strip())
        except Exception as exc:
            self.setStatus(f"Stop failed: {exc}")

    @Slot()
    def startStreams(self) -> None:
        self._client.start()
        self.setStatus("Listening to SST/SSL/SSS streams")

    @Slot()
    def stopStreams(self) -> None:
        self._client.stop()
        self.setStatus("Streams stopped")

    def _on_sst(self, _message: dict) -> None:
        return

    def _on_ssl(self, _message: dict) -> None:
        return

    def _on_sep_audio(self, _chunk: bytes) -> None:
        return

    def _on_pf_audio(self, _chunk: bytes) -> None:
        return


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
