# Temporal Phase Progress

## Completed

- Phase A: project skeleton + runnable PySide6/QML shell
- Phase B: SSH control + ODAS stream client scaffolding
- Phase C: source list and filters linked to SST/SSL stream state
- Phase D: recorder lifecycle, filename contract, and appBridge linkage baseline
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
- `9a80603` phase-c: complete source selection linkage and finalize filters
- `083811f` phase-d: add source-driven recorder lifecycle and filename contract
- `8eb279e` phase-d: link recorder lifecycle with source updates and recording status
- `21e19b7` ui: refine relative layout and enforce uv lint-format workflow rule
- `4235d96` phase-e: add agent governance instructions and skill pack

## Session Lessons

- In this uv project, run toolchain commands with `uv run`.
- QML tools should run via uv wrappers:
  `uv run pyside6-qmllint` and `uv run pyside6-qmlformat`.
- For Python and QML changes, use lint first, fix findings, then format.
- Keep implementation and corresponding tests in one atomic commit.
- Split workspace instruction ownership clearly:
  technical constraints in `.github/copilot-instructions.md`,
  workflow and handoff in `AGENTS.md`.
- Runtime note: `uv run temporal` exit code 1 may come from manual interrupt
  after window startup or failed remote SSH connect, not only startup failure.

## Next (Phase D/F)

1. Route SSS separated and post-filtered PCM chunks into recorder sessions.
2. Finalize source inactive timeout behavior under reconnect and jitter.
3. Expose recorder session and output file status in UI.
4. Validate with remote Linux odaslive end-to-end.

## Next Session Start Checklist

1. `git status --short --untracked-files=all`
2. `uv run ruff check src tests`
3. `uv run python -m unittest discover -s tests -p "test_*.py" -v`
4. Focus Phase D gap: stream audio write path + UI recording status.
