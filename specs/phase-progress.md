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
- Phase H implementation baseline: preview entrypoint, shared bridge injection,
  and bridge-driven header/center/sidebar wiring completed
- Phase H linkage refinement: removed QML-local preview branching and restored
  preview source-row semantics so sidebar rows represent the scenario catalog
  while charts/3D consume the visible source set
- Phase H preview workflow fix: preview timer startup moved onto a safe
  application path, main-button and listener semantics aligned with runtime,
  and chart/3D motion unified on one tracking clock
- Phase H preview model closure: `trackingFrames` became the shared preview
  time-series source for charts and 3D, right-sidebar unchecked rows no longer
  collapse into empty state, and preview docs/tests were aligned with the
  runtime-oriented bridge contract
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
- Do not collapse preview sidebar rows and visible chart/3D source sets into
  one bridge property; the sidebar needs the full scenario catalog while
  charts and 3D need the filtered visible set.
- Do not start preview simulation timers from `PreviewBridge.__init__`; defer
  startup until the bridge is attached to the GUI thread and the event loop is
  running.
- Preview motion ownership should stay on one simulation clock so chart
  samples, left-bottom start control, and 3D source points cannot drift apart.
- Preview can continue using stable demo data, but the schema should converge
  toward the same normalized runtime model instead of preserving a separate
  preview-only shape.
- Preview right-sidebar numbers should become frame-driven values rather than
  static metadata so UI refresh logic can be tested on the same timeline as
  charts and 3D.

## Next (Preview Model Convergence)

1. Extend preview `trackingFrames` so each source carries per-frame `energy`,
   then derive right-sidebar dynamic values from the current frame instead of
   static scenario metadata.
2. Align preview and runtime around one normalized source-tracking schema,
   keeping preview as stable demo data rather than introducing record/replay
   or abnormal-scene simulation in this phase.
3. Add regression tests that prove right-sidebar numeric values advance on the
   same frame clock as `chartXTicksModel`, chart series, and `sourcePositionsModel`.
4. Validate the full preview interaction set again in `uv run temporal-preview`:
   auto-start listener, standalone listener toggle, main-button stop order,
   unchecked-last-row behavior, and shared chart/3D motion.
5. Re-run remote Linux odaslive end-to-end validation after preview follow-up
   changes are merged.

## Next Session Start Checklist

1. `git status --short --untracked-files=all`
2. `uv run pyright`
3. `uv run python -m unittest tests.test_preview_bridge -v`
4. `uv run temporal-preview`
5. Review the preview model convergence items in
   `specs/plans/phase-h-preview-data-linkage.md`.
