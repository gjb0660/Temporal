# Commit Log Specification

## Baseline Evidence

This specification is derived from repository history sampling.

## Required Format For New Commits

Use one of:

1. `type(scope): subject`
2. `type: subject`

Allowed `type` values:

1. `fix`
2. `feat`
3. `refactor`
4. `specs`
5. `skill`
6. `governance`
7. `docs`
8. `chore`
9. `perf`

`scope` is optional but recommended when it improves retrieval precision.

## Type Boundaries

`specs` is reserved for agent-oriented SSOT, not agent behavior.
`skill` is reserved for skill capability and internal skill workflow changes.
`governance` is reserved for global agent-behavior governance and rule-ownership
changes (for example `AGENTS.md` and `.github/**` constraints).

## Subject Rules

Subject must satisfy all:

1. describe one intent only
2. use imperative style
3. avoid filler words and narrative phrasing
4. avoid trailing punctuation
5. be specific enough for grep-based retrieval

Default to single-line subject.
Do not add body unless risk rationale is necessary.

## Compatibility and Blocking Rules

For new commits:

1. do not introduce `phase-*` prefixes
2. do not use `ui:` as top-level type
3. do not mix multiple intents into one subject

If any blocking rule is violated, revise subject before commit.

## Atomic Commit Rule

A commit is atomic only if all are true:

1. one intent
2. one commit action
3. all required repository gates pass
4. no unresolved TODO tied to the same intent

If one condition fails, do not commit.

## Examples

Valid:

1. `fix(ui): tighten source list identity checks`
2. `skill: fold converge-commit optional subagent flow into references`
3. `governance: add converge-commit entry hint to AGENTS.md`
4. `chore: align markdownlint ignore patterns`

Invalid:

1. `phase-x: final fix`
2. `xxx:: clean up wording`
3. `ui: tweak layout spacing`
4. `fix: do many updates across app and docs and tests`
