---
title: ui-system
tracker: primary-feature
status: active
owner: codex/ui
updated: 2026-03-31
---

## Goal

完成主界面的视觉层级、操作布局与共享展示语义收口，使三栏结构、控制区、图表与 3D 视图具备统一的操作与阅读体验。

## Non-Goals

- 不拥有 preview-mode 入口与 PreviewBridge 启动职责。
- 不拥有远端控制、录音状态机或 SSS 路由真源。

## Facts

- 主界面需要保持三栏布局与稳定的信息层级。
- 左侧控制区需要围绕远端控制与监听控制呈现明确按钮语义。
- 3D 声源区域与整体视觉主题需要单独收口。
- `preview-mode` 与主界面共享同名 bridge 契约与状态投影接口。
- runtime `AppBridge` 目前已经稳定投影 `sourceRowsModel`、
  `sourcePositionsModel`、`elevationSeriesModel`、`azimuthSeriesModel`
  与筛选状态。
- runtime 使用 `core/ui_projection.py` 的 row / positions /
  chart ticks / series 计算实现。
- preview 仍保留 scenario 数据与 tick 推进驱动职责；runtime 仍保留
  SST 输入与 frame window 维护职责。
- 当前展示语义中，row / 3D positions 使用 current frame，
  chart 使用共享时间窗序列，并共享同一过滤语义。
- chart 时间轴以连接首帧 `timeStamp` 归零，并在重连后重新归零。
- chart 横轴显示单位为 0.01s，刻度以 200 整数步长为主体，最后
  一个刻度显示最新时间。
- source 颜色语义当前由 bridge 维护“连接内独立分配、重连重置”的
  状态化分配器输出；右栏、图表与 3D 必须共享该映射。
- 颜色分配前 4 色当前与 odas_web 基准调色板一致，扩展颜色使用固定表。

## Decision

- 将界面布局、视觉比重、按钮呈现与视觉风格作为独立 UI feature 收口。
- 将共享 bridge 契约、数据投影、过滤、空态与时序推进语义继续视为
  `ui-system` owner，并通过 shared projection layer 统一实现。
- 继续通过共享 `appBridge` 契约消费状态，不在 QML 内复制业务逻辑。
- 当前冻结 row、chart 与 3D 的过滤/空态契约，并保持 runtime/preview
  在同一 projection 实现层上演进。
- chart 时钟由 bridge 维护“原点 + 重连重置”语义，QML 仅消费 ticks。
- 颜色语义由 bridge allocator 单一维护，MUST NOT 在 projection/QML
  引入并行颜色业务语义。
- runtime 在 bridge 层应保持单一行为真源，MUST NOT 并行维护
  两套筛选、模型刷新、状态推导逻辑。

## Acceptance

1. 三栏布局在默认尺寸与较窄窗口下保持稳定层级。
2. 左侧控制区只呈现必要的操作按钮与对应状态。
3. 3D 声源区、标题层级与整体主题满足既定视觉目标。
4. 右栏 row 与 3D 共享 current frame 语义，chart 使用共享时间窗序列，
   三者共享同一过滤语义。
5. 取消最后一个勾选 source 后，row 集合保持稳定，只有图表与 3D 变空。
6. chart 在连接首帧显示 `0`，发生重连后重新从 `0` 起算。

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

## Todo

- [ ] 若后续新增展示轴或筛选维度，需先在 shared projection layer 扩展后再进入 bridge 层。
