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
6. Keep ODAS stream direction explicit:
   remote odaslive pushes to Temporal listeners.

## SSH Contract

- `remote.username` and `remote.private_key` are optional; empty string means missing.
- `odas.command` is executable name only; do not embed arguments in this field.
- `odas.args` is an array of non-blank strings.
- `odas.cwd` is optional working directory.
- `odas.log` is the runtime log path; default is `odaslive.log`.
- Relative `odas.log` resolves under `odas.cwd` when `odas.cwd` is set.
- Derive the control pid path from `odas.log`:
  replace the last extension with `.pid`, or append `.pid` when no extension exists.
- Remove legacy key compatibility; do not read deprecated fields.

## Stream Contract

- `streams.listen_host` is the Temporal local bind address for SST/SSL/SSS listeners.
- If `streams.listen_host` is omitted, default to `0.0.0.0`
  so remote ODAS can connect through any reachable local interface.
- When `streams.listen_host` is `0.0.0.0` or `::`,
  treat it as a bind-only wildcard and skip strict cfg host equality validation.
- `sst_port`, `ssl_port`, `sss_sep_port`, and `sss_pf_port`
  are Temporal local listening ports.
- Do not infer stream host from `remote.host`.

## SSH Semantics

- Call `paramiko.SSHClient.connect` once and pass optional credentials as `None`.
- Start odaslive in background without `nohup`.
- Apply `odas.cwd` before start, stop, status, and log read when configured.
- Start appends runtime output to `odas.log`
  and writes the spawned pid into the derived pid file.
- Treat one config target as one derived pid file and one controlled instance.
- Status reads only the derived pid file and validates:
  pid file exists, pid is numeric, `kill -0` succeeds,
  `/proc/<pid>/cmdline` exactly matches `odas.command + odas.args`,
  and `/proc/<pid>/cwd` exactly matches `odas.cwd` when configured.
- Stop targets only the pid recorded in the derived pid file.
- Read log tail from `odas.log` path.
- Treat validated process existence as the only source of truth
  for "odaslive has started".
- Do not treat `start_odaslive()` exit code alone as proof that odaslive is running.
- Verify startup by polling `status()` every 200 ms for up to 2 seconds.
- Expose three UI lifecycle states: stopped, starting, running.
- Adopt a remote instance after connect only when the same derived pid file is valid.
- Treat a same-name process without the derived pid file as "not running".
- Automatically delete stale or invalid pid files and treat them as "not running".
- Prefer the latest non-empty remote log line as the startup failure reason.
- Fall back to start command stderr or stdout when the log does not explain the failure.
- Wrap remote log panel lines in the UI instead of forcing horizontal scrolling.
- Filter raw startup failure details into a short human-readable reason
  before showing them in the status panel.
- Keep the raw log text in the log panel for diagnosis; only the status panel
  uses the filtered reason.
- Resolve relative `odas.cwd` against remote `$HOME`,
  not the login shell working directory.
- Before launching odaslive, validate that:
  the resolved working directory exists,
  the configured command is executable,
  the referenced ODAS cfg file exists,
  and the active cfg sink targets point at `streams.listen_host`
  and the configured ports.
- Do not validate cfg sinks by grepping the whole cfg text;
  ignore comments, examples, disabled blocks, and unrelated numbers.
- Treat preflight failure as a startup failure.
- If local listeners are not active when remote odaslive starts,
  Temporal must start them before launching odaslive.

## Stream Semantics

- Temporal listens locally for SST/SSL JSON streams and SSS PCM streams.
- Remote odaslive actively connects to those listeners.
- Treat `streamsActive=True` as proof that all configured local listeners
  have already completed `bind + listen`.
- `OdasClient.start()` must fail synchronously when any listener cannot bind,
  and it must roll back listeners that were already started in the same call.
- Listener sockets must accept a connection, read until disconnect,
  and then continue accepting later reconnects.

## Quality Requirements

- Keep pyright and qmllint clean for touched files.
- Cover JSON framing behavior with unittest.

## Acceptance Criteria

1. SSH connection test reports clear success or failure state.
2. Remote odaslive commands can be triggered from UI actions.
3. SST and SSL clients can receive and parse test lines without crash.
4. Config loader maps `odas.command`, `odas.args`, `odas.cwd`,
    `odas.log`, and `streams.listen_host` to backend model.
5. SSH start command supports optional working directory and does not use `nohup`.
6. SSH status and stop use the derived pid file and process identity validation.
7. Left-panel status says "starting" until process existence is verified.
8. Left-panel status never says "started" when odaslive failed to stay running.
9. Connection adopts only instances backed by the derived pid file.
10. Remote log text wraps in the left log panel.
11. The left status panel shows a filtered human-readable failure reason
    instead of raw shell paths and traces.
12. Temporal local listeners are started before remote odaslive launches.
