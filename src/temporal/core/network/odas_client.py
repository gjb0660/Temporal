from __future__ import annotations

from collections.abc import Callable

from temporal.core.models import OdasStreamConfig
from temporal.core.network.odas_stream_client import TcpAudioListener, TcpJsonListener

_Listener = TcpJsonListener | TcpAudioListener


class OdasClient:
    def __init__(
        self,
        config: OdasStreamConfig,
        on_sst: Callable[[dict], None],
        on_ssl: Callable[[dict], None],
        on_sep_audio: Callable[[bytes], None],
        on_pf_audio: Callable[[bytes], None],
    ) -> None:
        self._sst = TcpJsonListener(config.sst, on_sst, "sst")
        self._ssl = TcpJsonListener(config.ssl, on_ssl, "ssl")
        self._sep = TcpAudioListener(config.sss_sep, on_sep_audio, "sep")
        self._pf = TcpAudioListener(config.sss_pf, on_pf_audio, "pf")
        self._listeners: tuple[_Listener, ...] = (self._sst, self._ssl, self._sep, self._pf)

    def start(self) -> None:
        started: list[_Listener] = []
        try:
            for listener in self._listeners:
                listener.start()
                started.append(listener)
        except Exception:
            for listener in reversed(started):
                listener.stop()
            raise

    def stop(self) -> None:
        for listener in self._listeners:
            listener.stop()
