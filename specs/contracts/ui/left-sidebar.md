---
title: left-sidebar
status: active
stability: flexible
version: 0.2
---

## Role

定义左侧栏作为远程日志观察与主控制入口。
该 Contract 约束日志区、状态区和两枚主控制按钮的稳定交互语义。

## Invariants

- 左侧栏 MUST 同时包含上方日志区和下方控制区，且日志区 MUST 保持比控制区更高的视觉权重。
- 控制区 MUST 只暴露一枚远程 ODAS 主动作按钮和一枚监听动作按钮；MUST NOT 回退为复杂按钮矩阵。
- 两枚按钮的文字和启用状态 MUST 直接反映 bridge 当前状态；`启动中` 语义 MUST 通过禁用主按钮阻止重复触发。
- 业务动作 MUST 通过 `appBridge.toggleRemoteOdas()` 和 `appBridge.toggleStreams()` 路由；左侧栏 MUST NOT 自行拼接远端状态机或 SSH 控制逻辑。
- 详细日志 MUST 保留在日志区，状态区 MUST 只呈现人类可读摘要；MUST NOT 用原始 shell 细节替代状态说明。
- 日志文本 MUST 支持滚动、换行和复制，以便用户持续观察远端运行反馈。

## Variation Space

- 卡片比例、圆角、阴影和字体 MAY 演进，只要日志区仍然明显大于控制区。
- 按钮文案 MAY 在不破坏启动、停止、监听语义的前提下微调。
- 状态摘要的措辞 MAY 演进，但摘要区与原始日志区的分层 MUST 保持。

## Rationale

- 左侧栏承担的是“先观察、再控制”的入口语义；日志优先于控制可以避免只剩按钮而失去可观测性。
- 将控制状态直接绑定 bridge 真值，可以避免 UI 自建状态机带来的漂移。

## Anti-Patterns

- 在左侧栏中重新实现 SSH、监听或远端进程控制流程。
- 把原始远端错误直接塞进状态摘要区，导致用户无法快速判断当前状态。
- 为局部快捷实现恢复多按钮矩阵或隐藏控制入口。
