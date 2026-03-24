# ESPC Philosophy

> 本文用于解释 ESPC 的工作方式与设计动机
> 权威行为规则以 `specs/AGENTS.md` 为准

## Overview

Minimal ESPC 可以理解为一个**持续收敛的不确定性处理系统**：

1. **entropy-reduction loop**
2. **decision convergence system**

> 不确定性 → 事实 → 决策 → 执行 → 现实 → 再更新认知

它不是流程，而是一个循环。

## Key Idea

可以把 ESPC 看成一个“降熵过程”：

* 初始状态：信息不完整（高不确定性）
* 中间过程：通过事实与决策逐步收敛
* 结果：形成可验证的现实结果

这个过程会不断重复，而不是一次性完成。

## Concept Mapping

| 概念 | 作用 | 直观理解 |
| -- | -- | -- |
| Explorer | 获取事实 | 搞清楚世界是什么样 |
| Spec | 做出决策 | 在约束下选择路径 |
| Plan | 组织执行 | 把决策转成步骤 |
| Code | 产生结果 | 在现实中验证 |

## The Loop

ESPC 的实际运行形态更接近：

```text
Goal → Facts → Decision → Acceptance → Plan → Progress
→ Feedback → Facts（更新） → Todo
```

这个循环的特点是：

* 不断修正认知
* 逐步逼近目标
* 每一步都可以被验证

## Key Distinctions

这些概念的区分，是理解 ESPC 的关键。

### Goal vs Acceptance

* Goal：描述方向（想达成什么）
* Acceptance：描述完成条件（什么时候结束）

### Facts vs Decision

* Facts：必须接受的现实条件
* Decision：在这些条件下做出的选择

### Plan vs Todo

* Plan：当前执行路径
* Todo：未来或非关键事项

### Non-Goal vs Todo

* Non-Goal：明确排除的范围
* Todo：暂时不做，但未来可能做

## Why This Model Works

工程问题通常都可以拆成：

> 信息不完整 → 做出判断 → 验证结果 → 修正判断

ESPC 的作用，是把这个过程结构化：

* 让不确定性逐步减少
* 让决策更有依据
* 让结果可以被验证

## Practical Implications

### 对执行过程的影响

* 决策通常依赖已有事实，而不是直觉
* 执行路径会随着新信息不断调整
* “完成”由明确条件定义，而不是主观判断

### 对系统设计的影响

* 明确边界比增加功能更重要
* 清晰的完成条件有助于减少歧义
* 多个“真源”容易导致系统失控

## Common Misunderstandings

ESPC 常见的误解包括：

* 把它当成线性流程（实际上是循环）
* 把它当成文档结构（实际上是认知模型）
* 把它当成检查清单（实际上是收敛机制）

## Takeaways

可以用几条结论来快速理解 ESPC：

* 它是一个持续更新的决策系统
* 事实与决策的区分非常关键
* 执行与验证是同一循环的一部分
* “完成”需要明确的判断标准
* 单一真源有助于避免系统漂移
