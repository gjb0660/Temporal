---
title: preview-source
status: active
stability: semi
version: 0.1
---

## Role

定义预览相关 UI contract 的单一状态真源约束。
该 Contract 约束同一语义状态在 bridge 与模型层中只能有一个权威来源。

## Invariants

- `AppBridge` 与 `PreviewBridge` 各自 MUST 保持单一内部状态真源。
- 同一 UI contract 的内部状态 MUST NOT 同时维护 raw list state 与 `QmlListModel` 两套真源。
- 面向展示的派生状态 MUST 从权威状态推导。
- 面向展示的派生状态 MUST NOT 与权威状态独立漂移。
- 对同一语义状态的写入路径 MUST 保持单一。
- 对同一语义状态 MUST NOT 允许多个彼此独立的更新入口并行存在。

## Variation Space

- 权威状态 MAY 采用不同内部表示，只要同一语义只有一个最终真源。
- 展示层 MAY 派生缓存、过滤结果或排序视图，但它们 MUST 继续从权威状态重建。
- bridge 与模型之间的同步机制 MAY 演进，但 MUST 不引入双写或竞争性更新路径。

## Rationale

- 双真源状态会导致 UI 漂移、事件顺序不一致与同步成本失控。
- 将派生视图和权威状态分离，可以在不丢失一致性的前提下支持过滤、排序和局部刷新。

## Anti-Patterns

- 同时维护 raw list 与 `QmlListModel`，并分别接受写入。
- 为局部交互快捷性引入第二套不可回放的临时状态。
- 依赖刷新顺序碰巧一致来掩盖状态漂移。
