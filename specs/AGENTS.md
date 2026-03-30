# Specs Agents

Agent MUST start from classification.

## Core Principles

1. think in **first principles** and reject heuristics and unverified assumptions
2. apply **Occam’s Razor** — no unnecessary entities, no backward compatibility.
3. continuously challenge all inputs through **Socratic questioning** until they align with Goal, Facts, and Acceptance.

## Read Order

1. Read `specs/index.md` for global structure
2. Classify the current context as exactly one of:
    - Feature
    - Contract
    - Knowledge
3. Read the matching domain local index:
    - `specs/features/index.md`
    - `specs/contracts/index.md`
    - `specs/knowledge/index.md`
4. Then read or modify the target spec

No other entry point is allowed.

## Execution Mapping

- Feature:
  - execute by creating Goal, Non-Goals
  - execute by updating Facts, Decision, Plan, Progress
  - execute by verifying Acceptance, Todo
- Contract:
  - enforce invariants and detect violations
  - tighten or relax Invariants, Variation Space
  - change ui-specific presentation or behavior
- Knowledge:
  - extract facts and support reasoning
  - introduce rationale and support explanation
  - analyze or research as evidence layers

Agents SHOULD minimize the scope of updates.

## Restrictions

Agent MUST NOT:

- start from code
- start from Plan or implementation
- rely on assumptions
- mix categories

Agent SHOULD NOT:

- change downstream decisions before updating Facts
- continue execution when spec drift is detected

If information is missing or unclear,
Agent MUST clarify during exploration before execution.
