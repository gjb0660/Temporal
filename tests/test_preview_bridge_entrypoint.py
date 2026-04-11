from preview_bridge_support import (
    MagicMock,
    _FakeQmlEngine,
    _FakeQuitApp,
    patch,
    preview_main,
    run_with_bridge,
    sys,
    unittest,
)


class TestPreviewEntrypoint(unittest.TestCase):
    def test_preview_main_creates_qgui_application_before_bridge(self) -> None:
        sentinel_bridge = object()
        sentinel_app = object()
        events: list[str] = []

        with (
            patch("temporal.main.QGuiApplication") as qapp_cls,
            patch("temporal.main.PreviewBridge", return_value=sentinel_bridge) as bridge_cls,
            patch("temporal.main.run_with_bridge", return_value=7) as run_with_bridge,
        ):
            qapp_cls.instance.side_effect = lambda: None
            qapp_cls.side_effect = lambda argv: events.append("app") or sentinel_app
            bridge_cls.side_effect = lambda: events.append("bridge") or sentinel_bridge
            run_with_bridge.side_effect = lambda bridge: events.append("run") or 7

            result = preview_main()

        self.assertEqual(result, 7)
        self.assertEqual(events, ["app", "bridge", "run"])
        qapp_cls.assert_called_once_with(sys.argv)
        bridge_cls.assert_called_once_with()
        run_with_bridge.assert_called_once_with(sentinel_bridge)

    def test_run_with_bridge_stops_local_streams_on_about_to_quit_once(self) -> None:
        fake_app = _FakeQuitApp(return_code=7)
        fake_engine = _FakeQmlEngine()
        bridge = MagicMock()

        with (
            patch("temporal.app.bridge.QGuiApplication") as qapp_cls,
            patch("temporal.app.bridge.QQmlApplicationEngine", return_value=fake_engine),
        ):
            qapp_cls.instance.return_value = fake_app

            result = run_with_bridge(bridge)

        self.assertEqual(result, 7)
        self.assertEqual(fake_app.exec_calls, 1)
        bridge.setParent.assert_called_once_with(fake_engine)
        self.assertEqual(fake_engine.initial_properties.get("appBridge"), bridge)
        bridge.stopStreams.assert_called_once_with()

        fake_app.aboutToQuit.emit()
        bridge.stopStreams.assert_called_once_with()
