---
name: converge-commit
description: Review staged changes and prepare one atomic commit by first-principles cleanup and Occam-style reduction. Use when the task is commit-time review, pre-commit refactor convergence, staged diff quality checks, or "提交前审查/复查". Supports `mode=single|subagent`, defaults to single, and enables subagent mode only on delegated trigger conditions.
---

# Converge Commit

## Core Contract

Execute commit-time review on staged changes only.
Fail closed when staged changes are empty.
Converge to the minimum sustainable solution before commit.
Allow exactly one final atomic commit after all required gates pass.

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

Read [subagent-collaboration.md](./references/subagent-collaboration.md)
for the full optional workflow.

## Scope Gate

Review staged delta only:

1. run `git diff --cached --name-only` for file scope
2. run `git diff --cached` for behavior evidence

If staged delta is empty, stop with:

1. `atomicity_check=fail`
2. clear message: no staged changes, commit blocked

## Single-Agent Workflow

Run this exact loop:

1. first-principles review:
   - identify wrong assumptions, behavior risks, and code smells
2. Occam reduction:
   - remove redundant branches, dead code, and duplicate paths
   - keep only minimal sustainable logic
3. quick gate:
   - run checks related to changed files first
4. iterate:
   - continue review and reduction until no high-risk findings remain
5. full gate:
   - run repository required checks before commit
6. atomic commit:
   - produce one valid commit subject and commit once

## Optional Subagent Mode

Do not inline the optional workflow in this file.
Use [subagent-collaboration.md](./references/subagent-collaboration.md)
for delegated trigger, topology, challenge loop, and completion gates.

## Commit Subject Policy

Read [commit-log-spec.md](./references/commit-log-spec.md) before proposing commit subject.

Use for new commits:

1. `type(scope): subject`
2. `type: subject`

Default to single-line subject without body.
Allow body only when risk rationale is necessary.

## Output Contract

Always return:

1. `findings`
2. `reduction_decisions`
3. `gate_results`
4. `final_commit_subject`
5. `atomicity_check`
Read subagent-only output fields in
[subagent-collaboration.md](./references/subagent-collaboration.md).

## Atomicity Rules

A commit is valid only if all are true:

1. single intent
2. single commit action
3. required gates all green
4. no unresolved TODO related to this staged intent

If any rule fails, block commit.

## Anti-Patterns

1. do not review unstaged or unrelated changes as commit scope
2. do not skip full gate before final commit
3. do not keep dead branches for hypothetical compatibility
4. do not emit multiple commits for one staged intent

## References

1. [commit-log-spec.md](./references/commit-log-spec.md)
2. [subagent-collaboration.md](./references/subagent-collaboration.md)
