---
title: app-bridge-status
status: active
stability: semi
version: 0.2
---

## Role

定义 AppBridge 控制状态投影的单一语义边界。
该 Contract 约束 `controlPhase`、`controlDataState` 与 `controlSummary` 的真源关系，不定义 SSH/ODAS 底层协议实现。

## Invariants

- AppBridge MUST 暴露结构化控制状态：`controlPhase`、`controlDataState` 与 `controlSummary`。
- `status` MUST 作为兼容别名存在，且值 MUST 等于 `controlSummary`。
- 控制状态写入 MUST 以单次原子状态变更完成（phase + data-state + optional override）；MUST NOT 暴露中间半状态摘要。
- `controlPhase` MUST 仅使用固定集合：
  `idle`、`ssh_disconnected`、`ssh_connected_idle`、`odas_starting`、`odas_running`、`streams_listening`、`error`。
- `controlDataState` MUST 仅使用固定集合：
  `inactive`、`listening_remote_not_running`、`running_waiting_sst`、`receiving_sst`、`unavailable`。
- `controlSummary` MUST 始终为三行固定结构：
  第 1 行主状态（phase），第 2 行数据状态（data state），第 3 行计数（声源/候选/录制中）。
- `SST/SSL` 更新、筛选变化与计数变化 MUST NOT 直接覆盖主状态语义；它们只能通过 data-state 或计数行投影。
- 收数判定 MUST 以 SST 为准；当最近 SST 到达时间超过 2 秒窗口后，data-state MUST 从 `receiving_sst` 回退到 `running_waiting_sst`。
- preview 与 runtime MUST 复用同一套 `controlPhase/controlDataState/controlSummary` 契约语义。
- 状态语义映射 MUST 满足以下逐项约束：
  - `idle` + `inactive`：系统就绪且未监听。
  - `ssh_connected_idle` + `inactive`：控制通道已连接但监听未启动。
  - `odas_running` + `inactive`：远端 ODAS 已运行但本地监听未启动。
  - `odas_starting` + `running_waiting_sst`：远端启动流程中，尚未接收 SST。
  - `streams_listening` + `listening_remote_not_running`：监听已启动但远端 ODAS 未运行。
  - `streams_listening` + `running_waiting_sst`：远端 ODAS 已运行但尚未接收 SST。
  - `streams_listening` + `receiving_sst`：正在稳定接收 SST。
  - `error|ssh_disconnected` + `unavailable`：错误或断链场景下数据状态不可用。

## Variation Space

- `controlSummary` 文案 MAY 演进，但 `启动中/运行中/未运行/启动失败` 等关键语义 MUST 保持可识别。
- 当出现错误时，第 1 行主状态 MAY 使用更具体的错误原因，但相位 MUST 继续落在 `error` 或 `ssh_disconnected` 语义边界内。
- 第 3 行计数的排列与措辞 MAY 演进，但数据来源 MUST 保持为结构化计数字段。

## Rationale

- 摘要文本承担“当前状态”，高频数据承担“连续观测”，两者混用会直接导致认知噪声。
- 结构化状态可测试、可绑定、可迁移，避免把 UI 逻辑绑死在中文拼接字符串上。

## Anti-Patterns

- 在 `SST/SSL` 回调中直接覆盖第 1 行主状态。
- 通过字符串包含关系反推主状态阶段。
- preview 与 runtime 使用不同状态字段或不同阶段语义。
- 在收数超时后仍维持 `receiving_sst`，造成“无数据仍显示收数中”的状态漂移。
- 先后分离写入 phase/data-state 导致摘要重复刷新或瞬时错配。
