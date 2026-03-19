# Spec: Phase G UI Visual Parity Round 2

## Goal

Deliver a second visual-parity pass for the QML live-data page so that it more
closely matches the ODAS Studio reference in layout rhythm, control simplicity,
3D source-location readability, and Windows-native visual tone.

## Scope

- Keep the existing three-column page structure and Chinese human-facing copy.
- Refine the left column so the ODAS log area and ODAS control area use an
  overall height split close to 6:4.
- Simplify the ODAS control area to two operator-facing toggle buttons:
  start/stop and listen/stop-listening.
- Expose bridge state needed for button text, enabled state, and safe toggles.
- Enlarge the 3D source-location sphere and add a clear XYZ axis indicator.
- Reduce the header brand text size and shift the page theme closer to a
  Windows-native light application style.
- Validate by taking local screenshots after implementation and iterating until
  the page visually meets the reference checkpoints.

## Non-Goals

- Full production chart rendering from live SST history.
- New protocol features or backend transport changes outside bridge state and
  toggle behavior needed by the UI.
- Pixel-perfect cloning of every reference detail.
- A dedicated `uv run temporal-preview` entrypoint.
- In-UI preview scenario switching controls.
- Full-page preview energy filtering across source list, charts, and 3D view.

## Functional Requirements

1. The page keeps a stable three-column structure when the window is resized.
2. Header, content panels, and footer remain aligned without absolute page positioning.
3. Source and filter panels continue to bind to `appBridge` state.
4. The ODAS control area shows only two buttons in QML:
   `启动/停止` and `监听/停止监听`.
5. The start toggle connects SSH first when needed, starts remote odaslive,
   and stops both odaslive and active streams when toggled off.
6. The listen toggle starts or stops streams and remains disabled when remote
   odaslive is not running.
7. The left log panel continues to display remote `/tmp/odaslive.log` tail output.
8. The source-location area remains rotatable and displays active SST source
   positions when available.
9. The source-location area includes a clearly visible XYZ axis indicator in the
   lower-left overlay.

## Interface Additions

- `AppBridge.remoteConnected: bool`
- `AppBridge.odasRunning: bool`
- `AppBridge.streamsActive: bool`
- `AppBridge.toggleRemoteOdas()`
- `AppBridge.toggleStreams()`

Existing low-level bridge slots remain available for compatibility, but QML
uses the new toggle entry points.

## Current Preview Limitations

- Preview usage still depends on local QML properties rather than a standard
  application entrypoint.
- The right sidebar source list is not yet driven by the same preview scenario
  model as the center charts and 3D source view.
- The lower-right potential energy control is not yet defined as a full-page
  preview filtering mechanism.

## Forward Constraints

- Future preview work must inject state through `appBridge` rather than ad hoc
  QML-only flags.
- Future UI testing must use a dedicated preview entrypoint instead of editing
  `Main.qml` to enable preview mode.
- Future preview datasets must drive both the center pane and the right sidebar
  from one shared scenario model.

## Quality Requirements

- Use QML relative layouts, anchors, and size constraints instead of fixed page coordinates.
- Keep touched QML valid under qmllint and format it with `pyside6-qmlformat`.
- Keep touched Python files clean under `ruff check` and `ruff format`.
- Preserve readability at the default application size and at narrower widths.
- Keep dynamic status or log text inside bounded containers; do not let it
  resize the control-button row.

## Acceptance Criteria

1. At the default application size, the page visually matches the reference in
   overall composition, spacing, and hierarchy.
2. The left ODAS log area and left ODAS control area maintain an overall height
   split close to 6:4.
3. The left control area shows only the two toggle buttons and their state is
   consistent with bridge status.
4. The 3D source-location sphere is visually larger than the current version
   and occupies the main emphasis of its section.
5. The lower-left XYZ indicator is clearly visible without zooming.
6. The `Temporal Studio` title is visibly smaller than the current version.
7. The page theme reads as a Windows-native light UI with product branding,
   rather than a heavily custom green-tinted interface.
8. Local static checks and unit tests pass for touched files.

## Validation Workflow

1. Update this spec first.
2. Implement bridge, QML, and tests.
3. Run lint and format for touched Python and QML files.
4. Launch the app and capture screenshots at:
   - default size `1188x794`
   - a narrower width around `1024`
5. Compare screenshots against the reference and iterate until all acceptance
   criteria above are satisfied.

## Preventive Rules

- Keep the source-location area as a recognizable interactive 3D view; do not
  regress it to a placeholder or unreadable point cloud.
- Keep listen control blocked when odaslive is not running; do not let QML
  bypass backend safety checks.
- Keep left-column card proportions explicit in layout constraints so future
  text changes do not collapse the control area again.
