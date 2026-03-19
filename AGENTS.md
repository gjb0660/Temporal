# AGENTS

## Ownership

- This file defines agent roles, handoff contract, and execution workflow.
- Keep repository-wide technical constraints in .github/copilot-instructions.md.

## Roles

### Explore Agent

- Purpose: read-only protocol and reference discovery.
- Input: target repo/path, focused question list, expected depth.
- Output: file paths, concrete data contracts, open risks.

### Implement Agent

- Purpose: code delivery under repository constraints.
- Input: scoped task, acceptance checks, touched modules.
- Output: minimal diffs, updated tests, completed refactor pass, no unrelated changes.

### Review Agent

- Purpose: pre-merge risk review.
- Focus order:
  1. behavioral regressions
  2. protocol/data-loss risks
  3. reconnection and recording edge cases
  4. missing tests

## Handoff Contract

- Every handoff must include:
  - changed files list
  - assumptions
  - validation performed
  - unresolved risks

## Collaboration Workflow

- Use `vscode_askQuestions` only for true blocking decisions
  or missing required inputs.
- Do not pause for approval when the task is implementable
  from current context.
- Prepare or update a PRD before feature implementation.
- Follow technical boundaries and quality gates in .github/copilot-instructions.md.
- Keep rule and handoff docs terse; remove duplicated guidance.
- Place PRD files only under docs/prd.
- Update docs/phase-progress.md only in handoff stage.
- Execute in order: Explore -> Plan -> Code.
- For behavior changes with tests, complete Red -> Green -> Refactor before handoff.
- Commit implementation and corresponding tests together in one atomic commit.
- After bug fixes, append a local preventive rule.

## Forbidden

- No cross-layer shortcut (QML direct socket access).
- No destructive git cleanup (`git reset --hard`, `git clean -fd`).
- No git history rewrite or deletion.
- No modification outside workspace scope.
