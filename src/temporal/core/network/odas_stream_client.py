from __future__ import annotations

import socket
import threading
import time
from collections.abc import Callable

from temporal.core.models import OdasEndpoint
from temporal.core.network.json_stream import JsonStreamBuffer

JsonHandler = Callable[[dict], None]
AudioHandler = Callable[[bytes], None]


class TcpJsonSubscriber:
    def __init__(self, endpoint: OdasEndpoint, handler: JsonHandler, name: str) -> None:
        self._endpoint = endpoint
        self._handler = handler
        self._name = name
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name=f"json-{self._name}")
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _run(self) -> None:
        parser = JsonStreamBuffer()
        while self._running:
            try:
                with socket.create_connection(
                    (self._endpoint.host, self._endpoint.port), timeout=3
                ) as sock:
                    sock.settimeout(2)
                    while self._running:
                        chunk = sock.recv(4096)
                        if not chunk:
                            break
                        for msg in parser.feed(chunk):
                            self._handler(msg)
            except OSError:
                time.sleep(1.0)


class TcpAudioSubscriber:
    def __init__(self, endpoint: OdasEndpoint, handler: AudioHandler, name: str) -> None:
        self._endpoint = endpoint
        self._handler = handler
        self._name = name
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name=f"audio-{self._name}")
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _run(self) -> None:
        while self._running:
            try:
                with socket.create_connection(
                    (self._endpoint.host, self._endpoint.port), timeout=3
                ) as sock:
                    sock.settimeout(2)
                    while self._running:
                        chunk = sock.recv(4096)
                        if not chunk:
                            break
                        self._handler(chunk)
            except OSError:
                time.sleep(1.0)
