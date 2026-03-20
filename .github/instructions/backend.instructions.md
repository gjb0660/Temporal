---
description: "Use when: implementing Python backend services for ODAS control, SSH lifecycle, stream parsing, and recording pipelines."
applyTo: "src/temporal/{core/**,app.py,main.py}"
---

# Backend Instructions

- Keep ODAS endpoints configurable; never hardcode production host in logic.
- For touched Python files, run `uv run ruff check` first,
  fix findings, then run `uv run ruff format`.
- SSH controller must expose connect/start/stop/status with explicit errors.
- Single-instance remote process control must not use name matching as instance identity;
  use explicit control state such as a pid file and verify the real process.
- Remote stream direction must be explicit in spec and code;
  never reuse `remote.host` as the implicit SST/SSL/SSS listener address.
- JSON TCP parser must tolerate chunk boundaries and junk lines.
- Audio consumers must avoid blocking socket threads.
- Prefer pure functions for message normalization to ease testing.
