---
description: "Use when: implementing Python backend services."
applyTo: "src/**/*.py"
---

# Backend Instructions

## Scope

Applies to Python backend services and runtime logic.

## Source of Truth

- [specs/contracts/recording.md](../../specs/contracts/recording.md)
- [specs/contracts/remote-control.md](../../specs/contracts/remote-control.md)
- [specs/knowledge/odas-protocol.md](../../specs/knowledge/odas-protocol.md)

## Local Rules

- Runtime endpoints MUST remain configurable.
- Production hosts MUST NOT be hardcoded.
- Audio consumers MUST NOT block socket threads.
- Prefer pure functions for message normalization.

## Local Checks

- `uv run ruff check`
- fix findings before `uv run ruff format`
