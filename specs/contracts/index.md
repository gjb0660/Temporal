# Contracts

## Purpose

`contracts/` 是系统约束的唯一真源。

## Semantics

Contract 定义系统“不能被破坏的规则”。

- Feature = 做什么
- Contract = 不允许破坏什么

## Rules

- Contract MUST 稳定且可复用
- Contract MUST 与具体 feature 解耦
- Contract MUST NOT 引用 feature
- Contract MUST NOT 包含执行状态（Plan / Progress / Todo）
- Contract MUST NOT 描述交付步骤

## Structure

- 每个 contract MUST 为单一文件
- SHOULD 按领域组织（ui / api / data）

## Usage

Feature MAY 在以下位置引用 Contract：

- Facts
- Decision
- Non-Goals

## Boundary

- Contract MUST NOT 驱动执行
- Contract MUST NOT 感知 feature
- Contract MUST ONLY 定义约束

## Format

Contract spec MUST 遵循标准结构：

- UTF-8 + LF
- Markdown 格式
- YAML frontmatter metadata
- MUST 使用英文标题（# / ##）
- 正文 MUST 使用本地语言（如中文）

**Metadata**:

- `scope`:
  - `ui`: user interface constraints
  - `api`: interface and protocol constraints
  - `data`: schema and data-model constraints
- `stability`:
  - `strict`: must not change casually
  - `semi`: change allowed with explicit review
  - `flexible`: low-cost constraint, can evolve
- `version`: contract revision

**Template**:

```md
---
title: <contract-name>
scope: ui | api | data
stability: strict | semi | flexible
version: <version-number>
---

## Role

<what this contract is for>

## Invariants

- <must always hold>

## Allowed Changes

- <safe changes>

## Forbidden Changes

- <forbidden changes>

## Notes

<extra rationale or migration notes>
```

**Notes**:

- MUST NOT 添加执行结构（Plan / Progress / Todo）
- MUST NOT 缺失任何核心 section
- MUST NOT 改变 section 顺序
