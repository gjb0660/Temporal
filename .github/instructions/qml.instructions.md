---
description: "Use when: modifying QML UI."
applyTo: "src/**/*.qml"
---

# QML Instructions

## Scope

Applies to QML UI components and interaction logic.

## Source of Truth

- [specs/contracts/app-bridge.md](../../specs/contracts/app-bridge.md)
- [specs/contracts/preview-mapping.md](../../specs/contracts/preview-mapping.md)
- [specs/contracts/preview-source.md](../../specs/contracts/preview-source.md)

A QML file MUST be also mapped one-to-one with a UI specific contract
in `specs/contracts/ui/*.md`, CamelCase -> kebab-case.

## Local Rules

- QML MUST remain presentation-only.
- UI actions MUST go through bridge.
- DO NOT bypass bridge interaction paths.

## Local Checks

- `uv run pyside6-qmllint`
- fix findings before `uv run pyside6-qmlformat -i`
