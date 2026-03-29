# Knowledge Design and Evolution

## Overview

Knowledge 描述系统中的**事实、原理与认知模型**。

如果 Feature 回答的是「系统做什么」，
Contract 回答的是「系统不能破坏什么」，

那么 Knowledge 回答的是：

> 「系统为什么这样设计，以及世界本身如何运作」

Knowledge 不直接驱动执行，也不约束行为，
但它为 Feature 的决策与 Contract 的抽象提供基础。

---

## Nature of Knowledge

Knowledge 不是执行单元，也不是约束集合。

它的本质是：

> 对系统、问题域或外部世界的**稳定认知表达**

一个有效的 Knowledge 通常具备以下特征：

- 描述事实或规律，而不是任务或步骤
- 独立于具体 Feature 与执行阶段
- 不包含执行状态（如 Plan / Progress）
- 可以被引用，而不需要被“执行”
- 在较长时间内保持语义稳定

当内容表达：

- 行为或执行 → 更接近 Feature
- 约束或限制 → 更接近 Contract

---

## Role in the System

Knowledge 在系统中承担三个核心作用：

### Reality Anchoring

提供系统必须面对的现实基础，例如：

- 外部系统的行为模型（如 odas、ffmpeg）
- 技术约束（延迟、资源、并发模型）
- 已验证的事实与结论

这些内容构成 Feature 决策的输入边界。

---

### Decision Support

为 Feature 中的决策提供依据：

- 为什么选择某种架构
- 为什么放弃某种方案
- 提供权衡的背景与原理

Knowledge 不做决策，但支撑决策成立。

---

### Concept Abstraction

沉淀跨 Feature 的通用认知，例如：

- testing（可验证性与收敛）
- consistency（状态一致性模型）
- lifecycle（生命周期理解）

---

## Knowledge vs Feature vs Contract

三者构成系统的三个正交维度：

| 类型 | 关注点 | 是否执行 | 是否约束 |
| ---- | ------ | -------- | -------- |
| Feature | 做什么 | 是 | 否 |
| Contract | 不能破坏什么 | 否 | 是 |
| Knowledge | 为什么这样 | 否 | 否 |

关系可以理解为：

- Knowledge 提供认知基础
- Contract 从 Knowledge 中抽取约束
- Feature 在 Knowledge 与 Contract 的边界内执行

---

## Naming and Structure

Knowledge 的命名应表达一个**稳定知识域或概念**：

```text
<domain>.md
<domain>-<concept>.md
````

命名应避免：

- 时间语义（v2 / 2026）
- 过程语义（notes / draft / todo）
- 任务语义（fix / implement）

---

### Domain

`domain` 表示一个稳定的知识领域，例如：

- 系统认知：architecture, lifecycle, execution
- 外部系统：database, protocol
- 工程方法：testing, performance, reliability

---

### Concept

`concept` 表示该领域中的一个特定知识点，例如：

```text
testing-tdd
consistency-ssot
lifecycle-model
```

---

## Structural Patterns

Knowledge 通常呈现三种结构形态：

### Overview Knowledge

对一个领域的整体认知，例如：

- architecture
- odas（整体理解）

---

### Concept Knowledge

对某一原理或机制的抽象，例如：

- testing（TDD）
- consistency（SSOT）

---

### External Knowledge

对外部系统或库的整理，例如：

- odas-analysis
- ffmpeg-behavior

---

## Evolution of Knowledge

Knowledge 的演进是认知收敛，而不是任务推进。

---

### Refinement（细化）

从模糊到清晰：

```text
testing → testing-tdd → testing-strategy
```

---

### Extraction（抽取）

从实践中提取稳定认知：

- 从实现中抽象规律
- 从问题中总结模式

---

### Consolidation（收敛）

整合分散认知为统一结构

---

### Deprecation（淘汰）

淘汰不再成立的认知模型

---

## Stability and Scope

Knowledge 通常稳定，但可随认知更新：

- 新事实出现
- 原有假设被推翻
- 更优解释模型出现

与 Contract 不同：

> Knowledge 的变化是“认知更新”，而不是“约束调整”。

---

## Anti-Patterns

---

### Process Leakage

将流程或步骤写入 Knowledge：

- how-to guide
- step-by-step instructions

这些更适合作为 Feature 或外部文档。

---

### Execution State

包含 Plan、Todo、Progress 等内容：

- 破坏 Knowledge 的只读属性
- 引入时间维度

---

### Tool Binding

将 Knowledge 绑定到具体工具：

- unittest-specific
- framework-specific

应优先表达原理，而不是工具。

---

### Unstructured Notes

将 Knowledge 当作笔记容器：

- 无结构
- 无结论
- 无法引用

---

## Relationship with Agent

对于 Agent：

- Knowledge 是推理输入
- Contract 是约束边界
- Feature 是执行目标

Agent 应从 Knowledge 中提取事实，而不是执行它。

---

## Minimal Set Principle

Knowledge 应保持最小集合：

- 覆盖关键认知
- 支持主要决策
- 避免重复与冗余

过多 Knowledge 会导致：冗余、冲突、难以维护

---

## A Mental Model

可以将 Knowledge 看作：

> 系统的“认知层”

- Feature 是行为
- Contract 是约束
- Knowledge 是理解

三者共同构成系统的完整表达。

---

## Summary

Knowledge 提供系统理解的基础。

良好的 Knowledge 体系应：

- 表达事实与原理
- 独立于执行
- 支撑决策与约束
- 保持长期稳定与可引用性

> 目标是用最少的 Knowledge，支撑最清晰的系统理解。
