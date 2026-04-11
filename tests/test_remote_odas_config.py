from remote_odas_support import (
    RemoteOdasController,
    _extract_wrapper_cfg_path,
    _make_config,
    _make_streams,
    _sink_targets_match,
    _valid_cfg,
    unittest,
)


class TestRemoteOdasConfig(unittest.TestCase):
    def test_resolve_recording_sample_rates_from_cfg(self) -> None:
        controller = RemoteOdasController(_make_config(), _make_streams())

        sample_rates, warning = controller._resolve_recording_sample_rates(
            _valid_cfg(sep_fs=48000, pf_fs=44100)
        )

        self.assertEqual(sample_rates, {"sp": 48000, "pf": 44100})
        self.assertIsNone(warning)

    def test_resolve_recording_sample_rates_falls_back_with_warning(self) -> None:
        controller = RemoteOdasController(_make_config(), _make_streams())

        sample_rates, warning = controller._resolve_recording_sample_rates(
            "\n".join(
                [
                    'separated: { interface: { ip = "10.10.0.8"; port = 10000; }; };',
                    'postfiltered: { interface: { ip = "10.10.0.8"; port = 10010; }; };',
                ]
            )
        )

        self.assertEqual(sample_rates, {"sp": 16000, "pf": 16000})
        self.assertIsNotNone(warning)
        assert warning is not None
        self.assertIn("回退 16000Hz", warning)

    def test_should_validate_sink_host_is_false_for_wildcard(self) -> None:
        controller = RemoteOdasController(_make_config(), _make_streams(listen_host="0.0.0.0"))
        self.assertFalse(controller._should_validate_sink_host())

    def test_should_validate_sink_host_is_true_for_specific_host(self) -> None:
        controller = RemoteOdasController(
            _make_config(),
            _make_streams(listen_host="192.168.1.50"),
        )
        self.assertTrue(controller._should_validate_sink_host())

    def test_sink_targets_reject_comment_only_port_matches(self) -> None:
        cfg_text = "\n".join(
            [
                '# tracked: { interface: { ip = "10.10.0.8"; port = 9000; }; };',
                '# potential: { interface: { ip = "10.10.0.8"; port = 9001; }; };',
                '# separated: { interface: { ip = "10.10.0.8"; port = 10000; }; };',
                '# postfiltered: { interface: { ip = "10.10.0.8"; port = 10010; }; };',
                'tracked: { interface: { ip = "10.10.0.8"; port = 9100; }; };',
                'potential: { interface: { ip = "10.10.0.8"; port = 9101; }; };',
                'separated: { interface: { ip = "10.10.0.8"; port = 10100; }; };',
                'postfiltered: { interface: { ip = "10.10.0.8"; port = 10110; }; };',
            ]
        )

        self.assertEqual(
            _sink_targets_match(cfg_text, _make_streams(listen_host="10.10.0.8")),
            "preflight: tracked sink port mismatch",
        )

    def test_sink_targets_skip_host_match_for_wildcard_but_keep_port_checks(self) -> None:
        cfg_text = _valid_cfg(host="127.0.0.1")
        self.assertIsNone(_sink_targets_match(cfg_text, _make_streams(listen_host="0.0.0.0")))

    def test_sink_targets_require_matching_ports_for_wildcard_bind(self) -> None:
        cfg_text = "\n".join(
            [
                'tracked: { interface: { ip = "127.0.0.1"; port = 9100; }; };',
                'potential: { interface: { ip = "127.0.0.1"; port = 9001; }; };',
                'separated: { interface: { ip = "127.0.0.1"; port = 10000; }; };',
                'postfiltered: { interface: { ip = "127.0.0.1"; port = 10010; }; };',
            ]
        )

        self.assertEqual(
            _sink_targets_match(cfg_text, _make_streams(listen_host="0.0.0.0")),
            "preflight: tracked sink port mismatch",
        )

    def test_sink_targets_require_real_block_names(self) -> None:
        cfg_text = "\n".join(
            [
                'tracks: { interface: { ip = "10.10.0.8"; port = 9000; }; };',
                'hops: { interface: { ip = "10.10.0.8"; port = 9001; }; };',
                'audio_sep: { interface: { ip = "10.10.0.8"; port = 10000; }; };',
                'audio_pf: { interface: { ip = "10.10.0.8"; port = 10010; }; };',
            ]
        )

        self.assertEqual(
            _sink_targets_match(cfg_text, _make_streams(listen_host="10.10.0.8")),
            "preflight: tracked sink missing",
        )

    def test_extract_wrapper_cfg_path(self) -> None:
        wrapper_text = '#!/bin/sh\nexec odaslive -v -c "./configs/odas.cfg"\n'
        self.assertEqual(_extract_wrapper_cfg_path(wrapper_text), "./configs/odas.cfg")
