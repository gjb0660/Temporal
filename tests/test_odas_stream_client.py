import socket
import time
import unittest

from temporal.core.models import OdasEndpoint
from temporal.core.network.odas_stream_client import TcpAudioListener, TcpJsonListener


def _wait_for(predicate, timeout: float = 2.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return predicate()


class TestOdasStreamClient(unittest.TestCase):
    def test_json_listener_accepts_reconnect_and_parses_chunked_messages(self) -> None:
        received: list[dict] = []
        listener = TcpJsonListener(
            OdasEndpoint(host="127.0.0.1", port=0),
            received.append,
            "sst",
        )
        listener.start()
        self.assertTrue(_wait_for(lambda: listener.bound_port != 0))

        with socket.create_connection(("127.0.0.1", listener.bound_port), timeout=1.0) as client:
            client.sendall(b'{"src":[{"id":1}')
            client.sendall(b"]}\nnot-json\n")

        with socket.create_connection(("127.0.0.1", listener.bound_port), timeout=1.0) as client:
            client.sendall(b'{"src":[{"id":2}]}\n')

        self.assertTrue(_wait_for(lambda: len(received) == 2))
        listener.stop()

        self.assertEqual(received[0]["src"][0]["id"], 1)
        self.assertEqual(received[1]["src"][0]["id"], 2)

    def test_audio_listener_accepts_reconnect_and_stop_closes_thread(self) -> None:
        chunks: list[bytes] = []
        listener = TcpAudioListener(
            OdasEndpoint(host="127.0.0.1", port=0),
            chunks.append,
            "sep",
        )
        listener.start()
        self.assertTrue(_wait_for(lambda: listener.bound_port != 0))

        with socket.create_connection(("127.0.0.1", listener.bound_port), timeout=1.0) as client:
            client.sendall(b"abcd")

        with socket.create_connection(("127.0.0.1", listener.bound_port), timeout=1.0) as client:
            client.sendall(b"efgh")

        self.assertTrue(_wait_for(lambda: b"abcd" in chunks and b"efgh" in chunks))
        listener.stop()

        self.assertIsNone(listener._thread)


if __name__ == "__main__":
    unittest.main()
