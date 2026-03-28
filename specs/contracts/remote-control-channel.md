---
title: remote-control-channel
status: active
stability: semi
version: 0.1
---

## Role

定义远程 ODAS 控制链路的最小行为约束。
该 Contract 约束 SSH 控制、进程控制、流启动可观测性，以及面向 UI 的控制状态语义。

## Invariants

- SSH 控制接口 MUST 明确暴露 `connect`、`start`、`stop`、`status` 语义。
- 控制失败 MUST 以显式错误暴露，MUST NOT 静默吞掉失败。
- 单实例远程进程控制 MUST 使用显式实例标识，MUST NOT 依赖进程名匹配作为实例身份。
- 当流由 `start()` 启动时，监听就绪状态 MUST 同步可观测；在 bind/listen 成功前，系统 MUST NOT 报告流已激活。
- UI 暴露的 SSH 连接状态 MUST 反映真实控制通道健康状态，而不是历史成功状态。
- 当 `odas.command` 使用 wrapper script 时，远程 `stop` MUST 终止被控进程组，而不是仅终止 wrapper 入口 pid。

## Variation Space

- 实例标识 MAY 通过 pid file、显式 state file 或其他可验证控制状态实现。
- 错误暴露 MAY 采用异常、错误对象或状态信号，但语义 MUST 明确。
- 健康状态检测 MAY 通过 shell 存活、控制命令回执或等价机制实现。

## Rationale

- 远程控制的核心不是“能启动”，而是“能可靠识别、能可靠停止、能可靠反映真实状态”。
- 如果监听未就绪即对外宣称已启动，UI 与实际运行状态会发生漂移。
- wrapper script 会遮蔽真实被控进程；若只杀 wrapper，本质上并未完成停止语义。

## Anti-Patterns

- 通过进程名 grep 判断唯一实例。
- 以“曾经连接成功”代替“当前连接健康”。
- 在 socket bind/listen 之前向 UI 报告 stream active。
