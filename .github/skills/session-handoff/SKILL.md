---
name: session-handoff
description: "Use when: preparing end-of-session handoff, updating progress docs, recording validation status, and drafting a practical next-session checklist. Keywords: handoff, session summary, 会话交接, 阶段进度, next steps."
argument-hint: "handoff date and scope"
---

# Session Handoff Skill

## When To Use

Use this skill when ending a work session and handing off to a new chat/session.

Typical triggers:

- "整理会话纪要"
- "写交接文档"
- "总结本次进展并给下次任务"
- "更新阶段进度"

## Inputs

- Handoff date (for filename)
- Current objective and phase
- Workspace status and validation evidence

## Procedure

1. Collect status context.
2. Capture validation evidence.
3. Update progress documentation.
4. Create/update handoff document.
5. Produce concise chat summary for next session.

## Step Details

### 1) Collect Status Context

- Read `specs/index.md` first for repository routing and export rules.
- Inspect workspace status and current delivery scope. Example commands:
  - `git status --short --untracked-files=all`
- Identify completed scope, in-progress scope, and pending items.

### 2) Capture Validation Evidence

- Record checks that were actually executed in this session.
- If the repository uses uv, prefer uv-based commands;
  otherwise use the local standard toolchain.
- Temporal example commands:
  - `uv run pyside6-qmllint src/temporal/qml/Main.qml`
  - `uv run pyside6-qmlformat -i src/temporal/qml/Main.qml`
  - `uv run ruff check src tests`
  - `uv run python -m unittest discover -s tests -p "test_*.py" -v`

### 3) Update Progress Documentation

- Update the project progress document
  (for Temporal: `specs/in-progress.md`) with:
  - Completed phases and deltas
  - Next actionable items
  - Session lessons confirmed with user

### 4) Create/Update Handoff Document

- Use repository convention for handoff path and date naming.
- Temporal default: `specs/handoffs/session-YYYY-MM-DD.md`.
- Use [handoff template](./references/handoff-template.md).
- Write new handoff documents with English headings
  and concise Chinese technical body text.
- Store handoff Markdown files as UTF-8 without BOM and LF line endings.
- Include handoff contract fields when available
  (for example from AGENTS workflow):
  - changed files list
  - assumptions
  - validation performed
  - unresolved risks

### 5) Produce Chat Summary

- Return a short summary with:
  - What is done
  - What remains
  - Suggested first 3 commands or actions for next session

## Decision Points

- If no dedicated progress doc exists,
  write a short progress section in the handoff doc.
- If no tests/lints were run, explicitly state "not run" and explain the reason.
- If the workspace is dirty with unrelated changes,
  record this risk in handoff notes.

## Quality Checklist

- Documentation is concise and audience-appropriate
  (Temporal handoff docs use English headings and concise Chinese body text).
- Validation facts are consistent with actual git/test outputs.
- Content does not conflict with active repository rules
  (for Temporal: `.github/copilot-instructions.md` and `AGENTS.md`).
- If code changes are included in the same session,
  keep implementation and tests aligned in the same delivery unit.

## Exit Criteria

- Progress information reflects current session state
  in the repository's preferred location.
- A dated handoff note is available
  in the repository's chosen handoff location.
- Next-session checklist is specific enough to execute directly.
