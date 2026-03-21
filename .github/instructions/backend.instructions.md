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
- Listener readiness must be synchronous and observable from `start()`;
  do not report streams active before bind/listen succeeds.
- Static cfg validation must parse active sink targets;
  do not rely on whole-file string presence checks.
- Remote SSH helper functions must be bootstrapped once per live non-interactive
  `sh` control session and automatically re-bootstrapped after shell loss.
- UI-facing SSH-connected state must reflect live control-channel health.
- When `odas.command` uses a wrapper script, remote stop must terminate the whole
  controlled process group, not only the wrapper entry pid.
- JSON TCP parser must tolerate chunk boundaries and junk lines.
- Audio consumers must avoid blocking socket threads.
- Prefer pure functions for message normalization to ease testing.
