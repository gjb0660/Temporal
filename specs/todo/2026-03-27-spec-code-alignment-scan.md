# Spec Code Alignment Scan

## Goal

记录 2026-03-27 对当前 feature spec 与源码实现的一轮只读核对结果，
为后续代码修正提供最小行动入口。

## Scope

- `specs/features/*.md`
- `src/temporal/**`
- `tests/**`

## Summary

本轮扫描中，`routing-session`、`recording`、`remote-control`、
`media-pipeline` 的主要承诺与当前代码基本一致。

真实偏差主要集中在展示运行时边界：

1. production `AppBridge` 尚未生成图表序列模型。
2. `PreviewBridge` 仍在本地维护一套展示投影与过滤实现。

这意味着当前 spec 中关于“共享展示语义”的表述高于代码现状，
需要先回写 spec，再决定后续代码修正路径。

## Findings

### 1. ui-system overstates runtime chart parity

- `severity`: major
- `type`: conflict
- `file`: `specs/features/ui-system.md`
- `violation`: spec 声称右栏、图表与 3D 已共享同一套当前 frame 与过滤语义，
  但 production `AppBridge` 只更新 `sourceRowsModel` 与
  `sourcePositionsModel`，并未在运行时刷新 `elevationSeriesModel` 与
  `azimuthSeriesModel`。
- `impact`: production UI 中图表行为低于 spec 承诺，
  共享展示语义只在 preview bridge 中更完整。
- `code-evidence`:
  - `src/temporal/app.py` 仅在初始化时把图表模型置空。
  - `src/temporal/qml/CenterPane.qml` 已消费运行时图表模型。
- `minimal-fix`: 先将 ui-system spec 回写为“row 与 3D 已共享过滤语义，
  chart parity 仍待补齐”，后续再补 production 图表投影实现。

### 2. preview-mode still owns local projection logic

- `severity`: major
- `type`: conflict
- `file`: `specs/features/preview-mode.md`
- `violation`: spec 声称 preview 只消费 `ui-system` 的共享展示语义，
  但 `PreviewBridge` 仍本地实现 sidebar/filter/chart/positions 的完整投影。
- `impact`: preview 与 runtime 容易在排序、过滤、空态与图表语义上继续漂移。
- `code-evidence`:
  - `src/temporal/preview_bridge.py` 持有 `_sidebar_sources()`、
    `_visible_source_ids()`、`_refresh_preview_models()`、
    `_refresh_chart_models()` 与 `_series_items()`。
  - `tests/test_preview_bridge.py` 主要冻结的是 preview 本地实现，
    而不是 shared runtime layer。
- `minimal-fix`: 先将 preview-mode spec 回写为“当前保持语义对齐目标，
  但实现仍位于 PreviewBridge 本地”，后续再抽离共享 projection layer。

### 3. runtime-reliability should explicitly own parity gaps

- `severity`: major
- `type`: missing
- `file`: `specs/features/runtime-reliability.md`
- `violation`: 当前 reliability spec 尚未显式登记 production chart parity
  缺口与 preview/runtime projection parity 缺口。
- `impact`: 后续修正缺少明确 owner，容易再次被解释为 UI 文档问题。
- `minimal-fix`: 在 reliability spec 中把这两项列为当前活跃缺口与计划入口。

## Aligned Areas

### routing-session

- `AppBridge._route_audio_chunk()` 已按固定 4 通道做 PCM 去交织并推送到
  `AutoRecorder`。
- `tests/test_app_bridge_recording.py` 已覆盖 separated / post-filtered
  路由与会话暴露。

### recording

- `AppBridge._update_source_channel_map()` 已将可路由容量限制收入口径。
- `tests/test_app_bridge_recording.py` 已覆盖 over-capacity 行为。

### remote-control

- `AppBridge.startRemoteOdas()`、`_verify_odas_startup()` 与
  `_poll_remote_log()` 已体现 SSH、listener、远端状态校验的控制闭环。
- integration tests 已覆盖 listener bind 失败、控制通道失败、
  启动顺序等关键负路径。

## Next Actions

1. 先更新 `ui-system`、`preview-mode`、`runtime-reliability` 的 spec，
   使文档与当前代码事实一致。
2. 后续代码修正优先级：
   - production chart projection
   - shared projection layer extraction
   - parity tests across runtime and preview

## Remaining Risk

- 本报告未将 legacy 历史材料计入偏差。
- 本报告未把 `docs/core-features.md` 的简化表达视为阻断问题，
  因为本轮用户已明确允许其少于实际现状。
