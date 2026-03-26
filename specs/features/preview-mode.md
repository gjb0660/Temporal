---
title: preview-mode
tracker: primary-feature
status: active
owner: codex/ui
updated: 2026-03-27
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
- `PreviewBridge` 当前直接维护 scenario、selection、sample window、
  positions 与 chart series 的本地投影逻辑。
- preview 与 production 当前共享的是 bridge 契约名称与目标语义，
  而不是同一个 projection 实现层。

## Decision

- 通过独立 `temporal-preview` 入口启动共享 `Main.qml`。
- 使用 `PreviewBridge` 承接 preview 模式下的安全 no-op 控制与状态输出。
- 保持 preview 对 `ui-system` 的语义对齐目标，但按当前代码事实承认：
  preview 仍通过本地 bridge 实现展示投影，而不是消费单一共享 runtime layer。

## Acceptance

1. `temporal-preview` 可在无需修改 QML 的前提下启动主界面。
2. preview 与 production 共享同一套 `appBridge` 绑定名称。
3. preview 左侧动作只影响本地 preview 状态，不触发真实 SSH 或网络行为。

## Plan

1. 固化 preview 启动入口与共享启动辅助。
2. 固化 PreviewBridge 与 preview 数据真源边界。
3. 继续冻结 preview 当前 bridge 契约与展示行为，避免与 runtime 继续漂移。
4. 待 shared projection layer 成立后，再将 preview 的本地投影逻辑替换为共享实现。

## Progress

- [x] 已提供 `temporal-preview` 独立入口。
- [x] 已建立 PreviewBridge 与 preview 数据真源。
- [x] 已让共享主界面在 preview 模式下可稳定渲染。
- [x] 已用 preview 行为测试冻结 source rows、positions、chart series 与过滤联动。
- [ ] preview 仍未真正消费 runtime 与 ui-system 的单一 projection 实现层。

## Todo

- [ ] shared projection layer 建立后，将 PreviewBridge 的本地投影逻辑下沉为共享实现消费方。
- [ ] 如 preview-mode 未来扩展新的入口职责，在不侵占 `ui-system` owner 的前提下单独收口。
