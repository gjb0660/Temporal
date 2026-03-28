---
title: recording-lifecycle
status: active
stability: strict
version: 0.1
---

## Role

定义源驱动录音的启停生命周期语义。
该 Contract 约束录音何时开始、何时停止，以及停止条件如何保持唯一性。

## Invariants

- 录音启动语义 MUST 由 source 出现或进入活跃状态触发。
- 录音停止语义 MUST 由 source 消失或 inactive timeout 触发。
- 同一录音语义 MUST NOT 同时维护多套互相独立的停止规则。
- 生命周期判断 MUST 围绕 source 活跃性表达，MUST NOT 被无关的手写状态机替代。

## Variation Space

- inactive timeout 的具体阈值 MAY 调整，但 MUST 继续表达“source 不再活跃”的停止语义。
- 生命周期实现 MAY 使用不同状态表示或调度机制，但 MUST 保持单一启动语义与单一停止语义。
- 系统 MAY 记录额外生命周期事件用于观测，但 MUST NOT 改变核心启停触发条件。

## Rationale

- source 驱动生命周期是该功能的核心业务语义，不能被手写状态机随意替换。
- 多套停止规则并存会导致悬挂录音、提前截断或行为不可预测。

## Anti-Patterns

- 使用多个不一致的停止条件。
- 将 source 消失后的停止逻辑写成永不终止的悬挂录音。
- 让录音启停依赖与 source 活跃性无关的临时 UI 或流程状态。
