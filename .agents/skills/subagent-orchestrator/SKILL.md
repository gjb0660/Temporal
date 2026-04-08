---
name: subagent-orchestrator
description: General-purpose stage pipeline orchestration for multi-agent development. Use when work spans multiple domains and benefits from file-ownership parallelization, serial stage gates, baseline-aware pollution blocking, delegate-first supervision, and long-run convergence control.
---

# Subagent Orchestrator

## Core Contract

Keep this skill minimal and delegate-first.
Use first principles and Occam's Razor: keep only high-repeat, high-error controls.

Hard lines:

1. strict ownership boundaries
2. serial stage gates with bounded parallel windows
3. main stage or approved cluster close through `$converge-commit` atomic submit
4. immediate freeze on divergence
5. lookahead is a light gate at each stage close (record `none` with reason if no safe prep exists)
6. final hardening is a final-close gate (if fail, final close is blocked until revalidated)

## Boundary With Minimal ESPC

`$minimal-espc` decides whether delegated mode is enabled.
This skill executes multi-agent orchestration only after delegation is on.
Use `$minimal-espc` admission status block as input:
`source/category/stage/sync-risk/delegation`.
Do not redefine delegated trigger rules here
(`cross-layer + contract/Acceptance`) to avoid parallel decision sources.

## Supervisor Role

Treat local supervisor coding as an exception.
Main duties:

1. freeze objective, constraints, ownership, and admission gates
2. open/close parallel windows and arbitrate conflicts serially
3. run gate, pollution, and stage-sync evaluation
4. execute stage close according to hard line #3

## Worker Handoff

Pass only task-local context:

1. objective
2. ownership boundary
3. constraints and gate profile
4. [worker-execution-card.md](references/worker-execution-card.md)

Avoid passing full orchestration narrative unless required.

## Gates, Tools, and SLO

Use `fast` (in-stage) and `full` (stage-close) gates with baseline-exempt pollution checks.
Stage-close field names and pass/fail semantics are defined only in
[Stage-Close Output Contract (SSOT)](references/supervisor-stage-playbook.md#stage-close-output-contract-ssot).
Do not restate gate field lists in this file.

`fast/full` are execution profiles, not replacement terms for final pass/fail semantics.

Prefer built-in scripts; equivalent mechanisms are allowed:

- `scripts/run_stage_gate.py`
- `scripts/check_pollution_baseline.py`

`SLO` (Service Level Objective) here means the 60-minute stability target.
It is a background capability target, not a close gate.

## Divergence Policy

On divergence:

1. freeze parallel window immediately
2. return to latest stable checkpoint
3. arbitrate serially
4. reopen with revised ownership boundaries

## Consistency Check

Before publishing updates, verify supervisor rules and worker card remain aligned on:

1. gate vocabulary
2. pass/fail semantics
3. divergence behavior
4. ownership language
5. output contract source
   ([Stage-Close Output Contract (SSOT)](references/supervisor-stage-playbook.md#stage-close-output-contract-ssot) only)
6. appendix records stay evidence-only
   (no primary-field aliases or derived gate-summary fields)

## References

- [pipeline-template.md](references/pipeline-template.md)
- [supervisor-stage-playbook.md](references/supervisor-stage-playbook.md)
- [worker-execution-card.md](references/worker-execution-card.md)

## Mandatory Forward-Test

Run one blind subagent forward-test for major updates.
Pass only skill path and realistic request.
Do not leak expected output or diagnosis.
Expect output to include:

1. explicit serial/parallel segmentation
2. stage gates and convergence conditions
3. required lookahead handling
4. required final hardening handling
5. checkpoint and freeze-on-divergence behavior
6. delegate-first supervision stance
