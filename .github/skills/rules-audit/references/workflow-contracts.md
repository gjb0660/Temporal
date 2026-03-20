# Workflow Contracts

Audit these contracts whenever repository governance files
define or repeat agent workflow rules.

1. Python changes require lint -> fix -> format.
2. QML changes require lint -> fix -> format.
3. TDD must complete Red -> Green -> Refactor.
4. Rule documents must stay terse and avoid repeated guidance.
5. Agents must use `vscode_askQuestions` only at true blocking decisions.
6. Agents must not require a pre-code approval step
   for implementable tasks.
7. Workflow must be Explore -> Spec -> Plan -> Code.
8. `specs/index.md` is the static entry; `specs/in-progress.md`
   is the dynamic routing and state board.
9. New feature startup must check `specs/in-progress.md`
   for duplicate demand.
10. Code requires Definition and Execution unless the target feature
    declares `Exception: small-change`.
11. `small-change` relaxes Plan only; it does not waive Refactor.
12. Code completion requires Red -> Green -> Refactor -> Commit.
13. High-risk or test-driven behavior changes must run
    the existing Review Agent before Code is considered complete.
14. `docs/` is exported human-facing output,
    not the AI execution source.
15. Code is not complete until the commit is recorded in git.
16. If risk classification is unclear, audit must treat the change
    as high-risk by default.
17. English scenario: keep `.github/**` instruction files,
    `AGENTS.md`, code comments, and git commit messages in English;
    allow English Markdown only for retained legacy files
    or imported external reference material.
18. Chinese scenario: write newly created `specs/**/*.md`,
    `specs/handoffs/**/*.md`, and `docs/**/*.md`
    with English headings and Chinese body text;
    keep tables and explanatory comment examples in Chinese,
    preserve stable technical terms in English,
    and store Markdown files as UTF-8 without BOM and LF line endings.
19. Historical handoff documents must be governed
    by an explicit Chinese-normalization plan.
