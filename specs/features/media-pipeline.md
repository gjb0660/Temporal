---
title: media-pipeline
tracker: primary-feature
status: active
owner: codex/core
updated: 2026-03-31
---

## Goal

建立 SST 与 SSL 数据进入 UI 的最小链路，使声源列表与筛选面板具备实时联动基线。

## Non-Goals

- 不负责 3D 视图精修或 preview 场景驱动。
- 不负责录音状态机与 SSS 音频写入。

## Facts

- UI 需要消费 source 列表、source 数量与 potential 数量。
- ODAS `tracks/pots` JSON sink 输出是多行完整对象，不是 NDJSON。
- SST 与 SSL 输入可能存在分块与脏数据，需要容错解析。
- QML 只能通过 bridge 消费投影后的状态。
- 该能力在本轮 feature cutover 前已经完成核心交付。

## Decision

- 由 backend 解析 SST/SSL 并向 bridge 投影稳定的 UI 状态。
- JSON framing 以对象边界为真源，不再按换行切分 JSON 消息。
- 保持筛选状态与 source 摘要从同一 bridge 真源输出。
- 在本 feature 中只交付最小联动，不提前扩展录音与 preview 语义。

## Acceptance

1. SST 输入可驱动右侧 source 列表更新。
2. SSL 输入可驱动 potential 计数更新。
3. ODAS 多行 JSON 对象在分块输入下仍能被完整解析为顶层消息。
4. 脏数据不会导致应用崩溃或 UI 失去响应。

## Plan

1. 建立容错的 SST/SSL 解析路径。
2. 通过 bridge 暴露 UI 所需的最小摘要属性。
3. 验证 QML 可从 bridge 动态渲染 source 与计数状态。

## Progress

- [x] 已建立 SST/SSL 解析与容错基线。
- [x] 已通过 bridge 暴露 sourceItems、sourceCount 与 potentialCount。
- [x] 已完成 source 列表与筛选面板的最小联动。
- [x] 已收敛 JSON framing 为对象边界解析，移除 NDJSON 假设。

## Todo

- [ ] 更复杂的展示语义由 ui-system 承接，preview-mode 只消费共享展示结果。
