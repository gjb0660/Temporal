# PRD: Phase H Preview Entry and Bridge

## Goal

Promote preview mode from a local QML development switch into a standard
application entrypoint exposed as `uv run temporal-preview`.

## Scope

- Add a dedicated preview startup script.
- Provide a `PreviewBridge` that is injected as `appBridge`.
- Keep preview and production entrypoints on the same `Main.qml`.
- Define the minimum preview bridge API required by existing left, center, and
  right panels.

## Non-Goals

- Full preview data linkage for the right sidebar.
- In-UI preview scenario switching controls.
- Full preview filtering semantics for potential energy range.
- New production transport or recorder behavior.

## Functional Requirements

1. `uv run temporal-preview` launches the existing main window layout without
   requiring any manual QML edits.
2. Preview mode uses `PreviewBridge`, while `uv run temporal` continues to use
   `AppBridge`.
3. Both bridges are exposed to QML as `appBridge`.
4. `PreviewBridge` provides safe implementations for all QML methods and
   properties already used by:
   - left sidebar controls and status text
   - center pane chart and 3D bindings
   - right sidebar source and filter controls
5. Preview left-column actions toggle local preview state only and never start
   SSH, sockets, or live ODAS streams.

## Interface Additions

- `previewMode: bool`
- `previewScenarioKey: str`
- `previewScenarioKeys: list[str]`
- `setPreviewScenario(key: str)`
- `elevationSeries: list[dict]`
- `azimuthSeries: list[dict]`

Production bridge returns safe empty defaults for preview-only properties so
QML can bind the same interface in both entrypoints.

## Quality Requirements

- Keep `Main.qml` shared between preview and production.
- Keep preview bridge behavior deterministic and local-only.
- Do not require QML branching on different bridge object names.

## Acceptance Criteria

1. `uv run temporal-preview` launches the main UI successfully.
2. `uv run temporal` behavior remains unchanged.
3. No QML file edits are required to enter preview mode.
4. Existing page sections can render using preview bridge data and no-op
   controls without runtime errors.

## Validation Workflow

1. Add the `temporal-preview` script entry.
2. Launch `uv run temporal-preview`.
3. Verify the page loads with the same layout shell as production.
4. Verify left sidebar buttons and right sidebar controls no longer depend on
   live backend connectivity in preview mode.
