# Specs Index

## Purpose

- `specs/` is the AI execution source for Temporal.
- `docs/` is manual export output for human readers.
- This file defines static directory contract and reading principles.
- Active routing and mutable state live in `specs/in-progress.md`.

## Directory Contract

- `specs/index.md`: static contract and reading principles.
- `specs/in-progress.md`: active routing, feature state,
  and duplicate-demand checks.
- `specs/plans/`: transitional expansion area for complex plans
  until Execution is absorbed back into feature files.
- `specs/knowledge/`: external and domain reference material.
- `specs/decisions/`: cross-feature project decisions
  and stable protocol constraints.
- `specs/handoffs/`: session history and continuation notes.
- `docs/`: exported manuals and delivery-facing documentation.

## Reading Principles

- New feature startup: read `specs/in-progress.md` first
  to check for duplicate demand.
- Rules-audit, handoff, and docs export: read this file first.
- Implementation tasks may read this file or `specs/in-progress.md` first,
  depending on whether structure or active routing is needed.
- Do not treat `docs/` as the execution source.

## Feature Contract

- A feature must state its target clearly.
- Code requires Definition.
- Code requires Execution unless the target feature declares
  `Exception: small-change`.
- Small-change exceptions are valid only when Spec and external behavior
  remain unchanged.
- High-risk changes cannot rely on heuristic audit alone.

## Decision Boundaries

- Put cross-feature architecture choices in `specs/decisions/`.
- Put external or domain reference material in `specs/knowledge/`.
- Do not put agent behavior rules in `specs/decisions/`.
- Do not put feature state or session TODOs in `specs/decisions/`.
