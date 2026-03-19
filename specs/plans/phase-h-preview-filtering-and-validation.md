# Spec: Phase H Preview Filtering and Validation

## Goal

Turn preview mode into a repeatable UI validation workflow by making the
potential energy filter affect all preview views and by standardizing
`temporal-preview` as the UI test entrypoint.

## Scope

- Define preview filtering semantics for source and potential controls.
- Apply energy filtering to sidebar, charts, and 3D source view together.
- Establish screenshot-based validation workflow for preview scenarios.

## Non-Goals

- Production ODAS filtering redesign.
- Automated image diff infrastructure.
- New chart interaction features beyond scenario and filter validation.

## Filter Semantics

- `sourcesEnabled=false`: hide all preview sources from sidebar, charts, and 3D.
- `potentialsEnabled=false`: do not apply energy-range filtering.
- `potentialsEnabled=true`: apply the configured energy range to all preview
  views.

## Filtering Scope

The active preview energy range must filter:

- right sidebar source list
- center-pane elevation chart
- center-pane azimuth chart
- 3D source positions

## Functional Requirements

1. Preview mode reuses the existing right-sidebar filter controls.
2. Energy range changes in preview mode update the visible source set
   immediately.
3. Filtered-out sources disappear from sidebar rows, chart series, and 3D
   points in the same state transition.
4. Preview validation uses `uv run temporal-preview` as the standard operator
   entrypoint.
5. Validation covers both default window size and a narrower width.

## Validation Workflow

1. Launch `uv run temporal-preview`.
2. Verify all four baseline scenarios:
   - `referenceSingle`
   - `hemisphereSpread`
   - `equatorBoundary`
   - `emptyState`
3. For each non-empty scenario:
   - capture a default-size screenshot
   - capture a narrower-width screenshot
   - toggle source visibility
   - enable potential filtering
   - adjust the energy range and confirm filtered source removal
4. Record any scenario where sidebar, charts, and 3D do not remain consistent.

## Quality Requirements

- Keep preview filtering semantics explicit and documented.
- Keep preview validation reproducible across local runs.
- Do not require manual source-code edits to perform preview validation.

## Acceptance Criteria

1. Low-energy preview sources are removed from sidebar, charts, and 3D together.
2. Disabling potential filtering restores the full current scenario source set.
3. `temporal-preview` becomes the documented standard entrypoint for UI preview
   and screenshot validation.
4. Validation can be repeated on the four baseline scenarios without changing
   QML source files.
