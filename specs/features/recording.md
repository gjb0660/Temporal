---
title: recording
tracker: primary-feature
status: active
owner: codex/core
updated: 2026-04-20
---

## Goal

建立按声源生命周期自动触发的录音闭环，使 separated 与 post-filtered 流在声源出现和消失时自动启动与停止。

## Non-Goals

- 不负责 SSS 通道路由细节与会话列表可见性。
- 不覆盖云端存储、归档管理或后处理管线。

## Facts

- 录音文件命名必须满足 `ODAS_{source_id}_{timestamp}_{sp|pf}.wav`。
- 录音启停由声源出现、消失与超时状态驱动。
- 录音激活还必须满足 source 具备可路由的 SSS 通道容量。
- 录音 WAV 采样率来自远端 `odas.cfg`：`separated.fS -> sp`，`postfiltered.fS -> pf`。
- 当远端 `fS` 缺失或不可解析时，录音采样率回退到 `16000`，且通过 bridge 透出可见告警。
- 采样率变更仅作用于新建录音会话，不重建当前已打开 writer。
- UI 需要读取录音状态摘要，但不应拥有录音控制真源。

## Decision

- 使用每个 source 的录音状态机作为录音生命周期真源。
- 由 backend 在声源进入活跃态时启动录音，在失活后停止录音。
- 将可路由容量纳入录音激活条件，避免创建永远收不到音频的伪会话。
- 录音采样率由 remote preflight 解析结果驱动，并以 mode 级配置作用于新会话；识别失败时回退 `16000`，但不阻断远端启动与本地录音链路。
- 将 UI 可见状态作为 bridge 投影，而不是额外的控制入口。

## Acceptance

1. 新声源出现时会自动创建对应录音会话。
2. 声源超时或消失后会自动停止录音。
3. 输出 WAV 文件满足既定命名契约，且 WAV header 可被稳定解析。
4. 当 SST 声源数超过可路由容量时，录音激活数量不会超过可接收音频的 source 数。
5. 远端 `separated/postfiltered.fS` 能分别驱动 `sp/pf` WAV header 采样率。
6. 远端 `fS` 缺失或不可解析时回退 `16000` 且有可见告警。
7. 运行中采样率更新仅影响后续新建会话，不打断当前会话。

## Plan

1. 建立 source 生命周期状态机。
2. 接通 WAV 写入与录音摘要投影。
3. 将可路由容量接入录音激活条件。
4. 用测试冻结启停、命名与容量约束契约。

## Progress

- [x] 已建立按 source 驱动的录音状态机。
- [x] 已实现 WAV 文件命名与写入基线。
- [x] 已向 bridge 暴露录音状态摘要。
- [x] 已将可路由容量约束并入录音激活语义。
- [x] 已完成录音采样率自动识别、fallback 告警与新会话生效语义收敛。

## Todo

- [ ] SSS 路由与会话可见性继续由 `routing-session` 承接，不回流 `recording` 主闭环。
