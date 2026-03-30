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

4. Enforce spec-code sync.
   - Keep spec and code aligned
   - Update spec before continuing when facts invalidate the current decision
   - Do not continue through drift

5. Use references as needed.
   - `references/spec-entry.md`
   - `references/execution-flow.md`

## Output Contract

Return a compact status block:

- `source`: confirmed / missing
- `category`: feature / contract / knowledge / missing
- `stage`: named / missing
- `sync-risk`: yes / no

If any field is `missing` or `yes`,
do not proceed as if code stage is ready.

## Constraints

- Do not create a parallel workflow note
- Do not reinterpret repository constraints
- Do not skip domain index resolution
- Keep normal-use output compact
