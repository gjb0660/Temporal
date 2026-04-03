# Gate Checklists

## Fast Gate (in-stage)

Run this profile to keep iteration tight:

1. Targeted lint or static check on touched scope.
2. Targeted tests on touched behavior.
3. Ownership boundary check.
4. Pollution delta check.

Pass condition:

- no failing command
- no ownership violation
- no incremental pollution

## Full Gate (stage close)

Run this profile before atomic stage commit:

1. Full lint/static checks required by repo policy.
2. Full test suite or required gate test set.
3. Contract-sensitive checks, if applicable.
4. Documentation/spec consistency checks, if stage changes specs.
5. Pollution delta check against stage-entry baseline.

Pass condition:

- all required checks pass
- no unresolved critical findings
- no incremental pollution

## Mandatory Convergence Checklist

For every stage close:

1. Acceptance mapping submitted per agent.
2. Pollution report generated.
3. Ownership overlap scan complete.
4. Supervisor semantic review complete.
5. Atomic commit complete.
6. Stage-sync checkpoint complete.

## Divergence Trigger Checklist

Trigger freeze when one or more conditions hold:

1. Repeated gate failures with no net progress.
2. Repeated ownership overlap on same files.
3. Repeated rollback/retry loops.
4. Conflicting acceptance interpretations across agents.

Freeze action:

1. Stop parallel work.
2. Return to latest stable checkpoint.
3. Arbitrate serially.
4. Re-open with revised boundaries.
