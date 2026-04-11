from preview_bridge_support import (
    DEFAULT_PREVIEW_SCENARIO_KEY,
    PREVIEW_SCENARIO_KEYS,
    PreviewBridge,
    PreviewBridgeQtBase,
    _model_items,
    _source_ids,
    _target_id_for_source,
)


class TestPreviewBridgeScenarios(PreviewBridgeQtBase):
    def test_defaults_to_preview_reference_single_with_static_first_frame(self) -> None:
        bridge = PreviewBridge()
        source_rows = _model_items(bridge.sourceRowsModel)
        source_positions = _model_items(bridge.sourcePositionsModel)

        self.assertTrue(bridge.previewMode)
        self.assertEqual(bridge.previewScenarioKey, DEFAULT_PREVIEW_SCENARIO_KEY)
        self.assertEqual(bridge.previewScenarioKeys, list(PREVIEW_SCENARIO_KEYS))
        self.assertFalse(bridge.odasStarting)
        self.assertEqual(len(source_rows), 1)
        self.assertEqual(source_rows[0]["sourceId"], 15)
        self.assertEqual(source_rows[0]["label"], "声源")
        self.assertTrue(source_rows[0]["checked"])
        self.assertEqual(_source_ids(bridge), [15])
        self.assertEqual(len(source_positions), 1)
        self.assertEqual(source_positions[0]["id"], 15)
        self.assertEqual(bridge.recordingSessionsModel.count, 0)
        self.assertEqual(bridge.controlPhase, "idle")
        self.assertEqual(bridge.controlDataState, "inactive")
        self.assertIn("Temporal 就绪", str(bridge.controlSummary))
        self.assertIn("数据状态: 未监听", str(bridge.controlSummary))
        self.assertEqual(str(bridge.status), str(bridge.controlSummary))
        self.assertEqual(bridge.remoteLogText, "等待连接远程 odaslive...\n当前场景：参考单点")
        self.assertTrue(bridge.showPreviewScenarioSelector)
        self.assertEqual(bridge.headerNavLabelsModel.count, 3)

    def test_scenarios_keep_models_in_sync(self) -> None:
        expectations = {
            "referenceSingle": 1,
            "hemisphereSpread": 4,
            "equatorBoundary": 4,
            "emptyState": 0,
        }
        bridge = PreviewBridge()

        for scenario_key, expected_count in expectations.items():
            bridge.setPreviewScenario(scenario_key)

            source_rows = _model_items(bridge.sourceRowsModel)
            source_positions = _model_items(bridge.sourcePositionsModel)

            self.assertEqual(len(source_rows), expected_count)
            self.assertEqual(len(_source_ids(bridge)), expected_count)
            self.assertEqual(len(source_positions), expected_count)
            self.assertEqual(
                {row["sourceId"] for row in source_rows if row["checked"]},
                set(_source_ids(bridge)),
            )
            self.assertEqual({item["id"] for item in source_positions}, set(_source_ids(bridge)))
            if expected_count > 1:
                self.assertGreater(
                    len({row["badgeColor"] for row in source_rows}),
                    1,
                )

    def test_preview_scenario_options_are_exposed_in_chinese(self) -> None:
        bridge = PreviewBridge()

        options = _model_items(bridge.previewScenarioOptionsModel)

        self.assertEqual([item["key"] for item in options], list(PREVIEW_SCENARIO_KEYS))
        self.assertEqual(options[0]["label"], "参考单点")
        self.assertEqual(options[-1]["label"], "空状态")

    def test_scenario_switch_resets_selection_and_state(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")
        bridge.toggleStreams()
        bridge.advancePreviewTick()
        target_id = _target_id_for_source(bridge, 7)
        self.assertGreater(target_id, 0)
        bridge.setTargetSelected(target_id, False)

        self.assertTrue(any(item["sourceId"] == 7 for item in _model_items(bridge.sourceRowsModel)))
        self.assertFalse(
            any(
                item["sourceId"] == 7 and item["checked"]
                for item in _model_items(bridge.sourceRowsModel)
            )
        )

        bridge.setPreviewScenario("equatorBoundary")

        self.assertEqual(sorted(_source_ids(bridge)), [12, 15, 27, 31])
        self.assertTrue(all(row["checked"] for row in _model_items(bridge.sourceRowsModel)))
        self.assertEqual(bridge.remoteLogText, "等待连接远程 odaslive...\n当前场景：赤道边界")

    def test_unknown_preview_scenario_is_ignored(self) -> None:
        bridge = PreviewBridge()

        bridge.setPreviewScenario("missingScenario")

        self.assertEqual(bridge.previewScenarioKey, DEFAULT_PREVIEW_SCENARIO_KEY)

    def test_unchecked_last_source_keeps_rows_but_clears_visible_outputs(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")

        for source_id in [7, 15, 21, 31]:
            target_id = _target_id_for_source(bridge, source_id)
            self.assertGreater(target_id, 0)
            bridge.setTargetSelected(target_id, False)

        self.assertEqual(bridge.sourceRowsModel.count, 4)
        self.assertTrue(all(not item["checked"] for item in _model_items(bridge.sourceRowsModel)))
        self.assertEqual(_source_ids(bridge), [7, 15, 21, 31])
        self.assertEqual(bridge.sourcePositionsModel.count, 0)

    def test_empty_state_yields_no_fake_sources(self) -> None:
        bridge = PreviewBridge()

        bridge.setPreviewScenario("emptyState")

        self.assertEqual(bridge.sourceRowsModel.count, 0)
        self.assertEqual(_source_ids(bridge), [])
        self.assertEqual(bridge.sourcePositionsModel.count, 0)
        self.assertEqual(bridge.remoteLogText, "等待连接远程 odaslive...\n当前场景：空状态")

    def test_advance_preview_tick_updates_positions(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")
        bridge.toggleStreams()

        before_positions = _model_items(bridge.sourcePositionsModel)

        bridge.advancePreviewTick()

        self.assertNotEqual(_model_items(bridge.sourcePositionsModel), before_positions)

    def test_running_tick_keeps_single_toggle_selection_stable(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")
        bridge.toggleStreams()
        target_id = _target_id_for_source(bridge, 7)

        self.assertGreater(target_id, 0)
        bridge.setTargetSelected(target_id, False)

        for _ in range(20):
            bridge.advancePreviewTick()
            row = next(
                (
                    item
                    for item in _model_items(bridge.sourceRowsModel)
                    if int(item.get("targetId", 0)) == target_id
                ),
                None,
            )
            if row is None:
                self.fail("target row disappeared during running tick selection stability check")
            self.assertFalse(bool(row["checked"]))

    def test_preview_tick_uses_fixed_stride_and_interval(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("referenceSingle")
        bridge.toggleStreams()

        self.assertEqual(bridge._preview_tick_timer.interval(), 190)

        start_timestamp = int(bridge._last_sst.get("timeStamp", -1))
        bridge.advancePreviewTick()
        second_timestamp = int(bridge._last_sst.get("timeStamp", -1))
        bridge.advancePreviewTick()
        third_timestamp = int(bridge._last_sst.get("timeStamp", -1))

        self.assertEqual(second_timestamp - start_timestamp, 19)
        self.assertEqual(third_timestamp - second_timestamp, 19)

    def test_preview_timestamp_stays_monotonic_when_frames_loop(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("referenceSingle")
        bridge.toggleStreams()

        timestamps: list[int] = []
        for _ in range(40):
            bridge.advancePreviewTick()
            timestamps.append(int(bridge._last_sst.get("timeStamp", -1)))

        self.assertTrue(all(later > earlier for earlier, later in zip(timestamps, timestamps[1:])))
        self.assertTrue(
            all((later - earlier) == 19 for earlier, later in zip(timestamps, timestamps[1:]))
        )

    def test_hemisphere_spread_keeps_four_visible_sources_over_200_ticks(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")
        bridge.toggleStreams()

        expected_ids = {7, 15, 21, 31}
        for tick in range(200):
            bridge.advancePreviewTick()
            rows = _model_items(bridge.sourceRowsModel)
            points = _model_items(bridge.sourcePositionsModel)

            self.assertEqual(len(rows), 4, msg=f"tick={tick} row-count")
            self.assertEqual(len(points), 4, msg=f"tick={tick} point-count")
            self.assertEqual(
                {int(row["sourceId"]) for row in rows},
                expected_ids,
                msg=f"tick={tick} row-source-ids",
            )
            self.assertEqual(
                {int(point["id"]) for point in points},
                expected_ids,
                msg=f"tick={tick} point-source-ids",
            )

    def test_global_filters_update_sidebar_and_visible_outputs(self) -> None:
        bridge = PreviewBridge()
        bridge.setPreviewScenario("hemisphereSpread")

        bridge.setSourcesEnabled(False)

        self.assertFalse(bridge.sourcesEnabled)
        self.assertEqual(bridge.sourceRowsModel.count, 4)
        self.assertEqual(bridge.sourcePositionsModel.count, 0)
        self.assertEqual(bridge.elevationChartSeriesModel.count, 0)
        self.assertEqual(bridge.azimuthChartSeriesModel.count, 0)

        bridge.setSourcesEnabled(True)
        bridge.setPotentialsEnabled(True)
        bridge.setPotentialEnergyRange(0.8, 1.0)

        self.assertTrue(bridge.potentialsEnabled)
        self.assertEqual(bridge.potentialEnergyMin, 0.8)
        self.assertEqual(bridge.potentialEnergyMax, 1.0)
        self.assertEqual(
            [item["sourceId"] for item in _model_items(bridge.sourceRowsModel)], [7, 15, 21, 31]
        )
        self.assertEqual(_source_ids(bridge), [7, 15, 21, 31])

    def test_disappeared_sources_stay_listed_as_inactive_until_window_expires(self) -> None:
        bridge = PreviewBridge()
        bridge._scenario = {
            "key": "singleThenEmpty",
            "displayName": "singleThenEmpty",
            "status": "Temporal 就绪",
            "remoteLogLines": ["等待连接远程 odaslive..."],
            "sources": [{"id": 7, "color": "#4bc0c0", "energy": 0.9}],
            "trackingFrames": [
                {"sample": 0, "sources": [{"id": 7, "x": 1.0, "y": 0.0, "z": 0.0}]},
                {"sample": 19, "sources": []},
                {"sample": 1700, "sources": []},
            ],
        }
        bridge._reset_selected_sources()
        bridge._reset_preview_sample_window()
        bridge.toggleStreams()
        self.assertEqual(bridge.sourceRowsModel.get(0)["sourceId"], 7)
        self.assertTrue(bridge.sourceRowsModel.get(0)["active"])
        self.assertEqual(bridge.elevationChartSeriesModel.count, 1)

        bridge.advancePreviewTick()
        self.assertEqual(bridge.sourceRowsModel.count, 1)
        self.assertFalse(bridge.sourceRowsModel.get(0)["active"])
        self.assertEqual(bridge.elevationChartSeriesModel.count, 1)

        bridge._on_sst({"timeStamp": 1700, "src": []})
        self.assertEqual(bridge.sourceRowsModel.count, 0)
        self.assertEqual(bridge.elevationChartSeriesModel.count, 0)
