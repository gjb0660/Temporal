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
- 图表固定窗口、主刻度与颜色一致性等稳定约束已由 `specs/contracts/ui/chart-canvas.md` 承接。
- 图表后端路线结论已由 `ui-system-refactor-chart-canvas` 承接，`ui-system` 只消费其上层展示边界。

## Decision

- `ui-system` 继续作为共享展示语义 owner，统一维护布局、投影、过滤、空态与时序展示边界。
- QML 只消费 bridge 输出，不复制业务推导；runtime/preview 继续在同一 projection 层演进。
- row/chart/3D 的过滤与空态契约保持冻结，后续演进只能走 shared projection 单路径收敛。
- 颜色语义与图表时间窗只通过共享 bridge/projection 输出消费，不在 QML 或下游 feature 中复制业务语义。
- runtime 在 bridge 层保持单一行为真源；MUST NOT 并行维护两套筛选、模型刷新与状态推导逻辑。
- 图表后端路线与迁移门槛由 `ui-system-refactor-chart-canvas` 单独拥有；`ui-system` 不重复承载其实现裁决。

## Acceptance

1. 三栏布局在默认尺寸与较窄窗口下保持稳定层级。
2. 左侧控制区只呈现必要的操作按钮与对应状态。
3. 3D 声源区、标题层级与整体主题满足既定视觉目标。
4. 右栏 row 与 3D 共享 current frame 语义，chart 使用共享时间窗序列，三者共享同一过滤语义。
5. 取消最后一个勾选 source 后，row 集合保持稳定，只有图表与 3D 变空。
6. chart 在连接首帧显示 `0`，发生重连后重新从 `0` 起算。
7. chart 行为持续满足 `specs/contracts/ui/chart-canvas.md`，且 `ui-system` 不再复写其中的稳定约束。
8. `ui-system` 与 `ui-system-refactor-chart-canvas` 的 owner 边界保持一致，不出现路线冲突或重复裁决。

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
