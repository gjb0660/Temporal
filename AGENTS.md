# Workspace Agents

This repository uses Minimal ESPC.

All executable specs are under `specs/`.
repository constraints belong to `.github/copilot-instructions.md`

Minimal ESPC is an **entropy-reduction loop**
and **decision convergence system**

Agents MUST:

- treat specs as the single source of truth
- read `specs/AGENTS.md` before working in specs/
- keep spec and code consistent

Agents MUST NOT:

- infer behavior from code without spec
- create parallel sources of truth

## Agent Modes

- Explorer: establish facts and open questions
- Spec: define Goal, Facts, Decision, and Acceptance
- Plan: define the minimal execution path
- Code: implement the current spec and keep it verifiable
- Review: verify acceptance coverage, regressions, and spec-code consistency

## Execution Flow

### Stage Entry

- Enter Explorer when facts are insufficient
- Enter Spec when Goal and Acceptance can be defined
- Enter Plan when Decision is clear
- Enter Code only when Plan and Acceptance exist

### Stage Exit

- Exit Explorer when facts are sufficient
- Exit Spec when Acceptance is testable and bounded
- Exit Plan when critical path is minimal and explicit
- Exit Code only when code, tests, and spec are consistent

## Code Loop

When in Code:

Red → Green → Refactor → Commit

- Each step MUST be verifiable
- Refactor MUST preserve behavior
- Do not accumulate large unverified changes

## Change Discipline

- Spec and code MUST be updated together
- Progress MUST reflect reality
- If facts invalidate decision, update spec first
