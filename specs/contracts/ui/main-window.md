---
title: main-window
status: active
stability: flexible
version: 0.2
---

## Role

定义应用主窗口作为用户界面的顶层空间外壳。
该 Contract 约束页面级结构、主题透传和三栏主区域的稳定心智地图。

## Invariants

- 主窗口 MUST 作为唯一页面级外壳同时承载 header、footer、左栏、中栏和右栏。
- 主窗口 MUST 保持左栏、中栏、右栏三块主区域同时可见；中栏 MUST 作为剩余宽度的主要承载区。
- 主窗口 MUST 统一定义并下发共享 theme token；子组件 MUST 通过该主题对象保持视觉一致性。
- 主窗口 MUST 只负责组装和绑定 `appBridge`；MUST NOT 在本地重新塑形场景数据、拼接 row 集合或向子组件注入额外的 preview 专用分支状态。
- 默认窗口与最小窗口尺寸 MUST 继续保证三栏信息可读；MUST NOT 通过缩放把任一主区域退化为隐藏入口。

## Variation Space

- 具体尺寸、间距、字体和颜色方案 MAY 演进，只要三栏主结构和可读性保持稳定。
- header、footer 和各区域内部实现 MAY 重写，但页面级空间锚点和职责分工 MUST 保持清晰。
- 主题 token 的内部组织 MAY 调整，但跨组件共享主题这一入口 MUST 保持单一。

## Rationale

- 主窗口定义的是用户对整页结构的方向感；如果顶层壳体频繁改变，局部组件再稳定也无法形成可依赖的界面地图。
- 统一主题和统一 bridge 入口可以避免页面级重复塑形和视觉语义漂移。

## Anti-Patterns

- 在主窗口中重新拼接 `sourceRows()`、preview fixtures 或其他局部派生数据。
- 通过缩放或模式分支把三栏中的任一区域隐藏成二级入口。
- 让子组件各自维护独立主题常量而不是消费共享 theme。
