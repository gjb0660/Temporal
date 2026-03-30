---
title: preview-mode
tracker: primary-feature
status: active
owner: codex/ui
updated: 2026-03-31
---

## Goal

将 preview 模式收敛为标准应用入口，使共享主界面可以在不修改 QML 的前提下使用 PreviewBridge 启动与渲染。

## Non-Goals

- 不在本文件中拥有共享展示语义、过滤规则或 bridge 契约 owner。
- 不将 preview 入口职责扩展为 UI 视觉系统 owner。

## Facts

- preview 与 production 需要共享同一份主界面布局。
- preview 需要独立入口、独立 bridge 与本地安全控制行为。
- preview fixture 数据必须保留在 Python 真源，而不是散落在 QML 层。
- `PreviewBridge` 当前维护 scenario、selection 与 sample window 推进驱动；
  通过复用 `AppBridge` 的共享行为层完成 row / positions / chart 投影。
- preview 与 production 当前共享 bridge 契约名称、目标语义与投影实现层。
- preview chart 时间窗语义当前与 runtime 对齐：单位 `0.01s`、主体刻度
  步长 `200`、最后刻度显示最新时间、重启/切换后归零。
- preview fixture 仅作为 source 位置数据真源；chart 时间轴由 bridge + shared
  chart-time 规则统一生成，不再以 fixture 内绝对 sample 作为显示真源。
- preview 允许保持 fixture 数据源与 runtime 不同，但不允许在 chart 语义
  上继续漂移。

## Decision

- 通过独立 `temporal-preview` 入口启动共享 `Main.qml`。
- 使用 `PreviewBridge` 承接 preview 模式下的安全 no-op 控制与状态输出。
- `PreviewBridge` 以 `AppBridge` 作为行为真源，除数据来源外不得分叉 bridge 逻辑。
- 保持 preview 对 `ui-system` 的语义对齐目标，并将展示投影统一委托给 shared projection layer。
- 保持 preview 与 runtime 除数据来源外的 chart 语义一致，不在 QML 层引入分支逻辑。

## Acceptance

1. `temporal-preview` 可在无需修改 QML 的前提下启动主界面。
2. preview 与 production 共享同一套 `appBridge` 绑定名称。
3. preview 左侧动作只影响本地 preview 状态，不触发真实 SSH 或网络行为。
4. preview chart 在流重启或场景切换后从 `0` 重新起算，并保持 `200` 主体刻度 + 最新时间尾刻度语义。

## Plan

1. 固化 preview 启动入口与共享启动辅助。
2. 固化 PreviewBridge 与 preview 数据真源边界。
3. 继续冻结 preview 当前 bridge 契约与展示行为，避免与 runtime 继续漂移。
4. 保持 preview 场景驱动与 shared projection layer 的边界清晰，不回流重复投影逻辑。

## Progress

- [x] 已提供 `temporal-preview` 独立入口。
- [x] 已建立 PreviewBridge 与 preview 数据真源。
- [x] 已让共享主界面在 preview 模式下可稳定渲染。
- [x] 已用 preview 行为测试冻结 source rows、positions、chart series 与过滤联动。
- [x] preview 已消费 runtime 与 ui-system 的单一 projection 实现层。

## Todo

- [ ] 如 preview-mode 未来扩展新的入口职责，在不侵占 `ui-system` owner 的前提下单独收口。
