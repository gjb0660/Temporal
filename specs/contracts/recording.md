---
title: recording
scope: api
stability: strict
version: 0.1
---

## Role

定义源驱动录音的命名语义与生命周期约束。
该 Contract 约束录音输出的可识别性、一致性与停止条件。

## Invariants

- 录音文件名 MUST 使用 `ODAS_{source_id}_{timestamp}_{sp|pf}.wav` 格式。
- 录音启动语义 MUST 由 source 出现或进入活跃状态触发。
- 录音停止语义 MUST 由 source 消失或 inactive timeout 触发。
- 录音输出 MUST 保留可解析的 source identity 与 timestamp。
- 同一录音语义 MUST NOT 同时维护多套互相独立的命名规则。

## Variation Space

- `timestamp` 的具体格式 MAY 演进，但 MUST 保持稳定、可解析、可排序。
- inactive timeout 的具体阈值 MAY 调整，但 MUST 继续表达“source 不再活跃”的停止语义。
- `sp|pf` 的内部命名来源 MAY 实现演进，但对外区分语义 MUST 保持稳定。

## Rationale

- 录音文件不是临时产物，而是后续定位、追溯、验证的重要边界对象。
- 如果文件名失去 source identity 或 timestamp，后续分析与问题归因会退化。
- source 驱动生命周期是该功能的核心业务语义，不能被手写状态机随意替换。

## Anti-Patterns

- 将录音命名改为仅时间戳或随机名。
- 使用多个不一致的停止条件。
- 将 source 消失后的停止逻辑写成永不终止的悬挂录音。
