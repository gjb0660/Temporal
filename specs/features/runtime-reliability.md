---
title: runtime-reliability
tracker: feature
status: exploring
owner: copilot
updated: 2026-03-26
---

## Goal

收敛运行时中的高风险可靠性缺口，使远端控制、监听启动、过滤联动与录音路由由行为级测试与可重复验证保护，而不是停留在局部 happy-path。

## Non-Goals

- 不替换现有测试框架。
- 不借可靠性名义重构整个运行时架构。

## Facts

- 纯解析与基础录音测试相对充分，但关键状态机与负路径覆盖仍不完整。
- listener 启动、远端启动校验、过滤联动与 shell 语义属于高风险边界。
- 本地质量门禁与运行文档仍需持续对齐当前系统事实。

## Decision

- 以行为级测试优先，冻结异步、shell、生命周期与 UI 可见状态的真实契约。
- 优先补齐 public slot、listener startup、remote startup、config 负路径与音频边界测试。
- 让 targeted unittest、静态检查与运行验证共同构成 reliability 收口路径，而不是再维持独立 delivery feature。

## Acceptance

1. 远端控制相关 public slot 同时拥有成功与失败路径测试。
2. listener bind 失败与远端启动失败不会再被错误上报为成功状态。
3. 过滤、路由与配置负路径有稳定测试保护。
4. 可靠性验证不会破坏既有 parser 与 recorder 基线。

## Plan

1. 为高风险契约补 red tests。
2. 以最小修复收敛失败路径与状态机缺口。
3. 运行 targeted unittest 与本地质量门禁，并确认行为回归受控。

## Progress

- [x] 已明确高风险测试缺口与目标覆盖面。
- [ ] 仍需补齐 AppBridge、listener、remote shell 与 filtering 的行为级测试。
- [ ] 仍需完成 targeted unittest、静态检查与残余风险记录。

## Todo

- [ ] 若发现无法在本轮关闭的缺口，必须显式登记为 deferred risk，而不是继续隐含存在。
