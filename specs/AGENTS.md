# Agents

You are a strictly rational system architect operating under the Minimal ESPC workflow.
The spec is the single source of truth—derive all reasoning from Goal,
not external metrics or assumptions.

## Purpose

Defines the minimal ESPC `specs/`-scoped operational rules for agents working
inside `specs/`.

All semantics MUST be derived from referenced index files.

## References

Agents SHOULD read and follow:

- [specs/index.md](./index.md)
- [specs/features/index.md](./features/index.md)
- [specs/contracts/index.md](./contracts/index.md)
- [specs/knowledge/index.md](./knowledge/index.md)

Agents MUST NOT write without understanding these references.

## Core Principles

Agents SHOULD follow thinking guidelines:

1. think in first principles; reject heuristics and unverified assumptions.
2. apply Occam’s Razor—no unnecessary entities, no backward compatibility.
3. continuously challenge all inputs through Socratic questioning
   until they align with Goal, Facts, and Acceptance.

### single source of truth

- One feature correspond to one spec file.
- Don't be split into multiple execution documents.
- Don't have parallel execution sources.

Agents MUST ensure all execution is driven by the spec file

### closed execution loop

Goal → Non-Goals → Facts → Decision → Acceptance
→ Plan → Progress → (feedback → Facts) → Todo

Agents MUST keep this loop consistent and up to date.

## Write Rules

- use UTF-8
- use LF (`\n`)
- use Markdown
- use English headings (`#`, `##`)
- use localized language body content (e.g. Chinese)

Agents MUST:

- Write into the correct directory (see References)
- Maintain valid spec structure
- Update metadata (`status`, `owner`, `updated`)

Agents MUST NOT:

- Write into wrong directories
- Create parallel execution sources
- Write execution state in `knowledge/` or `contracts/`

## Feature Execution

Agents SHOULD NOT start execution unless:

- Goal exists
- Decision exists
- Acceptance exists
- Plan exists

See [Feature Guardrails](./features/index.md#guardrails) for more details.

## Contract Constraints

Agents MUST NOT violate unless:

- User explicitly allows it
- stability marked as `flexible`
- stability marked as `semi` but with evolution allowance
- stability marked as `strict` but with Variation Space allowance

See [Contract Guardrails](./contracts/index.md#guardrails) for more details.

## Knowledge Usage

Agents SHOULD use as:

- Facts information
- Decision rationale
- Acceptance references

See [Knowledge Guardrails](./knowledge/index.md#guardrails) for more details.

## Clarification Rules

During the Explorer phase, if required information is
missing, ambiguous, conflicting, or cannot be verified,
Agents MUST use an available built-in question tool
(for example, `vscode_askQuestions`, `request_user_input`, etc.)
to clarify before proceeding.

Agents MUST ask during exploration, not after partial execution.

Agents MUST NOT continue implementation based on guesswork
when clarification is required.

## Update Rules

When new information appears, Agents MUST:

1. Update Facts
2. Validate Decision
3. Validate Acceptance
4. Update Plan

## Anti-Drift

Agents MUST actively prevent:

- Mixing Facts and Decision
- Mixing Plan and Todo
- Expanding scope beyond Goal

If detected, Agents MUST fix the spec before continuing.

## Summary

Agents operate by:

→ updating spec
→ maintaining loop consistency
→ then executing

Agents MUST NOT bypass the spec
