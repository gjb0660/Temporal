# Spec: Phase H Preview Data Linkage

## Goal

Promote preview mode into a shared bridge-driven scenario model and remove
local preview/runtime branching from QML. The page should consume finalized
bridge outputs rather than deriving preview behavior inside components.

## Scope

- Keep preview scenario data in Python and expose finalized UI-facing outputs
  from the bridge.
- Drive the header from bridge-provided scenario visibility and nav labels.
- Bind right-sidebar rows, center charts, and 3D source positions directly to
  bridge data.
- Remove local preview fallback logic from `CenterPane.qml`,
  `RightSidebar.qml`, and `SourceSphereView.qml`.
- Support scenario-local source selection state in preview mode.

## Non-Goals

- Energy-range filtering semantics for preview mode.
- Production SST history rendering.
- A preview-only page layout redesign.
- Preserving legacy QML `previewMode` branches for compatibility.

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
   `elevationSeries`, `azimuthSeries`, `chartXTicks`, `headerNavLabels`, and
   `showPreviewScenarioSelector` from the active scenario and preview mode.
3. `AppBridge` exposes matching runtime-safe defaults for the same UI-facing
   properties.
4. The green header bar shows the scenario switcher only when
   `showPreviewScenarioSelector == true`.
5. In preview mode, the scenario switcher replaces the static right-side
   navigation labels rather than appearing beside them.
6. Switching scenarios updates sidebar rows, chart series, and 3D source data
   together in one bridge transition.
7. After switching scenarios, all source ids in the new scenario are selected
   by default.
8. `setSourceSelected()` updates sidebar checked state, visible source ids,
   chart series, and 3D source positions together.
9. `SourceSphereView.qml` renders only bridge-provided source points and does
   not synthesize preview fallback points locally.

## Rules

- A source id keeps the same visual color across list badge, charts, and 3D.
- `emptyState` must render a valid empty UI state and must not fake live source
  ids or preview fallback points.
- Empty source lists render an explicit empty-state message rather than QML
  placeholder rows.
- Preview scenario switching remains invisible in production mode.
- `sourcesEnabled` and `potentialsEnabled` remain UI state only in this phase;
  they do not filter preview data yet.
- QML must not derive preview/runtime display branches from `previewMode` for
  header navigation, chart ticks, source rows, or 3D fallback points.

## Interface Additions

- `sourceRows: list[{sourceId, label, checked, enabled, badge, badgeColor}]`
- `previewScenarioOptions: list[{key, label}]`
- `showPreviewScenarioSelector: bool`
- `headerNavLabels: list[str]`
- `chartXTicks: list[str]`

Production `AppBridge` must expose safe defaults:

- `sourceRows == []`
- `previewScenarioOptions == []`
- `showPreviewScenarioSelector == false`
- `headerNavLabels == ["配置", "录制", "相机"]`
- `chartXTicks == ["0", "200", "400", "600", "800", "1000", "1200", "1400", "1600"]`

## Quality Requirements

- Keep preview linkage deterministic and independent from live ODAS messages.
- Keep scenario changes immediate and side-effect free.
- Avoid duplicating scenario data between QML and Python bridge layers.
- Keep row shaping, tick selection, and header visibility policy out of QML.

## Acceptance Criteria

1. The right sidebar source list is derived from the active preview scenario.
2. Scenario switching updates header selection, sidebar rows, chart series, and
   3D data together.
3. Source badge colors, checked state, and rendered series correspond to the
   same source ids.
4. `emptyState` shows a stable empty layout without fake source rows or fake 3D
   points.
5. QML no longer contains local preview/runtime branch logic for header
   navigation, center-pane ticks, sidebar placeholder rows, or sphere fallback
   points.

## Validation Workflow

- `uv run pyside6-qmllint src/temporal/qml/Main.qml`
- `uv run pyside6-qmllint src/temporal/qml/AppHeader.qml`
- `uv run pyside6-qmllint src/temporal/qml/RightSidebar.qml`
- `uv run pyside6-qmllint src/temporal/qml/CenterPane.qml`
- `uv run pyside6-qmllint src/temporal/qml/SourceSphereView.qml`
- `uv run ruff check src tests`
- `uv run python -m unittest discover -s tests -p "test_*.py" -v`
- Launch `uv run temporal-preview` and verify:
  - the header shows the scenario switcher only when
    `showPreviewScenarioSelector == true`
  - the scenario switcher replaces static navigation in preview mode
  - switching scenarios updates sidebar, charts, and 3D together
  - source checkbox toggles remove and restore the same source across all views
  - `emptyState` shows a stable empty UI without fake source rows
