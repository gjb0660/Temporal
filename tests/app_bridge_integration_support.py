# ruff: noqa: F401
import tempfile


import unittest


import wave


from datetime import datetime


from pathlib import Path


from time import monotonic


from unittest.mock import patch


from temporal.app.bridge import AppBridge


from temporal.app.fake_runtime import FakeClient, FakeClock, FakeRemote, fake_app_bridge


from temporal.core.recording.auto_recorder import AutoRecorder


from temporal.core.ssh.remote_odas import CommandResult


class _FailingOdasClient(FakeClient):
    def start(self) -> None:
        self.start_calls += 1
        raise OSError("bind failed")


class _FakeRemoteOdasController(FakeRemote):
    def __init__(self, cfg: object, streams: object) -> None:
        super().__init__(cfg, streams)
        self.start_result = CommandResult(code=0, stdout="4242\n", stderr="")
        self.stop_result = CommandResult(code=0, stdout="", stderr="")
        self.log_output = "startup ok\nready\n"
        self.status_output = ""
        self.status_sequence: list[str] = []
        self.start_status_sequence: list[str] = []
        self.keep_running_after_stop = False
        self.status_exception: Exception | None = None
        self.log_exception: Exception | None = None
        self.status_calls = 0
        self.clear_calls = 0
        self.clear_result = CommandResult(code=0, stdout="", stderr="")

    def start_odaslive(self) -> CommandResult:
        super().start_odaslive()
        self.status_sequence = list(self.start_status_sequence)
        return self.start_result

    def stop_odaslive(self) -> CommandResult:
        self.stop_calls += 1
        if not self.keep_running_after_stop:
            self.running = False
            self.status_output = ""
            self.status_sequence = []
        return self.stop_result

    def status(self) -> CommandResult:
        self.status_calls += 1
        if self.status_exception is not None:
            self.connected = False
            raise self.status_exception
        if self.status_sequence:
            self.status_output = self.status_sequence.pop(0)
        return CommandResult(code=0, stdout=self.status_output, stderr="")

    def read_log_tail(self, _lines: int = 80) -> CommandResult:
        if not self.connected:
            raise RuntimeError("SSH is not connected")
        if self.log_exception is not None:
            raise self.log_exception
        return CommandResult(code=0, stdout=self.log_output, stderr="")

    def clear_log(self) -> CommandResult:
        if not self.connected:
            raise RuntimeError("SSH is not connected")
        self.clear_calls += 1
        if self.clear_result.code == 0:
            self.log_output = ""
        return self.clear_result


class _BootstrapFailingRemoteOdasController(_FakeRemoteOdasController):
    def connect(self) -> None:
        self.connect_calls += 1
        raise RuntimeError("SSH control shell timed out")


class AppBridgeIntegrationBase(unittest.TestCase):
    def _make_bridge(
        self,
        recorder: AutoRecorder,
        *,
        client_cls: type[FakeClient] = FakeClient,
        remote_cls: type[_FakeRemoteOdasController] = _FakeRemoteOdasController,
    ) -> AppBridge:
        return fake_app_bridge(
            client_cls=client_cls,
            remote_cls=remote_cls,
            recorder_instance=recorder,
        )

    def _drain_startup(self, bridge: AppBridge) -> None:
        while bridge.odasStarting:
            bridge._verify_odas_startup()

    def _summary_lines(self, bridge: AppBridge) -> list[str]:
        lines = str(bridge.controlSummary).splitlines()
        self.assertEqual(len(lines), 3)
        return lines
