---
title: ui-system
tracker: primary-feature
status: active
owner: codex/ui
updated: 2026-03-26
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
- `sourceRowsModel`、`sourcePositionsModel`、图表序列与 ticks 需要共享同一时序语义。
- source 勾选、energy 过滤、空态判定与 3D/图表可见性存在共享规则。

## Decision

- 将界面布局、视觉比重、按钮呈现与视觉风格作为独立 UI feature 收口。
- 将共享 bridge 契约、数据投影、过滤、空态与时序推进语义并入本文件统一承接。
- 继续通过共享 `appBridge` 契约消费状态，不在 QML 内复制业务逻辑。
- 让右栏、图表与 3D 都从统一的当前 frame 与过滤语义派生。

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
4. 收敛共享 bridge 契约、tracking 投影、过滤与空态语义。

## Progress

- [x] 已完成三栏结构与布局节奏调整。
- [x] 已收敛左侧按钮区与日志区比例。
- [x] 已完成 3D 区域强调与整体主题方向收口。
- [x] 已识别共享 bridge 契约与数据投影属于 ui-system owner。
- [x] 已收敛首批 trackingFrames 与过滤语义规则。
- [ ] 仍需完成共享展示语义的最终验收与稳定文档化。

## Todo

- [ ] `preview-mode` 只消费本文件定义的共享展示语义，未来如新增入口职责应单独立新 feature。
