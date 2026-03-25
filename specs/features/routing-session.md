---
title: routing-session
tracker: primary-feature
status: active
owner: codex/core
updated: 2026-03-26
---

## Goal

补齐 SSS 音频路由与会话暴露闭环，使分离流与后滤流能稳定写入录音器，并向 UI 暴露可读的录音会话状态。

## Non-Goals

- 不扩展动态声道协商。
- 不改造录音管理窗口或上层管理界面。

## Facts

- 分离流与后滤流需要分别路由到 `sp` 与 `pf` 模式。
- channel mapping 需要在 SST 更新中保持稳定。
- UI 需要读取活动录音会话列表，用于确认当前录音可见性。
- 录音激活的容量约束由 `recording` 拥有，本文件只拥有路由与会话暴露语义。

## Decision

- 保持 source_id 到 channel_index 的稳定映射作为路由真源。
- 将 SSS separated 与 post-filtered 写入路径分别绑定到对应 recorder mode。
- 通过 bridge 暴露 `recordingSessions`，但不将 UI 变成会话 owner。

## Acceptance

1. 分离流和后滤流的 PCM 数据都能写入对应录音会话。
2. UI 可以读取当前活动录音会话列表。
3. 停止监听后，录音数量与会话列表会同步清空。

## Plan

1. 打通 SSS 到 recorder 的分流写入路径。
2. 固化 channel mapping 复用与清理规则。
3. 验证 bridge 会话快照与监听停止行为。

## Progress

- [x] 已打通 separated 与 post-filtered 路由写入。
- [x] 已固化 channel mapping 稳定性。
- [x] 已向 bridge 暴露活动录音会话可见性。

## Todo

- [ ] 若后续引入动态通道协商，应作为新 feature 单独定义，不回流本文件扩 scope。
