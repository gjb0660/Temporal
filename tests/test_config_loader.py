from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from temporal.core.config_loader import load_config


class TestConfigLoader(unittest.TestCase):
    def test_empty_remote_credentials_are_treated_as_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cfg_path = Path(temp_dir) / "odas.toml"
            cfg_path.write_text(
                "\n".join(
                    [
                        "[remote]",
                        'host = "127.0.0.1"',
                        "port = 22",
                        'username = ""',
                        'private_key = ""',
                        "",
                        "[odas]",
                        'args = ["-c", "/opt/odas/config/odas.cfg", "-v"]',
                        'log = "/tmp/odaslive.log"',
                        'cwd = "/opt/odas"',
                        "",
                        "[streams]",
                        "sst_port = 9000",
                        "ssl_port = 9001",
                        "sss_sep_port = 10000",
                        "sss_pf_port = 10010",
                    ]
                ),
                encoding="utf-8",
            )

            config = load_config(cfg_path)

            self.assertIsNone(config.remote.username)
            self.assertIsNone(config.remote.private_key)
            self.assertEqual(config.remote.odas_command, "odaslive")
            self.assertEqual(config.remote.odas_args, ["-c", "/opt/odas/config/odas.cfg", "-v"])
            self.assertEqual(config.remote.odas_cwd, "/opt/odas")
            self.assertEqual(config.remote.odas_log, "/tmp/odaslive.log")

    def test_default_args_and_log_are_used_when_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cfg_path = Path(temp_dir) / "odas.toml"
            cfg_path.write_text(
                "\n".join(
                    [
                        "[remote]",
                        'host = "127.0.0.1"',
                        "port = 22",
                        "",
                        "[odas]",
                        'command = "odaslive"',
                        "",
                        "[streams]",
                        "sst_port = 9000",
                        "ssl_port = 9001",
                        "sss_sep_port = 10000",
                        "sss_pf_port = 10010",
                    ]
                ),
                encoding="utf-8",
            )

            config = load_config(cfg_path)
            self.assertEqual(config.remote.odas_args, [])
            self.assertIsNone(config.remote.odas_cwd)
            self.assertEqual(config.remote.odas_log, "odaslive.log")

    def test_command_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            cfg_path = Path(temp_dir) / "odas.toml"
            cfg_path.write_text(
                "\n".join(
                    [
                        "[remote]",
                        'host = "127.0.0.1"',
                        "port = 22",
                        "",
                        "[odas]",
                        'command = "/opt/odas/bin/odaslive"',
                        'args = ["-c", "/opt/odas/config/odas.cfg", "-v"]',
                        "",
                        "[streams]",
                        "sst_port = 9000",
                        "ssl_port = 9001",
                        "sss_sep_port = 10000",
                        "sss_pf_port = 10010",
                    ]
                ),
                encoding="utf-8",
            )

            config = load_config(cfg_path)
            self.assertEqual(config.remote.odas_command, "/opt/odas/bin/odaslive")


if __name__ == "__main__":
    unittest.main()
