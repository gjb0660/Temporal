# In Progress

## Usage

- Check this file before starting a new feature.
- Treat entries below as the live routing and state source.
- Use `blocked` only when an external dependency or input
  stops direct progress.
- Do not treat blocked features as directly codable.

## Active Features

- Phase H preview entry and bridge
  State: planned
  Summary: Implement Phase H preview entry and bridge so
  `uv run temporal-preview` becomes the standard UI test entrypoint.
  Spec: [phase-h-preview-entry-and-bridge.md](./plans/phase-h-preview-entry-and-bridge.md)

- Phase H preview data linkage
  State: planned
  Summary: Implement Phase H preview data linkage for right sidebar source rows,
  center charts, and 3D point synchronization.
  Spec: [phase-h-preview-data-linkage.md](./plans/phase-h-preview-data-linkage.md)

- Phase H preview filtering and validation
  State: planned
  Summary: Implement Phase H preview filtering and screenshot workflow so the
  energy range control filters sidebar, charts, and 3D together.
  Spec: [phase-h-preview-filtering-and-validation.md](./plans/phase-h-preview-filtering-and-validation.md)

- Remote runtime validation and reconnect hardening
  State: specified
  Summary: Validate remote Linux odaslive end-to-end: SSH connect, start/stop
  lifecycle, remote log tail, SST/SSL updates, and recorder session visibility.
  Spec: [phase-f-integration-runbook-risks.md](./plans/phase-f-integration-runbook-risks.md)

## Recently Completed (Last 7 Days)

- Phase A: project skeleton + runnable PySide6/QML shell
  Spec: [phase-a-project-skeleton.md](./plans/phase-a-project-skeleton.md)

- Phase B: SSH control + ODAS stream client scaffolding
  Spec: [phase-b-remote-control-and-streams.md](./plans/phase-b-remote-control-and-streams.md)

- Phase C: source list and filters linked to SST/SSL stream state
  Spec: [phase-c-sources-filters.md](./plans/phase-c-sources-filters.md)

- Phase D: recorder lifecycle, filename contract,
  and appBridge linkage baseline
  Spec: [phase-d-auto-recording.md](./plans/phase-d-auto-recording.md)

- Phase D extension: SSS routing and recorder session visibility
  Spec: [phase-d-sss-routing-and-session-visibility.md](./plans/phase-d-sss-routing-and-session-visibility.md)

- Phase F extension: recorder activation aligned with channel mapping
  Spec: [phase-f-channel-cap-alignment.md](./plans/phase-f-channel-cap-alignment.md)

- Phase F: integration validation, runbook, and risks documentation
  Spec: [phase-f-validation-and-delivery.md](./plans/phase-f-validation-and-delivery.md)

- Phase G: Chinese UI parity pass, remote odaslive log panel,
  and 3D source view scaffolding
  Spec: [phase-g-ui-visual-parity.md](./plans/phase-g-ui-visual-parity.md)

- Phase G extension: source sphere rebuild, empty-state cleanup,
  and default Z-up orientation
  Spec: [phase-g-ui-visual-parity.md](./plans/phase-g-ui-visual-parity.md)

- Phase H preview planning baseline: entry, linkage,
  and validation specs defined
  Spec: [phase-h-preview-entry-and-bridge.md](./plans/phase-h-preview-entry-and-bridge.md)

- Rule update: Pyright config aligned with Facade and namespace package rule
  Spec: [phase-e-agent-governance.md](./plans/phase-e-agent-governance.md)

- Phase E: Agent governance files
  (`.github/copilot-instructions.md`, `AGENTS.md`, `.github/instructions/*`)
  Spec: [phase-e-agent-governance.md](./plans/phase-e-agent-governance.md)

- Rule update: `specs/in-progress.md` only updated during handoff stage
  Spec: [phase-e-agent-governance.md](./plans/phase-e-agent-governance.md)

- Rule update: governance language ownership deduplicated,
  and historical handoff normalization started
  Spec: [phase-e-agent-governance.md](./plans/phase-e-agent-governance.md)

- Rule update: root-cause-first prompt aligned with
  question-first exploration and no-assumption governance
  Spec: [phase-e-agent-governance.md](./plans/phase-e-agent-governance.md)

## Session Lessons

- In this uv project, run toolchain commands with `uv run`.
- For Python and QML changes, use lint first,
  fix findings, then format.
- Keep implementation and corresponding tests in one atomic commit.
- Preview workflows should use a dedicated application entrypoint.
- Keep specs and handoff docs on English headings with concise Chinese body.
- For root-cause repair prompts, clarify first and do not proceed on
  unstated assumptions.
