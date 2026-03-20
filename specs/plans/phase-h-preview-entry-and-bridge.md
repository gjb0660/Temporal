# Spec: Phase H Preview Entry and Bridge

## Goal

Promote preview mode from a local QML switch into a standard application
entrypoint exposed as `uv run temporal-preview`.

## Scope

- Add a dedicated preview startup script.
- Provide a `PreviewBridge` that is injected as `appBridge`.
- Keep preview and production entrypoints on the same `Main.qml`.
- Define the minimum preview bridge API required by existing left, center, and
  right panels.

## Implemented Shape

- `pyproject.toml` exposes:
  - `temporal = "temporal.main:main"`
  - `temporal-preview = "temporal.preview_main:main"`
- `src/temporal/app.py` exposes a shared `run_with_bridge()` startup helper.
- `src/temporal/preview_main.py` launches `Main.qml` through
  `run_with_bridge(PreviewBridge())`.
- `src/temporal/preview_bridge.py` owns preview state and preview-safe control
  behavior.
- `src/temporal/preview_data.py` is the Python source of truth for preview
  scenarios.

## Non-Goals

- Full preview data linkage for the right sidebar.
- In-UI preview scenario switching controls.
- Full preview filtering semantics for potential energy range.
- New production transport or recorder behavior.

## Functional Requirements

1. `uv run temporal-preview` launches the existing main window layout without
   requiring manual QML edits.
2. Preview mode uses `PreviewBridge`, while `uv run temporal` continues to use
   `AppBridge`.
3. Both bridges are exposed to QML as `appBridge`.
4. `PreviewBridge` provides safe implementations for all QML methods and
   properties currently used by:
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
- Keep preview fixture data in Python rather than local QML JavaScript.

## Acceptance Criteria

1. `uv run temporal-preview` launches the main UI successfully.
2. `uv run temporal` behavior remains unchanged.
3. No QML file edits are required to enter preview mode.
4. Existing page sections render using preview bridge data and no-op controls
   without runtime errors.
5. `CenterPane.qml` no longer imports a local preview fixture script.

## Validation Workflow

- `uv run pyside6-qmllint src/temporal/qml/Main.qml`
- `uv run pyside6-qmllint src/temporal/qml/CenterPane.qml`
- `uv run pyside6-qmllint src/temporal/qml/RightSidebar.qml`
- `uv run ruff check src tests`
- `uv run python -m unittest discover -s tests -p "test_*.py" -v`
- Launch `uv run temporal-preview` and verify:
  - the main layout renders without editing QML
  - center pane shows preview charts and 3D data
  - right sidebar still shows placeholder source rows in this phase
  - left sidebar actions only change local preview state
