---
description: "Use when: implementing Python backend services for ODAS control, SSH lifecycle, stream parsing, and recording pipelines."
applyTo: "src/temporal/{core/**,app.py,main.py}"
---

# Backend Instructions

- Keep ODAS endpoints configurable; never hardcode production host in logic.
- For touched Python files, run `uv run ruff check` first,
  fix findings, then run `uv run ruff format`.
- SSH controller must expose connect/start/stop/status with explicit errors.
- JSON TCP parser must tolerate chunk boundaries and junk lines.
- Audio consumers must avoid blocking socket threads.
- Prefer pure functions for message normalization to ease testing.
