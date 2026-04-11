# ruff: noqa: F401
import threading


import unittest


from dataclasses import dataclass


from pathlib import Path


from temporal.app.bridge import AppBridge


from temporal.app.fake_runtime import FakeRecorder, FakeRemote, fake_app_bridge


from temporal.core.config_loader import TemporalConfig


from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig


@dataclass
class _Session:
    source_id: int
    mode: str
    filepath: Path


class _FakeRecorder(FakeRecorder):
    def __init__(self, _output_dir) -> None:
        super().__init__(_output_dir)
        self._active: set[int] = set()
        self.pushed: list[tuple[int, str, bytes]] = []
        self._sessions: dict[tuple[int, str], _Session] = {}
        self.sample_rates: dict[str, int] = {"sp": 16000, "pf": 16000}

    def update_active_sources(self, source_ids) -> None:
        next_active = {int(source_id) for source_id in source_ids if int(source_id) > 0}
        for source_id in next_active:
            self._sessions[(source_id, "sp")] = _Session(
                source_id=source_id,
                mode="sp",
                filepath=Path(f"ODAS_{source_id}_sp.wav"),
            )
            self._sessions[(source_id, "pf")] = _Session(
                source_id=source_id,
                mode="pf",
                filepath=Path(f"ODAS_{source_id}_pf.wav"),
            )
        for source_id in list(self._active):
            if source_id in next_active:
                continue
            self._sessions.pop((source_id, "sp"), None)
            self._sessions.pop((source_id, "pf"), None)
        self._active = next_active

    def sweep_inactive(self):
        return []

    def active_sources(self) -> set[int]:
        return set(self._active)

    def push(self, source_id: int, mode: str, pcm_chunk: bytes) -> None:
        if (int(source_id), str(mode)) not in self._sessions:
            return
        self.pushed.append((source_id, mode, pcm_chunk))

    def stop_all(self) -> None:
        self._active.clear()
        self.pushed.clear()
        self._sessions.clear()

    def sessions_snapshot(self):
        sessions = list(self._sessions.values())
        sessions.sort(key=lambda item: (item.source_id, item.mode))
        return sessions

    def set_sample_rates(self, sample_rates: dict[str, int]) -> None:
        self.sample_rates = dict(sample_rates)


def _fake_config() -> TemporalConfig:
    remote = RemoteOdasConfig(
        host="172.21.16.222",
        port=22,
        username="odas",
        private_key="~/.ssh/id_rsa",
        odas_command="./odas_loop.sh",
        odas_args=[],
        odas_cwd="workspace/ODAS/odas",
        odas_log="odaslive.log",
    )
    streams = OdasStreamConfig(
        sst=OdasEndpoint(host="192.168.1.50", port=9000),
        ssl=OdasEndpoint(host="192.168.1.50", port=9001),
        sss_sep=OdasEndpoint(host="192.168.1.50", port=10000),
        sss_pf=OdasEndpoint(host="192.168.1.50", port=10010),
    )
    return TemporalConfig(remote=remote, streams=streams)


class AppBridgeRecordingBase(unittest.TestCase):
    def _make_bridge(self) -> AppBridge:
        return fake_app_bridge(
            cfg=_fake_config(),
            remote_cls=FakeRemote,
            recorder_cls=_FakeRecorder,
        )

    def _target_id_for_source(self, bridge: AppBridge, source_id: int) -> int:
        fallback_target_id = 0
        for index in range(bridge.sourceRowsModel.count):
            row = bridge.sourceRowsModel.get(index)
            if int(row.get("sourceId", 0)) != int(source_id):
                continue
            target_id = int(row.get("targetId", 0))
            if bool(row.get("active")):
                return target_id
            fallback_target_id = target_id
        return fallback_target_id
