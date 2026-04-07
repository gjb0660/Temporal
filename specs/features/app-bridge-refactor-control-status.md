---
title: app-bridge-refactor-control-status
tracker: refactor
status: done
owner: codex/core
updated: 2026-04-08
---

## Goal

重构 AppBridge 与左侧控制区的状态表达，降低 ODAS 控制交互中的认知噪声。
建立结构化状态契约，确保状态摘要稳定、数据接收语义可区分，并在单一状态区完成三行表达。

## Non-Goals

- 不改变 SSH/ODAS 远程控制协议与生命周期规则。
- 不新增按钮矩阵或隐藏控制入口。
- 不引入双轨状态模型（本次一次性切换）。

## Facts

- 当前左侧状态区直接绑定 `appBridge.status`，并承接了阶段摘要与高频计数混合语义。
- `stream_projection` 在 `SST/SSL/筛选` 路径中频繁写入状态字符串，导致主状态高频跳变。
- `remote_lifecycle` 仍承担真实控制阶段判定，是阶段语义的权威来源。
- 现有测试已覆盖启动、停止、异常与 preview/runtime 基本行为。

## Decision

- 新增结构化接口：`controlPhase`、`controlDataState`、`controlSummary`；`status` 保留兼容别名并等于 `controlSummary`。
- 固定 `controlPhase` 枚举：
  `idle`、`ssh_disconnected`、`ssh_connected_idle`、`odas_starting`、`odas_running`、`streams_listening`、`error`。
- 固定 `controlDataState` 枚举：
  `inactive`、`listening_remote_not_running`、`running_waiting_sst`、`receiving_sst`、`unavailable`。
- 高频 `SST/SSL/筛选` 更新不再覆盖主状态行；通过 data-state 与计数行投影。
- 收数判定仅基于 SST，超时窗口固定 2 秒。
- 左侧控制区采用“单一状态区 + 日志区”模型，状态区用三行文本承载主状态、数据状态与计数。
- preview/runtime 统一复用同一状态契约，不保留双标准。

## Acceptance

1. AppBridge 暴露 `controlPhase`、`controlDataState` 与 `controlSummary`，且 `status == controlSummary`。
2. `controlSummary` 固定为三行文本：主状态、数据状态、计数。
3. 监听中但未启动、已启动未收数、收数中三类状态可稳定区分，且收数超时 2 秒后自动回退。
4. LeftSidebar 删除独立指标区，状态区单区绑定 `controlSummary`。
5. preview/runtime 在相同阶段语义下输出一致状态字段行为。

## Plan

1. 先更新 contract：新增 AppBridge 状态契约并更新 left-sidebar 契约。
2. 重构 backend 状态写入链：remote lifecycle 负责阶段摘要，stream projection 停止高频覆盖。
3. 改造 LeftSidebar 绑定，收敛为单状态区三行文本。
4. 更新 integration/recording/preview 测试断言到 `phase + data-state + 三行摘要` 语义。
5. 执行 unittest、pyright、ruff、qmllint 验证闭环。

## Progress

- [x] 完成状态契约设计并固化阶段与数据子状态枚举。
- [x] 完成 AppBridge 结构化状态字段与兼容别名设计。
- [x] 完成左侧栏单状态区三行语义布局落地。
- [x] 完成回归与静态检查并收口 spec 状态。

## Todo

- [ ] 若后续出现新的状态语义分叉，优先更新 contract，再改实现。
