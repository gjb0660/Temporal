# PRD: Phase D SSS Routing and Session Visibility

## Goal

Complete the missing SSS audio write path and expose active
recording sessions in UI-facing bridge state.

## Scope

- Route separated and post-filtered PCM chunks to recorder writes.
- Keep fixed channel mapping compatible with odas_web behavior.
- Expose active session summary for operator visibility.
- Keep source lifecycle based start and stop contract unchanged.

## Non-Goals

- Dynamic channel count discovery.
- Speech-to-text pipeline changes.
- Recording management window redesign.

## Functional Requirements

1. Route SSS separated stream to recorder mode `sp`.
2. Route SSS post-filtered stream to recorder mode `pf`.
3. Maintain source_id to channel_index mapping stability across SST updates.
4. Expose `recordingSessions` as appBridge property for QML rendering.
5. Clear session state when streams are stopped.

## Quality Requirements

- Add unittest coverage for channel map reuse.
- Add unittest coverage for separated and post-filtered audio routing.
- Add unittest coverage for session snapshot visibility in appBridge.
- Keep lint and unit tests green for touched files.

## Acceptance Criteria

1. PCM chunks from SSS are written to mapped source sessions.
2. UI can read non-empty `recordingSessions` during active recording.
3. Stopping streams resets recording count and session list.
4. Test suite passes with the new routing and session tests.
