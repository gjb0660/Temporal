from chart_bridge_contract_support import (
    ChartBridgeContractBase,
    _model_items,
    patch,
    queue,
    threading,
    time,
)


class TestChartBridgeIngress(ChartBridgeContractBase):
    def test_missing_timestamp_frame_is_ignored(self) -> None:
        bridge = self._make_runtime_bridge()
        baseline_window = _model_items(bridge.chartWindowModel)
        baseline_elevation = _model_items(bridge.elevationChartSeriesModel)
        baseline_azimuth = _model_items(bridge.azimuthChartSeriesModel)

        bridge._on_sst({"src": [{"id": 15, "x": 1.0, "y": 0.0, "z": 0.0}]})

        self.assertEqual(_model_items(bridge.chartWindowModel), baseline_window)
        self.assertEqual(_model_items(bridge.elevationChartSeriesModel), baseline_elevation)
        self.assertEqual(_model_items(bridge.azimuthChartSeriesModel), baseline_azimuth)
        self.assertFalse(hasattr(bridge, "_runtime_chart_next_fallback_sample"))

    def test_runtime_chart_commit_is_throttled_to_interval(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge._set_streams_active(True)
        messages = [
            {"timeStamp": 0, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]},
            {"timeStamp": 19, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]},
            {"timeStamp": 38, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]},
            {"timeStamp": 57, "src": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]},
        ]
        with (
            patch("temporal.app.stream_projection.refresh_chart_models") as refresh_mock,
            patch(
                "temporal.app.stream_projection.monotonic",
                side_effect=[1.00, 1.00, 1.01, 1.01, 1.02, 1.02, 1.07, 1.07],
            ),
        ):
            for message in messages:
                bridge._on_sst(message)

        self.assertEqual(refresh_mock.call_count, 2)

    def test_ssl_ingress_queue_is_bounded_and_applies_backpressure(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge.setPotentialsEnabled(True)
        bridge._ssl_ingress_queue = queue.Queue(maxsize=1)
        bridge._set_ssl_ingress_accepting(True)
        done = threading.Event()

        def _producer() -> None:
            bridge._on_ssl({"timeStamp": 0, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]})
            bridge._on_ssl({"timeStamp": 1, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]})
            done.set()

        worker = threading.Thread(target=_producer, daemon=True)
        worker.start()
        time.sleep(0.15)

        self.assertLessEqual(bridge._ssl_ingress_queue.qsize(), 1)
        self.assertGreater(bridge._ssl_ingress_blocked_count, 0)
        self.assertFalse(done.is_set())

        bridge._drain_ssl_ingress_batch(flush_all=True)
        worker.join(timeout=1.0)
        self.assertFalse(worker.is_alive())
        bridge._set_ssl_ingress_accepting(False)

    def test_ssl_ingress_tick_batches_messages_before_projection(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge.setPotentialsEnabled(True)
        bridge._set_ssl_ingress_accepting(True)
        now = time.monotonic()
        for sample in range(5):
            bridge._ssl_ingress_queue.put(
                (
                    {"timeStamp": sample, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]},
                    now,
                )
            )

        with patch("temporal.app.stream_projection.on_ssl_batch") as batch_mock:
            bridge._on_ssl_ingress_timeout()

        self.assertEqual(batch_mock.call_count, 1)
        self.assertEqual(len(batch_mock.call_args.args[1]), 5)
        self.assertEqual(bridge._ssl_ingress_queue.qsize(), 0)
        bridge._set_ssl_ingress_accepting(False)

    def test_ssl_ingress_backpressure_path_keeps_full_frame_sequence(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge.setPotentialsEnabled(True)
        bridge._ssl_ingress_queue = queue.Queue(maxsize=8)
        bridge._set_ssl_ingress_accepting(True)
        frame_total = 200

        def _producer() -> None:
            for sample in range(frame_total):
                bridge._on_ssl(
                    {"timeStamp": sample, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]}
                )

        worker = threading.Thread(target=_producer, daemon=True)
        worker.start()
        while worker.is_alive():
            bridge._drain_ssl_ingress_batch()
            time.sleep(0.001)
        bridge._drain_ssl_ingress_batch(flush_all=True)

        self.assertEqual(bridge._runtime_last_ssl_sample, frame_total - 1)
        bridge._set_ssl_ingress_accepting(False)

    def test_ssl_chart_commit_uses_dirty_gate_and_interval_throttle(self) -> None:
        bridge = self._make_runtime_bridge()
        bridge.setPotentialsEnabled(True)
        bridge._set_streams_active(True)
        bridge._chart_next_commit_at = 0.0
        with (
            patch("temporal.app.stream_projection.refresh_chart_models") as refresh_mock,
            patch("temporal.app.stream_projection.monotonic", side_effect=[1.00, 1.01, 1.02]),
        ):
            for sample in range(60):
                bridge._on_ssl(
                    {"timeStamp": sample, "src": [{"x": 1.0, "y": 0.0, "z": 0.0, "E": 0.88}]}
                )

        self.assertEqual(refresh_mock.call_count, 0)
        self.assertTrue(bridge._chart_commit_dirty)
