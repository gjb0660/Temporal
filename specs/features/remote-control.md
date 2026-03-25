---
title: remote-control
tracker: primary-feature
status: active
owner: codex/core
updated: 2026-03-26
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
- 远端运行验证、重连加固与 fallback 说明仍需要通过集成层持续收口。

## Decision

- 通过 backend 持有 SSH 控制会话与远端进程组控制语义。
- 以派生 pid 文件和真实进程校验作为远端运行状态真源。
- 将监听按钮与远端启动按钮拆为不同控制语义，避免错误耦合。
- 将关键运行路径验证、重连风险与 fallback 说明并入本文件，而不是维持独立 research owner。

## Acceptance

1. UI 可触发远端连接、启动、停止与状态查询。
2. 远端 odaslive 的运行状态只由校验后的真实进程存在性决定。
3. 本地监听启停不会隐式停止远端 odaslive 或断开 SSH。
4. 远端关键运行路径具备可重复的集成验证证据，主要重连与恢复风险有明确缓解与 fallback 描述。

## Plan

1. 固化 SSH 控制接口与进程组控制规则。
2. 固化本地监听与远端启动的先后语义。
3. 冻结远端状态与错误原因的 UI 投影方式。
4. 补齐关键运行路径验证，并收敛重连与 fallback 文档。

## Progress

- [x] 已建立 SSH 连接与远端命令控制基线。
- [x] 已落地本地监听与远端启动的依赖顺序。
- [x] 已固化 pid 文件、日志与状态校验语义。
- [x] 已确认远端运行验证与重连风险属于 remote-control owner。
- [ ] 仍需补齐关键运行路径的集成验证证据与风险说明收口。

## Todo

- [ ] 若验证中发现新的结构性约束，提炼到 contracts 或新的 feature，而不是继续回拆独立风险文件。
