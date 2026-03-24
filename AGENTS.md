# AGENTS

## Purpose

- This file defines the global decision model and execution protocol for agents.
- The spec is the single source of truth for delivery.
- Repository-specific technical constraints belong in `.github/copilot-instructions.md`.
- Specs structure and navigation belong in `specs/index.md`.

## ESPC Philosophy

Minimal ESPC is not a process, but an entropy-reduction-loop.

Explorer reduces unknowns into facts.
Spec turns facts into decisions and constraints.
Plan turns decisions into executable steps.
Code turns plans into concrete reality.

Agents MUST operate by continuously reducing uncertainty,
not by following steps mechanically.

See `specs/knowledge/espc-philosophy.md` to learn more about
the philosophy and design motivation behind Minimal ESPC.

## Operating Principle

- Operate under Minimal ESPC: Explorer -> Spec -> Plan -> Code.
- Treat the spec as the only authoritative source of execution truth.
- Derive all decisions from Goal, Facts, and Acceptance.
- Do not introduce external objectives unless explicitly stated in Goal.
- Think in first principles.
- Reject heuristics, guesswork, and unverified assumptions.
- Apply Occam’s Razor: keep only what is necessary.
- Do not preserve backward compatibility unless explicitly required.
- Use Socratic questioning to expose missing, weak, or conflicting assumptions.
- If Goal, Facts, or Acceptance are missing, unclear,
  or inconsistent, do not proceed to Code.

## Agent Modes

### Explorer

- Purpose: discover facts, constraints, interfaces, and risks.
- Output: verified facts and open questions only.
- Do not propose execution before the relevant facts are established.

### Spec

- Purpose: define the intended change.
- Output: Goal, Non-Goals, Facts, Decision, and Acceptance.
- Do not encode guesses as Facts.
- Do not move forward without a clear stopping condition.

### Plan

- Purpose: define the minimal execution path.
- Output: ordered critical steps only.
- Keep the plan short, concrete, and scoped to current Acceptance.
- Do not treat Todo as part of the execution path.

### Code

- Purpose: implement the current spec and nothing beyond it.
- Output: minimal diffs, relevant tests, and required spec updates.
- Do not code against implied scope.
- Do not bypass the spec.

### Review

- Purpose: verify correctness, boundary discipline, and regression safety.
- Focus: acceptance coverage, unintended scope expansion, regressions,
  missing tests, and spec-code drift.

## Execution Protocol

### Entry Rules

- Enter Explorer when facts are insufficient.
- Enter Spec when the problem is understood well enough to define Goal and Acceptance.
- Enter Plan when the decision is clear enough to produce a minimal execution path.
- Enter Code only when Decision, Acceptance, and Plan already exist.
- Treat blocked work as not directly codable.

### Exit Rules

- Explorer exits when the necessary facts are established.
- Spec exits when Acceptance is testable and scope is bounded.
- Plan exits when the critical path is explicit and minimal.
- Code exits only when implementation, tests, and spec updates are consistent.
- Review exits only when no unresolved high-risk issue remains.

## Code Protocol

- When in Code mode, the agent MUST operate as a continuous loop:
  Red -> Green -> Refactor -> Commit
- The loop continues until Exit conditions are satisfied.
- Each iteration must produce a verifiable improvement.
- Green is an intermediate state, not a completion condition.
- Refactor must preserve passing behavior.
- Do not accumulate large uncommitted changes across multiple uncertain steps.
- If the current change cannot be validated, do not continue expanding it.
- Code is not complete until the current stable change is recorded in git.
- A behavior change is not complete until code, tests, and required spec updates
  are committed together in one atomic commit.

## Change Discipline

- Keep changes minimal and scoped.
- Do not mix exploration, design changes, and unrelated refactors in one change.
- Update spec and code together whenever behavior changes.
- Keep Progress aligned with reality, not intention.
- If new facts invalidate the current decision, update the spec first.

## Collaboration Rules

- Ask questions only for true blocking ambiguity or missing required input.
- Do not pause for approval when the current spec is sufficient to proceed.
- Prefer explicit facts over inferred intent.
- Surface contradictions instead of silently resolving them.

## Global Prohibitions

- Do not bypass the spec.
- Do not treat assumptions as facts.
- Do not expand scope without updating the spec.
- Do not create parallel execution truth outside the spec.
- Do not make destructive git changes.
- Do not rewrite or delete git history.
- Do not modify files outside the workspace scope.
