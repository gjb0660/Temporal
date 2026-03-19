# Temporal Phase Progress

## Completed

- Phase A: project skeleton + runnable PySide6/QML shell
- Phase B: SSH control + ODAS stream client scaffolding
- Phase C: source list and filters linked to SST/SSL stream state
- Phase D: recorder lifecycle, filename contract, and appBridge linkage baseline
- Phase D extension: SSS routing and recorder session visibility
- Phase F extension: recorder activation aligned with channel mapping
- Phase F: integration validation, runbook, and risks documentation
- Phase G: Chinese UI parity pass, remote odaslive log panel,
  and 3D source view scaffolding
- Phase G extension: source sphere rebuild, empty-state cleanup,
  and default Z-up orientation
- Phase H preview planning baseline: entry, linkage,
  and validation PRDs defined
- Rule update: Pyright config aligned with Facade and namespace package rule
- Phase E: Agent governance files
  (`.github/copilot-instructions.md`, `AGENTS.md`, `.github/instructions/*`)
- Rule update: `docs/phase-progress.md` only updated during handoff stage

## PRD Index

- docs/prd/phase-a-project-skeleton.md
- docs/prd/phase-b-remote-control-and-streams.md
- docs/prd/phase-c-sources-filters.md
- docs/prd/phase-d-auto-recording.md
- docs/prd/phase-d-sss-routing-and-session-visibility.md
- docs/prd/phase-e-agent-governance.md
- docs/prd/phase-f-channel-cap-alignment.md
- docs/prd/phase-f-validation-and-delivery.md
- docs/prd/phase-f-integration-runbook-risks.md
- docs/prd/phase-g-ui-visual-parity.md
- docs/prd/phase-h-preview-entry-and-bridge.md
- docs/prd/phase-h-preview-data-linkage.md
- docs/prd/phase-h-preview-filtering-and-validation.md
- docs/prd/copilot-to-codex-skill.md

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
- `daf2281` phase-d: route sss audio and expose recording sessions
- `37b3679` phase-f: align recorder activation with channel mapping
- `e40a929` docs: update phase progress guidelines for session handoff
- `86717e1` phase-f: finalize integration validation and ops docs
- `3a67f18` docs: add copilot-to-codex skill prd file
- `22786f5` ui: refine phase g ui parity and odas controls
- `816f7c0` docs: add ui prd for main windows
- `295d921` ui: rebuild center pane preview and source sphere view
- `1a2c689` ui: clear empty-state center pane placeholders
- `8863e3f` docs: add phase h-j preview planning prds

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
- Large QML pages become hard to iterate quickly; split reusable controls and
  panels before visual polish to keep UI fixes isolated and reviewable.
- Dynamic status/log text must live inside bounded containers so it does not
  resize action rows or break panel rhythm.
- Preview workflows should use a dedicated application entrypoint instead of
  toggling local QML flags.
- Preview datasets should drive the right sidebar and center pane from one
  shared scenario model.

## Next (UI Finish and Runtime Validation)

1. Implement Phase H preview entry and bridge so `uv run temporal-preview`
   becomes the standard UI test entrypoint.
2. Implement Phase H preview data linkage for right sidebar source rows,
   center charts, and 3D point synchronization.
3. Implement Phase H preview filtering and screenshot workflow so the energy
   range control filters sidebar, charts, and 3D together.
4. Run full local quality gates with uv wrappers:
   `uv run ruff check src tests`,
   `uv run pyside6-qmllint src/temporal/qml/Main.qml`,
   `uv run python -m unittest discover -s tests -p "test_*.py" -v`.
5. Validate remote Linux odaslive end-to-end:
   SSH connect, start/stop lifecycle, remote log tail, SST/SSL updates,
   and recorder session visibility.
6. Finalize reconnect and source inactive timeout behavior under jitter.

## Next Session Start Checklist

1. `git status --short --untracked-files=all`
2. `uv run ruff check src tests`
3. `uv run pyside6-qmllint src/temporal/qml/Main.qml`
4. `uv run python -m unittest discover -s tests -p "test_*.py" -v`
5. Execute runbook smoke test and collect artifacts under `recordings/`.
6. Read the Phase H preview PRDs and begin implementation from
   `temporal-preview` entry.
