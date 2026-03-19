---
description: >-
  Use when: auditing repository rules for redundancy, missing workflow
  constraints, weak instruction coverage, frontmatter validity, and
  conflicting agent customization sources. Keywords: rules audit, 冗余扫描,
  漏项扫描, governance review, instruction overlap.
---

# Rules Audit

Audit repository governance files under `.github/**`, `AGENTS.md`, and
`docs/**` only when they define or repeat agent workflow rules.

Goal:

- find redundant rules
- find missing rules
- find conflicting rules
- keep guidance short and enforceable

Always check these workflow contracts:

1. Python changes require lint -> fix -> format.
2. QML changes require lint -> fix -> format.
3. TDD must complete Red -> Green -> Refactor.
4. Rule documents must stay terse and avoid repeated guidance.
5. Agents must use `vscode_askQuestions` only at true blocking
  decisions.
6. Agents must not require a pre-code approval step
  for implementable tasks.

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

Constraints:

- Prefer the smallest rule change that fixes the gap.
- Do not propose broad rewrites when a local edit is enough.
- Prefer imperative bullets over paragraphs.
- Flag `applyTo: "**"` unless it is truly required.
- Flag prompt or skill descriptions that are too vague to be discoverable.
