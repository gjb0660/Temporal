---
name: rules-audit
description: "Use when: auditing repository rules for redundancy, missing workflow constraints, weak instruction coverage, discoverability gaps, and conflicting customization sources. Keywords: rules audit, governance review, instruction overlap, 冗余扫描, 漏项扫描, 治理审计."
argument-hint: "audit scope or governance concern"
---

# Rules Audit Skill

## When To Use

Use this skill when auditing repository governance files for rule drift,
redundancy, missing workflow constraints,
or weak wording that cannot be enforced reliably.

Typical triggers:

- "跑一轮 rules audit"
- "扫描规则冗余和遗漏"
- "检查治理文件有没有冲突"
- "审计 instructions、skills、AGENTS 是否一致"

## Scope

Audit repository governance files under `.github/**`, `AGENTS.md`,
and `specs/**` only when they define or repeat agent workflow rules.

## Goal

- find redundant rules
- find missing rules
- find conflicting rules
- keep guidance short and enforceable

## Procedure

1. Read the active governance baseline.
2. Check every required workflow contract.
3. Record findings by severity and file.
4. Produce a minimal consolidation plan.
5. Produce a validation checklist.

## Workflow Contracts To Check

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

## Output Format

Return findings in this order:

1. Critical conflicts.
2. Missing coverage.
3. Redundant or repeated guidance.
4. Weak wording that should become explicit requirements.

For each finding, include:

- file path
- why it matters
- minimal edit direction

Then return:

1. A consolidation plan that removes duplication without losing
   necessary file-specific instructions.
2. A minimal patch plan grouped by file.
3. A validation checklist with exact commands to run after edits.

## Constraints

- Prefer the smallest rule change that fixes the gap.
- Do not propose broad rewrites when a local edit is enough.
- Prefer imperative bullets over paragraphs.
- Flag `applyTo: "**"` unless it is truly required.
- Flag skill descriptions that are too vague to be discoverable.
