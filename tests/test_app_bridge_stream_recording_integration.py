from app_bridge_integration_support import (
    AppBridgeIntegrationBase,
    AutoRecorder,
    FakeClock,
    Path,
    _FakeRemoteOdasController,
    datetime,
    monotonic,
    tempfile,
    wave,
)


class TestAppBridgeStreamRecordingIntegration(AppBridgeIntegrationBase):
    def test_sst_ssl_sss_flow_updates_status_and_writes_audio(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()

            bridge.startStreams()
            lines_before = self._summary_lines(bridge)
            bridge._on_sst({"src": [{"id": 2}, {"id": 4}]})
            bridge.setPotentialsEnabled(True)
            bridge._on_ssl({"src": [{"E": 0.3}, {"E": 0.7}]})
            lines_after = self._summary_lines(bridge)
            self.assertEqual(lines_before[0], lines_after[0])
            self.assertEqual(lines_before[1], lines_after[1])
            self.assertEqual(bridge.controlPhase, "streams_listening")
            self.assertEqual(bridge.controlDataState, "listening_remote_not_running")

            chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00"
            bridge._on_sep_audio(chunk)
            bridge._on_pf_audio(chunk)

            bridge.stopStreams()

            files = sorted(Path(temp_dir).glob("ODAS_*_*.wav"))
            self.assertGreaterEqual(len(files), 4)
            self.assertEqual(bridge.potentialCount, 2)
            self.assertEqual(bridge.recordingSourceCount, 0)
            self.assertEqual(bridge.controlPhase, "ssh_connected_idle")
            self.assertEqual(bridge.controlDataState, "inactive")
            lines_final = self._summary_lines(bridge)
            self.assertIn("SSH 已连接，远程 odaslive 未运行", lines_final[0])
            self.assertIn("未监听", lines_final[1])

    def test_remote_start_applies_sample_rates_to_new_wav_headers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.sample_rates = {"sp": 48000, "pf": 44100}

            bridge.startRemoteOdas()
            self._drain_startup(bridge)
            bridge._on_sst({"src": [{"id": 2}]})
            chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00"
            bridge._on_sep_audio(chunk)
            bridge._on_pf_audio(chunk)
            bridge.stopStreams()

            sp_files = sorted(Path(temp_dir).glob("ODAS_*_sp.wav"))
            pf_files = sorted(Path(temp_dir).glob("ODAS_*_pf.wav"))
            self.assertTrue(sp_files)
            self.assertTrue(pf_files)
            with wave.open(str(sp_files[0]), "rb") as sp_wav:
                self.assertEqual(sp_wav.getframerate(), 48000)
            with wave.open(str(pf_files[0]), "rb") as pf_wav:
                self.assertEqual(pf_wav.getframerate(), 44100)

    def test_remote_start_sample_rate_warning_keeps_fallback_rate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.sample_rate_warning = "录音采样率自动识别失败，已回退 16000Hz"

            bridge.startRemoteOdas()
            self.assertIn("回退 16000Hz", "\n".join(bridge._remote_log_lines))
            self._drain_startup(bridge)
            bridge._on_sst({"src": [{"id": 4}]})
            chunk = b"\x01\x00\x02\x00\x03\x00\x04\x00"
            bridge._on_sep_audio(chunk)
            bridge.stopStreams()

            sp_files = sorted(Path(temp_dir).glob("ODAS_*_sp.wav"))
            self.assertTrue(sp_files)
            with wave.open(str(sp_files[0]), "rb") as sp_wav:
                self.assertEqual(sp_wav.getframerate(), 16000)

    def test_timeout_recovery_creates_new_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            clock = FakeClock(datetime(2026, 3, 19, 12, 0, 0))
            recorder = AutoRecorder(
                output_dir=temp_dir,
                inactive_timeout_sec=1.0,
                now_fn=clock.now,
            )
            bridge = self._make_bridge(recorder)
            bridge.connectRemote()
            bridge.startStreams()
            bridge._on_sst({"src": [{"id": 7}]})
            first_session = sorted(recorder.sessions_snapshot(), key=lambda item: item.mode)
            self.assertEqual(len(first_session), 2)

            clock.advance(1.2)
            bridge._on_sst({"src": []})
            self.assertEqual(recorder.sessions_snapshot(), [])

            clock.advance(0.1)
            bridge._on_sst({"src": [{"id": 7}]})
            second_session = sorted(recorder.sessions_snapshot(), key=lambda item: item.mode)
            self.assertEqual(len(second_session), 2)

            first_paths = {session.filepath.name for session in first_session}
            second_paths = {session.filepath.name for session in second_session}
            self.assertNotEqual(first_paths, second_paths)
            bridge.stopStreams()

    def test_clear_recording_files_cleans_local_outputs_and_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            try:
                bridge._on_sst({"timeStamp": 0, "src": [{"id": 2, "x": 1.0, "y": 0.0, "z": 0.0}]})
                initial_phase = bridge.controlPhase

                files_before = sorted(Path(temp_dir).glob("ODAS_*_*.wav"))
                self.assertEqual(len(files_before), 2)
                self.assertEqual(bridge.recordingSourceCount, 1)
                self.assertTrue(bridge._recording_sessions)

                bridge.clearRecordingFiles()

                self.assertEqual(sorted(Path(temp_dir).glob("ODAS_*_*.wav")), [])
                self.assertEqual(bridge.recordingSourceCount, 0)
                self.assertEqual(bridge._recording_sessions, [])
                self.assertEqual(bridge.controlPhase, initial_phase)
            finally:
                recorder.stop_all()

    def test_streams_running_sst_timeout_falls_back_to_waiting_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()
            bridge.startStreams()
            bridge._on_sst({"src": [{"id": 2}], "timeStamp": 1})
            self.assertEqual(bridge.controlDataState, "receiving_sst")

            bridge._last_sst_monotonic = monotonic() - 3.0
            bridge._apply_state_status()

            self.assertEqual(bridge.controlDataState, "running_waiting_sst")
            self.assertIn("等待 SST", self._summary_lines(bridge)[1])
            bridge.stopStreams()

    def test_on_sst_emits_receiving_state_before_metrics_refresh(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = AutoRecorder(output_dir=temp_dir)
            bridge = self._make_bridge(recorder)
            remote = bridge._remote
            self.assertIsInstance(remote, _FakeRemoteOdasController)
            remote.status_output = "4242\n"

            bridge.connectRemote()
            bridge.startStreams()
            self.assertEqual(bridge.controlDataState, "running_waiting_sst")

            emitted_summaries: list[str] = []
            bridge.controlSummaryChanged.connect(
                lambda: emitted_summaries.append(str(bridge.controlSummary))
            )

            bridge._on_sst({"src": [{"id": 2}], "timeStamp": 1})

            self.assertGreaterEqual(len(emitted_summaries), 1)
            first_lines = emitted_summaries[0].splitlines()
            self.assertEqual(len(first_lines), 3)
            self.assertIn("正在接收 SST", first_lines[1])
            self.assertEqual(bridge.controlDataState, "receiving_sst")
            bridge.stopStreams()
