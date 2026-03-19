# Spec: Phase H Preview Data Linkage

## Goal

Upgrade preview data from a center-pane-only fixture into a shared scenario
model that drives the right sidebar source list, the center charts, and the 3D
source view together.

## Scope

- Define a shared preview scenario data model.
- Bind the right sidebar source list to current preview scenario data.
- Add in-UI preview scenario switching.
- Keep scenario switching inside the preview UI rather than command-line flags.

## Non-Goals

- Full preview energy filtering semantics.
- Production SST history rendering.
- Preview-specific page layout redesign.

## Data Model

Each preview scenario must define:

- `key`
- `displayName`
- `sources[{id, x, y, z, energy}]`
- `elevationSeries`
- `azimuthSeries`
- optional `status`
- optional `remoteLogLines`

Baseline scenarios:

- `referenceSingle`
- `hemisphereSpread`
- `equatorBoundary`
- `emptyState`

## Functional Requirements

1. Preview scenario data is stored in one shared model consumed by the preview
   bridge.
2. The right sidebar source list renders from the current scenario rather than
   from static placeholder rows.
3. The center charts and 3D source view render from the same current scenario.
4. Preview mode exposes a scenario switcher in the UI.
5. Switching scenarios updates:
   - source rows in the right sidebar
   - chart series in the center pane
   - 3D source positions and colors
6. After switching scenarios, all sources in the new scenario start selected by
   default.

## Rules

- A source id keeps the same visual color across list badge, charts, and 3D.
- `emptyState` must render a valid empty UI state and must not fake live source
  ids.
- Preview scenario switching is only visible in preview mode.

## Quality Requirements

- Keep preview linkage deterministic and independent from live ODAS messages.
- Keep scenario changes immediate and side-effect free.
- Avoid duplicating scenario data between QML and Python bridge layers.

## Acceptance Criteria

1. The right sidebar source list is derived from the active preview scenario.
2. Scenario switching updates sidebar, charts, and 3D content together.
3. Source badges, checked state, and rendered series correspond to the same
   source ids.
4. `emptyState` shows a stable empty layout without pretending source data
   exists.

## Validation Workflow

1. Launch `uv run temporal-preview`.
2. Switch through all baseline scenarios in the UI.
3. Confirm the right sidebar and center pane update together for each scenario.
4. Confirm all source rows are selected by default after each scenario change.
