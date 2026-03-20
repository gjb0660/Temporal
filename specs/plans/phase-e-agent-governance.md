# Spec: Phase E Agent Governance and Collaboration

## Goal

Codify stable Copilot collaboration rules for Temporal delivery.

## Scope

- Define repository-level coding and safety rules.
- Define domain-specific instruction files for backend, qml, and tests.
- Define agent handoff contract and review focus order.
- Define ODAS workflow skill for repeatable implementation quality.
- Define governance repair and governance audit skills
   for repeatable rule maintenance.
- Define a push prompt for advancing work with
   spec update, test-first execution, and final commit discipline.

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
12. Treat code work as incomplete until the commit is recorded in git.
13. Treat unclear risk classification as high-risk by default.
14. Keep governance repair workflow under
      `.github/skills/rules-governance/`.
15. Keep governance audit workflow under
      `.github/skills/rules-audit/` instead of prompt form.
16. Keep next-step progression prompt under
   `.github/prompts/push.prompt.md`.

## Quality Requirements

- Keep markdownlint clean on all governance files.
- Keep frontmatter valid when required by instruction system.
- Keep skill names, folder names, and descriptions aligned
   for discovery.
- Keep prompt descriptions specific enough for discovery.

## Acceptance Criteria

1. Agent can load and apply rules without ambiguity.
2. Rule files reflect current repository conventions.
3. Review agent priorities cover regression and data-loss risks.
4. Governance audit and repair workflows are discoverable as skills.
5. Next-step progression workflow is discoverable as a prompt.
