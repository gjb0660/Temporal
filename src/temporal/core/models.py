from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(slots=True)
class SourcePoint:
    source_id: int
    x: float
    y: float
    z: float
    energy: float | None = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class OdasEndpoint:
    host: str
    port: int


@dataclass(slots=True)
class OdasStreamConfig:
    sst: OdasEndpoint
    ssl: OdasEndpoint
    sss_sep: OdasEndpoint
    sss_pf: OdasEndpoint


@dataclass(slots=True)
class RemoteOdasConfig:
    host: str
    port: int
    username: str | None = None
    private_key: str | None = None
    odas_command: str = "odaslive"
    odas_args: list[str] = field(default_factory=list)
    odas_cwd: str | None = None
    odas_log: str = "odaslive.log"
