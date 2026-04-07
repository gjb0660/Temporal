# Workspace Agents

This repository uses `$minimal-espc` as the required spec-first working skill.

Agents MUST load and follow `$minimal-espc` before:

- working under `specs/`
- changing behavior
- switching execution stage
- continuing after spec drift or uncertainty

Repository-specific constraints remain in `.github/copilot-instructions.md`.

For staged-diff review and pre-commit convergence,
agents SHOULD use `$converge-commit` as the required code-last workflow.

Do not create parallel workflow rules outside the skill.
