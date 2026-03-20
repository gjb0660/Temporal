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
2. Check every required workflow contract in
   [workflow-contracts](./references/workflow-contracts.md).
3. Record findings by severity and file.
4. Produce a minimal consolidation plan.
5. Produce a validation checklist.

## Audit Reference

- Use [workflow-contracts](./references/workflow-contracts.md)
  as the canonical audit checklist.
- Keep the main SKILL focused on scope, process,
  output structure, and constraints.

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
