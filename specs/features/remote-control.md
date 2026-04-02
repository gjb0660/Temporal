---
title: remote-control
tracker: primary-feature
status: active
owner: codex/core
updated: 2026-03-31
---

## Goal

建立远端 odaslive 的控制与运行验证闭环，使 Temporal 能通过明确的 SSH、监听与重连语义管理远端运行状态。

## Non-Goals

- 不把录音路由或 preview-mode 模拟状态混入远端控制职责。
- 不替代全部交付质量门禁汇总。

## Facts

- 远端控制需要显式 connect、start、stop、status 操作。
- 本地 listeners 与远端 odaslive 是独立生命周期资源。
- 远端启动需要在本地监听资源可用后进行。
- rootless 环境下 `/proc/$pid/cwd` 与 `/proc/$pid/exe` 不能作为稳定门控。
- 远端运行态主真值模型已收敛为 pid-only。
- 在 pid-only 下，无 `odaslive.pid` 的存量进程不会被自动接管。

## Decision

- 通过 backend 持有 SSH 控制会话与远端进程组控制语义。
- 远端 running 仅由 pid-only 模型判定：
  `odaslive.pid` 存在、pid 为纯数字、`kill -0 pid` 成功。
- `temporal_start` 必须完成 pid 文件写入与回读一致性校验；写入失败或不一致必须显式失败。
- `temporal_stop` 先按进程组停止，失败回退按 pid 停止；仅在确认停止后清理 pid 文件。
- 将监听按钮与远端启动按钮拆为不同控制语义，避免错误耦合。
- 日志读取异常但控制通道存活时，仍需继续执行状态同步收敛。

## Acceptance

1. UI 可触发远端连接、启动、停止与状态查询。
2. 远端 odaslive 运行状态仅由 pid-only 模型决定，不依赖流数据推断。
3. 本地监听启停不会隐式停止远端 odaslive 或断开 SSH。
4. `temporal_start` 在 pid 文件持久化失败时必须显式失败，不允许静默成功。
5. 日志读取异常（非断链）场景下，控制状态仍会同步收敛，避免按钮误回退。

## Plan

1. 固化 SSH 控制接口与进程组控制规则。
2. 固化本地监听与远端启动的先后语义。
3. 冻结远端状态与错误原因的 UI 投影方式。
4. 补齐关键运行路径验证，并收敛重连与 fallback 文档。

## Progress

- [x] 已建立 SSH 连接与远端命令控制基线。
- [x] 已落地本地监听与远端启动的依赖顺序。
- [x] 已固化 pid-only 真值模型：pid 文件存在、数字校验通过，且 `kill -0` 成功。
- [x] 已完成 start 的 pid 持久化失败显式报错与 stop 的清理时序约束。
- [x] 已完成日志读取异常路径的状态同步收敛补强。
- [x] 已确认远端运行验证与重连风险属于 remote-control owner。
- [ ] 仍需补齐关键运行路径的集成验证证据与风险说明收口。

## Todo

- [ ] 若验证中发现新的结构性约束，提炼到 contracts 或新的 feature，而不是继续回拆独立风险文件。
