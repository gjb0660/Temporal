---
name: minimal-espc
description: "Required spec-first workflow skill for this repository. Trigger before working in specs/, before behavior-changing code, when switching stage, or when spec drift/uncertainty appears. Loads the Minimal ESPC entry path, stage flow, and spec-code sync rules. Do not skip when execution depends on spec interpretation."
---

# Minimal ESPC

## Goal

Provide the required Minimal ESPC working protocol for this repository
without creating a parallel source of truth.

Use this skill to establish:

- the spec entry path
- the current execution stage
- the spec-code synchronization rule

## Core Principles

1. think in **first principles** and reject heuristics and unverified assumptions
2. apply **Occam’s Razor** — no unnecessary entities, no backward compatibility
3. continuously challenge all inputs through **Socratic questioning**
   until they align with Goal, Facts, and Acceptance

## When to Use

Use this skill when:

- starting work in `specs/`
- changing behavior or acceptance-relevant code
- switching between exploration, specification, planning, coding, or review
- spec drift, ambiguity, or uncertainty appears
- complex, high-drift tasks may require conditional delegated supervision

Do not proceed as code-ready if this skill has not been applied.

## Procedure

1. Confirm governing sources.
   - Read `AGENTS.md`
   - Read repository constraints from `.github/copilot-instructions.md`

2. Resolve spec entry path.
   - Read `specs/index.md`
   - Classify the current context as exactly one of:
     - Feature
     - Contract
     - Knowledge
   - Read the matching domain index before editing any spec file

3. Resolve execution stage.
   - Determine the current stage and exit condition
   - If facts are insufficient, stay in exploration
   - If plan or acceptance is missing, do not treat code stage as ready
   - Use [execution-flow](./references/execution-flow.md) as needed

4. Enforce spec-code sync.
   - Keep spec and code aligned
   - Update spec before continuing when facts invalidate the current decision
   - Do not continue through drift
   - Use [spec-entry](./references/spec-entry.md) as needed

5. Apply Delegated TDD Supervision conditionally.
   - Trigger only when both are true:
     - `cross-layer` change: at least two layers among spec or code
     - `contract/Acceptance` semantics are changing
   - Follow [delegated-mode](./references/delegated-tdd-supervision.md) details
   - Otherwise keep the default single-agent path

## Output Contract

Return a compact status block:

- `source`: confirmed / missing
- `category`: feature / contract / knowledge / missing
- `stage`: named / missing
- `sync-risk`: yes / no
- `delegation`: on / off

If `delegation` is `on`,
state additional compact status block for each subagent:

- `workspace`: shared / isolated-worktree
- `semantic-gate`: pass / fail
- `pollution-gate`: pass / fail
- `atomic-submit`: pass / fail
- `cleanup`: pass / fail

If any field is `missing` or `yes`,
do not proceed as if code stage is ready.
If `delegation` is `on`,
code-ready is true only when all above are `pass`.

## Constraints

- Do not create a parallel workflow note
- Do not reinterpret repository constraints
- Do not skip domain index resolution
- Keep normal-use output compact
- Do not trigger delegated mode by default
- When delegated mode is on,
  keep final delivery as one supervising-agent atomic commit
