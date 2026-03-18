---
description: "Use when: writing unit or integration tests for protocol parsing, reconnect behavior, and recording correctness."
applyTo: ["tests/**"]
---

# Test Instructions

- Unit tests first for protocol parsing and recorder transitions.
- Avoid real network in unit tests; use fake sockets and deterministic fixtures.
- Include reconnect and malformed message cases.
- Verify filename contract and timestamp presence for recording outputs.
