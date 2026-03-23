# Knowledge

## Purpose

`knowledge/` 是可复用的参考知识库。

## Semantics

Knowledge 表示“已确认的信息与结论”，不参与执行。

## Rules

- Knowledge MUST 为只读内容
- Knowledge MUST NOT 包含执行状态：
  - Plan
  - Progress
  - Todo
- Knowledge MUST NOT 驱动执行

## Structure

Knowledge 文件：

- MUST 可扫描（结构清晰）
- MUST 提供明确结论（Key Points / Conclusions）

## Usage

Feature MAY 在以下位置引用 Knowledge：

- Facts
- Decision

## Boundary

- Knowledge MUST NOT 参与执行
- Knowledge MUST NOT 定义约束（属于 contract）
- Knowledge MUST ONLY 提供信息

## Format

Knowledge spec MUST 遵循标准结构：

- UTF-8 + LF
- Markdown
- SHOULD 使用英文标题（# / ##）
- 正文 SHOULD 使用本地语言（如中文）

**Guidelines**:

- SHOULD 提供清晰结构（分段 / 列表）
- SHOULD 提供可提取结论（Key Points / Conclusions）
- SHOULD 包含来源引用（如文献 / 数据）
- SHOULD 总-分-总结构（Overview → Details → Summary）

**Examples**:

```md
# Knowledge Example

## 1. Overview

Key Points

## 2. Details

...

## N. Summary

Conclusions

## References
- [Source 1](url)
- [Source 2](url)
```

**Notes**:

- SHOULD NOT 包含执行结构（Plan / Progress / Todo）
- SHOULD NOT 包含约束定义（Contract）
