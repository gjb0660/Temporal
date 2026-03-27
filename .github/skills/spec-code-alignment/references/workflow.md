# Workflow Reference

## Model

Work in this order:

1. detect
2. classify
3. decide
4. report
5. apply if requested

## Detect

For the audited scope:

1. identify the claimed truth in the active feature spec
2. identify the verified behavior from code, tests, or runtime evidence
3. record only concrete mismatches

Do not infer intent from implementation alone.

## Classify

Each mismatch must have:

- `owner-layer`
  - `feature`
  - `contract`
  - `implementation`

- `contradiction-class`
  - `aligned`
  - `spec-overstates-code`
  - `code-exceeds-spec`
  - `owner-drift`
  - `foundational-contradiction`
  - `docs-only`

- `severity`
  - `major`
  - `minor`

## Decide

Choose one decision for each major mismatch:

- `repair-code`
  - use when active feature truth is still valid and the gap is behavioral

- `update-spec`
  - use when verified facts show that active feature truth is stale and the change does not break governing constraints

- `escalate`
  - use when the contradiction is foundational, ownership is unclear, or the skill would need to invent intent

## Decision Rules

Choose `repair-code` only when:

1. the active feature truth is still the target truth
2. the mismatch is not foundational
3. the smallest owning implementation layer can be changed directly

Choose `update-spec` only when:

1. the new reality is verified
2. the behavior appears intentional or relied upon
3. related contracts remain satisfied
4. the contradiction is not foundational

Choose `escalate` when:

1. `Goal`, `Non-Goals`, `Decision`, or `Acceptance` is no longer defensible
2. a contract is violated or unclear
3. ownership cannot be determined without inventing intent
4. ordinary alignment would require changing multiple truth layers at once

## Report

Write or update a dated report under `specs/todo/`.

The report must capture:

- scope
- summary
- findings
- next actions
- remaining risk

## Apply

### Repair Code

1. confirm the spec is still the target truth
2. add or update focused tests when needed
3. implement the smallest repair
4. validate the smallest relevant test or diagnostic set

### Update Spec

1. update only sections proved stale by verified facts
2. do not normalize accidental behavior
3. do not rewrite foundational logic through ordinary drift handling

### Escalate

1. stop ordinary repair
2. record the contradiction as major
3. state the conflicting owner layer
4. state what decision is required before work can continue

## Output Summary

Final output should state:

1. audited scope
2. key contradiction classes
3. chosen decisions
4. report path
5. applied changes, if any
6. escalations, if any
7. remaining work
