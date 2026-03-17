# AGENTS

## Roles

### Explore Agent
- Purpose: protocol and reference discovery.
- Input: target repo/path, specific question list.
- Output: file paths, concrete data contracts, risks.

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

## Forbidden
- No cross-layer shortcut (QML direct socket access).
- No hard reset of git state.
- No adding `__init__.py` in Python source tree.
