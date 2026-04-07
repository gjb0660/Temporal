import unittest

from temporal.core.network.json_stream import JsonStreamBuffer


class TestJsonStreamBuffer(unittest.TestCase):
    def test_parses_multiline_odas_tracks_payload(self) -> None:
        parser = JsonStreamBuffer()
        result = parser.feed(
            b"{\n"
            b'    "timeStamp": 123,\n'
            b'    "src": [\n'
            b'        { "id": 7, "tag": "", "x": 0.100, "y": -0.200, "z": 0.300, "activity": 0.900 },\n'
            b'        { "id": 9, "tag": "", "x": 0.400, "y": 0.500, "z": 0.600, "activity": 0.800 }\n'
            b"    ]\n"
            b"}\n"
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["timeStamp"], 123)
        self.assertEqual(len(result[0]["src"]), 2)
        self.assertEqual(result[0]["src"][0]["id"], 7)
        self.assertEqual(result[0]["src"][1]["id"], 9)

    def test_handles_chunk_boundary_for_multiline_object(self) -> None:
        parser = JsonStreamBuffer()
        first = parser.feed(b'{\n    "timeStamp": 42,\n    "src": [\n')
        second = parser.feed(b'        { "x": 0.1, "y": 0.2, "z": 0.3, "E": 0.7 }\n    ]\n}\n')
        self.assertEqual(first, [])
        self.assertEqual(len(second), 1)
        self.assertEqual(second[0]["timeStamp"], 42)
        self.assertEqual(second[0]["src"][0]["E"], 0.7)

    def test_does_not_emit_inner_src_items_as_top_level_messages(self) -> None:
        parser = JsonStreamBuffer()
        result = parser.feed(
            b"{\n"
            b'    "timeStamp": 77,\n'
            b'    "src": [\n'
            b'        { "id": 1, "x": 1.0, "y": 0.0, "z": 0.0 },\n'
            b'        { "id": 2, "x": 0.0, "y": 1.0, "z": 0.0 }\n'
            b"    ]\n"
            b"}\n"
        )
        self.assertEqual(len(result), 1)
        self.assertIn("timeStamp", result[0])
        self.assertIn("src", result[0])

    def test_skips_invalid_fragments_and_recovers_next_object(self) -> None:
        parser = JsonStreamBuffer()
        result = parser.feed(
            b"junk-prefix\n{invalid}\n"
            b"{\n"
            b'    "timeStamp": 89,\n'
            b'    "src": [\n'
            b'        { "category": "nonspeech" }\n'
            b"    ]\n"
            b"}\n"
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["timeStamp"], 89)

    def test_ndjson_input_is_not_supported(self) -> None:
        parser = JsonStreamBuffer()
        result = parser.feed(b'{"a": 1}\n{"b": 2}\n')
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
