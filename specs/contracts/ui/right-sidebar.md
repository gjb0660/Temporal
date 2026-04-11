---
title: right-sidebar
status: active
stability: flexible
version: 0.7
---

## Role

定义右侧栏作为声源列表、筛选器和录音会话的联合信息面板。
该 Contract 约束右栏如何稳定呈现对象状态和筛选入口，而不定义底层筛选或录音逻辑。

## Invariants

- 右侧栏 MUST 保持“声源”“筛选器”“录音会话”三段纵向结构，MUST NOT 混入场景切换入口。
  - 标题 MUST 保持一致字号与风格语义
  - 按内容自然排版（wrap content）
- 声源行 MUST 直接消费 bridge 提供的 row 数据；用户取消勾选后，对应 row MUST 继续保留，仅改变勾选状态。
- 声源行勾选写入 MUST 以 `targetId` 调用 bridge 交互接口；MUST NOT 以展示 `sourceId` 作为写入主键。
- `sourceId`/`targetId` 身份映射与连续性前提 MUST 引用 `specs/contracts/tracking-identity.md`；右栏 MUST NOT 并行复写该规则。
- 声源行 MAY 在对象短时消失后继续保留为历史行；历史行 MUST 明确区分为非活跃态，并在其最后样本超出 chart 的 `1600` 样本窗口后移除。
- 声源行的 `active` 判定 MUST 基于 `targetId`，MUST NOT 由展示 `sourceId` 反推，以避免 `sourceId` 漂移或复用时误亮历史行。
- 当没有活动声源或没有活跃录音会话时，右栏 MUST 显示稳定空态文案，MUST NOT 伪造占位列表项。
- 录音会话摘要 MUST 按 `targetId` 分组；每个 target MUST 仅显示一行摘要。
- 录音会话摘要格式 MUST 为 `Target <id> | Source <source_id> | files: <n>`。
- 摘要 `<n>` MUST 仅统计当前活跃会话；MUST NOT 将最近结束会话混入摘要统计。
- 摘要中的 `source_id` MUST 优先来自活跃会话；当无活跃会话时，MUST 来自最近结束会话中的最新 source。
- 录音会话摘要 MUST NOT 展示 mode token。
- 录音会话详情 MUST 通过悬停提示显示，且逐行遵循 `<filename>`。
- 悬停详情 MAY 包含最近结束会话；当 target 仅有最近结束会话时，摘要 MUST 显示 `Target <id> | Source <source_id> | files: 0`。
- 声源 badge 的颜色和标签 MUST 忠实反映 bridge 输出，MUST NOT 在右栏本地推导另一套身份语义。
- 运行态高频刷新期间，右栏勾选交互 MUST 保持单击原子性；MUST NOT 因无意义整表重建导致单击失效或回弹体感。
- 在 `1600` 样本历史窗口内，右栏行之间的 badge 颜色 MUST 唯一；当历史目标数量超过默认调色板容量（12）时，bridge 投影层 MUST 优先保留活跃目标，并按 `lastSample` 保留最新非活跃历史行，淘汰最旧非活跃历史行。
- 筛选器开关和能量范围控件 MUST 继续通过现有 bridge 接口路由，右栏 MUST NOT 在本地重建筛选状态真源。
- “筛选器-声源”总开关 MUST NOT 清空声源列表；它只影响图表与 3D 可见输出。
- 右栏 MUST 作为对象状态面板，而不是图表或球体时序数据的生产者。

## Variation Space

- 行高、分隔线、字号和分区间距 MAY 演进，只要三段层级仍然稳定且易于扫描。
- 空态文案 MAY 调整，但空态必须继续表达“当前无可展示对象”，而不是技术错误。
- 录音会话展示方式 MAY 演进为更丰富的摘要，但其只读信息面板语义 MUST 保持。
- 录音会话摘要行 MAY 自动换行（wrap），但分组语义与摘要字段语义 MUST 保持不变。
- preview 自检区正文字体 MAY 调整，但 MUST 保持“小字号可读、不过度抢占右栏标题层级”。

## Rationale

- 右栏承载的是对象级可见性和筛选入口；取消最后一个勾选后仍保留 row，可以避免对象从用户心智地图中瞬间消失。
- 当对象短时消失时保留历史行并降级为非活跃态，可以让用户持续追踪身份而不误判为 UI 抖动。
- 让 badge 颜色与其他视图保持一致，可以维持跨区域的身份追踪。

## Anti-Patterns

- 在右栏本地拼接 preview/runtime 占位行或另一套 badge 颜色规则。
- 用户取消勾选后直接删除 row，导致对象与可见性状态混淆。
- 把场景切换器、图表时序控制或录音逻辑实现塞进右栏。
