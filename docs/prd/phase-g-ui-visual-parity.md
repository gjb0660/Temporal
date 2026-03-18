# PRD: Phase G UI Visual Parity

## Goal

Deliver a QML live-data page that visually matches the original odas_web page,
switches human-facing UI copy to Chinese, and upgrades the source-location area
from a placeholder into a real rotatable QtQuick3D scene.

## Scope

- Rebuild the main page layout with responsive QML layouts.
- Match the reference page structure, spacing, typography, colors, and panel rhythm.
- Replace the local monitor card with remote odaslive log output.
- Replace the placeholder source-location sphere with a rotatable QtQuick3D scene.
- Unify ODAS control button styling and align the energy-range labels with the slider.
- Keep existing appBridge actions and bindings working.
- Validate with local screenshots and iterative visual adjustment.

## Non-Goals

- Full production chart rendering from live SST history.
- Backend protocol changes beyond minimal read-only UI support if required.

## Functional Requirements

1. The page keeps a stable three-column structure when the window is resized.
2. Header, content panels, and footer remain aligned without absolute page positioning.
3. Source and filter panels continue to bind to appBridge state.
4. The ODAS control area keeps all current actions callable from the UI and uses
   a consistent custom button style.
5. The central 3D visualization supports drag rotation and displays active SST
   source positions when available.
6. The left log panel displays remote `/tmp/odaslive.log` tail output through the bridge.

## Quality Requirements

- Use QML relative layouts, anchors, and size constraints instead of fixed page coordinates.
- Keep touched QML valid under qmllint.
- Preserve readability at the current default size and at narrower widths.

## Acceptance Criteria

1. At the default application size, the page visually matches the reference page
   in overall composition and spacing.
2. At smaller and larger window sizes, columns and sections remain readable and aligned.
3. Source list, filters, and control buttons still reflect live appBridge state.
4. Local static checks pass for touched files.
