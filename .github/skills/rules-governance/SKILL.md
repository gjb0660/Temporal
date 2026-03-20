---
name: rules-governance
description: "Use when: repairing agent governance after workflow drift, fixing completion-standard gaps, aligning AGENTS/specs/skills, removing stale rule references, and turning session lessons into enforceable repository rules. Keywords: rules governance, governance repair, rule fix, execution standard, completion boundary, rules drift, 治理修正, 规则治理, 完成标准."
argument-hint: "governance gap or failure mode to repair"
---

# Rules Governance Skill

## When To Use

Use this skill when repository workflow rules have drifted from actual practice,
when an agent completed work with the wrong execution standard,
or when governance files disagree about routing, quality gates,
or completion criteria.

Typical triggers:

- "修正规则"
- "分析为什么执行标准不合格"
- "把这次治理经验固化下来"
- "同步 AGENTS、specs、skill"
- "清理规则冗余和旧引用"

## Inputs

- The failure mode or workflow gap to repair
- The authoritative files currently carrying the rule
- Whether the task is audit-only or audit-plus-fix

## Procedure

1. Read the active governance baseline.
2. Locate the concrete failure mode.
3. Classify the gap before editing.
4. Apply the smallest cross-file repair.
5. Validate rule alignment and file reality.
6. Commit only the intended governance files.
7. Report residual risks and ambiguities.

## Step Details

### 1) Read The Active Governance Baseline

- Read `AGENTS.md` for workflow and completion rules.
- Read `.github/copilot-instructions.md` for repository quality gates.
- Read `specs/index.md` for static contract.
- Read `specs/in-progress.md` for dynamic routing if the rules point there.
- Read `.github/skills/rules-audit/SKILL.md` if the fix must remain auditable.
- Read any touched skill file if it already participates in the flow.

### 2) Locate The Concrete Failure Mode

- Identify the exact point where behavior and rules diverged.
- Prefer one falsifiable statement, for example:
  - completion claimed before git commit
  - review gate too conditional
  - static index points to the wrong live board
  - skill or handoff still names a retired file
- Check the current workspace state before editing.
- Treat recent user edits as authoritative unless they directly conflict
  with the requested repair.

### 3) Classify The Gap Before Editing

Classify each finding into one of these buckets:

- Missing boundary: a completion or entry condition is implied but not explicit.
- Rule drift: two governance files say different things.
- Dead reference: a rule points to a file or path that no longer matches reality.
- Weak auditability: the rule exists but the audit skill cannot detect its absence.
- Overlap: the same rule is duplicated in the wrong layer.

Edit only the files needed to fix the active bucket.

### 4) Apply The Smallest Cross-File Repair

- Put workflow behavior in `AGENTS.md`.
- Put repository quality gates in `.github/copilot-instructions.md`.
- Put static routing and collaboration contract in `specs/index.md`.
- Put dynamic routing and live state in `specs/in-progress.md`.
- Put audit checks in `.github/skills/rules-audit/SKILL.md`.
- Put task-specific end-of-session procedure in the relevant skill.
- If a rule points to a live file that does not exist,
  create the file or retarget the rule immediately.
- Prefer imperative bullets over narrative paragraphs.
- Prefer minimal edits over broad rewrites.

### 5) Validate Rule Alignment And File Reality

- Search for stale terms and retired paths after editing.
- Run markdownlint on every touched Markdown file.
- Confirm that newly referenced files actually exist in the workspace.
- Confirm that the repaired rule is present in every required layer,
  but not duplicated into unrelated layers.
- If the repair changes completion semantics,
  confirm the wording is explicit enough to audit mechanically.

### 6) Commit Only The Intended Governance Files

- Inspect git status before commit.
- If unrelated changes exist, do not revert them.
- Use a path-limited commit when needed so the governance fix stays atomic.
- Treat the repair as incomplete until the commit is recorded in git.

### 7) Report Residual Risks And Ambiguities

- List any unchanged files that still carry historical wording.
- Note any duplicate systems that still coexist temporarily.
- If a weak area remains but is not safe to change now,
  name it as follow-up instead of silently stretching this patch.

## Decision Points

- If the task is audit-only, stop after findings and patch plan.
- If the task requests a fix, do not stop at analysis.
- If risk classification is unclear, treat the change as high-risk.
- If an execution rule cannot be validated by current wording,
  strengthen the wording instead of adding commentary around it.
- If historical handoff notes disagree with current governance,
  do not rewrite them unless the task explicitly includes historical cleanup.

## Quality Checklist

- Completion boundary is explicit and testable.
- Static and dynamic routing files are not confused.
- Audit skill can detect the repaired rule.
- No stale file path remains in touched governance files.
- Markdownlint passes on all touched Markdown files.
- The final fix is recorded in git.

## Exit Criteria

- The target governance gap is repaired at the correct layer.
- Referenced live files exist and match the rule text.
- Validation was run and reported accurately.
- A focused git commit records the repair when code changes were requested.
