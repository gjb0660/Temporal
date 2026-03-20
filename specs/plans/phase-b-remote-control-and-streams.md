# Spec: Phase B Remote Control and Stream Scaffolding

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
5. Keep SSH config contract explicit and minimal:
   `odas.command`, `odas.args`, `odas.cwd`, `odas.log`.

## SSH Contract

- `remote.username` and `remote.private_key` are optional; empty string means missing.
- `odas.command` is executable name only; do not embed arguments in this field.
- `odas.args` is an array of non-blank strings.
- `odas.cwd` is optional working directory.
- `odas.log` is the runtime log path; default is `odaslive.log`.
- Relative `odas.log` resolves under `odas.cwd` when `odas.cwd` is set.
- Remove legacy key compatibility; do not read deprecated fields.

## SSH Semantics

- Call `paramiko.SSHClient.connect` once and pass optional credentials as `None`.
- Start odaslive in background without `nohup`.
- Apply `odas.cwd` before start, stop, status, and log read when configured.
- Start appends runtime output to `odas.log`.
- Status uses `pgrep -af` against the executable name derived from `odas.command`.
- Stop uses `pkill -f` against the executable name derived from `odas.command`.
- Read log tail from `odas.log` path.

## Quality Requirements

- Keep pyright and qmllint clean for touched files.
- Cover JSON framing behavior with unittest.

## Acceptance Criteria

1. SSH connection test reports clear success or failure state.
2. Remote odaslive commands can be triggered from UI actions.
3. SST and SSL clients can receive and parse test lines without crash.
4. Config loader maps `odas.command`, `odas.args`, `odas.cwd`,
    and `odas.log` to backend model.
5. SSH start command supports optional working directory and does not use `nohup`.
6. SSH status and stop use `pgrep/pkill` with the configured executable name.
