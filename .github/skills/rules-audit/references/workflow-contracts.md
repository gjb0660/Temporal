# Workflow Contracts

Audit these contracts whenever repository governance files define or repeat
agent workflow rules.

## Toolchain Gates

- Python changes require lint -> fix -> format.
- QML changes require lint -> fix -> format.
- TDD must complete Red -> Green -> Refactor.
- Rule documents must stay terse.

## Decision Gates

- Agents must use `vscode_askQuestions` only at true blocking decisions.
- Agents must not require a pre-code approval step for implementable tasks.
- Workflow must be Explore -> Spec -> Plan -> Code.
- `specs/index.md` is the static entry.
- `specs/in-progress.md` is the dynamic routing and state board.
- New feature startup must check `specs/in-progress.md` for duplicate demand.

## Code Exit

- Code requires Definition.
- Code requires Execution unless the target feature declares
    `Exception: small-change`.
- `small-change` relaxes Plan only.
- Code completion requires Red -> Green -> Refactor -> Commit.
- High-risk or test-driven behavior changes must run the existing Review
    Agent before Code is considered complete.
- Code is not complete until the commit is recorded in git.
- If risk classification is unclear, audit must treat the change as
    high-risk by default.

## Content Ownership

- `docs/` is exported human-facing output.
- `.github/**` instruction files must stay in English.
- `AGENTS.md` must stay in English.
- Source code comments must stay in English.
- Git commit messages must stay in English.
- New `docs/**/*.md` must use English headings and concise Chinese body
    text.
- New `specs/**/*.md` must use English headings and concise Chinese body
    text.
- New handoff documents under `specs/handoffs/` must follow the handoff
    contract in `specs/index.md`.
- Repository text files must use UTF-8 without BOM and LF.
- Retained English historical specs, docs, or handoffs may be reported as
    audit observations only.

## Prompt Scope

- `.github/prompts/*.md` are scenario-specific prompts, not the repository
    workflow baseline.
