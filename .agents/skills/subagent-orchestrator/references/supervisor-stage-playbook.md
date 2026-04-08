# Supervisor Stage Playbook

Use this page as the single supervisor reference for stage pipeline execution.

## Core Operating Rules

1. Start from first principles, then keep only the minimum controls needed.
2. Apply Occam's Razor: automate only high-repeat, high-error links.
3. Delegate by default; local supervisor coding is an exception.
4. Reuse the same agents through the full pipeline, then close after final gate pass.
5. Require lookahead planning at each stage close; if none is safe, record `none` with reason.
6. Require a final hardening round with high-risk simulation records.

## Time-Ordered Pipeline Contract

For each stage:

1. Serial stage freeze.
2. Parallel execution window.
3. Serial convergence review.
4. Supervisor stage close through `$converge-commit` atomic submit.
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

Pass when all required checks pass, no unresolved critical findings, no incremental pollution,
and all primary stage-close gates in `Stage-Close Output Contract (SSOT)` are `pass`.

### Mandatory Stage Close Checklist

1. Acceptance mapping submitted per agent.
2. Pollution report generated.
3. Delegation admission snapshot recorded
   (`source/category/stage/sync-risk/delegation`).
4. Ownership overlap scan completed.
5. Supervisor semantic review completed.
6. Stage close completed through `$converge-commit` atomic submit.
7. Stage-sync checkpoint completed.
8. Lookahead recorded (`tasks` or `none` with reason).

## Stage-Close Output Contract (SSOT)

Use this as the only output contract at stage close.

Required primary status block:

1. `source`
2. `category`
3. `stage`
4. `sync-risk`
5. `delegation`
6. `semantic-gate`
7. `pollution-gate`
8. `static-gate`
9. `atomic-submit`
10. `cleanup`

Required appendix record:

1. `task-slice`
2. `acceptance-mapping`
3. `pollution-check`
4. `ownership-check`
5. `atomic-commit-summary`
6. `stage-sync`
7. `remaining-risk`
8. `divergence-events`
9. `lookahead`

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

Record the full SSOT payload at stage close:

1. include all required primary status fields
2. include all required appendix record fields
3. do not add alias names for SSOT fields
4. do not add appendix fields that restate primary gate outcomes

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

same names as SSOT primary status block plus:

1. stability-slo-window-minutes
2. uncontrolled-drift-events
3. final-pollution-delta
4. final-stage-sync
5. final-remaining-risk
6. hardening-result: pass|fail
7. hardening-fail-action (required when hardening-result=fail)

Final-close gate:

- If `hardening-result=fail`, final close is blocked by default.
- Close only after fix/mitigation and revalidation.

SLO semantics:

- `SLO` means the 60-minute stability target.
- It is a background capability objective, not a gate and not a required record field.

## Script Quickstart

Scripts are recommended defaults, not mandatory when equivalent checks exist.

```bash
python scripts/run_stage_gate.py --profile fast --commands-file .tmp/gates.json --report .tmp/fast-gate.json
python scripts/run_stage_gate.py --profile full --commands-file .tmp/gates.json --report .tmp/full-gate.json
python scripts/check_pollution_baseline.py --capture --baseline .tmp/stage-baseline.json
python scripts/check_pollution_baseline.py --compare --baseline .tmp/stage-baseline.json --report .tmp/pollution-report.json
```
