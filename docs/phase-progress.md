# Temporal Phase Progress

## Completed

- Phase A: project skeleton + runnable PySide6/QML shell
- Phase B: SSH control + ODAS stream client scaffolding
- Phase C: source list and filters linked to SST/SSL stream state
- Rule update: Pyright config aligned with Facade and namespace package rule
- Phase E: Agent governance files
  (`.github/copilot-instructions.md`, `AGENTS.md`, `.github/instructions/*`)

## PRD Index

- docs/prd/phase-a-project-skeleton.md
- docs/prd/phase-b-remote-control-and-streams.md
- docs/prd/phase-c-sources-filters.md
- docs/prd/phase-d-auto-recording.md
- docs/prd/phase-e-agent-governance.md
- docs/prd/phase-f-validation-and-delivery.md

## Git Commits

- `7111e7e` phase-a: bootstrap temporal skeleton and runnable qml shell
- `541f7e6` chore: align pyright config and use namespace packages
- `28d5325` phase-b: add ssh control and odas stream client scaffolding
- `5ec3043` phase-c: wire source and potential counters into app bridge and qml
- `39a5eb6` phase-c: add source/potential filter controls and energy range handling
- `4235d96` phase-e: add agent governance instructions and skill pack

## Next (Phase D/F)

1. Integrate recorder state machine with source lifecycle callbacks.
2. Implement filename contract and finalize wav writer behavior.
3. Add recorder transition tests and reconnect edge-case tests.
4. Validate with remote Linux odaslive end-to-end.
