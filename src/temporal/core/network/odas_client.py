from __future__ import annotations

from collections.abc import Callable

from temporal.core.models import OdasStreamConfig
from temporal.core.network.odas_stream_client import TcpAudioSubscriber, TcpJsonSubscriber


class OdasClient:
    def __init__(
        self,
        config: OdasStreamConfig,
        on_sst: Callable[[dict], None],
        on_ssl: Callable[[dict], None],
        on_sep_audio: Callable[[bytes], None],
        on_pf_audio: Callable[[bytes], None],
    ) -> None:
        self._sst = TcpJsonSubscriber(config.sst, on_sst, "sst")
        self._ssl = TcpJsonSubscriber(config.ssl, on_ssl, "ssl")
        self._sep = TcpAudioSubscriber(config.sss_sep, on_sep_audio, "sep")
        self._pf = TcpAudioSubscriber(config.sss_pf, on_pf_audio, "pf")

    def start(self) -> None:
        self._sst.start()
        self._ssl.start()
        self._sep.start()
        self._pf.start()

    def stop(self) -> None:
        self._sst.stop()
        self._ssl.stop()
        self._sep.stop()
        self._pf.stop()
