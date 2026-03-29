---
name: spec-code-alignment
description: Detect, classify, and resolve drift between active feature truth and verified implementation evidence.
argument-hint: feature scope or alignment mode
---

# Spec Code Alignment

## When to Use

Use this skill when you need to:

- inspect drift between a feature spec and current code
- decide whether the next restoring action belongs to spec, code, or governance
- generate or update an alignment report under `specs/todo/`
- continue alignment work from an existing report

Typical triggers:

- spec/code drift
- unclear ownership of a mismatch
- disagreement between feature truth and verified behavior
- suspected governance contradiction

## Goal

Restore one coherent execution truth without creating a second one.

## Operating Model

- `specs/features/**` is the active execution truth.
- Code, tests, and runtime behavior are evidence, not peer truth sources.
- Verified facts may show that active feature truth is stale.
- `specs/contracts/**` defines constraints that ordinary alignment work must not break.
- `specs/todo/**` records unresolved drift and restoring actions. It is not execution truth.

## Guardrails

- Do not treat implementation as self-justifying truth.
- Do not rewrite feature truth without verified facts.
- Do not silently normalize foundational contradictions.
- Do not mix multiple restoring decisions in one ordinary step.
- Do not turn the report into a second plan or a second spec.

## Procedure

1. Load the governing spec and relevant constraints.
2. Inspect verified implementation evidence.
3. Classify each mismatch by owner and contradiction type.
4. Choose one restoring decision for the current step:
   - repair code
   - update spec
   - escalate
5. Write or update a report in `specs/todo/`.
6. Apply changes only if the requested mode is not scan-only.

Detailed rules and output shape are defined in:

- [Workflow Reference](./references/workflow.md)
- [Report Template](./references/report-template.md)

## Completion Checks

This skill is complete when:

1. audited scope is explicit
2. each mismatch has one owner and one recommended action
3. unresolved drift is recorded in `specs/todo/`
4. any applied change preserves single-source-of-truth semantics
5. any foundational contradiction is escalated, not silently absorbed
