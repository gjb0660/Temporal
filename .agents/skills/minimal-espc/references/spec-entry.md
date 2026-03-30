# Spec Entry

Agent MUST start from classification.

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
  execute through the feature spec and keep Goal, Facts, Decision,
  Acceptance, Plan, and Progress consistent with real work

- Contract:
  enforce invariants, detect violations, and update constraints only
  as contract work

- Knowledge:
  extract facts, support reasoning, and refine reusable understanding

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
