---
description: "Use when: writing tests."
applyTo: "tests/**"
---

# Test Instructions

## Scope

Applies to unit and integration tests.

## Source of Truth

- [specs/contracts/recording.md](../../specs/contracts/recording.md)
- [specs/knowledge/unittest.md](../../specs/knowledge/unittest.md)

## Local Rules

- Use unittest.
- Avoid real network in unit tests.
- Prefer deterministic inputs and fake IO.
- Keep test helpers minimal.

## Local Checks

- `uv run python -m unittest discover -s tests -p "test_*.py" -v`
