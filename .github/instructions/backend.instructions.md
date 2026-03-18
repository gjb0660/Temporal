---
description: "Use when: implementing Python backend services for ODAS control, SSH lifecycle, stream parsing, and recording pipelines."
applyTo: ["src/temporal/core/**", "src/temporal/app.py", "src/temporal/main.py"]
---

# Backend Instructions

- Keep ODAS endpoints configurable; never hardcode production host in logic.
- SSH controller must expose connect/start/stop/status with explicit errors.
- JSON TCP parser must tolerate chunk boundaries and junk lines.
- Audio consumers must avoid blocking socket threads.
- Prefer pure functions for message normalization to ease testing.
