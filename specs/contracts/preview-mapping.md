---
title: preview-mapping
status: active
stability: semi
version: 0.1
---

## Role

定义预览界面的稳定视觉映射与可感知交互边界。
该 Contract 约束 source 视觉身份、filter 行为与布局调整的可理解性。

## Invariants

- source id 到 color 的视觉映射 MUST 保持稳定。
- filters MUST 可逆，且 MUST NOT 产生隐藏副作用。
- 布局调整 MUST 保持既有信息层级，不得引入隐蔽控制路径或跨区域重复操作入口。
- 视觉变化 MUST 保持 source 身份可追踪，MUST NOT 让同一 source 在无显式语义切换时表现为不同对象。

## Variation Space

- 色彩方案 MAY 整体调整，但 source id 到 color 的稳定映射原则 MUST 保持。
- filter 的表现形式 MAY 演进，但用户 MUST 能理解当前筛选状态并撤销它。
- 布局结构、面板尺寸与视觉样式 MAY 调整，只要信息层级与控制路径仍然显式。

## Rationale

- 稳定的 source 视觉映射是操作员建立空间记忆和识别习惯的基础。
- 不可逆 filter 和隐藏控制入口会破坏操作者对当前系统状态的判断。

## Anti-Patterns

- 让相同 source 在同一会话中随机切换颜色或身份样式。
- 使用会改变数据语义却没有显式反馈的 filter。
- 为局部快捷实现引入隐藏按钮、隐藏状态或跨区域重复控制入口。
