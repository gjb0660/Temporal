# Delegated TDD Supervision

## Minimal Invariants

- Trigger invariant:
  delegated mode enters only when Trigger Gate passes.
- Execution invariant:
  supervising agent MUST choose shared or isolated subagent workspaces based on concrete isolation needs.
- Convergence invariant:
  final delivery MUST be one supervising-agent atomic commit.
- Cleanup invariant:
  flow is complete only when temporary isolation resources,
  if any, are cleaned up.

## Workspace Decision

- Keep the supervising agent in the primary repository directory.
- Default to shared subagent workspaces when ownership is clear,
  file overlap is low, and tool side effects are manageable.
- Use isolated worktrees is unavoidable, only when it
  materially reduces, edit collision, permission, or pollution risk:
  - `git worktree add --detach .tmp/<workspace> <base-ref>`

## Supervisory Loop

1. Split work by behavior slice and assign non-overlapping ownership.
2. Require each subagent to run local TDD loops step by step:
   - `Red -> Green -> Refactor`
3. Collect subagent outputs and review sequentially.
4. Apply two gates before integration:
   - semantic gate: Acceptance and contract alignment
   - pollution gate: no out-of-scope files, no legacy contract regressions
5. Re-dispatch fixes when either gate fails.

## Atomic Delivery Rule

- Keep subagent commits as temporary execution artifacts.
- Final delivery MUST be one supervising-agent atomic commit.
- If spec changes are required for the same execution unit,
  include spec and code in the same atomic commit.

## Fail-Closed Completion Gate

When `delegation: on`, completion requires all conditions:

- `semantic-gate: pass`
- `pollution-gate: pass`
- `atomic-submit: pass`
- `cleanup: pass`

Any failed or pending condition means `code-ready=false`.

## Structured Execution Record

Record the following fields in the final supervising summary:

- `task-slice`
- `red-findings`
- `green-fixes`
- `refactor-cleanups`
- `acceptance-mapping`
- `pollution-check`
- `atomic-commit-summary`
- `cleanup-check`

## Cleanup Gate

After each subagent is closed:

1. Remove temporary isolation resources created for the subagent.
2. If an isolated worktree was created, run:
   - `git worktree remove .tmp/<workspace>`.
3. If removal fails:
   - inspect worktree state
   - finish minimal cleanup
   - rerun the required cleanup step
4. Do not use `--force` by default.

Flow is complete only when `cleanup` is done.

## Anti-Patterns

- Do not force isolated worktrees without a concrete isolation need
- Do not ask a subagent to finish all RED, GREEN, and REFACTOR work in one handoff
- Do not skip per-cycle supervising review before the next cycle starts
