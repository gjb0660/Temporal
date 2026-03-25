# Contracts

## Purpose

`contracts/` 是系统约束的唯一真源。

## Index Rules

- 本文件仅指导 contract 的语义与格式
- 本文件不枚举具体 contract 文件
- 本文件不承载 contract 的更新状态
- 具体 contract 文件通过目录遍历发现

## Semantics

Contract 定义系统“不能被破坏的规则”

- Feature = 做什么
- Contract = 不允许破坏什么

Contract MUST:

- 每个 contract 为单一文件
- 稳定且可复用
- 与具体 feature 解耦

Contract MUST NOT:

- 引用 feature
- 包含执行结构（Plan / Progress / Todo）
- 描述交付步骤

Contract SHOULD：

- 按领域组织（ui / api / data）
- 感知设计意图
- 定义约束空间

Contract SHOULD NOT:

- 陷入技术细节
- 枚举具体行为

Contract MAY:

- 阐明缘由
- 定义变更空间
- 列举反模式

## Guardrails

Contracts 每个 section 的语义约束如下：

### Role

- 定义 contract 的语义责任
- MUST 描述 contract 是什么以及它负责什么
- MUST NOT 包含约束（使用 Invariants）
- MUST NOT 包含解释（使用 Rationale）
- MUST NOT 包含允许的变更（使用 Variation Space）
- SHOULD 简洁（1–3 句）

### Invariants

- 定义不可谈判的约束
- MUST 最小且稳定
- MUST NOT 编码实现细节

### Variation Space

- 定义设计的自由度
- MUST 描述维度，而非枚举变体
- MUST 保持在 Invariants 隐含的边界内
- SHOULD 最小但足以支持设计探索

### Rationale

- 定义 Invariants 的因果解释
- MUST 解释为什么 Invariants 存在
- MUST NOT 重述 Variation Space
- SHOULD 提供设计意图以指导 Variation Space 的使用

### Anti-Patterns

- 定义常见的错误解决方案
- MUST NOT 作为主要约束
- SHOULD 描述违反 Invariants 或 Rationale 的模式
- SHOULD 帮助 agents 避免错误实现，而非枚举所有无效情况

## Relationship

Contract 可以引用：

- 其他 Contract 作为约束前提
- Knowledge 作为背景与参考来源

Contract MAY 在以下位置被引用：

- Repository Rules
- Workspace Skills
- Feature Facts, Decision, Non-Goals

## Frontmatter

### `title`

- contract 的唯一标识符，与文件名一致
- 应与功能或领域相关，不随时间变化

### `scope`

- `ui`: 用于用户可见的视觉与交互约束
- `api`: 用于行为、调用与边界交互约束
- `data`: 用于字段、模式、类型与状态约束

### `stability`

- `strict`: 不得随意更改
- `semi`: 允许在明确评审后更改
- `flexible`: 低成本约束，可以演进

### `version`

- contract 的修订版本，格式为 `<major>.<minor>`，如 `1.0`。

## Format

Contract spec 须遵循标准结构：

- UTF-8 + LF
- Markdown 格式
- YAML frontmatter metadata
- 英文标题（# / ##）
- 本地语言正文（如中文）

**Template**:

```md
---
title: <contract-name>
scope: ui | api | data
stability: strict | semi | flexible
version: <major>.<minor>
---

## Role

<what this contract is responsible for (semantic anchor)>

## Invariants

- <must always hold>

## Variation Space

- <allowed dimensions of change (NOT enumerating cases)>

## Rationale (Optional)

- <why these invariants exist>
- <design intent that constrains how variation space should be used>

## Anti-Patterns (Optional)

- <commonly misused or harmful patterns>
```
