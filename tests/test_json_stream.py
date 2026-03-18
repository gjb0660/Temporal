import unittest

from temporal.core.network.json_stream import JsonStreamBuffer


class TestJsonStreamBuffer(unittest.TestCase):
    def test_parses_complete_lines(self) -> None:
        parser = JsonStreamBuffer()
        result = parser.feed(b'{"a": 1}\n{"b": 2}\n')
        self.assertEqual(result, [{"a": 1}, {"b": 2}])

    def test_handles_chunk_boundary(self) -> None:
        parser = JsonStreamBuffer()
        first = parser.feed(b'{"a": 1')
        second = parser.feed(b"}\n")
        self.assertEqual(first, [])
        self.assertEqual(second, [{"a": 1}])

    def test_skips_invalid_json_lines(self) -> None:
        parser = JsonStreamBuffer()
        result = parser.feed(b'not-json\n{"ok": true}\n')
        self.assertEqual(result, [{"ok": True}])


if __name__ == "__main__":
    unittest.main()
