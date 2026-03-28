---
title: app-bridge
status: active
stability: flexible
version: 0.2
---

## Role

定义 QML 展示层与 Python 后端之间的职责边界。
该 Contract 约束 UI 动作如何经由 bridge 路由到后端，不定义预览状态真源或视觉映射策略。

## Invariants

- QML MUST 作为展示层存在，MUST NOT 实现协议逻辑。
- QML MUST NOT 承担业务状态编排职责。
- UI 触发的服务动作 MUST 经由 `appBridge` 暴露的 slots/signals 路由。
- QML 与后端之间的交互边界 MUST 通过显式 bridge 接口表达，MUST NOT 通过隐藏控制路径、隐式全局状态或直接后端访问绕过。

## Variation Space

- QML 组件结构、视觉样式与布局细节 MAY 演进。
- bridge 的内部实现 MAY 调整，但 UI → bridge → backend 的职责路径 MUST 保持清晰。
- bridge 对外暴露的具体方法集合 MAY 演进，但展示层与业务层的职责分离 MUST 保持。

## Rationale

- 展示层一旦承载协议或业务编排，调试边界会立刻塌陷。
- 显式 bridge 边界可以把 UI 动作、状态变化与服务调用放在可审计的路径上。

## Anti-Patterns

- 在 QML 中直接发网络请求或解析协议数据。
- 绕过 bridge 直接调用后端对象或依赖隐式共享状态。
