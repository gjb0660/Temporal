# AGENTS

## Ownership

- This file defines agent roles and execution workflow.
- Keep repository-wide technical constraints in .github/copilot-instructions.md.

## Roles

### Explore Agent

- Purpose: read-only protocol and reference discovery.
- Output: file paths, concrete data contracts, and open risks.

### Implement Agent

- Purpose: code delivery under repository constraints.
- Output: minimal diffs, updated tests, and no unrelated changes.

### Review Agent

- Purpose: pre-merge risk review.
- Focus: regressions, data-loss risks, reconnect edge cases,
  missing tests, and refactor quality.

## Collaboration Workflow

- Use `vscode_askQuestions` only for true blocking decisions
  or missing required inputs.
- Do not pause for approval when the task is implementable
  from current context.
- Follow technical boundaries and touched-scope quality gates
  in .github/copilot-instructions.md.
- Use specs/index.md for static structure and collaboration contract.
- Use specs/in-progress.md for active routing and duplicate-demand checks.
- Keep project decisions under specs/decisions/.
- Keep phase implementation specs under specs/plans/
  until absorbed into feature Execution sections.
- Start new features by checking specs/in-progress.md first.
- Execute in order: Explore -> Spec -> Plan -> Code.
- Update specs/in-progress.md only in handoff stage.
- During implementation, do not change existing `#` or `##` headings in
  `specs/**/*.md`, `docs/**/*.md`, `.github/**/*.md`, or `AGENTS.md`.
- Exceptions are limited to `rules-governance` work, newly created Markdown
  files, or explicit user-requested document restructuring.
- When localizing existing Markdown, keep existing `#` and `##` headings.

### Code Entry

- Enter Code only after Definition exists.
- Enter Code only after Execution exists,
  unless the target feature declares `Exception: small-change`.
- Treat blocked features as not directly codable.

### Code Exit

- Follow Red -> Green -> Refactor -> Commit.
- Green is an intermediate state, not a completion condition.
- Before commit: touched-scope tests are green,
  touched-scope lint and format gates pass,
  and behavior changes sync required Spec updates.
- Code is not complete until the commit is recorded in git.
- Commit implementation, related tests, and required Spec updates
  together in one atomic commit.
- Run the existing Review Agent before considering Code complete
  for high-risk or test-driven behavior changes.
- If risk is unclear, treat the change as high-risk.

- Keep rule and handoff docs terse; remove duplicated guidance.
- After a bug fix, add one preventive rule to the nearest applicable
  repository rule file.

## Forbidden

- No cross-layer shortcut (QML direct socket access).
- No destructive git cleanup (`git reset --hard`, `git clean -fd`).
- No git history rewrite or deletion.
- No modification outside workspace scope.
