---
name: decision-import
description: Use this skill only when a human explicitly asks to treat the current staged diff as intentional and reconcile the feature spec from it. This is a one-shot, turn-scoped flow. Do not use for normal spec-first work.
---

# Decision Import Skill

Use this skill as an explicit exception to Minimal ESPC.

## Preconditions

- human explicitly invokes this flow
- changes exist in the current staged diff
- intent is: do not revert; reconcile spec from these changes

Otherwise, do not use this skill.

## Scope

- applies only to the current turn
- applies only to the current staged snapshot
- MUST NOT persist across turns

## Authority

1. human instruction (current turn)
2. contracts and repo rules
3. feature spec
4. staged diff (as decision evidence only)

Spec remains the single source of truth.

## Behavior

- do not revert staged changes
- infer the accepted decision from the diff
- update the feature spec with minimal edits
- restore spec–code consistency
- continue normal Minimal ESPC execution

## Allowed Updates

- Facts, Decision, Acceptance
- Plan, Progress, Todo
- metadata

## Guardrails

MUST NOT silently change:

- Goal
- Non-Goals
- Contracts

If implied, require human confirmation.

## Partial Code

- staged code may be incomplete or contain TODO
- import the decision, not completion
- Progress MUST reflect reality
- unfinished work stays in Plan or Todo

## After Reconciliation

Continue normal flow:

- complete required implementation
- check code quality
- run repository gates
- keep spec and code aligned atomically

## Completion

Done when:

- spec reflects the accepted decision
- code and validation state are consistent

If incomplete:

- Progress = actual state
- Plan = remaining critical work
- Todo = deferred work
