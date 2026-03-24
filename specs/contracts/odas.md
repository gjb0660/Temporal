---
title: odas
scope: api
stability: strict
version: 0.1
---

## Role

本契约定义 ODAS 作为外部音频感知子系统时的**不可破坏集成边界约束**。

该契约约束 ODAS 输出与系统下游解释之间的边界关系，
不定义产品工作流、UI 行为或具体功能交付步骤。

## Invariants

- ODAS MUST 被视为感知信号的外部生产者，而不是产品级业务语义的拥有者。
- 集成边界 MUST 保持以下语义的明确区分：
  - localization candidates（定位候选）
  - tracked sources（跟踪源）
  - separated audio streams（分离音频流）
- Socket 输出 MUST 被视为连续字节流，而不是基于消息边界的读取。
- 解析层 MUST 满足传输安全性：
  - MUST 正确处理拼接的 payload（concatenated payloads）
  - MUST 正确处理分片的 payload（fragmented payloads）
- 下游生命周期语义 MUST 由宿主系统定义，MUST NOT 从 ODAS 原始字段中隐式推断。
- ODAS 配置文件 MUST 作为 enabled sinks、endpoint targets 和传输行为的单一真源（SSOT）。
- 解析层 MUST 保持轻语义（interpretation-light），MUST NOT 嵌入产品策略。
- 集成逻辑 MUST 能容忍缺失、非激活或占位型 source 条目，而不破坏语义分层。
- ODAS 集成边界 MUST 保持可替换性，下游模块 MUST 依赖内部稳定抽象，而不是直接依赖 ODAS payload 结构。
- 基于该边界派生的其他契约 MUST NOT 假设 UI、存储、录音或编排行为，除非这些行为在独立契约中明确定义。

## Variation Space

- 系统 MAY 选择不同的内部抽象模型来表示 ODAS 输出，只要语义分层保持不变。
- 系统 MAY 将原始 ODAS payload 转换为标准化内部模型，但 MUST NOT 在传输/解析边界中隐式引入产品语义。
- buffering、framing、retry、reconnection 和 backpressure 策略 MAY 自由实现，但 MUST 保证流安全与语义正确性。
- 系统 MAY 支持 ODAS 输出类型的任意子集，但 MUST 对未支持的类型显式失败，而不是静默误读。
- 下游生命周期策略、阈值、录音规则与可视化方式 MAY 自由变化，但 MUST 在本契约之外定义。
- 部署形态 MAY 变化：
  - 本地进程
  - 容器化
  - 远程进程
  前提是集成边界始终保持传输正确性与配置驱动。

## Rationale

- ODAS 提供的是感知信号，而产品语义属于宿主系统；混合两者会导致耦合和不稳定行为。
- 流式传输正确性是基础前提；一旦 framing 错误，上层所有解释都会失真。
- 语义分层可以避免将 localization、tracking 与 audio 错误混用。
- 将策略排除在解析层之外，可以保证系统的可替换性、可审计性与可测试性。
- 以配置作为传输真源，可以避免运行时行为与配置预期发生隐式漂移。

## Anti-Patterns

- 将一次 socket read 当作一条完整消息。
- 在没有下游契约的情况下，将 ODAS 的 source id 或 activity 字段视为业务真值。
- 将 localization、tracking 与 audio separation 混为单一 source 模型。
- 在 ODAS 解析层中嵌入录音、UI 或工作流策略。
- 在 ODAS 配置之外硬编码 endpoint、sink 或输出假设。
- 下游模块直接依赖 ODAS 原始 payload 结构，而不通过内部抽象层。
