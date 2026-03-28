# Contract Design and Evolution

## Overview

Contract 用于描述系统中那些**不应被随意破坏的设计前提**。

如果 Feature 回答的是「系统做什么」，
那么 Contract 回答的是「系统不能破坏什么」。

Contract 不驱动执行，但定义了所有执行必须遵守的边界。

---

## Contract as Constraint Layer

Contract 不是模块划分，也不是功能描述。

它关注的不是“系统是什么”，而是：

> 当系统发生变化时，哪些性质必须保持成立。

这些性质通常具有以下特征：

- 跨多个 Feature 存在
- 不依赖具体实现方式
- 一旦破坏，系统行为将变得不可预测或不一致

因此，Contract 更接近“结构约束”，而不是“能力描述”。

---

## Role in the System

Contract 在系统中承担三个核心作用：

### Boundary Definition

定义系统各部分之间的边界，例如：

- UI 与 Backend 的职责分离
- 外部系统与内部系统的集成方式
- 数据流与控制流的分离

---

### Invariant Enforcement

定义系统必须维持的不变量，例如：

- 状态应保持单一真源
- 标识与视觉映射必须稳定
- 生命周期应具有清晰且唯一的触发路径

这些不变量通常是系统正确性的基础。

---

### Constraint Reuse

提供跨 Feature 的共享约束，例如：

- lifecycle
- ordering
- idempotency
- ssot

这些约束往往不是某一个 Feature 独有，而是在多个能力之间复用。

---

## Contract vs Feature

Contract 与 Feature 是两个正交维度：

| 维度 | Feature | Contract |
| ---- | ------ | -------- |
| 本质 | 能力 | 约束 |
| 关注点 | 做什么 | 不能破坏什么 |
| 生命周期 | 持续演进 | 相对稳定 |
| 是否执行 | 是 | 否 |

Feature 可以依赖 Contract，但 Contract 不应依赖具体 Feature。

---

## Naming as Semantic Anchor

Contract 的命名不是分类，而是语义锚点。
推荐结构：

```text
<domain>-<constraint>
```

一个名称应当能够被自然展开为一条约束，例如：

- 某种状态必须唯一
- 某种映射必须稳定
- 某种边界必须存在

当名称只描述对象或领域时，往往缺少约束语义，
容易演变为“内容容器”。

---

## Atomicity of Contracts

Contract 更接近“最小约束单元”，而不是文档集合。

当一个 Contract 同时包含多个关注点时：

- 语义会变得模糊
- 可验证性下降
- 演进时容易产生冲突

因此，Contract 往往会随着理解加深而被拆分为更小的单元。

这种拆分不是增加复杂度，而是减少歧义。

---

## Evolution of Contracts

Contract 的演进通常不是频繁修改，而是结构性变化。

从长期来看，约束的变化大致呈现三种趋势：

---

### Tightening（收紧）

约束变得更严格，系统自由度降低，但一致性增强。

例如，从多种可能收敛为单一表达。

---

### Relaxation（放宽）

约束被适度放宽，以支持更多场景或兼容性。

例如，允许更多输入形式。

---

### Rewriting（重写）

约束的前提发生改变，原有语义不再适用。

例如，系统模型发生根本性调整。

---

这些变化反映的不是“规则改变”，而是：

> 对系统本质理解的变化。

---

## Stability as Signal

`stability` 可以被理解为一种演进信号。

它并不控制是否允许修改，而是表达：

- 这个约束更可能保持稳定
- 还是仍处于探索中

因此：

- 高稳定性通常对应基础假设
- 低稳定性通常对应尚未收敛的设计

这有助于人类和 Agent 在面对多个约束时，
判断哪些更可靠，哪些更需要谨慎对待。

---

## Anti-Patterns

一些常见的误用方式包括：

---

### Treating Contract as Domain Container

将 Contract 用作领域描述，而不是约束表达。

结果是：

- 边界模糊
- 内容膨胀
- 难以验证

---

### Mixing Multiple Concerns

在同一 Contract 中混合多个维度，例如：

- 状态 + 行为 + UI
- 协议 + 生命周期 + 命名

这会破坏其作为“最小约束单元”的性质。

---

### Embedding Implementation Details

将具体实现方式写入 Contract，例如：

- 技术选型
- 框架绑定
- 具体调用路径

这会导致 Contract 随实现变化而失效。

---

### Non-Verifiable Constraints

描述无法判断是否被违反的规则。

这类内容更适合作为 Knowledge，而不是 Contract。

---

## Minimal Set Principle

Contract 的目标不是覆盖所有细节，而是覆盖：

- 最容易被破坏的关键点
- 最难修复的系统错误来源
- 跨多个 Feature 的共性约束

一个良好的系统通常拥有：

> 尽可能少，但足够强的 Contract 集合

---

## Summary

Contract 是系统中的约束层：

- 它定义系统的边界，而不是能力
- 它独立于实现，但约束所有实现
- 它来源于 Knowledge，但高于 Knowledge
- 它限制 Feature 的演进空间

> 目标是用最少的 Contract，限制最大的错误空间。
