---
title: ui-system
tracker: primary-feature
status: active
owner: codex/ui
updated: 2026-04-02
---

## Goal

完成主界面的视觉层级、操作布局与共享展示语义收口，使三栏结构、控制区、图表与 3D 视图具备统一的操作与阅读体验。

## Non-Goals

- 不拥有 preview-mode 入口与 PreviewBridge 启动职责。
- 不拥有远端控制、录音状态机或 SSS 路由真源。

## Facts

- 主界面当前是三栏结构，并已形成控制区、图表区、3D 区的稳定信息层级。
- `preview-mode` 与 production 共享同名 `appBridge` 契约与同一投影实现层。
- runtime 已稳定投影 `sourceRowsModel`、`sourcePositionsModel`、`elevationChartSeriesModel`、`azimuthChartSeriesModel` 与筛选状态。
- runtime/preview 的语义分工已固定：preview 负责 scenario 数据推进，runtime 负责 SST 输入与窗口维护；展示投影共享。
- 当前可视化语义已固定：row/3D 基于 current frame，chart 基于共享时间窗，三者共享同一过滤语义。
- chart 时间语义已固定为：首帧归零、重连后重新归零、单位 0.01s、固定 1600 滚动窗口、可见区间 200 整除主刻度线+标签、latest 去重标注。
- source 颜色由 bridge 输出并按空间目标连续性保持稳定映射，row/3D/chart 共享同一映射；默认配置使用固定调色池且长度满足可见 `<=8`。
- 若异常配置导致调色池长度小于可见上限，系统按“先 Top8 再颜色分配”处理；颜色槽位耗尽后可丢弃超限目标并发出告警。
- `sourceId` 在输入侧可作为短期跟踪标识展示，但不再作为颜色身份主键。
- 颜色前 4 色与 odas_web 基准调色板一致，扩展颜色使用固定表。
- 图表后端路线在 `ui-system-refactor-chart-canvas` 已锁定：长期目标态为 `QtGraphs`，短期过渡态为 `Canvas`（仅风险控制用途），`QtCharts` 禁用。

## Decision

- `ui-system` 继续作为共享展示语义 owner，统一维护布局、投影、过滤、空态与时序展示边界。
- QML 只消费 bridge 输出，不复制业务推导；runtime/preview 继续在同一 projection 层演进。
- row/chart/3D 的过滤与空态契约保持冻结，后续演进只能走 shared projection 单路径收敛。
- 颜色语义由 bridge allocator 单一维护；MUST NOT 在 projection/QML 引入并行颜色业务语义或业务 fallback。
- runtime 在 bridge 层保持单一行为真源；MUST NOT 并行维护两套筛选、模型刷新与状态推导逻辑。
- 后端路线由 `ui-system` 统一约束：功能演进默认面向 `QtGraphs` 目标态设计；过渡态使用 `Canvas`，不引入或恢复 `QtCharts` 依赖。
- 在过渡态结束前，启动稳定性优先级高于后端替换速度；任何实现必须先消除可复现崩溃前提，再进入后端迁移。

## Acceptance

1. 三栏布局在默认尺寸与较窄窗口下保持稳定层级。
2. 左侧控制区只呈现必要的操作按钮与对应状态。
3. 3D 声源区、标题层级与整体主题满足既定视觉目标。
4. 右栏 row 与 3D 共享 current frame 语义，chart 使用共享时间窗序列，三者共享同一过滤语义。
5. 取消最后一个勾选 source 后，row 集合保持稳定，只有图表与 3D 变空。
6. chart 在连接首帧显示 `0`，发生重连后重新从 `0` 起算。
7. chart 行为满足 `specs/contracts/ui/chart-canvas.md` 的固定 1600 滚动窗口与主刻度约束，不再依赖旧的“尾刻度最新值”语义。
8. `ui-system` 与 `ui-system-refactor-chart-canvas` 的后端路线结论保持一致，不出现“QtCharts 可用”冲突陈述。
9. preview 多点场景（如 `hemisphereSpread`）连续运行时，在同帧候选 `<=8` 且默认调色池容量满足可见上限前提下，不应误触发 Top8 删除路径。

## Plan

1. 收敛页面结构、卡片比例与视觉层级。
2. 收敛控制区的按钮布局与文案。
3. 收敛 3D 视图强调与整体主题风格。
4. 补齐 production bridge 的图表序列投影，使其与 row/3D 的过滤语义一致。
5. 为 runtime 与 preview 的展示 parity 建立可重复验证入口。

## Progress

- [x] 已完成三栏结构与布局节奏调整。
- [x] 已收敛左侧按钮区与日志区比例。
- [x] 已完成 3D 区域强调与整体主题方向收口。
- [x] 已识别共享 bridge 契约与数据投影属于 ui-system owner。
- [x] 已冻结 row 稳定、3D 过滤与空态判定的首批行为语义。
- [x] 已在 runtime `AppBridge` 收口 elevation/azimuth chart series 投影。
- [x] 已抽离 shared projection layer，并由 runtime 与 preview 共同消费。
- [x] 已同步 chart 后端路线 owner 语义（目标 QtGraphs，过渡 Canvas，禁用 QtCharts）。

## Todo

- [ ] 若后续新增展示轴或筛选维度，需先在 shared projection layer 扩展后再进入 bridge 层。
