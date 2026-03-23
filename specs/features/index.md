# Features

## Purpose

`features/` 是系统唯一的执行入口与执行真源。

所有代码变更 MUST 由 feature spec 驱动。

## Semantics

每个 feature：

- MUST 是一个完整 ESPC 闭环
- MUST 使用单一 spec 文件
- MUST 承载全部执行信息

## Rules

- 一个 feature MUST 对应一个 spec 文件
- MUST NOT 拆分为多个执行文档
- MUST NOT 存在平行执行源

## Execution Model

Feature MUST 遵循以下闭环：

Goal → Non-Goals → Facts → Decision → Acceptance
→ Plan → Progress → (feedback → Facts) → Todo

## Preconditions

Agents MUST NOT 开始执行，除非：

- Goal 已定义
- Decision 已存在
- Acceptance 已明确
- Plan 已存在

## Relationship

Feature MAY 引用：

- contracts（约束）
- knowledge（背景）

## Boundary

- Feature MUST 是唯一执行入口
- 所有执行状态 MUST 存在于 feature 内
- 任何目录不得承载执行状态（除 feature）

## Format Template

Feature spec MUST 遵循标准结构：

- UTF-8 + LF
- Markdown 格式
- YAML frontmatter metadata
- MUST 使用英文标题（# / ##）
- 正文 MUST 使用本地语言（如中文）

**Metadata**:

- `title`: stable identifier (function/domain-based, not time-based)
- `tracker`:
  - `feature`: deliver new capability
  - `bugfix`: fix incorrect behavior
  - `refactor`: improve existing structure
  - `research`: clarify unknowns
- `status`:
  - `exploring`: not ready to execute
  - `active`: in progress
  - `blocked`: cannot proceed
  - `done`: completed
- `owner`: current responsible agent
- `updated`: last meaningful update (YYYY-MM-DD)

**Template**:

```md
---
title: <feature-name>
tracker: feature | bugfix | refactor | research
status: exploring | active | blocked | done
owner: <agent|human>
updated: YYYY-MM-DD
---

## Goal
## Non-Goals

## Facts
## Decision

## Acceptance
1. <acceptance criteria 1>
2. <acceptance criteria 2>

## Plan
1. <step 1>
2. <step 2>

## Progress
- [ ] <current progress item>
- [x] <completed item>

## Todo
- [ ] <non-critical or next-stage item>
```

**Notes**:

- MUST NOT 添加具体执行细节（如代码实现）
- MUST NOT 缺失任何核心 section
- MUST NOT 改变 section 顺序
