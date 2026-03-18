from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Property, QObject, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from temporal.core.config_loader import load_config
from temporal.core.network.odas_client import OdasClient
from temporal.core.network.odas_message_view import build_source_items, count_potentials
from temporal.core.ssh.remote_odas import RemoteOdasController


class AppBridge(QObject):
    statusChanged = Signal()
    sourceItemsChanged = Signal()
    sourceCountChanged = Signal()
    potentialCountChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._status = "Temporal ready"
        self._root = Path(__file__).resolve().parents[2]
        self._cfg_path = self._root / "config" / "odas.example.toml"
        self._cfg = load_config(self._cfg_path)
        self._remote = RemoteOdasController(self._cfg.remote)
        self._source_items: list[str] = []
        self._potential_count = 0
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

    @Property(list, notify=sourceItemsChanged)  # type: ignore[reportCallIssue]
    def sourceItems(self) -> list[str]:
        return self._source_items

    @Property(int, notify=sourceCountChanged)  # type: ignore[reportCallIssue]
    def sourceCount(self) -> int:
        return len(self._source_items)

    @Property(int, notify=potentialCountChanged)  # type: ignore[reportCallIssue]
    def potentialCount(self) -> int:
        return self._potential_count

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
        self._update_stream_status("Listening to SST/SSL/SSS streams")

    @Slot()
    def stopStreams(self) -> None:
        self._client.stop()
        self.setStatus("Streams stopped")

    def _on_sst(self, message: dict) -> None:
        items = build_source_items(message)
        if items != self._source_items:
            self._source_items = items
            self.sourceItemsChanged.emit()
            self.sourceCountChanged.emit()
        self._update_stream_status("SST update")

    def _on_ssl(self, message: dict) -> None:
        count = count_potentials(message)
        if count != self._potential_count:
            self._potential_count = count
            self.potentialCountChanged.emit()
        self._update_stream_status("SSL update")

    def _on_sep_audio(self, _chunk: bytes) -> None:
        return

    def _on_pf_audio(self, _chunk: bytes) -> None:
        return

    def _update_stream_status(self, prefix: str) -> None:
        self.setStatus(f"{prefix} | sources={self.sourceCount} potentials={self._potential_count}")


def run() -> int:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    bridge = AppBridge()
    engine.rootContext().setContextProperty("appBridge", bridge)

    qml_path = Path(__file__).resolve().parent / "qml" / "Main.qml"
    engine.load(str(qml_path))

    if not engine.rootObjects():
        return 1

    return app.exec()
