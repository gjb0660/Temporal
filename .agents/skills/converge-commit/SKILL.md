---
name: converge-commit
description: Review staged changes and prepare one atomic commit by first-principles cleanup and Occam-style reduction. Use when the task is commit-time review, pre-commit refactor convergence, staged diff quality checks, or "提交前审查/复查". Supports `mode=single|subagent`, defaults to single, and enables subagent mode only on delegated trigger conditions.
---

# Converge Commit

## Core Contract

Review commit-time staged changes only.
Use first-principles review first, then Occam reduction.
Review mandatory range = touched files plus one-hop neighbors.
Fail closed when staged changes are empty.
Allow exactly one final atomic commit after all sustainability gates pass.

## Trigger Signals

Activate this skill when requests include commit-time review intent:

1. `review staged changes`
2. `commit`
3. `复查`
4. `提交前审查`

## Mode Routing

Support two modes:

1. `mode=single` (default)
2. `mode=subagent` (optional), use only when:
   1. user explicitly requests it
   2. delegated trigger from `$minimal-espc` passes

Read [subagent-collaboration.md](./references/subagent-collaboration.md) for
delegated trigger, topology, and completion details.

## Scope Gate

Review staged delta only, then expand to mandatory review range:

1. run `git diff --cached --name-only` for touched file scope
2. run `git diff --cached` for behavior evidence
3. expand to touched plus one-hop neighbors:
   - direct callers and callees
   - directly coupled spec or contract references
   - immediate tests guarding touched semantics
4. apply range policy:
   - any failure inside touched plus one-hop blocks exit and commit
   - failures outside this range are recorded in `remaining-risk` and may
     trigger a focused refactor plan suggestion, but do not directly block
     this commit

If staged delta is empty, stop with:

1. `atomic-submit=fail`
2. `cleanup=fail`
3. clear message: no staged changes, commit blocked

## Single-Agent Workflow (Minimal Path)

Use this fixed six-step loop.
Repeat steps 1-4 multi-round until convergence is reached, then run step 5.
Execute step 6 only after all five gates are `pass`.

1. first-principles review:
   - identify wrong assumptions, semantic risks, and code smells
   - classify smells with
     [refactoring-required-elective.md](./references/refactoring-required-elective.md)
2. Occam reduction:
   - remove dead code, duplicate paths, and redundant branches
   - keep only the minimum sustainable entities
3. mandatory smell closure:
   - all safely fixable smells in mandatory range must be fixed in this commit
   - cross-boundary or unsafe items must be recorded in `remaining-risk` and
     `refactor-plan-suggestions`
4. quick gate:
   - run mandatory-range checks first: `pyright`, `ruff`, `qmllint`
5. full gate:
   - run repository required checks: `pyright`, `ruff`, `qmllint`,
     `qmlformat`, `markdownlint`, `unittest`
   - before each full-gate exit attempt, answer:
     1. which concrete assumption risk was removed?
     2. can fewer entities still satisfy active Acceptance semantics?
     3. if deferred now, how will this area decay in one to three iterations?
6. atomic commit:
   - propose one valid subject and commit exactly once

## Unified Sustainability Gates (Hard)

This section is the only exit/commit decision source.
Do not exit loop or commit unless all gates are `pass`:

1. `semantic-gate`:
   - acceptance semantics match active specs and contracts
   - no unresolved assumption that can change intended behavior
2. `pollution-gate`:
   - no dead code, unreachable branches, duplicate logic, or commented-out
     fallback code in mandatory range
   - mandatory-range safely fixable smells are cleared in this commit
   - mandatory-range unresolved items are only allowed when they are unsafe or
     cross-boundary and explicitly escalated
3. `static-gate`:
   - required static checks are green for mandatory range
   - repository full-gate static and test checks are green before commit
4. `atomic-submit`:
   - single intent, single commit action, valid commit subject format
5. `cleanup`:
   - no unresolved TODO/FIXME/HACK for this staged intent
   - staged diff is reduced to minimum sustainable change set

Any failed gate blocks loop exit and blocks commit.
If any gate fails, return to the convergence loop (step 1 or step 2), then
re-run step 5; do not jump directly to step 6.

## Output Contract

Primary status block (aligned with `$minimal-espc`):

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

Appendix fields (secondary, not primary gate keys):

1. `findings`
2. `reduction-decisions`
3. `final-commit-subject`
4. `remaining-risk`
5. `refactor-plan-suggestions`

Read subagent-only extension fields in
[subagent-collaboration.md](./references/subagent-collaboration.md).

## Atomicity Rules

Do not define atomicity twice.
Atomicity is accepted only when all five gates are `pass` and commit subject
policy in [commit-log-spec.md](./references/commit-log-spec.md) is satisfied
(`type(scope): subject` or `type: subject`).

## Anti-Patterns

1. do not review unstaged or unrelated changes as commit scope
2. do not defer safely fixable mandatory-range smells to later commits
3. do not emit multiple commits for one staged intent

## References

1. [commit-log-spec.md](./references/commit-log-spec.md)
2. [subagent-collaboration.md](./references/subagent-collaboration.md)
3. [refactoring-required-elective.md](./references/refactoring-required-elective.md)
