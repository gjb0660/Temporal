---
title: recording-filename
status: active
stability: strict
version: 0.1
---

## Role

定义源驱动录音输出的文件命名语义。
该 Contract 约束录音产物如何保留可解析身份与时间信息。

## Invariants

- 录音文件名 MUST 使用 `ODAS_{source_id}_{timestamp}_{sp|pf}.wav` 格式。
- 录音输出 MUST 保留可解析的 source identity 与 timestamp。
- 同一录音语义 MUST NOT 同时维护多套互相独立的命名规则。
- 文件名中的语义字段 MUST 对后续追溯可用，MUST NOT 退化为仅供显示的人类标签。

## Variation Space

- `timestamp` 的具体格式 MAY 演进，但 MUST 保持稳定、可解析、可排序。
- `sp|pf` 的内部命名来源 MAY 实现演进，但对外区分语义 MUST 保持稳定。
- 文件扩展名之外的附加元数据 MAY 另行存储，但 MUST NOT 替代文件名中的核心身份字段。

## Rationale

- 录音文件不是临时产物，而是后续定位、追溯、验证的重要边界对象。
- 如果文件名失去 source identity 或 timestamp，后续分析与问题归因会退化。

## Anti-Patterns

- 将录音命名改为仅时间戳或随机名。
- 为不同调用路径引入不兼容的文件名模板。
- 把 source identity 放到无法从文件名恢复的外部状态中。
