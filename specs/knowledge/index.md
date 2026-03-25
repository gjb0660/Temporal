# Knowledge

## Purpose

`knowledge/` 是可复用的参考知识库。

## Index Rules

- 本文件仅指导 knowledge 的语义与格式
- 本文件不枚举具体 knowledge 文件
- 本文件不承载 knowledge 的更新状态
- 具体 knowledge 文件通过目录遍历发现

## Semantics

Knowledge 表示“已确认的信息与结论”，只提供信息，不参与执行。

Knowledge SHOULD:

- 只读内容
- 提供可提取的明确结论（要点 / 结论）
- 提供可扫描的清晰结构（分段 / 列表）

Knowledge SHOULD NOT:

- 驱动执行 (属于 feature)
- 定义约束（属于 contract）

Knowledge MAY:

- 包含来源引用（如文献 / 数据）
- 总-分-总结构（Overview → Details → Summary）

## Guardrails

Knowledge 每个 section 的语义约束如下：

### Overview

- SHOULD 提供清晰的要点总结
- SHOULD NOT 过于冗长或细节

### Summary

- SHOULD 提供明确的结论或启示
- SHOULD NOT 过于模糊或宽泛

## Relationship

Knowledge 可以引用：

- 其他 Knowledge 作为补充知识
- 图片、表格、web资源等作为辅助材料

Knowledge MAY 在以下位置被引用：

- Repository Rules
- Workspace Skills
- Feature Facts, Decision 与 Acceptance
- Contract Rationale

## Format

Knowledge spec 建议遵循标准结构：

- UTF-8 + LF
- Markdown 格式
- 英文标题（# / ##）
- 本地语言正文（如中文）

**Examples**:

```md
# Knowledge Example

## 1. Overview

Key Points

## 2. ...

## N. Summary

Conclusions

## References
- [Source 1](url)
- [Source 2](url)
```

## Anti-Patterns

- SHOULD NOT 包含执行结构（Plan / Progress / Todo）
- SHOULD NOT 包含约束定义（Contract）
