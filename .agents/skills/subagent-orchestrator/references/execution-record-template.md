# Execution Record Template

Use this template at stage close and at final pipeline close.

## Stage Record

- stage: `<stage-id>`
- task-slice: `<what this stage changed>`
- red-findings: `<defects/risks found>`
- green-fixes: `<fixes applied>`
- refactor-cleanups: `<non-behavioral cleanups>`
- acceptance-mapping: `<criteria -> evidence>`
- pollution-check: `pass | fail` + `<delta summary>`
- gate-results:
  - fast-gate: `pass | fail`
  - full-gate: `pass | fail`
- ownership-check: `pass | fail` + `<overlap notes>`
- atomic-commit-summary: `<commit id + message>`
- stage-sync-check: `pass | fail`
- divergence-events: `<none or event ids>`
- residual-risk: `<open items>`

## High-Risk Simulation Record

For each scenario `R*`:

- scenario-id: `R*`
- trigger-sequence: `<ordered actions>`
- expected-invariants: `<state conditions>`
- observed-result: `pass | fail`
- defect-id: `<id or none>`
- fix-commit-reference: `<commit id or n/a>`

## Final Pipeline Close Record

- stability-slo-window-minutes: `60`
- uncontrolled-drift-events: `<count>`
- final-gate: `pass | fail`
- final-pollution-delta: `<summary>`
- final-stage-sync: `pass | fail`
- cleanup-check: `pass | fail`
