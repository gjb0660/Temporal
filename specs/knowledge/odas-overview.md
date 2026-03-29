# ODAS (Open embeddeD Audition System)

## Overview

ODAS 是一个开源的实时音频处理系统。

它提供以下核心能力：

- 声源定位（sound source localization）
- 声源跟踪（sound source tracking）
- 声源分离（sound source separation）
- 后滤波音频输出（post-filtered audio output）

ODAS 作为外部系统运行，其行为由配置文件定义。

## Key Outputs

ODAS 暴露多种输出类型：

### SSL (Sound Source Localization)

- 表示潜在声源方向（potential sound sources）
- 不具备稳定性（not stable）
- 可能包含噪声或误检（false positives）

### SST (Sound Source Tracking)

- 表示随时间持续跟踪的声源（tracked sources）
- 在帧之间保持稳定标识（stable identifiers）
- 常用于状态推导与可视化输入

### SSS (Sound Source Separation)

包含两种形式：

- separated：原始分离音频
- postfiltered：经过后滤波增强的音频

## Output Characteristics

- 所有输出由配置文件显式定义
- 输出可能通过以下方式传输：
  - sockets（TCP / UDP）
  - 文件（WAV 或流）
- 各输出类型彼此独立

## Config Relationship

- ODAS 行为完全由配置文件决定
- 未在配置中启用的输出不会产生
- 下游系统无法从 ODAS 获取未配置的输出

## Integration Boundary

ODAS 负责：

- 音频处理
- 声源检测与跟踪
- 音频分离

ODAS 不负责：

- UI 渲染
- 业务逻辑
- 录音策略
- 文件命名规则
- 工作流编排

## Interpretation Notes

- SSL 表示“候选感知”，而非稳定实体
- SST 表示“时间连续的跟踪结果”，其业务语义由下游系统决定
- SSS 表示音频信号输出，不包含业务上下文
- 不同输出类型在语义上是分层的

## Non-Goals

本知识文档不定义：

- 集成流程（属于 Skill）
- 不可变约束（属于 Contract）
- 产品行为或策略

## Summary

- ODAS 是外部感知系统，提供 SSL / SST / SSS 三类能力
- 配置文件决定 ODAS 的输出能力范围
- 输出以流或文件形式提供，各类型相互独立
- ODAS 不包含产品语义，业务解释由下游系统决定
- 本文仅描述事实，不定义执行方式或约束规则
