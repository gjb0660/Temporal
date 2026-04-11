from __future__ import annotations

from datetime import datetime, timedelta
from typing import TypeVar
from unittest.mock import patch

from temporal.app.bridge import AppBridge
from temporal.core.config_loader import TemporalConfig
from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig
from temporal.core.ssh.remote_odas import CommandResult


class FakeClock:
    def __init__(self, start: datetime) -> None:
        self.current = start

    def now(self) -> datetime:
        return self.current

    def advance(self, seconds: float) -> None:
        self.current = self.current + timedelta(seconds=seconds)


class FakeRecorder:
    def __init__(self, _output_dir: object | None = None) -> None:
        self._active: set[int] = set()
        self.push_calls = 0
        self.stop_calls = 0

    def stop_all(self) -> None:
        self.stop_calls += 1
        self._active.clear()

    def clear_recording_files(self) -> int:
        self.stop_all()
        return 0

    def sessions_snapshot(self) -> list[object]:
        return []

    def update_active_sources(self, source_ids: list[int]) -> None:
        self._active = {int(source_id) for source_id in source_ids if int(source_id) > 0}

    def sweep_inactive(self) -> list[int]:
        return []

    def active_sources(self) -> set[int]:
        return set(self._active)

    def push(self, _source_id: int, _mode: str, _pcm_chunk: bytes) -> None:
        self.push_calls += 1


class FakeClient:
    def __init__(self, **_kwargs: object) -> None:
        self.started = False
        self.start_calls = 0
        self.stop_calls = 0

    def start(self) -> None:
        self.started = True
        self.start_calls += 1

    def stop(self) -> None:
        self.started = False
        self.stop_calls += 1


class FakeRemote:
    def __init__(self, _config: object, _streams: object) -> None:
        self.connected = False
        self.running = False
        self.connect_calls = 0
        self.start_calls = 0
        self.stop_calls = 0
        self.sample_rates = {"sp": 16000, "pf": 16000}
        self.sample_rate_warning: str | None = None

    def connect(self) -> None:
        self.connected = True
        self.connect_calls += 1

    def is_connected(self) -> bool:
        return self.connected

    def start_odaslive(self) -> CommandResult:
        self.running = True
        self.start_calls += 1
        return CommandResult(code=0, stdout="123\n", stderr="")

    def stop_odaslive(self) -> CommandResult:
        self.running = False
        self.stop_calls += 1
        return CommandResult(code=0, stdout="", stderr="")

    def status(self) -> CommandResult:
        stdout = "123\n" if self.running else ""
        return CommandResult(code=0, stdout=stdout, stderr="")

    def read_log_tail(self, _lines: int = 80) -> CommandResult:
        if not self.connected:
            raise RuntimeError("SSH is not connected")
        stdout = "odaslive ready\n" if self.running else "connected\n"
        return CommandResult(code=0, stdout=stdout, stderr="")

    def clear_log(self) -> CommandResult:
        if not self.connected:
            raise RuntimeError("SSH is not connected")
        return CommandResult(code=0, stdout="", stderr="")

    def recording_sample_rates(self) -> dict[str, int]:
        return dict(self.sample_rates)

    def recording_sample_rate_warning(self) -> str | None:
        return self.sample_rate_warning


def fake_config() -> TemporalConfig:
    remote = RemoteOdasConfig(
        host="127.0.0.1",
        port=22,
        username="odas",
        private_key="~/.ssh/id_rsa",
        odas_args=["-c", "/opt/odas/config/odas.cfg"],
        odas_log="/tmp/odaslive.log",
    )
    streams = OdasStreamConfig(
        sst=OdasEndpoint(host="127.0.0.1", port=9000),
        ssl=OdasEndpoint(host="127.0.0.1", port=9001),
        sss_sep=OdasEndpoint(host="127.0.0.1", port=10000),
        sss_pf=OdasEndpoint(host="127.0.0.1", port=10010),
    )
    return TemporalConfig(remote=remote, streams=streams)


_ClientT = TypeVar("_ClientT", bound=FakeClient)
_RemoteT = TypeVar("_RemoteT", bound=FakeRemote)
_RecorderT = TypeVar("_RecorderT", bound=FakeRecorder)


def _ensure_fake_parent(cls: type[object], base: type[object], name: str) -> None:
    if not issubclass(cls, base):
        raise TypeError(f"{name} must inherit from {base.__name__}")


def _patch_fake(target: str, cls: type, instance: object | None = None):
    return patch(target, cls) if instance is None else patch(target, return_value=instance)


def fake_app_bridge(
    cfg: TemporalConfig | None = None,
    client_cls: type[_ClientT] = FakeClient,
    remote_cls: type[_RemoteT] = FakeRemote,
    recorder_cls: type[_RecorderT] = FakeRecorder,
    *,
    client_instance: object | None = None,
    remote_instance: object | None = None,
    recorder_instance: object | None = None,
) -> AppBridge:
    _ensure_fake_parent(client_cls, FakeClient, "client_cls")
    _ensure_fake_parent(remote_cls, FakeRemote, "remote_cls")
    _ensure_fake_parent(recorder_cls, FakeRecorder, "recorder_cls")
    with (
        patch("temporal.app.bridge.load_config", return_value=cfg or fake_config()),
        _patch_fake("temporal.app.bridge.OdasClient", client_cls, client_instance),
        _patch_fake("temporal.app.bridge.RemoteOdasController", remote_cls, remote_instance),
        _patch_fake("temporal.app.bridge.AutoRecorder", recorder_cls, recorder_instance),
    ):
        return AppBridge()
