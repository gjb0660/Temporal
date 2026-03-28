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

## File Naming

- MUST 使用 kebab-case（小写 + 连字符）
- SHOULD 表示一个稳定的知识领域，长期有效，无需重命名
- SHOULD 基于概念，而非基于任务
- SHOULD NOT 包含流程、笔记或时间语义
- SHOULD 优先保持单文件聚合（避免过度拆分）

```text
<domain>.md
<domain>-<concept>.md
```

### `domain`

一个稳定的知识领域（knowledge domain）
表达**一类可长期复用的认知模型或知识集合**
典型包括：

1. 系统级认知：表达 **系统如何运作的认知模型**， 例如：
    - architecture, execution-model, consistency, lifecycle
2. 外部知识域：表达 **外部系统/库的稳定知识集合**，例如：
    - odas, ffmpeg, webrtc
3. 工程方法论：表达 **跨 feature 的通用规律**，例如：
    - testing, performance, reliability

### `concept`

一个可独立引用的稳定子概念（sub-concept）
表达domain 内**一个相对独立的知识切面**
典型包括：

1. 结构性切面（Structure）：描述系统或领域的组成方式，例如：
    - overview, protocol, layering
2. 行为/机制（Mechanism）：描述运行方式或机制，例如：
    - model, state-machine
3. 约束/特性（Constraint / Property）：描述不可忽略的关键约束或特性，例如：
    - bottleneck, pattern
4. 集成语义（Integration Semantics）：描述系统之间的交互方式，例如：
    - integration, pipeline

> 如果无法明确 concept 的边界，则应当合并回 `<domain>.md`

### References Layer

- SHOULD 加工成可直接引用的 markdown 文件
- SHOULD NOT 直接构成知识内容
- MAY 参考源码的分析记录
- MAY 调查研究的结论报告
- MAY 知识来源的原始材料（如文献、数据集、图表等）

存储在 `references/` 目录下，并通过相对路径引用

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
