---
title: recording-sample-rate-mismatch
tracker: bugfix
status: done
owner: codex/core
updated: 2026-04-01
---

## Goal

修复录音 WAV 采样率固定为 `16000` 的偏差，使录音采样率自动跟随远端 `odas.cfg`
中的 `separated.fS` 与 `postfiltered.fS`。

## Non-Goals

- 不改变录音生命周期语义（source 驱动启停）。
- 不改变录音文件命名规则。
- 不改变 SSS 路由容量与通道映射策略。

## Facts

- 当前 `AutoRecorder` 在 writer 初始化时固定 `setframerate(16000)`。
- 远端启动 preflight 已能读取并解析远端 `odas.cfg`。
- 运行时 `sp/pf` 录音分别对应 `separated/postfiltered` 两类输出。
- 本次修复必须保持运行可用：采样率识别失败时仍可录音。
- 录音主 feature 由 `recording` 定义，生命周期约束由
  `contracts/recording-lifecycle` 定义。

## Decision

- 在 remote preflight 阶段解析 `separated.fS` 与 `postfiltered.fS` 并缓存结果。
- 将采样率识别结果通过只读接口暴露给 bridge，再传递给 recorder。
- 识别失败时回退 `16000`，并输出用户可见告警，不阻断启动流程。
- 新采样率仅作用于后续新建录音会话，不重建已有 writer。

## Acceptance

1. 远端 cfg 中 `separated.fS/postfiltered.fS` 可分别驱动 `sp/pf` WAV header 采样率。
2. 当 `fS` 缺失或无法解析时，录音仍可进行，且 WAV 采样率回退到 `16000`。
3. fallback 场景存在用户可见告警信息。
4. 运行中更新采样率配置不会打断当前会话，仅影响后续新会话。

## Plan

1. 扩展 remote preflight 的 cfg 解析，提取并缓存录音采样率与 warning。
2. 扩展 recorder 为 mode 级采样率配置，并在新建 writer 时应用。
3. 在 bridge 的远端启动链路应用采样率配置并透出 fallback 告警。
4. 补充 recorder / remote / bridge 测试并回归全量门禁。

## Progress

- [x] 已确认固定 `16000` 的代码位置与影响路径。
- [x] 已确认远端 cfg 读取路径可复用到采样率识别。
- [x] 已完成 remote/recorder/bridge 收敛并通过回归门禁。

## Todo

- [ ] 后续可考虑把采样率与声道数一起纳入录音元数据观测。
