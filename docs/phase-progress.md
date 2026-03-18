# Temporal Phase Progress

## Completed

- Phase A: project skeleton + runnable PySide6/QML shell
- Phase B: SSH control + ODAS stream client scaffolding
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
- `4235d96` phase-e: add agent governance instructions and skill pack

## Next (Phase C/D/F)

1. Replace chart placeholders with real-time elevation/azimut plotting.
2. Build source model and right-panel filtering linked to SST/SSL.
3. Integrate recorder state machine with stream callbacks.
4. Add tests for JSON framing, source lifecycle, and filename contract.
5. Validate with remote Linux odaslive end-to-end.
