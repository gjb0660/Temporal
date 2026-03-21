from __future__ import annotations

import socket
import threading
from collections.abc import Callable

from temporal.core.models import OdasEndpoint
from temporal.core.network.json_stream import JsonStreamBuffer

JsonHandler = Callable[[dict], None]
AudioHandler = Callable[[bytes], None]


class _TcpListenerBase:
    _ACCEPT_TIMEOUT_SEC = 0.2
    _READ_TIMEOUT_SEC = 0.2

    def __init__(self, endpoint: OdasEndpoint, name: str) -> None:
        self._endpoint = endpoint
        self._name = name
        self._running = False
        self._thread: threading.Thread | None = None
        self._server: socket.socket | None = None

    @property
    def bound_port(self) -> int:
        if self._server is None:
            return self._endpoint.port
        return self._server.getsockname()[1]

    def start(self) -> None:
        if self._running:
            return
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self._endpoint.host, self._endpoint.port))
            server.listen(1)
            server.settimeout(self._ACCEPT_TIMEOUT_SEC)
        except OSError:
            server.close()
            raise
        self._server = server
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True, name=self._name)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._server is not None:
            try:
                self._server.close()
            except OSError:
                pass
            self._server = None
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _run(self) -> None:
        server = self._server
        if server is None:
            return
        try:
            while self._running:
                try:
                    client, _ = server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    if self._running:
                        continue
                    break
                with client:
                    client.settimeout(self._READ_TIMEOUT_SEC)
                    self._handle_client(client)
        finally:
            try:
                server.close()
            except OSError:
                pass
            if self._server is server:
                self._server = None

    def _handle_client(self, client: socket.socket) -> None:
        raise NotImplementedError


class TcpJsonListener(_TcpListenerBase):
    def __init__(self, endpoint: OdasEndpoint, handler: JsonHandler, name: str) -> None:
        super().__init__(endpoint, f"json-{name}")
        self._handler = handler

    def _handle_client(self, client: socket.socket) -> None:
        parser = JsonStreamBuffer()
        while self._running:
            try:
                chunk = client.recv(4096)
            except OSError:
                continue
            if not chunk:
                return
            for msg in parser.feed(chunk):
                self._handler(msg)


class TcpAudioListener(_TcpListenerBase):
    def __init__(self, endpoint: OdasEndpoint, handler: AudioHandler, name: str) -> None:
        super().__init__(endpoint, f"audio-{name}")
        self._handler = handler

    def _handle_client(self, client: socket.socket) -> None:
        while self._running:
            try:
                chunk = client.recv(4096)
            except OSError:
                continue
            if not chunk:
                return
            self._handler(chunk)
