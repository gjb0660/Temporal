# PRD: Phase C Sources and Filters MVP

## Goal

Deliver live SST/SSL parsing and UI linkage for source list and filter panel.

## Scope

- Parse SST tracked JSON and SSL potential JSON safely.
- Expose source summary and filter state through appBridge properties.
- Render dynamic source list in QML from appBridge data.
- Keep current chart placeholders unchanged in this phase.

## Non-Goals

- Full elevation/azimut chart rendering.
- 3D sphere source rendering.
- Production recording orchestration.

## Functional Requirements

1. SST parser extracts non-zero source ids and xyz coordinates.
2. SSL parser extracts potential count and optional energy values.
3. appBridge publishes:

   - sourceItems: list of source labels
   - sourceCount: integer
   - potentialCount: integer

4. QML Sources panel binds to sourceItems dynamically.
5. Stream status text includes source and potential counters.

## Quality Requirements

- Pass pyright, qmllint, markdownlint, unittest.
- Handle malformed JSON without crash.

## Acceptance Criteria

1. Given SST with ids [1, 2], UI shows two source entries.
2. Given SSL with three potentials, potential counter is 3.
3. Given malformed lines, app remains responsive.
4. Static checks and tests pass for touched files.
