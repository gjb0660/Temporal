# Spec: Phase H Preview Data Linkage

## Goal

Implement the next Phase H step by promoting preview mode into a shared
scenario model that drives the header switcher, right-sidebar source list,
center charts, and 3D source sphere together.

## Scope

- Extend preview scenario data into a `sources`-first Python model.
- Drive header scenario options from bridge-provided preview data.
- Bind right-sidebar source rows to the active preview scenario.
- Keep center charts and 3D source positions derived from the same active
  scenario.
- Support scenario-local source selection state in preview mode.

## Non-Goals

- Energy-range filtering semantics for preview mode.
- Production SST history rendering.
- A preview-only page layout redesign.

## Data Model

Each preview scenario must define:

- `key`
- `displayName`
- `sources[{id, x, y, z, energy, color}]`
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

1. Preview scenario data is stored in one shared Python model consumed by the
   preview bridge.
2. `PreviewBridge` derives `sourceRows`, `sourceIds`, `sourcePositions`,
   `elevationSeries`, and `azimuthSeries` from the active scenario.
3. `PreviewBridge` exposes `previewScenarioOptions` for the header switcher as
   `list[{key, label}]`.
4. The green header bar shows a scenario switcher only when
   `appBridge.previewMode == true`.
5. Switching scenarios updates sidebar rows, chart series, and 3D source data
   together in one bridge transition.
6. After switching scenarios, all source ids in the new scenario are selected
   by default.
7. `setSourceSelected()` updates sidebar checked state, visible source ids,
   chart series, and 3D source positions together.

## Rules

- A source id keeps the same visual color across list badge, charts, and 3D.
- `emptyState` must render a valid empty UI state and must not fake live source
  ids.
- Preview scenario switching remains invisible in production mode.
- `sourcesEnabled` and `potentialsEnabled` remain UI state only in this phase;
  they do not filter preview data yet.

## Interface Additions

- `sourceRows: list[{sourceId, label, checked, enabled, badge, badgeColor}]`
- `previewScenarioOptions: list[{key, label}]`

Production `AppBridge` must expose safe defaults:

- `sourceRows == []`
- `previewScenarioOptions == []`

## Quality Requirements

- Keep preview linkage deterministic and independent from live ODAS messages.
- Keep scenario changes immediate and side-effect free.
- Avoid duplicating scenario data between QML and Python bridge layers.
- Keep row shaping and badge color mapping out of `Main.qml`.

## Acceptance Criteria

1. The right sidebar source list is derived from the active preview scenario.
2. Scenario switching updates header selection, sidebar rows, chart series, and
   3D data together.
3. Source badge colors, checked state, and rendered series correspond to the
   same source ids.
4. `emptyState` shows a stable empty layout without fake source rows or fake 3D
   points.

## Validation Workflow

- `uv run pyside6-qmllint src/temporal/qml/Main.qml`
- `uv run pyside6-qmllint src/temporal/qml/AppHeader.qml`
- `uv run pyside6-qmllint src/temporal/qml/RightSidebar.qml`
- `uv run pyside6-qmllint src/temporal/qml/CenterPane.qml`
- `uv run ruff check src tests`
- `uv run python -m unittest discover -s tests -p "test_*.py" -v`
- Launch `uv run temporal-preview` and verify:
  - the header shows the scenario switcher only in preview mode
  - switching scenarios updates sidebar, charts, and 3D together
  - source checkbox toggles remove and restore the same source across all views
  - `emptyState` shows a stable empty UI without fake source rows
