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
- Prepare or update a feature spec before feature implementation.
- Follow technical boundaries and quality gates in .github/copilot-instructions.md.
- Keep rule and handoff docs terse; remove duplicated guidance.
- Keep AI-facing specs and workflow docs under specs/.
- Keep static structure guidance in specs/index.md.
- Keep active routing and state in specs/in-progress.md.
- Store project decisions under specs/decisions/.
- Keep phase implementation specs under specs/plans/
  until absorbed into feature Execution sections.
- Start new features by checking specs/in-progress.md
  for duplicate demand.
- Read specs/index.md first for rules-audit, handoff,
  and docs export tasks.
- Update specs/in-progress.md only in handoff stage.
- Execute in order: Explore -> Spec -> Plan -> Code.
- Do not enter Code without Definition.
- Do not enter Code without Execution unless the target feature
  declares `Exception: small-change`.
- Treat blocked features as not directly codable.
- For behavior changes with tests, complete Red -> Green -> Refactor before handoff.
- Commit implementation and corresponding tests together in one atomic commit.
- After a bug fix, add one preventive rule to the nearest applicable
  repository rule file.

## Forbidden

- No cross-layer shortcut (QML direct socket access).
- No destructive git cleanup (`git reset --hard`, `git clean -fd`).
- No git history rewrite or deletion.
- No modification outside workspace scope.
