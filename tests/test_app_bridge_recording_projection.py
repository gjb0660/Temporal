from app_bridge_recording_support import (
    AppBridgeRecordingBase,
    _FakeRecorder,
    threading,
)


class TestAppBridgeRecordingProjection(AppBridgeRecordingBase):
    def test_sst_updates_recording_count(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst({"src": [{"id": 2}, {"id": 0}, {"id": 5}]})

        self.assertEqual(bridge.recordingSourceCount, 2)
        self.assertEqual(bridge.controlPhase, "idle")
        self.assertEqual(bridge.controlDataState, "inactive")
        self.assertIn("Temporal 就绪", str(bridge.controlSummary))
        self.assertIn("数据状态: 未监听", str(bridge.controlSummary))
        self.assertIn("录制中=2", str(bridge.controlSummary))
        self.assertEqual(str(bridge.status), str(bridge.controlSummary))

    def test_stop_streams_resets_recording_count(self) -> None:
        bridge = self._make_bridge()
        bridge._on_sst({"src": [{"id": 3}]})

        bridge.stopStreams()

        self.assertEqual(bridge.recordingSourceCount, 0)
        self.assertIn("Temporal 就绪", str(bridge.controlSummary))

    def test_sep_audio_routes_to_mapped_sources(self) -> None:
        bridge = self._make_bridge()
        recorder = bridge._recorder
        self.assertIsInstance(recorder, _FakeRecorder)

        bridge._on_sst({"src": [{"id": 101}, {"id": 202}, {"id": 303}, {"id": 404}]})

        chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00\x0b\x00\x0c\x00\x0d\x00\x0e\x00"
        bridge._on_sep_audio(chunk)

        self.assertEqual(len(recorder.pushed), 4)
        expected = {
            (101, "sp"): b"\x01\x00\x0b\x00",
            (202, "sp"): b"\x02\x00\x0c\x00",
            (303, "sp"): b"\x03\x00\x0d\x00",
            (404, "sp"): b"\x04\x00\x0e\x00",
        }
        actual = {(source_id, mode): pcm for source_id, mode, pcm in recorder.pushed}
        self.assertEqual(actual, expected)

    def test_pf_audio_routes_to_mapped_sources(self) -> None:
        bridge = self._make_bridge()
        recorder = bridge._recorder
        self.assertIsInstance(recorder, _FakeRecorder)

        bridge._on_sst({"src": [{"id": 1}, {"id": 2}]})

        chunk = b"\x11\x00\x22\x00\x33\x00\x44\x00"
        bridge._on_pf_audio(chunk)

        actual = {(source_id, mode): pcm for source_id, mode, pcm in recorder.pushed}
        self.assertEqual(actual.get((1, "pf")), b"\x11\x00")
        self.assertEqual(actual.get((2, "pf")), b"\x22\x00")

    def test_sep_audio_ingress_from_background_thread_routes_without_ui_queue(self) -> None:
        bridge = self._make_bridge()
        recorder = bridge._recorder
        self.assertIsInstance(recorder, _FakeRecorder)
        bridge._on_sst({"src": [{"id": 101}, {"id": 202}]})
        chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00"

        worker = threading.Thread(target=lambda: bridge._on_sep_audio(chunk), daemon=True)
        worker.start()
        worker.join(timeout=2.0)

        self.assertFalse(worker.is_alive())
        actual = {(source_id, mode): pcm for source_id, mode, pcm in recorder.pushed}
        self.assertEqual(actual.get((101, "sp")), b"\x01\x00")
        self.assertEqual(actual.get((202, "sp")), b"\x02\x00")

    def test_potential_and_recording_long_run_keeps_bounded_runtime_structures(self) -> None:
        bridge = self._make_bridge()
        recorder = bridge._recorder
        self.assertIsInstance(recorder, _FakeRecorder)
        bridge.setPotentialsEnabled(True)
        bridge._set_streams_active(True)
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 101}, {"id": 202}]})
        chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00"

        for sample in range(3000):
            bridge._on_ssl(
                {
                    "timeStamp": sample,
                    "src": [
                        {"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.92},
                        {"x": 0.0, "y": 1.0, "z": 0.0, "E": 0.77},
                        {"x": 0.0, "y": 0.0, "z": 1.0, "E": 0.55},
                    ],
                }
            )
            if sample % 2 == 0:
                bridge._on_sep_audio(chunk)
            else:
                bridge._on_pf_audio(chunk)
            if sample % 10 == 0:
                bridge._chart_next_commit_at = 0.0
                bridge._on_chart_commit_timeout()

        self.assertEqual(len(recorder.pushed), 6000)
        self.assertLessEqual(len(bridge._runtime_potential_trail), 150)
        self.assertLessEqual(len(bridge._runtime_potential_history), 300)
        self.assertEqual(bridge.potentialPositionsModel.count, 150)
        samples = [int(bridge.potentialPositionsModel.get(index)["sample"]) for index in range(150)]
        self.assertEqual(min(samples), 2950)
        self.assertEqual(max(samples), 2999)

    def test_recording_sessions_updates_on_sst_and_stop(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst({"timeStamp": 0, "src": [{"id": 2, "x": 1.0, "y": 0.0, "z": 0.0}]})

        self.assertEqual(len(bridge._recording_sessions), 1)
        session_row = bridge._recording_sessions[0]
        target_id = int(session_row.get("targetId", 0))
        self.assertGreater(target_id, 0)
        self.assertEqual(
            str(session_row.get("summary", "")),
            f"Target {target_id} | Source 2 | files: 2",
        )
        details = str(session_row.get("details", ""))
        self.assertNotIn("Source ", details)
        self.assertIn("ODAS_2_sp.wav", details)
        self.assertIn("ODAS_2_pf.wav", details)
        self.assertTrue(bool(session_row.get("hasActive")))

        bridge._on_sst({"timeStamp": 19, "src": []})
        self.assertEqual(len(bridge._recording_sessions), 1)
        recent_only = bridge._recording_sessions[0]
        self.assertEqual(
            str(recent_only.get("summary", "")),
            f"Target {target_id} | Source 2 | files: 0",
        )
        recent_details = str(recent_only.get("details", ""))
        self.assertNotIn("Source ", recent_details)
        self.assertIn("ODAS_2_sp.wav", recent_details)
        self.assertIn("ODAS_2_pf.wav", recent_details)
        self.assertFalse(bool(recent_only.get("hasActive")))

        bridge.stopStreams()

        self.assertEqual(bridge._recording_sessions, [])

    def test_source_id_drift_keeps_target_grouped_recording_sessions(self) -> None:
        bridge = self._make_bridge()
        bridge._on_sst({"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        first_target_id = self._target_id_for_source(bridge, 7)
        self.assertGreater(first_target_id, 0)

        bridge._on_sst({"timeStamp": 19, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]})
        bridge._on_sst({"timeStamp": 38, "src": [{"id": 17, "x": 1.0, "y": 0.0, "z": 0.0}]})

        self.assertEqual(len(bridge._recording_sessions), 1)
        session_row = bridge._recording_sessions[0]
        self.assertEqual(int(session_row.get("targetId", 0)), first_target_id)
        self.assertEqual(
            str(session_row.get("summary", "")),
            f"Target {first_target_id} | Source 17 | files: 2",
        )
        details = str(session_row.get("details", ""))
        self.assertIn("ODAS_17_sp.wav", details)
        self.assertIn("ODAS_7_sp.wav", details)

    def test_sst_over_capacity_limits_recording_to_mapped_sources(self) -> None:
        bridge = self._make_bridge()

        bridge._on_sst({"src": [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}]})

        self.assertEqual(len(bridge._source_channel_map), 4)
        self.assertEqual(bridge.recordingSourceCount, 4)
        details_blob = "\n".join(
            str(item.get("details", "")) for item in bridge._recording_sessions
        )
        self.assertNotIn("ODAS_5_", details_blob)

    def test_unchecked_last_source_keeps_rows_but_clears_visible_outputs(self) -> None:
        bridge = self._make_bridge()
        bridge._on_sst(
            {
                "src": [
                    {"id": 2, "x": 1.0, "y": 0.0, "z": 0.0},
                    {"id": 5, "x": 0.0, "y": 1.0, "z": 0.0},
                ]
            }
        )

        bridge.setTargetSelected(self._target_id_for_source(bridge, 2), False)
        self.assertEqual(bridge.sourcePositionsModel.count, 1)

        bridge.setTargetSelected(self._target_id_for_source(bridge, 5), False)

        self.assertEqual(bridge.sourceRowsModel.count, 2)
        self.assertEqual(bridge.sourcePositionsModel.count, 0)
