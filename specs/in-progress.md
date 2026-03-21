# In Progress

## Usage

- 开始新特性前先检查此文件。
- 将下方条目视为当前唯一的活动路由与状态来源。
- 只有在外部依赖或缺失输入直接阻断推进时才使用 `blocked`。
- 不要把 `blocked` 条目当作可以直接开工编码的任务。

## Active Features

- Phase H preview model convergence follow-up
  State: specified
  Summary: 基于已落地的 preview 入口、共享 bridge 注入和统一 tracking
  timeline，继续收口逐帧 energy、右栏动态数值，以及 preview/runtime
  规范化数据模型对齐。
  Specs:
  [phase-h-preview-data-linkage.md](./plans/phase-h-preview-data-linkage.md),
  [phase-h-preview-filtering-and-validation.md](./plans/phase-h-preview-filtering-and-validation.md)

- Phase I: 新增测试完整性与可靠性加固计划
  Spec: [phase-i-test-completeness-and-hardening.md](./plans/phase-i-test-completeness-and-hardening.md)

- Remote runtime validation and reconnect hardening
  State: specified
  Summary: 补齐远端 Linux `odaslive` 的端到端验证与重连加固，包括 SSH
  连接、启动/停止生命周期、远端日志跟随、SST/SSL 更新和录音会话可见性。
  Spec: [phase-f-integration-runbook-risks.md](./plans/phase-f-integration-runbook-risks.md)

## Recently Completed (Last 7 Days)

- Phase A: 项目骨架与可运行的 PySide6/QML shell
  Spec: [phase-a-project-skeleton.md](./plans/phase-a-project-skeleton.md)

- Phase B: 完成 SSH 控制与 ODAS 流客户端脚手架，并持续收口远端控制与流监听语义，
  包括修正 listener 方向为 `ODAS -> Temporal`、明确 wildcard bind 默认值、
  收紧 preflight 覆盖、澄清远端 odaslive 与本地 listener 的独立生命周期、
  以及将远端停止语义收紧到 wrapper 启动场景下的受控进程组
  Spec: [phase-b-remote-control-and-streams.md](./plans/phase-b-remote-control-and-streams.md)

- Phase C: 声源列表与筛选联动到 SST/SSL 流状态
  Spec: [phase-c-sources-filters.md](./plans/phase-c-sources-filters.md)

- Phase D: recorder 生命周期、文件名契约与 appBridge 联动基线
  Spec: [phase-d-auto-recording.md](./plans/phase-d-auto-recording.md)

- Phase D extension: SSS 路由与录音会话可见性
  Spec: [phase-d-sss-routing-and-session-visibility.md](./plans/phase-d-sss-routing-and-session-visibility.md)

- Phase F extension: 录音激活逻辑与 channel mapping 对齐
  Spec: [phase-f-channel-cap-alignment.md](./plans/phase-f-channel-cap-alignment.md)

- Phase F: 集成验证、runbook 与风险文档
  Spec: [phase-f-validation-and-delivery.md](./plans/phase-f-validation-and-delivery.md)

- Phase G: 中文 UI 对齐、远端 odaslive 日志面板、3D 声源视图脚手架、
  source sphere 重建、空态清理与默认 Z-up 朝向
  Spec: [phase-g-ui-visual-parity.md](./plans/phase-g-ui-visual-parity.md)

- Phase H preview entry and bridge baseline: 完成 specs 定义、preview
  入口落地、共享 bridge 注入，以及 header/center/sidebar 绑定迁移到
  统一 bridge 契约
  Spec: [phase-h-preview-entry-and-bridge.md](./plans/phase-h-preview-entry-and-bridge.md)

- Phase H preview linkage and workflow baseline: 去除 QML 本地 preview 分支、
  恢复 sidebar 目录集与可见集分离语义、将 timer 启动迁移到安全的应用路径、
  对齐主按钮与 listener 的 runtime 语义，并在共享 `trackingFrames`
  上统一图表与 3D 运动时钟
  Specs:
  [phase-h-preview-data-linkage.md](./plans/phase-h-preview-data-linkage.md),
  [phase-h-preview-filtering-and-validation.md](./plans/phase-h-preview-filtering-and-validation.md)

- Phase E governance refresh: agent 治理文件落地、Pyright 配置与 Facade
  及 namespace package 规则对齐、`specs/in-progress.md`
  成为仅在 handoff 更新的 live board，并完成治理语言归属去重与
  root-cause-first 探索规则收紧
  Spec: [phase-e-agent-governance.md](./plans/phase-e-agent-governance.md)

## Session Lessons

- 在这个 uv 项目里，工具链命令统一通过 `uv run` 执行。
- Python 与 QML 改动先跑 lint，修完问题后再 format。
- 实现与对应测试保持在同一个原子提交里。
- Preview 工作流应使用独立的应用入口，而不是复用本地 QML 开关。
- Preview 可以继续使用稳定演示数据，但数据 schema 应逐步向
  真实 runtime 的统一规范模型收口，而不是长期保留 preview-only 结构。
- Preview 右栏数字应逐步改成逐帧驱动，而不是长期停留在静态 metadata，
  这样 UI 刷新逻辑才能与图表和 3D 共用同一时间线验证。
- Specs 与 handoff 文档保持英文标题、中文正文。
- 处理 root-cause 修复请求时，先澄清再推进，不要在关键前提未明确时自行假设。
- 对远端 ODAS 接入来说，wildcard bind（`0.0.0.0`）只是 bind 侧默认值，
  不能在 preflight 检查里当作远端 sink host 字面值使用。
- 对 ODAS 控制交互来说，SSH、远端 odaslive 与本地 listener 的生命周期要显式区分：
  SSH 只在远端启动时惰性连接，listener 是独立资源，停止监听不应隐含停止远端
  odaslive 或断开 SSH。
- 当远端 ODAS 通过 wrapper 脚本启动时，停止语义必须作用于整个受控进程组；
  只杀 wrapper pid 不足以完成真正的远端停机。
- UI 中 listener 按钮的可用态必须反映实时的 SSH 控制通道健康状态，
  而不能只依赖“曾经连接成功过”的陈旧状态。
