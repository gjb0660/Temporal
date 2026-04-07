import socket
import time
import unittest

from temporal.core.models import OdasEndpoint, OdasStreamConfig
from temporal.core.network.odas_client import OdasClient
from temporal.core.network.odas_stream_client import TcpAudioListener, TcpJsonListener


def _wait_for(predicate, timeout: float = 2.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return predicate()


class TestOdasStreamClient(unittest.TestCase):
    def test_listener_bound_to_wildcard_accepts_loopback_client(self) -> None:
        received: list[dict] = []
        listener = TcpJsonListener(
            OdasEndpoint(host="0.0.0.0", port=0),
            received.append,
            "sst",
        )
        listener.start()
        self.assertNotEqual(listener.bound_port, 0)

        with socket.create_connection(("127.0.0.1", listener.bound_port), timeout=1.0) as client:
            client.sendall(
                b"{\n"
                b'    "timeStamp": 9,\n'
                b'    "src": [\n'
                b'        { "id": 9, "x": 0.0, "y": 0.0, "z": 1.0 }\n'
                b"    ]\n"
                b"}\n"
            )

        self.assertTrue(_wait_for(lambda: len(received) == 1))
        listener.stop()

        self.assertEqual(received[0]["src"][0]["id"], 9)

    def test_json_listener_accepts_reconnect_and_parses_chunked_messages(self) -> None:
        received: list[dict] = []
        listener = TcpJsonListener(
            OdasEndpoint(host="127.0.0.1", port=0),
            received.append,
            "sst",
        )
        listener.start()
        self.assertNotEqual(listener.bound_port, 0)

        with socket.create_connection(("127.0.0.1", listener.bound_port), timeout=1.0) as client:
            client.sendall(
                b"{\n"  #
                b'    "timeStamp": 1,\n'
                b'    "src": [\n'
                b'        { "id": 1, "x": 1.0, "y": 0.0'
            )
            client.sendall(
                b', "z": 0.0 }\n'  #
                b"    ]\n"
                b"}\n"
                b"not-json\n"
            )

        with socket.create_connection(("127.0.0.1", listener.bound_port), timeout=1.0) as client:
            client.sendall(
                b"{\n"
                b'    "timeStamp": 2,\n'
                b'    "src": [\n'
                b'        { "id": 2, "x": 0.0, "y": 1.0, "z": 0.0 }\n'
                b"    ]\n"
                b"}\n"
            )

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
        self.assertNotEqual(listener.bound_port, 0)

        with socket.create_connection(("127.0.0.1", listener.bound_port), timeout=1.0) as client:
            client.sendall(b"abcd")

        with socket.create_connection(("127.0.0.1", listener.bound_port), timeout=1.0) as client:
            client.sendall(b"efgh")

        self.assertTrue(_wait_for(lambda: b"abcd" in chunks and b"efgh" in chunks))
        listener.stop()

        self.assertIsNone(listener._thread)

    def test_listener_start_raises_synchronously_when_port_is_occupied(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as blocker:
            blocker.bind(("127.0.0.1", 0))
            blocker.listen(1)
            port = blocker.getsockname()[1]
            listener = TcpJsonListener(
                OdasEndpoint(host="127.0.0.1", port=port),
                lambda _message: None,
                "sst",
            )

            with self.assertRaises(OSError):
                listener.start()

            self.assertEqual(listener.bound_port, port)
            self.assertIsNone(listener._thread)

    def test_odas_client_rolls_back_started_listeners_after_bind_failure(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as blocker:
            blocker.bind(("127.0.0.1", 0))
            blocker.listen(1)
            occupied_port = blocker.getsockname()[1]
            client = OdasClient(
                config=OdasStreamConfig(
                    sst=OdasEndpoint(host="127.0.0.1", port=0),
                    ssl=OdasEndpoint(host="127.0.0.1", port=occupied_port),
                    sss_sep=OdasEndpoint(host="127.0.0.1", port=0),
                    sss_pf=OdasEndpoint(host="127.0.0.1", port=0),
                ),
                on_sst=lambda _message: None,
                on_ssl=lambda _message: None,
                on_sep_audio=lambda _chunk: None,
                on_pf_audio=lambda _chunk: None,
            )

            with self.assertRaises(OSError):
                client.start()

            self.assertIsNone(client._sst._server)
            self.assertIsNone(client._sst._thread)


if __name__ == "__main__":
    unittest.main()
