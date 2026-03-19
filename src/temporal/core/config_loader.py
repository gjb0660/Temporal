from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import tomli

from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig


@dataclass(slots=True)
class TemporalConfig:
    remote: RemoteOdasConfig
    streams: OdasStreamConfig


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_odas_args(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("odas.args must be an array of strings")

    args = [str(item).strip() for item in value]
    if any(not item for item in args):
        raise ValueError("odas.args must not contain blank items")
    return args


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
        username=_optional_string(remote_raw.get("username")),
        private_key=_optional_string(remote_raw.get("private_key")),
        odas_command=str(odas_raw.get("command", "odaslive")).strip() or "odaslive",
        odas_args=_parse_odas_args(odas_raw.get("args")),
        odas_cwd=_optional_string(odas_raw.get("cwd")),
        odas_log=str(odas_raw.get("log", "odaslive.log")).strip() or "odaslive.log",
    )

    host = remote.host
    streams = OdasStreamConfig(
        sst=OdasEndpoint(host=host, port=int(streams_raw.get("sst_port", 9000))),
        ssl=OdasEndpoint(host=host, port=int(streams_raw.get("ssl_port", 9001))),
        sss_sep=OdasEndpoint(host=host, port=int(streams_raw.get("sss_sep_port", 10000))),
        sss_pf=OdasEndpoint(host=host, port=int(streams_raw.get("sss_pf_port", 10010))),
    )

    return TemporalConfig(remote=remote, streams=streams)
