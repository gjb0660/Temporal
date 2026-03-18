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
    sourcesEnabledChanged = Signal()
    potentialsEnabledChanged = Signal()
    potentialRangeChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._status = "Temporal ready"
        self._root = Path(__file__).resolve().parents[2]
        self._cfg_path = self._root / "config" / "odas.example.toml"
        self._cfg = load_config(self._cfg_path)
        self._remote = RemoteOdasController(self._cfg.remote)
        self._last_sst: dict = {}
        self._last_ssl: dict = {}
        self._source_items: list[str] = []
        self._potential_count = 0
        self._sources_enabled = True
        self._potentials_enabled = False
        self._potential_min = 0.0
        self._potential_max = 1.0
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

    @Property(bool, notify=sourcesEnabledChanged)  # type: ignore[reportCallIssue]
    def sourcesEnabled(self) -> bool:
        return self._sources_enabled

    @Property(bool, notify=potentialsEnabledChanged)  # type: ignore[reportCallIssue]
    def potentialsEnabled(self) -> bool:
        return self._potentials_enabled

    @Property(float, notify=potentialRangeChanged)  # type: ignore[reportCallIssue]
    def potentialEnergyMin(self) -> float:
        return self._potential_min

    @Property(float, notify=potentialRangeChanged)  # type: ignore[reportCallIssue]
    def potentialEnergyMax(self) -> float:
        return self._potential_max

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

    @Slot(bool)
    def setSourcesEnabled(self, enabled: bool) -> None:
        if self._sources_enabled == enabled:
            return
        self._sources_enabled = enabled
        self.sourcesEnabledChanged.emit()
        self._refresh_sources()
        self._update_stream_status("Source filter update")

    @Slot(bool)
    def setPotentialsEnabled(self, enabled: bool) -> None:
        if self._potentials_enabled == enabled:
            return
        self._potentials_enabled = enabled
        self.potentialsEnabledChanged.emit()
        self._refresh_potentials()
        self._update_stream_status("Potential filter update")

    @Slot(float, float)
    def setPotentialEnergyRange(self, minimum: float, maximum: float) -> None:
        low = min(minimum, maximum)
        high = max(minimum, maximum)
        if self._potential_min == low and self._potential_max == high:
            return
        self._potential_min = low
        self._potential_max = high
        self.potentialRangeChanged.emit()
        self._refresh_potentials()
        self._update_stream_status("Potential range update")

    def _on_sst(self, message: dict) -> None:
        self._last_sst = message
        self._refresh_sources()
        self._update_stream_status("SST update")

    def _on_ssl(self, message: dict) -> None:
        self._last_ssl = message
        self._refresh_potentials()
        self._update_stream_status("SSL update")

    def _on_sep_audio(self, _chunk: bytes) -> None:
        return

    def _on_pf_audio(self, _chunk: bytes) -> None:
        return

    def _update_stream_status(self, prefix: str) -> None:
        self.setStatus(f"{prefix} | sources={self.sourceCount} potentials={self._potential_count}")

    def _refresh_sources(self) -> None:
        items = build_source_items(self._last_sst, enabled=self._sources_enabled)
        if items != self._source_items:
            self._source_items = items
            self.sourceItemsChanged.emit()
            self.sourceCountChanged.emit()

    def _refresh_potentials(self) -> None:
        count = count_potentials(
            self._last_ssl,
            min_energy=self._potential_min,
            max_energy=self._potential_max,
            enabled=self._potentials_enabled,
        )
        if count != self._potential_count:
            self._potential_count = count
            self.potentialCountChanged.emit()


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
