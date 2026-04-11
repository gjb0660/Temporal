---
title: app-side-checkbox
status: active
stability: flexible
version: 0.3
---

## Role

定义侧栏复选框作为密集列表中的轻量选择元件。
该 Contract 约束勾选、禁用和标签呈现的稳定语义，而不定义业务对象本身。

## Invariants

- 侧栏复选框 MUST 保持紧凑、可扫描的勾选框加标签结构，适合在窄侧栏中密集排列。
- `checked` 和 `enabled` 语义 MUST 由外部状态驱动；组件 MUST NOT 在内部持有业务对象数据真源。
- 禁用态 MUST 继续保留可读的占位语义，MUST NOT 让用户误判为行已消失。
- 交互语义 MUST 保持为单一可预测的 toggle，MUST NOT 扩展为树形选择器或多级控制器。
- 在高频外部刷新场景下，单次点击 toggle MUST 保持可达；组件集成方 MUST NOT 通过无意义重建破坏点击原子性。

## Variation Space

- 指示器尺寸、文字样式和间距 MAY 演进，只要紧凑列表语义保持稳定。
- 勾选标记的具体造型 MAY 调整，但启用、禁用、已选、未选四种状态 MUST 继续可辨认。
- 组件可以被不同侧栏列表复用，只要其仍然只承担轻量选择语义。

## Rationale

- 侧栏列表依赖高密度可扫描性；一旦复选框语义膨胀，就会破坏整栏节奏。
- 将状态真源留在外部可以避免原子组件变成隐蔽的业务状态容器。

## Anti-Patterns

- 在组件内部缓存 source、filter 或其他业务对象状态。
- 把该控件扩展成包含多级展开或复杂附属动作的复合控件。
- 禁用后直接移除标签或让整行不可辨认。
