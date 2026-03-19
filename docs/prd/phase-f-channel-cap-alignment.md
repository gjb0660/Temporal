# PRD: Phase F Channel-Cap Recording Alignment

## Goal

Align recorder session activation with available SSS channel capacity.
Prevent creating recorder sessions that can never receive audio.

## Scope

- Keep odas_web-compatible fixed 4-channel mapping.
- Start recorder sessions only for mapped source IDs.
- Keep UI recording count aligned with routable sources.
- Add unit tests for over-capacity source frames.

## Non-Goals

- Dynamic channel-count negotiation from runtime stream metadata.
- Changes to ODAS protocol payload schema.
- Multi-host or distributed recorder orchestration.

## Functional Requirements

1. If SST contains more than 4 valid sources,
   only mapped 4 sources enter recorder active state.
2. Audio routing remains source_id <- channel_index mapping based.
3. Recording status in appBridge reflects only routable
   recording sources.
4. Existing reconnect/timeout behavior remains unchanged.

## Quality Requirements

- Add unittest coverage for over-capacity source input.
- Keep ruff, qmllint, and unittest checks green.

## Acceptance Criteria

1. Given 5+ sources in SST,
   appBridge recordingSourceCount does not exceed 4.
2. recordingSessions includes only mapped source IDs.
3. Existing recording tests continue to pass without regression.
