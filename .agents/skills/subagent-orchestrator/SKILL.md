---
name: subagent-orchestrator
description: General-purpose stage pipeline orchestration for multi-agent development. Use when work spans multiple domains and benefits from file-ownership parallelization, serial stage gates, baseline-aware pollution blocking, delegate-first supervision, and long-run convergence control.
---

# Subagent Orchestrator

## Overview

Use this skill to run a multi-agent implementation pipeline that stays convergent over long sessions.
Prefer delegation, then enforce convergence with serial gates and atomic stage closure.

## Core Rules

1. Think in first principles.
2. Apply Occam's Razor.
3. Automate only high-repeat, high-error links.
4. Slice parallel work by file ownership first.
5. Keep the supervisor delegate-first.
6. Keep final integration and stage closure with the supervisor.
7. Reuse the same agents for the full pipeline.
8. Close agents only after final gate pass.

## Delegate-First Supervision

Treat supervisor local implementation as an exception.
Delegate all non-blocking execution to subagents whenever ownership can be isolated.

Supervisor responsibilities:

- freeze stage objective and boundaries
- assign ownership and concurrency windows
- run convergence gates
- resolve conflicts serially
- perform atomic stage commit

Do not let supervisor become the execution bottleneck.

## Pipeline Contract

Follow a strict timeline:

1. Serial stage freeze.
2. Parallel execution window.
3. Serial convergence review.
4. Atomic stage commit.
5. Stage-sync checkpoint.
6. Next-stage admission.

Allow sub-stage cluster merge when explicitly planned.
Keep one supervisor atomic commit per main stage.

Use [pipeline-template.md](references/pipeline-template.md) for the stage skeleton.

## Load Balancing

Keep supervisor judgment as final authority.
Use evidence to support assignment, not to replace judgment.

Minimum evidence set:

- recent change volume
- current unresolved workload
- conflict hotspot signals

Prefer least-loaded capable agent first.
Rebalance only at stage boundaries or explicit freeze points.

## Gates and Pollution Policy

Run two gate tiers:

- fast gate during parallel iteration
- full gate at stage closure

Run pollution checks with baseline exemption:

- capture baseline at stage entry
- block only incremental pollution introduced in the stage

Use:

- [gate-checklists.md](references/gate-checklists.md)
- `scripts/run_stage_gate.py`
- `scripts/check_pollution_baseline.py`

## Divergence and Stability

Stability SLO:

- keep continuous convergence for 60 minutes with no loss of control

Divergence trigger examples:

- repeated gate failure with no net progress
- repeated ownership overlap conflicts
- uncontrolled retry loops

On divergence:

1. Freeze parallel window immediately.
2. Return to the latest stable checkpoint.
3. Arbitrate serially.
4. Reopen parallel only with updated boundaries.

## Execution Record

Log each stage with the required fields in
[execution-record-template.md](references/execution-record-template.md).

Do not skip:

- acceptance mapping
- pollution check
- stage-sync status
- atomic submit summary
- unresolved risks

## Script Usage

Run fast/full stage gates:

```bash
python scripts/run_stage_gate.py --profile fast --commands-file .tmp/gates.json --report .tmp/fast-gate.json
python scripts/run_stage_gate.py --profile full --commands-file .tmp/gates.json --report .tmp/full-gate.json
```

Capture and compare pollution baseline:

```bash
python scripts/check_pollution_baseline.py --capture --baseline .tmp/stage-baseline.json
python scripts/check_pollution_baseline.py --compare --baseline .tmp/stage-baseline.json --report .tmp/pollution-report.json
```

## Mandatory Forward-Test Before Release

For major skill updates, run one blind subagent forward-test:

1. Pass only skill path plus a realistic orchestration request.
2. Do not leak expected output or diagnosis.
3. Verify output includes:
   - explicit serial/parallel segmentation
   - stage gates and convergence conditions
   - checkpoint and freeze-on-divergence behavior
   - delegate-first supervision stance
