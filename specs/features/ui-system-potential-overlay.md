---
title: ui-system-potential-overlay
tracker: feature
status: active
owner: codex/ui
updated: 2026-04-10
---

## Goal

在中栏建立 ODAS potential overlay 语义：tracked 与 potential 双层叠加展示，并保持 runtime/preview 同一投影路径。

## Non-Goals

- 不把 potential 引入右栏 source 勾选身份语义。
- 不在本轮为 potential 引入跨帧稳定身份跟踪。
- 不扩张为第三张图或新增页面级布局区域。

## Facts

- 现有中栏 chart/3D 只消费 tracked（SST）投影；potential（SSL）此前仅用于计数。
- 右栏已存在 potential 开关与能量范围控件。
- ODAS SSL potential 负载包含 `{x, y, z, E}`，不包含可稳定绑定 source 勾选的身份 id。
- 当前系统已固定 shared projection 路径：runtime 与 preview 共享同一展示投影实现层。
- potential 规范细节已由 `specs/contracts/potential-overlay.md` 作为唯一 SSOT 承载。

## Decision

- 中栏采用 tracked + potential 双层叠加，不再把 potential 语义折叠为计数-only。
- `ui-system-potential-overlay` 只拥有执行边界；potential 渲染、过滤与节流规则统一引用 `specs/contracts/potential-overlay.md`。
- runtime 与 preview 继续共享同一投影路径，不在 QML 或 bridge 下游复制 potential 业务规则。

## Acceptance

1. 中栏 chart/3D 同时可见 tracked 与 potential 两层语义。
2. 关闭 `声源` 开关只隐藏 tracked 层，potential 层保持独立可见性。
3. 关闭 `筛选器-potential` 开关只隐藏 potential 层，tracked 层保持独立可见性。
4. 调整 potential 能量范围会实时重算 potential 可见输出，不影响 tracked 可见输出。
5. potential overlay 的显示行为持续满足 `specs/contracts/potential-overlay.md`。
6. runtime 与 preview 在同输入下保持 potential overlay 输出一致。

## Plan

1. 同步 UI contracts，收敛为对 `specs/contracts/potential-overlay.md` 的单路径引用。
2. 在 projection/bridge 路径接入并验证 potential 解析、缓存与过滤重算。
3. 扩展 chart 与 3D 模型输入，支持 tracked + potential 混合渲染。
4. 增补 runtime/preview 行为测试与 QML 合同测试。

## Progress

- [x] 已冻结 potential overlay 的产品语义边界。
- [x] contracts 更新与代码落地已完成（规则以 `specs/contracts/potential-overlay.md` 为准）。
- [x] runtime/preview parity 回归已完成（含 potential 节流语义）。

## Todo

- [ ] 若后续要引入 potential 跨帧身份语义，需独立 feature 定义，不在本轮隐式扩展。
