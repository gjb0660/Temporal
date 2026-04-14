---
name: decision-import
description: Use this skill only when a human explicitly asks to treat the current staged diff as intentional and reconcile the feature spec from it. This is a one-shot, turn-scoped exception lane and MUST hand control back to minimal-espc after reconciliation.
---

# Decision Import Skill

Use this skill as a one-shot exception lane to reconcile spec from the
current staged diff.

It does not replace normal `$minimal-espc` execution.

## Scope

- applies only to the current turn
- applies only to the current staged snapshot
- MUST NOT persist across turns

## Flow

### 1) Admission

- explicit invocation of this skill counts as human attestation
- current staged diff MUST exist
- if staged diff is empty, stop immediately with `not-applicable` status
- if `not-applicable`, spec MUST NOT be modified

### 2) Reconcile

- do not revert staged changes
- treat staged diff as conditionally accepted decision evidence for this turn
- spec remains the single source of truth
- apply minimal spec edits only to:
  - Facts, Decision, Acceptance
  - Plan, Progress, Todo
  - metadata
- import decision only, not completion
- staged code may be partial or contain TODO
- Progress MUST reflect actual state; unfinished work stays in Plan or Todo

### 3) Guardrails (Non-Blocking Proposal Lane)

- Goal, Non-Goals, and Contracts are hard-boundary fields
- if staged diff implies changes to hard-boundary fields:
  - continue reconciliation in this lane
  - MUST emit an explicit governance risk proposal
  - MUST add governance follow-up in Todo
- MUST NOT silently claim hard-boundary changes are fully ratified

### 4) Handoff

- after reconciliation, hand control back to `$minimal-espc`
- implementation, quality gates, and repository checks are governed by
  `$minimal-espc` and repository rules, not by this skill

## Output Contract

Return a compact status block:

- `input-fingerprint`: get staged fingerprint by running `git write-tree`
- `imported-decisions`: list of imported decisions from staged diff
- `proposed-governance`: list of proposed governance if hard-boundary changes are implied
- `handoff-skills`: list of skills to trigger after handoff, e.g. `"$minimal-espc"`

## Completion

Done when:

- spec reflects accepted decision evidence from current staged diff
- any hard-boundary implication is captured as proposal + governance Todo
