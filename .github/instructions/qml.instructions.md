---
description: "Use when: building or modifying QML pages and components for ODAS visualization and operator interactions."
applyTo: ["src/temporal/ui/qml/**"]
---

# QML Instructions

- Keep layout aligned with ODAS Studio information hierarchy.
- Do not implement protocol/business logic in QML.
- All actions route through `appBridge` slots.
- Source colors must remain stable per source id.
- Filters must be reversible and side-effect free.
