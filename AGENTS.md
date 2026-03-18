# AGENTS

## Roles

### Explore Agent

- Purpose: read-only protocol and reference discovery.
- Input: target repo/path, focused question list, expected depth.
- Output: file paths, concrete data contracts, open risks.

### Implement Agent

- Purpose: code delivery under repository constraints.
- Input: scoped task, acceptance checks, touched modules.
- Output: minimal diffs, updated tests, no unrelated refactors.

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

- Clarify ambiguity with vscode_askQuestions before implementation.
- Prepare or update a PRD before feature implementation.
- Place PRD files only under docs/prd.
- Keep Python code in src layout with PEP 420 namespace packages.
- Keep QML in flat layout under src/temporal/qml.
- Execute in order: Explore -> Plan -> Approval -> Code.
- After bug fixes, append a local preventive rule.

## Forbidden

- No cross-layer shortcut (QML direct socket access).
- No destructive git cleanup (`git reset --hard`, `git clean -fd`).
- No adding `__init__.py` in Python source tree.
- No git history rewrite or deletion.
- No modification outside workspace scope.
