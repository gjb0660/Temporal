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
  and validation specs defined
- Rule update: Pyright config aligned with Facade and namespace package rule
- Phase E: Agent governance files
  (`.github/copilot-instructions.md`, `AGENTS.md`, `.github/instructions/*`)
- Rule update: `specs/phase-progress.md` only updated during handoff stage

## Spec Index

- specs/plans/phase-a-project-skeleton.md
- specs/plans/phase-b-remote-control-and-streams.md
- specs/plans/phase-c-sources-filters.md
- specs/plans/phase-d-auto-recording.md
- specs/plans/phase-d-sss-routing-and-session-visibility.md
- specs/plans/phase-e-agent-governance.md
- specs/plans/phase-f-channel-cap-alignment.md
- specs/plans/phase-f-validation-and-delivery.md
- specs/plans/phase-f-integration-runbook-risks.md
- specs/plans/phase-g-ui-visual-parity.md
- specs/plans/phase-h-preview-entry-and-bridge.md
- specs/plans/phase-h-preview-data-linkage.md
- specs/plans/phase-h-preview-filtering-and-validation.md
- specs/copilot-to-codex-skill.md

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
6. Read the Phase H preview specs and begin implementation from
   `temporal-preview` entry.
