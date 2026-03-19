# Spec: Phase D Source-Driven Auto Recording

## Goal

Implement source lifecycle driven recording for separated and post-filtered streams.

## Scope

- Track source active and inactive transitions.
- Start recording when source appears.
- Stop recording after source disappears or timeout.
- Write WAV files for separated and post-filtered channels.

## Non-Goals

- Cloud storage sync.
- Long-term archive management UI.
- Advanced post-processing pipeline.

## Functional Requirements

1. Use filename format ODAS_{source_id}_{timestamp}_{sp|pf}.wav.
2. Persist per-source recorder state machine.
3. Handle stream drop and source timeout gracefully.
4. Expose recording status summary to UI bridge.

## Quality Requirements

- Add unittest cases for source lifecycle transitions.
- Validate writer behavior for short and empty segments.

## Acceptance Criteria

1. New source triggers recording start automatically.
2. Inactive source triggers stop after configured timeout.
3. Output files follow naming contract and can be opened.
