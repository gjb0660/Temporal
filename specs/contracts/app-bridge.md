---
title: app-bridge
scope: api
stability: flexible
version: 0.1
---

## Role

定义 QML 展示层与 Python 后端之间的职责边界。
该 Contract 约束 UI 交互路径、状态真源与可视映射稳定性。

## Invariants

- QML MUST 作为展示层存在，MUST NOT 实现协议逻辑。
- QML MUST NOT 承担业务状态编排职责。
- UI 触发的服务动作 MUST 经由 `appBridge` 暴露的 slots/signals 路由。
- `AppBridge` 与 `PreviewBridge` 各自 MUST 保持单一内部状态真源。
- 同一 UI contract 的内部状态 MUST NOT 同时维护 raw list state 与 `QmlListModel` 两套真源。
- source id 到 color 的视觉映射 MUST 保持稳定。
- filters MUST 可逆，且 MUST NOT 产生隐藏副作用。
- 布局调整 MUST 保持既有信息层级，不得引入隐蔽控制路径或跨区域重复操作入口。

## Variation Space

- QML 组件结构、视觉样式与布局细节 MAY 演进。
- bridge 的内部实现 MAY 调整，但 UI → bridge → backend 的职责路径 MUST 保持清晰。
- 色彩方案 MAY 整体调整，但 source id 到 color 的稳定映射原则 MUST 保持。

## Rationale

- 展示层一旦承载协议或业务编排，调试边界会立刻塌陷。
- 双真源状态会导致 UI 漂移、事件顺序不一致与同步成本失控。
- 稳定的 source 视觉映射是操作员建立空间记忆和识别习惯的基础。

## Anti-Patterns

- 在 QML 中直接发网络请求或解析协议数据。
- 通过多个模型副本拼接同一 UI 语义。
- 为局部快捷实现引入隐藏按钮、隐藏状态或不可逆 filter。
