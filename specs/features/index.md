# Features

## Purpose

`features/` 是系统唯一的执行入口与执行真源。

## Index Rules

- 本文件仅指导 feature 的语义与格式
- 本文件不枚举具体 feature 文件
- 本文件不承载 feature 的执行状态
- 具体 feature 文件通过目录遍历发现

## Semantics

Feature 定义系统“必须完成的行为”，是代码变更的直接驱动者。

Feature MUST:

- 每个 feature 为单一文件
- 所有代码变更由 spec 驱动，是一个完整的极简 ESPC 闭环
- 承载该执行单元的目标、事实、决策、验收、计划与进度

Feature MUST NOT:

- 包含具体代码实现
- 缺失任何核心 section
- 改变核心 section 顺序

## Guardrails

Feature 每个 section 的语义约束如下：

## Goal

- SHOULD be clear and focused
- SHOULD NOT be vague or broad

### Non-Goals

- SHOULD clarify out-of-scope items
- SHOULD NOT be empty or trivial

### Facts

- SHOULD be verified realities
- SHOULD NOT contain assumptions or solutions

### Decision

- SHOULD be based on Facts
- SHOULD represent the current chosen approach only

### Acceptance

- SHOULD be clear and testable
- SHOULD NOT be vague or aspirational

### Plan

- SHOULD be the critical path
- SHOULD NOT include optional or future work

### Progress

- SHOULD reflect actual execution only
- SHOULD NOT include future actions

### Todo

- SHOULD contain non-critical or deferred work
- SHOULD NOT replace Plan

## Relationship

Feature 可以引用：

- 其他 Feature 作为执行依赖
- contracts 作为约束来源
- knowledge 作为背景与参考来源

## File Naming

- MUST 与 title 一致，使用 kebab-case
- MUST 表达能力或领域（function/domain），而不是时间或阶段
- MUST NOT 包含时间、阶段或版本信息（如 phase-a, v2）
- MUST NOT 混合多个语义（如 test-and-hardening）
- SHOULD 优先体现能力边界，而不是实现细节或根因
- SHOULD 在长期演进中仍成立，才是有效命名

> Naming defines boundary. Boundary defines system.

### `primary-feature` and `feature`

能力型 Feature 使用纯能力名：`<capability>.md`
如 `recording.md`、`media-pipeline.md`、`ui-system.md`

### `bugfix`

语义是 fix incorrect behavior，命名应直接暴露被修正的行为偏差。

行为修正类名称应直接暴露错误行为：`<capability>-<failure>.md`
如 `recording-stop-failure.md`、`preview-mode-freeze.md`

### `refactor`

语义是 improve existing structure，而不是交付新能力

结构调整类名称应体现被调整对象：`<capability>-refactor-<target>.md`
如 `recording-refactor-pipeline.md`、`ui-system-layout-refactor.md`

### `research`

语义是 clarify unknowns，而不是预设结论。

探索类名称应表达待澄清的问题域：`<domain>-analysis.md` / `<domain>-research.md`
如 `odas-integration-research.md`、`session-handoff-analysis.md`

## Frontmatter

### `title`

- identifier 与文件名一致
- 功能或领域相关，不随时间变化

### `tracker`

- `primary-feature`
  - 表示系统的一级长期能力域，是系统主骨架的一部分
  - Acceptance 必须体现该长期能力独立成立
- `feature`：
  - 表示独立执行单元，但不属于一级长期能力域
  - Acceptance 必须体现该 supporting capability 或工作单元已形成独立闭环
- `bugfix`
  - 表示修正已承诺行为的偏差
  - Acceptance 必须体现 failure-path 或回归证据
- `refactor`：
  - 表示调整既有结构，不引入新的外部能力语义
  - Acceptance 必须体现行为边界不变
- `research`：
  - 表示澄清未知问题域，不直接驱动代码变更
  - 可以不落代码实现，但必须收敛 Facts 与 Decision

### `status`

- `exploring`：问题边界仍在收集，尚未形成可执行闭环
- `active`：当前 feature 正在推进，进度以该文件为准
- `blocked`：存在外部阻断，当前不能继续推进
- `done`：当前验收闭环已完成

### `owner`

可以为 agent 或 human：

- `<agent-role>`：实际参与执行的 agent，如 `codex/ui`
- `<human-name>`：实际参与执行的 human，如 `garrett`

### `updated`

- 最近一次有意义的更新，格式为 `YYYY-MM-DD`，如 `2026-03-25`

## Format

Feature spec 须遵循标准结构：

- UTF-8 + LF
- Markdown 格式
- YAML frontmatter metadata
- 英文标题（# / ##）
- 本地语言正文（如中文）

**Template**:

```md
---
title: <feature-name>
tracker: primary-feature | feature | bugfix | refactor | research
status: exploring | active | blocked | done
owner: <agent-role> | <human-name>
updated: YYYY-MM-DD
---

## Goal

<clear and focused goal statement>

## Non-Goals
- <clarify out-of-scope item 1>
- <clarify out-of-scope item 2>

## Facts
- <evidence or reality 1>
- <evidence or reality 2>

## Decision
- <chosen approach 1>
- <chosen approach 2>

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
- [ ] <non-critical and deferred item>
```
