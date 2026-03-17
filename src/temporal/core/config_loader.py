from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import tomli

from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig


@dataclass(slots=True)
class TemporalConfig:
    remote: RemoteOdasConfig
    streams: OdasStreamConfig


def load_config(path: str | Path) -> TemporalConfig:
    cfg_path = Path(path)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")

    with cfg_path.open("rb") as f:
        raw = tomli.load(f)

    remote_raw = raw.get("remote", {})
    odas_raw = raw.get("odas", {})
    streams_raw = raw.get("streams", {})

    remote = RemoteOdasConfig(
        host=str(remote_raw.get("host", "127.0.0.1")),
        port=int(remote_raw.get("port", 22)),
        username=str(remote_raw.get("username", "odas")),
        private_key=str(remote_raw.get("private_key", "~/.ssh/id_rsa")),
        odas_command=str(odas_raw.get("command", "odaslive -c /opt/odas/config/odas.cfg -v")),
    )

    host = remote.host
    streams = OdasStreamConfig(
        sst=OdasEndpoint(host=host, port=int(streams_raw.get("sst_port", 9000))),
        ssl=OdasEndpoint(host=host, port=int(streams_raw.get("ssl_port", 9001))),
        sss_sep=OdasEndpoint(host=host, port=int(streams_raw.get("sss_sep_port", 10000))),
        sss_pf=OdasEndpoint(host=host, port=int(streams_raw.get("sss_pf_port", 10010))),
    )

    return TemporalConfig(remote=remote, streams=streams)
