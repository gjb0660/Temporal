# PRD: Phase B Remote Control and Stream Scaffolding

## Goal

Enable remote odaslive control and baseline ODAS stream client plumbing.

## Scope

- Add SSH private-key connection workflow.
- Implement start and stop command execution for remote odaslive.
- Add tolerant TCP JSON stream client scaffolding for SST and SSL.
- Prepare audio stream channel scaffolding for SSS ports.

## Non-Goals

- Full reconnect policy tuning.
- Full chart rendering and source interaction UI.
- Production-grade recorder state machine.

## Functional Requirements

1. Expose connect, start, stop operations through appBridge slots.
2. Keep stream handlers resilient to malformed chunks and lines.
3. Keep protocol ports aligned with ODAS defaults.
4. Keep socket operations inside backend layer only.

## Quality Requirements

- Keep pyright and qmllint clean for touched files.
- Cover JSON framing behavior with unittest.

## Acceptance Criteria

1. SSH connection test reports clear success or failure state.
2. Remote odaslive commands can be triggered from UI actions.
3. SST and SSL clients can receive and parse test lines without crash.
