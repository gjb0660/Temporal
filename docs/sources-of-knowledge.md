# Sources of Knowledge: the Evidence or Reference Layer

## Overview

Knowledge 来源于更底层的材料集合，这一层称为：

> Evidence Layer（证据层）或 Reference Layer（参考层）

该层包含原始信息与分析材料，
而 Knowledge 是对这些内容的提炼与结构化表达。

---

## Nature of the Evidence Layer

Evidence Layer 的本质是：

> 未经过完全抽象与收敛的“原始认知材料”

其特征包括：

- 可能不完整或不一致
- 可能包含噪声与冗余
- 结构松散不稳定
- 不适合直接用于决策

---

## Role in the System

---

### Raw Source

提供原始信息来源，例如：

- 分析记录
- 实验数据
- 外部资料

---

### Traceability

支持 Knowledge 的可追溯性：

- 结论可回溯来源
- 支持验证与修正

---

### Exploration Support

在探索阶段提供材料：

- 未收敛问题
- 不确定的行为
- 多种解释路径

---

## Relationship with Knowledge

关系结构：

```text
Evidence → Knowledge → (Feature / Contract)
````

---

### Transformation

从 Evidence 到 Knowledge 通常经历：

- 筛选（去除噪声）
- 抽象（提取规律）
- 收敛（形成稳定表达）

---

### Key Distinction

| 属性 | Evidence | Knowledge |
| ---- | -------- | --------- |
| 完整性 | 不保证 | 已收敛 |
| 结构 | 松散 | 结构化 |
| 稳定性 | 低 | 高 |
| 可引用性 | 低 | 高 |

---

## File Organization

Evidence Layer 通常以独立子目录存在，例如：

```text
knowledge/
├── references/
│   ├── <domain>-analysis.md
│   ├── <domain>-research.md
```

---

### Naming Characteristics

Evidence 文件通常具有以下命名特征：

```text
<domain>-analysis.md
<domain>-research.md
<domain>-notes.md
```

这些命名反映的是：

> “正在理解某个东西”，而不是“已经形成稳定认知”

---

## Boundaries

---

### Evidence vs Knowledge

Evidence 不应：

- 被 Feature 直接引用作为决策依据
- 被当作最终结论使用
- 替代 Knowledge 的表达

Knowledge 不应：

- 直接包含原始数据或大段记录
- 变成分析过程的容器

---

## Evolution

---

### Accumulation（积累）

不断增加新的材料：

- 新分析
- 新数据
- 新观察

---

### Pruning（裁剪）

移除无价值或过时内容：

- 重复材料
- 已被 Knowledge 吸收的内容
- 明显错误的记录

---

### Promotion（提升）

当认知收敛时：

```text
evidence → knowledge
```

---

## Anti-Patterns

---

### Treating Evidence as Knowledge

直接使用 analysis / notes 作为决策依据：

- 容易引入未验证结论
- 增加不确定性

---

### Over-Preserving Raw Data

无限保留所有材料：

- 增加噪声
- 降低可维护性

---

### Mixing Layers

将 Evidence 与 Knowledge 混合在同一文件：

- 模糊“结论”与“过程”
- 破坏可读性

---

## A Mental Model

可以将这一层理解为：

> 系统的“感知与记忆层”

- Evidence 是感知与记录
- Knowledge 是理解
- Contract 是约束
- Feature 是行为

---

## Summary

Evidence Layer 提供 Knowledge 的来源，但不是 Knowledge 本身。

一个良好的体系应：

- 保留必要的原始材料以支持追溯
- 将稳定认知提炼为 Knowledge
- 避免让未收敛内容进入决策路径

> 目标用最少的 Evidence，支撑最可靠的 Knowledge。
