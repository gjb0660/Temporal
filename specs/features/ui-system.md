---
title: ui-system
tracker: primary-feature
status: active
owner: codex/ui
updated: 2026-03-27
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
  `sourcePositionsModel` 与筛选状态，但尚未在运行时生成图表序列模型。
- `PreviewBridge` 已具备 sidebar、positions、chart series 与 sample window
  的本地投影实现，因此“共享展示语义”当前仍停留在 owner 目标，
  而非单一实现层。
- source 勾选、空态判定与 3D 可见性在 runtime 与 preview 中都已有显式行为，
  但图表 parity 仍未在 production bridge 中收口。

## Decision

- 将界面布局、视觉比重、按钮呈现与视觉风格作为独立 UI feature 收口。
- 将共享 bridge 契约、数据投影、过滤、空态与时序推进语义继续视为
  `ui-system` owner，但按当前代码事实记录为“目标边界已明确、实现仍分置”。
- 继续通过共享 `appBridge` 契约消费状态，不在 QML 内复制业务逻辑。
- 当前先冻结 row 与 3D 的过滤/空态契约；图表与 runtime parity
  在代码补齐前不再作为已完成事实表述。

## Acceptance

1. 三栏布局在默认尺寸与较窄窗口下保持稳定层级。
2. 左侧控制区只呈现必要的操作按钮与对应状态。
3. 3D 声源区、标题层级与整体主题满足既定视觉目标。
4. 右栏 row、图表与 3D 共享同一套当前 frame 与过滤语义。
5. 取消最后一个勾选 source 后，row 集合保持稳定，只有图表与 3D 变空。

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
- [ ] runtime `AppBridge` 仍未生成 elevation/azimuth chart series。
- [ ] 共享展示语义仍由 runtime 与 preview 两套 bridge 分别实现，
  尚未收敛为单一 projection layer。

## Todo

- [ ] 补齐 production 图表模型后，再恢复“图表与 3D 已共享同一套语义”的强表述。
- [ ] `preview-mode` 后续若改为真实消费共享 projection layer，再从本文件移除实现分置说明。
