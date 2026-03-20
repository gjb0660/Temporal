# Spec: Phase E Agent Governance and Collaboration

## Goal

Codify stable Copilot collaboration rules for Temporal delivery.

## Scope

- Define repository-level coding and safety rules.
- Define domain-specific instruction files for backend, qml, and tests.
- Define agent handoff contract and review focus order.
- Define ODAS workflow skill for repeatable implementation quality.

## Non-Goals

- Runtime application features.
- Deployment pipeline automation.
- External policy synchronization.

## Functional Requirements

1. Keep instruction files discoverable under .github hierarchy.
2. Keep rule wording actionable and concise.
3. Enforce Explore -> Spec -> Plan -> Code workflow.
4. Require `vscode_askQuestions` only for true blocking decisions
   or missing required inputs.
5. Include constraints for non-destructive git operations.
6. Do not require a pre-code approval step for implementable tasks.
7. Keep `specs/index.md` as the static contract entry.
8. Keep `specs/in-progress.md` as the dynamic routing and state source.
9. Keep handoff contract only in `specs/index.md`.
10. Define Code as `Red -> Green -> Refactor -> Commit`
   after Spec and Plan entry conditions are satisfied.
11. Use the existing Review Agent to evaluate Refactor quality
   for high-risk or test-driven behavior changes.

## Quality Requirements

- Keep markdownlint clean on all governance files.
- Keep frontmatter valid when required by instruction system.

## Acceptance Criteria

1. Agent can load and apply rules without ambiguity.
2. Rule files reflect current repository conventions.
3. Review agent priorities cover regression and data-loss risks.
