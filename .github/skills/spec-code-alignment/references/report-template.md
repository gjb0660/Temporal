# Report Template

Use a dated file under `specs/todo/`, for example:

- `specs/todo/2026-03-27-spec-code-alignment-scan.md`

## Goal

State why this alignment report exists.

## Scope

State the audited feature, code paths, and constraints reviewed.

## Summary

Give a short result summary:

- no drift
- drift found
- escalation required

## Findings

For each finding, use this structure:

### 1. <Short Title of Finding>

- severity: minor | major | critical
- type: aligned | spec-overstates-code | code-exceeds-spec | owner-drift |
        foundational-contradiction | docs-only
- file: feature or contract spec file path
- violation: what the spec claims vs what the code does
- impact: how this drift affects the product, team, or users
- code-evidence: specific code paths, tests, or behaviors
- minimal-fix: the smallest code or spec change that would restore alignment
- recommended: repair-code | update-spec | escalate

## Aligned Areas

List the parts checked with no meaningful drift.

## Next Actions

List the smallest restoring actions in execution order.

## Remaining Risk

List unresolved ambiguity, missing evidence, or governance blockers.
