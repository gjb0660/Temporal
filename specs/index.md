# Specs Index

## Purpose

- `specs/` is the AI execution source for Temporal.
- `docs/` is manual export output for human readers.
- This file defines static directory contract, collaboration contract,
  and reading principles.
- Active routing and mutable state live in `specs/in-progress.md`.

## Directory Contract

- `specs/index.md`: static contract and reading principles.
- `specs/in-progress.md`: active routing, feature state,
  and duplicate-demand checks.
- `specs/phase-progress.md`: retired compatibility entry;
  do not use it as the live progress board.
- `specs/plans/`: transitional expansion area for complex plans
  until Execution is absorbed back into feature files.
- `specs/knowledge/`: external and domain reference material.
- `specs/decisions/`: cross-feature project decisions
  and stable protocol constraints.
- `specs/handoffs/`: session history and continuation notes.
- `docs/`: exported manuals and delivery-facing documentation.

## Document Contract

- Write newly created `specs/**/*.md` with English headings and concise
  Chinese body text.
- Keep tables and explanatory comment examples in Chinese.
- Preserve stable technical terms in English.
- Read `.github/copilot-instructions.md` for docs-language rules and
  historical docs handling.
- Retained historical English spec material may remain temporarily and should
  be tracked as audit statistics instead of standalone findings.

## Reading Principles

- New feature startup: read `specs/in-progress.md` first
  to check for duplicate demand.
- Rules-audit, handoff, and docs export: read this file first.
- Implementation tasks may read this file or `specs/in-progress.md` first,
  depending on whether structure or active routing is needed.
- Do not treat `docs/` as the execution source.

## Feature Contract

- A feature must state its target clearly.
- Code entry requires Definition.
- Code entry requires Execution unless the target feature declares
  `Exception: small-change`.
- `small-change` relaxes full Plan requirements only;
  it does not waive Refactor.
- Code is not complete until the commit is recorded in git.

## Handoff Contract

- Every handoff must include:
  - changed files list
  - assumptions
  - validation performed
  - unresolved risks
- Create new handoff documents under `specs/handoffs/` with English headings
  and concise Chinese body text.
- Historical handoff documents may drift temporarily and should be normalized
  in scheduled batches instead of ad hoc rewrites.

## Decision Boundaries

- Put cross-feature architecture choices in `specs/decisions/`.
- Put external or domain reference material in `specs/knowledge/`.
- Do not put agent behavior rules in `specs/decisions/`.
- Do not put feature state or session TODOs in `specs/decisions/`.
