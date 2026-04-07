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
3. supervisor-only atomic stage close
4. immediate freeze on divergence
5. lookahead is a light gate at each stage close (record `none` with reason if no safe prep exists)
6. final hardening is a final-close gate (if fail, final close is blocked until revalidated)

## Supervisor Role

Treat local supervisor coding as an exception.
Main duties:

1. freeze objective, constraints, ownership, and admission gates
2. open/close parallel windows and arbitrate conflicts serially
3. run gate/pollution evaluation and stage-sync checkpoints
4. close each main stage with one atomic commit

## Worker Handoff

Pass only task-local context:

1. objective
2. ownership boundary
3. constraints and gate profile
4. [worker-execution-card.md](references/worker-execution-card.md)

Avoid passing full orchestration narrative unless required.

## Gates, Tools, and SLO

Use `fast` (in-stage) and `full` (stage-close) gates with baseline-exempt pollution checks.
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
