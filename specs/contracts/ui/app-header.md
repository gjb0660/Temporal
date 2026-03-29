---
title: app-header
status: active
stability: flexible
version: 0.2
---

## Role

定义应用头部作为全局品牌与上下文切换锚点。
该 Contract 约束顶部菜单条、品牌条以及右侧全局上下文区域的稳定语义。

## Invariants

- 头部 MUST 保持白色菜单条和绿色品牌条两层结构，MUST 作为整页最上方的
  稳定导航锚点。
- 品牌条左侧 MUST 保留产品身份区域；右侧 MUST 保留全局上下文区域。
- 右侧全局上下文区域 MUST 在“预览场景切换器”和“静态导航标签”之间
  二选一，MUST NOT 同时呈现两者。
- 预览场景选项 MUST 来自 `appBridge` 提供的数据；场景切换动作 MUST 通过
  bridge 路由，MUST NOT 在 QML 中硬编码场景 key 或本地推导模式。
- 头部 MUST NOT 承载声源筛选、录音控制或内容区专属操作。

## Variation Space

- 菜单文案、品牌图形和右侧标签内容 MAY 演进，只要头部仍然承担全局而非
  局部语义。
- 场景切换控件的具体样式 MAY 变化，但其位置和与静态导航互斥的语义 MUST
  保持。
- 头部视觉层次 MAY 重绘，但顶部双层结构和品牌识别入口 MUST 保持可辨认。

## Rationale

- 用户会把头部当作全局上下文入口，而不是内容区的一部分；把局部控制塞进
  头部会破坏层级边界。
- 预览场景切换与静态导航语义冲突，互斥呈现可以保持顶部区域的单一解释。

## Anti-Patterns

- 在头部同时显示预览场景切换器和静态导航标签。
- 在 QML 中硬编码场景列表或依赖本地 `previewMode` 分支决定右侧内容。
- 把内容区操作或 source 级控制塞到头部右侧。
