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
- Define document language, encoding, and line-ending rules
  with explicit ownership boundaries across governance files.

## Non-Goals

- Runtime application features.
- Deployment pipeline automation.
- External policy synchronization.

## Functional Requirements

1. Keep instruction files discoverable under .github hierarchy.
2. Keep rule wording actionable and concise.
3. Keep `AGENTS.md` as the workflow authority for execution order,
   code entry, code exit, and git-safety behavior.
4. Keep `specs/index.md` as the static contract entry.
5. Keep `specs/in-progress.md` as the dynamic routing and state source.
6. Keep handoff contract only in `specs/index.md`.
7. Keep governance repair workflow under
      `.github/skills/rules-governance/`.
8. Keep governance audit workflow under
      `.github/skills/rules-audit/` instead of prompt form.
9. Keep next-step progression prompt under
   `.github/prompts/push.prompt.md`.
10. Keep `specs/index.md` as the language contract for new
   `specs/**/*.md` and `specs/handoffs/**/*.md` files.
11. Keep `.github/copilot-instructions.md` as the language contract for new
   `docs/**/*.md`, source code comments, git commit messages,
   and repository encoding or line-ending policy.
12. Treat retained English historical specs, docs, and handoffs as audit
   observations or statistics instead of standalone findings.
13. Normalize historical handoff language in scheduled batches,
   not through incidental rewrites.

## Quality Requirements

- Keep markdownlint clean on all governance files.
- Keep frontmatter valid when required by instruction system.
- Keep skill names, folder names, and descriptions aligned
   for discovery.
- Keep prompt descriptions specific enough for discovery.
- Keep repository encoding and line-ending policy enforceable
  through repo config.

## Acceptance Criteria

1. Agent can load and apply rules without ambiguity.
2. Rule files reflect current repository conventions.
3. Review agent priorities cover regression and data-loss risks.
4. Governance audit and repair workflows are discoverable as skills.
5. Next-step progression workflow is discoverable as a prompt.
6. Language and encoding rules are assigned to explicit governance owners
   without ambiguity.
