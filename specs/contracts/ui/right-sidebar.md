---
title: right-sidebar
status: active
stability: flexible
version: 0.2
---

## Role

定义右侧栏作为声源列表、筛选器和录音会话的联合信息面板。
该 Contract 约束右栏如何稳定呈现对象状态和筛选入口，而不定义底层筛选或录音逻辑。

## Invariants

- 右侧栏 MUST 保持“声源”“筛选器”“录音会话”三段纵向结构，MUST NOT 混入场景切换入口。
  - 标题 MUST 保持一致字号与风格语义
  - 按内容自然排版（wrap content）
- 声源行 MUST 直接消费 bridge 提供的 row 数据；用户取消勾选后，对应 row MUST 继续保留，仅改变勾选状态。
- 当没有活动声源或没有活跃录音会话时，右栏 MUST 显示稳定空态文案，MUST NOT 伪造占位列表项。
- 声源 badge 的颜色和标签 MUST 忠实反映 bridge 输出，MUST NOT 在右栏本地推导另一套身份语义。
- 筛选器开关和能量范围控件 MUST 继续通过现有 bridge 接口路由，右栏 MUST NOT 在本地重建筛选状态真源。
- 右栏 MUST 作为对象状态面板，而不是图表或球体时序数据的生产者。

## Variation Space

- 行高、分隔线、字号和分区间距 MAY 演进，只要三段层级仍然稳定且易于扫描。
- 空态文案 MAY 调整，但空态必须继续表达“当前无可展示对象”，而不是技术错误。
- 录音会话展示方式 MAY 演进为更丰富的摘要，但其只读信息面板语义 MUST 保持。
- preview 自检区正文字体 MAY 调整，但 MUST 保持“小字号可读、不过度抢占右栏标题层级”。

## Rationale

- 右栏承载的是对象级可见性和筛选入口；取消最后一个勾选后仍保留 row，可以避免对象从用户心智地图中瞬间消失。
- 让 badge 颜色与其他视图保持一致，可以维持跨区域的身份追踪。

## Anti-Patterns

- 在右栏本地拼接 preview/runtime 占位行或另一套 badge 颜色规则。
- 用户取消勾选后直接删除 row，导致对象与可见性状态混淆。
- 把场景切换器、图表时序控制或录音逻辑实现塞进右栏。
