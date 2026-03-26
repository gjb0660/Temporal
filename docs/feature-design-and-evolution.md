# Feature Design and Evolution

## Overview

Feature 是系统中的**执行单元**，同时也是**能力表达单元**。

它用于描述：

* 系统当前具备什么能力
* 当前能力如何被实现与验证

Feature 不是任务列表，也不是历史记录，而是一个始终保持“当前态”的模型，用来驱动执行并反映系统真实状态。

---

## Feature as a Living Model

Feature 不记录历史，而是持续收敛到当前最成立的状态。

当信息发生变化时：

* Facts 会更新
* Decision 会调整
* Plan 会变化

这些变化不会以过程形式累积，而是直接替换为新的当前状态。

历史由版本控制系统承载，Feature 只表达“现在成立的结构”。

---

## Capability and Work

Feature 可以从两个角度理解：

### Capability（能力）

当 Feature 表达系统长期存在的一类能力时，它是系统结构的一部分。

例如：

```text
recording
media-pipeline
ui-system
```

这些 Feature 描述的是系统“能做什么”。

---

### Work（工作单元）

当 Feature 表达的是围绕能力展开的一次具体工作时，它更接近执行过程。

例如：

```text
recording-stop-failure
recording-refactor-pipeline
runtime-reliability
session-handoff-analysis
```

这些 Feature 描述的是系统“正在做什么”。

---

## Structural Roles of Features

从系统结构上看，Feature 会自然形成两种角色：

### Primary Feature

Primary Feature 构成系统的能力骨架。

它们通常具有：

* 稳定的能力边界
* 长期存在的语义
* 可以独立理解，不依赖上下文

删除一个 Primary Feature，通常意味着系统失去一种核心能力。

---

### Supporting Feature

Supporting Feature 围绕能力展开，是能力演进过程中的执行单元。

它们通常表现为：

* 行为修正
* 结构调整
* 问题澄清
* 质量收口
* 迁移与对齐

它们不会引入新的一级能力，而是让已有能力变得更正确、更稳定或更清晰。

---

## Naming and Boundary Clarity

Feature 的命名是能力边界的第一表达。

一个好的名称应让人和 Agent 在没有上下文的情况下理解其语义。

---

### Naming as Capability Expression

Feature 名称应优先表达能力或领域，而不是过程或阶段。

例如：

```text
recording
media-pipeline
routing-session
ui-system
governance
```

这些名称具有稳定性，不依赖时间或阶段。

相对地：

```text
phase-a
v2
2026-q1
final-ui
```

这些名称依赖时间或上下文，不适合作为 Feature 标识。

---

### Capability vs Work in Naming

Feature 名称通常呈现两种形态：

#### 能力型命名

```text
recording
preview-mode
remote-control
```

表达系统长期能力。

---

#### 工作型命名

```text
recording-stop-failure
recording-refactor-pipeline
runtime-reliability
validation-delivery
```

通常包含：

* 行为偏差（failure）
* 结构调整（refactor）
* 质量收口（reliability）
* 过程或阶段（validation, foundation）

它们描述的是一次工作，而不是能力本身。

---

### Naming Patterns as Signals

命名可以提供稳定的语义信号：

#### 行为修正

```text
<capability>-<failure>
```

例如：

```text
recording-stop-failure
preview-mode-freeze
```

---

#### 结构调整

```text
<capability>-refactor-<target>
```

例如：

```text
recording-refactor-pipeline
ui-system-layout-refactor
```

---

#### 问题探索

```text
<domain>-analysis
<domain>-research
```

例如：

```text
odas-integration-research
session-handoff-analysis
```

---

命名应尽量避免模糊表达：

```text
fix-1
patch
misc-update
```

这些名称无法提供有效语义信息。

---

### Boundary over Process

命名应优先体现能力边界，而不是实现过程或技术原因。

当同一根因影响多个能力时，应分别在各自能力下表达，而不是合并为一个跨能力的 Feature。

---

### No Time Semantics in Naming

Feature 名称不应包含：

* 阶段（phase）
* 顺序（step）
* 版本（v1 / v2）
* 时间（日期 / 周期）

这些信息属于执行过程，应体现在：

* Plan
* Progress

而不是进入命名。

---

### Structural Simplicity

Feature 结构应围绕能力展开，而不是层级或阶段。

对于较大的能力，可以使用目录承载子特性：

```text
preview-mode.md
preview-mode/
```

此时：

* 父 Feature 表达稳定能力
* 子 Feature 表达局部问题或子能力

而不是通过文件名编码层级关系。

---

## Evolution of Features

Feature 的演进不是扩展内容，而是收敛当前状态。

---

### In-place Evolution (原地演进)

当目标未变化时，Feature 在原地持续更新：

* 新信息进入 Facts
* Decision 根据事实调整
* Plan 随之变化

文档始终保持当前最优解。

---

### Splitting into New Features (拆分新 Feature)

当出现以下情况时，通常意味着需要新的 Feature：

* 出现新的独立目标
* 可以形成独立验证闭环
* 当前问题不再属于原能力边界

这时，与其扩展原 Feature，不如拆分为新的执行单元。

---

### Completion and Stability (自然结束)

当 Feature 满足其验证条件后，它会自然进入完成状态。

完成后的 Feature：

* 不再扩展 scope
* 保持为稳定结果
* 可被其他 Feature 参考

---

## Common Misunderstandings

### 把阶段当成 Feature

```text
initial
phase-a
v2
```

这些表达时间或进度，而不是能力。

---

### 把质量当成能力

```text
runtime-reliability
performance
stability
```

这些描述的是“做得好不好”，而不是“能做什么”。

---

### 混合多个语义

```text
test-and-hardening
validation-and-delivery
```

这类命名混合不同语义，容易造成边界模糊。

---

## A Simple Heuristic

可以用一个简单的问题判断 Feature 的性质：

> 如果这个名称在系统长期演进后仍然成立，它更可能是在表达能力；
> 如果它只在当前阶段成立，它更可能是在表达一项工作。

---

## Summary

Feature 是一个持续收敛的当前态模型：

* 它描述能力，也驱动执行
* 它不记录历史，只表达现在
* 有的 Feature 构成系统骨架
* 有的 Feature 表达演进过程
* 命名帮助理解边界，而不是记录过程

> 一个好的 Feature，看起来不像“任务”，而像“系统的一部分”。
