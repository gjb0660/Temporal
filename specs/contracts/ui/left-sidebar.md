---
title: left-sidebar
status: active
stability: flexible
version: 0.5
---

## Role

定义左侧栏作为远程日志观察与主控制入口。
该 Contract 约束日志区、单一状态区和两枚主控制按钮的稳定交互语义。

## Invariants

- 左侧栏 MUST 同时包含上方日志区和下方控制区，且日志区 MUST 保持比控制区更高的视觉权重。
- 日志卡片 MUST 保持“标题 + 日志内容 + 底部操作区”三段结构。
- 日志卡片底部操作区 MUST 同时提供“清空录音文件”和“清空日志”入口，且“清空日志”按钮 MUST 位于最右侧。
- 控制区 MUST 只暴露一枚远程 ODAS 主动作按钮和一枚监听动作按钮；MUST NOT 回退为复杂按钮矩阵。
- 两枚按钮的文字和启用状态 MUST 直接反映 bridge 当前状态；`启动中` 语义 MUST 通过禁用主按钮阻止重复触发。
- 业务动作 MUST 通过 `appBridge.toggleRemoteOdas()` 和 `appBridge.toggleStreams()` 路由；左侧栏 MUST NOT 自行拼接远端状态机或 SSH 控制逻辑。
- 控制区 MUST 包含单一状态区；状态区 MUST 绑定 `appBridge.controlSummary`。
- 状态文本 MUST 采用三行固定结构：主状态、数据状态、计数，不追加独立指标区或并列状态区。
- 状态区 MUST 只呈现摘要与计数语义；不用原始 shell 细节替代状态说明。
- 清空日志动作 MUST 通过 `appBridge.clearRemoteLog()` 路由；UI MUST NOT 在远端确认成功前主动清空日志显示。
- 清空录音文件动作 MUST 通过 `appBridge.clearRecordingFiles()` 路由；UI MUST NOT 直接操作录音目录。
- 清空日志成功后，日志区 MUST 回到统一空态占位；MUST NOT 继续展示本地录音采样率 warning。
- 清空日志成功后，日志区 MUST 继续绑定既有轮询投影链路；新增远端日志到达时 MUST 继续刷新显示。
- 日志区 MUST 保留 shell 详细日志。
- 日志文本 MUST 支持滚动、换行和复制，以便用户持续观察远端运行反馈。

## Variation Space

- 卡片比例、圆角、阴影和字体 MAY 演进，只要日志区仍然明显大于控制区。
- 按钮文案 MAY 在不破坏启动、停止、监听语义的前提下微调。
- 底部操作区的按钮数量 MAY 演进，但清空日志入口的“底部右侧”语义 MUST 保持。
- 状态区措辞 MAY 演进，但三行结构与日志区分层 MUST 保持。

## Rationale

- 左侧栏承担的是“先观察、再控制”的入口语义；日志优先于控制可以避免只剩按钮而失去可观测性。
- 将控制状态直接绑定 bridge 真值，可以避免 UI 自建状态机带来的漂移。

## Anti-Patterns

- 在左侧栏中重新实现 SSH、监听或远端进程控制流程。
- 把原始远端错误直接塞进状态摘要区，导致用户无法快速判断当前状态。
- 用额外独立指标区替代三行状态区，破坏单区语义。
- 把 `SST/SSL` 高频事件流水覆盖到主状态行，导致主状态跳变噪声过高。
- 为局部快捷实现恢复多按钮矩阵或隐藏控制入口。
