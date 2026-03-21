from __future__ import annotations

# pyright: reportMissingImports=false

from dataclasses import dataclass
from pathlib import Path

import tomli  # pyright: ignore[reportMissingImports]

from temporal.core.models import OdasEndpoint, OdasStreamConfig, RemoteOdasConfig


@dataclass(slots=True)
class TemporalConfig:
    remote: RemoteOdasConfig
    streams: OdasStreamConfig


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("expected a string value")
    text = value.strip()
    return text or None


def _required_string(value: object, field_name: str, default: str) -> str:
    if value is None:
        text = default
    else:
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")
        text = value
    text = text.strip()
    if not text:
        raise ValueError(f"{field_name} must not be blank")
    return text


def _parse_odas_args(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("odas.args must be an array of strings")

    args: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError("odas.args must be an array of strings")
        text = item.strip()
        if not text:
            raise ValueError("odas.args must not contain blank items")
        args.append(text)
    return args


def _required_int(value: object, field_name: str, default: int) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer")
    if not isinstance(value, (int, str)):
        raise ValueError(f"{field_name} must be an integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer") from exc


def _stream_endpoint(
    streams_raw: dict[str, object], key: str, default_port: int, host: str
) -> OdasEndpoint:
    return OdasEndpoint(
        host=host,
        port=_required_int(streams_raw.get(key), key, default_port),
    )


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
        port=_required_int(remote_raw.get("port"), "remote.port", 22),
        username=_optional_string(remote_raw.get("username")),
        private_key=_optional_string(remote_raw.get("private_key")),
        odas_command=_required_string(odas_raw.get("command"), "odas.command", "odaslive"),
        odas_args=_parse_odas_args(odas_raw.get("args")),
        odas_cwd=_optional_string(odas_raw.get("cwd")),
        odas_log=_required_string(odas_raw.get("log"), "odas.log", "odaslive.log"),
    )

    listen_host = _required_string(
        streams_raw.get("listen_host"),
        "streams.listen_host",
        "0.0.0.0",
    )
    streams = OdasStreamConfig(
        sst=_stream_endpoint(streams_raw, "sst_port", 9000, listen_host),
        ssl=_stream_endpoint(streams_raw, "ssl_port", 9001, listen_host),
        sss_sep=_stream_endpoint(streams_raw, "sss_sep_port", 10000, listen_host),
        sss_pf=_stream_endpoint(streams_raw, "sss_pf_port", 10010, listen_host),
    )

    return TemporalConfig(remote=remote, streams=streams)
