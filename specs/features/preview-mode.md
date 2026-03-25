---
title: preview-mode
tracker: primary-feature
status: active
owner: codex/ui
updated: 2026-03-26
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
- preview 依赖 `ui-system` 所拥有的共享展示语义，而不是自行分叉派生。

## Decision

- 通过独立 `temporal-preview` 入口启动共享 `Main.qml`。
- 使用 `PreviewBridge` 承接 preview 模式下的安全 no-op 控制与状态输出。
- 共享展示语义由 `ui-system` 拥有，preview 只消费共享 `appBridge` 绑定名称与状态语义。

## Acceptance

1. `temporal-preview` 可在无需修改 QML 的前提下启动主界面。
2. preview 与 production 共享同一套 `appBridge` 绑定名称。
3. preview 左侧动作只影响本地 preview 状态，不触发真实 SSH 或网络行为。

## Plan

1. 固化 preview 启动入口与共享启动辅助。
2. 固化 PreviewBridge 与 preview 数据真源边界。
3. 验证共享主界面在 preview 模式下稳定渲染。

## Progress

- [x] 已提供 `temporal-preview` 独立入口。
- [x] 已建立 PreviewBridge 与 preview 数据真源。
- [x] 已让共享主界面在 preview 模式下可稳定渲染。

## Todo

- [ ] 如 preview-mode 未来扩展新的入口职责，在不侵占 `ui-system` owner 的前提下单独收口。
