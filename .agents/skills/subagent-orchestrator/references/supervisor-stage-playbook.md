# Supervisor Stage Playbook

Use this page as the single supervisor reference for stage pipeline execution.

## Core Operating Rules

1. Start from first principles, then keep only the minimum controls needed.
2. Apply Occam's Razor: automate only high-repeat, high-error links.
3. Delegate by default; local supervisor coding is an exception.
4. Reuse the same agents through the full pipeline, then close after final gate pass.
5. Require lookahead planning at each stage close; if none is safe, record `none`.
6. Require a final hardening round with high-risk simulation records.

## Time-Ordered Pipeline Contract

For each stage:

1. Serial stage freeze.
2. Parallel execution window.
3. Serial convergence review.
4. Supervisor atomic stage commit.
5. Stage-sync checkpoint.
6. Next-stage admission.

Stage cluster option:

- Use only for tightly coupled sub-stages.
- Keep sub-stage gates explicit.
- Commit once at cluster close.
- Do not bypass cluster-level full gate and stage-sync.

## Load Balancing Baseline

Supervisor judgment is final. Use evidence to support assignment:

1. recent change volume
2. unresolved workload
3. conflict hotspot signals

Default policy: assign least-loaded capable agent first; rebalance only at stage boundary or freeze event.

## Gate Profiles and Pass Criteria

### Fast Gate (in-stage)

1. Targeted lint/static checks in touched scope.
2. Targeted tests in touched behavior.
3. Ownership boundary check.
4. Pollution delta check.

Pass when all commands pass, no ownership violation, no incremental pollution.

### Full Gate (stage close)

1. Full lint/static checks required by repo policy.
2. Full test suite or required stage gate set.
3. Contract-sensitive checks when applicable.
4. Spec/docs consistency checks if stage changed them.
5. Pollution delta check against stage-entry baseline.

Pass when all required checks pass, no unresolved critical findings, no incremental pollution.

### Mandatory Stage Close Checklist

1. Acceptance mapping submitted per agent.
2. Pollution report generated.
3. Ownership overlap scan completed.
4. Supervisor semantic review completed.
5. Atomic commit completed.
6. Stage-sync checkpoint completed.

## Divergence and Freeze

Freeze immediately if one or more conditions hold:

1. repeated gate failures with no net progress
2. repeated ownership overlap on same files
3. repeated retry/rollback loops
4. conflicting acceptance interpretations

Freeze flow:

1. stop parallel window
2. return to latest stable checkpoint
3. arbitrate serially
4. reopen only with revised boundaries and refreshed baseline

## Execution Record Minimum

Record at stage close:

1. stage id and task slice
2. acceptance mapping
3. pollution check result and delta
4. gate results (fast/full)
5. ownership check result
6. atomic commit summary
7. stage-sync result
8. unresolved risks
9. divergence-events (or `none`)

## High-Risk Simulation Record

For each scenario `R*`, record:

1. scenario-id
2. trigger-sequence
3. expected-invariants
4. observed-result
5. defect-id
6. fix-commit-reference

## Final Pipeline Close Record

Record at final close:

1. stability-slo-window-minutes
2. uncontrolled-drift-events
3. final-gate
4. final-pollution-delta
5. final-stage-sync
6. cleanup-check

SLO semantics:

- `stability-slo-window-minutes=60` is a capability target, not an automatic blocker.
- If unmet, record concrete cause and remedy in final close record.

## Script Quickstart

Scripts are recommended defaults, not mandatory when equivalent checks exist.

```bash
python scripts/run_stage_gate.py --profile fast --commands-file .tmp/gates.json --report .tmp/fast-gate.json
python scripts/run_stage_gate.py --profile full --commands-file .tmp/gates.json --report .tmp/full-gate.json
python scripts/check_pollution_baseline.py --capture --baseline .tmp/stage-baseline.json
python scripts/check_pollution_baseline.py --compare --baseline .tmp/stage-baseline.json --report .tmp/pollution-report.json
```
