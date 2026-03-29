---
description: "Use when: writing tests."
applyTo: "tests/**"
---

# Test Instructions

## Scope

Applies to unit and integration tests.

## Source of Truth

- [specs/contracts/recording-filename.md](../../specs/contracts/recording-filename.md)
- [specs/contracts/recording-lifecycle.md](../../specs/contracts/recording-lifecycle.md)
- [specs/knowledge/testing.md](../../specs/knowledge/testing.md)

A test file SHOULD be generated from a feature's Acceptance Criteria.

## Local Rules

- Use unittest.
- Avoid real network in unit tests.
- Prefer deterministic inputs and fake IO.
- Keep test helpers minimal.

## Local Checks

- `uv run python -m unittest discover -s tests -p "test_*.py" -v`
