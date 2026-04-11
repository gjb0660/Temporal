---
title: potential-overlay
status: active
stability: semi
version: 0.1
---

## Role

定义 potential 叠加层在图表与空间视图中的唯一约束真源。
该 Contract 约束 potential 数据语义、可见性控制、渲染边界与运行态一致性。

## Invariants

- potential 输入 MUST 来源于 SSL potential 事件，并保持 `{x, y, z, E}` 语义；MUST NOT 伪造稳定身份 id。
- potential 与 tracked MUST 保持语义分层；potential MUST NOT 复用 tracked 的身份主键或勾选主键。
- potential 可见性 MUST 由独立开关控制，并与“声源”开关并行独立。
- potential 能量范围控件 MUST 仅影响 potential 层；MUST NOT 影响 tracked 层可见性。
- chart 的 potential 序列 MUST 使用 11 档能量色阶散点语义，MUST NOT 连线伪造连续身份轨迹。
- chart 的 potential 历史写入 MUST 使用 SSL 帧节流（默认 `stride=20`）。
- chart 的 potential 散点半径默认 MUST 为 `3`（对齐 `odas_web`）。
- chart 的 potential 时序窗口 MUST 与共享图表窗口对齐（默认 `1600` samples）。
- 3D 的 potential 点位 MUST 使用 11 档能量色阶与固定大小语义；默认大小 MUST 为 tracked 点位大小的 `0.625x`。
- 3D 的 potential 点位 MUST 使用不透明材质与方点语义，并支持默认 `50` 帧短尾迹；`life` MUST NOT 用于透明度衰减。
- 3D 渲染层级 MUST 保持 potential 在下、tracked 在上；MUST NOT 让 potential 覆盖 tracked。
- potential 颜色字面量 MUST 使用 Qt 可解析格式（如 `#RRGGBB`）；MUST NOT 使用会导致 Qt 路径退化的颜色格式。
- runtime 与 preview MUST 共享同一 potential 投影路径与同一可见性语义；MUST NOT 引入并行 fallback 规则。
- 下游 UI contracts/features MUST 引用本 Contract；MUST NOT 在本 Contract 之外并行定义 potential 业务规则。

## Variation Space

- potential 调色板、视觉样式和点位材质 MAY 演进，只要不变量中的分层、可见性与一致性语义保持。
- potential 的节流实现方式 MAY 调整，只要默认写入节奏与时序语义保持与上游约束一致。
- potential 的投影实现 MAY 重构，只要 runtime/preview 单路径消费与行为一致性保持。

## Rationale

- potential 没有稳定身份 id，必须与 tracked 身份语义隔离，否则会污染交互主键和跨视图一致性。
- 将 potential 规则集中到单一 contract，可避免 chart、3D、sidebar 各自维护并行规则导致漂移。

## Anti-Patterns

- 用 source 勾选身份去驱动 potential 可见集。
- 在任一 UI 层本地补一套 potential 节流、颜色或层级规则。
- 将 potential 渲染为连续折线并暗示稳定身份。
