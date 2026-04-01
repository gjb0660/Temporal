---
title: ui-system-refactor-chart-canvas
tracker: refactor
status: active
owner: codex/ui
updated: 2026-04-02
---

## Goal

锁定 chart 后端技术路线，先用第一性原理定义“必须成立的稳定性与语义目标”，
再用奥卡姆剃刀收敛到最小可持续方案：
长期目标态为 `QtGraphs`，短期过渡态为 `Canvas`（仅风险控制用途），
并禁用 `QtCharts`。

## Non-Goals

- 不在本执行单元引入缩放、平移、悬停分析等交互能力。
- 不在本执行单元扩展 potential 点云图层或新增第三张图。
- 不重构 `SourceSphereView`、左/右侧边栏或录音链路。
- 不改变 `specs/contracts/ui/chart-canvas.md` 已冻结的只读趋势图契约。

## Facts

- `specs/contracts/ui/chart-canvas.md` 已冻结图表不变量：双轴趋势图、空网格安全、
  source 颜色一致、只读语义、`0.01s` 横轴、`1600` 固定窗口与 `200` 主刻度。
- Qt 官方文档已标注：`Qt Charts` 自 Qt 6.10 起 deprecated，
  新项目建议使用 `Qt Graphs`。
- Qt 官方文档已标注：使用 `Qt Charts` 的 Qt Quick 工程，
  需将默认 `QGuiApplication` 替换为 `QApplication`。
- 当前仓库入口仍使用 `QGuiApplication`：
  `src/temporal/main.py` 与 `src/temporal/app.py` 均以 `QGuiApplication` 启动。
- 2026-04-02 本地复现实验（Windows + PySide6 6.8.3 + offscreen）显示：
  以 `QGuiApplication` 加载 `Main.qml` 可复现 `access violation`（exit `-1073741819`）；
  切换为 `QApplication` 后同路径可正常完成加载（roots=`1`，exit=`0`）。
- Qt 官方 Canvas 文档明确提示：
  对 `Canvas.Image` 路径，应避免大画布、频繁更新与动画；
  并建议优先考虑 `QQuickPaintedItem`（C++/QPainter）而非 JS/Context2D。
- Qt Graphs 迁移文档明确存在 6.8 代际差异；
  其列出的缺口（如标题/图例等）需逐项比对当前 contract 是否依赖。
- 当前 chart contract 语义以趋势折线与固定时间窗为核心，
  不依赖 `QtCharts` 特有的 widget 体系或高级交互语义。
- 当前实现事实是 `ChartCanvas.qml` 使用 `Canvas/onPaint`，
  且横轴网格与标签仍按“刻度索引等分”绘制，而非按 sample 值映射。
- 当前已观测到 3 个回归风险：
  1) 刻度与折线缺少“画卷式”左移效果；
  2) `latest` 非 200 整除时，左侧点位可能出现越界；
  3) preview 固定 200 sample 步长会掩盖非整除边界问题。
- 当前仓库版本窗口为 `PySide6 6.8.x`（当前锁定 `6.8.3`）。
- 苏格拉底式假设挑战 1：我们要优化的是“现在看起来可用”，
  还是“跨版本仍可验证并可维护”？
- 苏格拉底式假设挑战 2：若一阶问题是启动崩溃前提，
  是否应先消除该前提，再讨论后端美学偏好？
- 苏格拉底式假设挑战 3：在禁用 `QtCharts` 的前提下，
  我们是否接受 `Canvas` 仅作为短期过渡并承担可控性能约束？

## Decision

- 采用奥卡姆剃刀：`ChartCanvas` 仅负责绘制，不再承担业务推导或 JSON 解码。
- 路线三元锁定：
  目标态为 `QtGraphs`，过渡态为 `Canvas`（仅风险控制用途），
  禁止态为 `QtCharts`。
- 过渡态前置条件（必须先满足）：
  启动路径必须移除 `QtCharts` 运行依赖，不得保留
  `QGuiApplication + QtCharts` 崩溃链路。
- 过渡态使用边界：
  `Canvas` 仅作为短期风险缓冲，继续执行固定窗口、固定主刻度、
  `<=8` 可见序列与节流刷新约束，不在过渡期扩展交互能力。
- 在 `Canvas` 过渡态下，横轴实现语义进一步冻结：
  点与刻度共享窗口域 `[latest-1600, latest]` 映射，
  禁止以刻度索引等分替代 sample 值映射。
- preview 时钟语义冻结为 `sampleStride=19` 与 `timerIntervalMs=190`；
  场景数据移除 `sampleWindow` 配置入口，帧可循环但 `timeStamp` 不回跳。
- 输入契约去兼容化：
  图表渲染仅消费 `points`，不再保留 `values` 回退路径。
- 目标态切换触发条件（全部满足才可移除过渡态）：
  1) 版本窗口允许进入 Qt 6.10+ 策略；
  2) `QtGraphs` 路径通过 chart contract 全量语义回归；
  3) runtime/preview parity 回归通过。
- `QtCharts` 禁用策略固定：
  过渡与目标阶段均不得恢复 `QtCharts` 依赖，除非明确开启新一轮 spec 决策。
- 继续保持共享输入契约与语义边界不变：
  `chartWindowModel`、`elevationChartSeriesModel`、`azimuthChartSeriesModel`、
  gap 断点、固定窗口与 Top8 颜色语义保持冻结。

## Acceptance

1. 本 feature 的 Facts 明确记录官方弃用事实、迁移事实与本地崩溃复现实验，
   且包含具体日期与环境前提。
2. 本 feature 的 Decision 明确写出“目标态/过渡态/禁止态”三元路线，
   结论为“目标 `QtGraphs`，过渡 `Canvas`，禁用 `QtCharts`”。
3. 过渡态前置条件在 spec 中可验证：必须先消除当前可复现崩溃前提，
   不得继续接受 `QGuiApplication + QtCharts` 路径或 `QtCharts` 运行依赖。
4. 过渡态退出条件在 spec 中可验证：版本窗口、contract 语义回归、
   runtime/preview parity 三项全部满足后才允许移除过渡态。
5. chart contract 核心语义保持不变：时间窗、gap、颜色一致性与只读边界不退化。
6. `ui-system` 上层 owner spec 与本 feature 结论一致，不出现“QtCharts 可用”冲突表述。
7. 存在一份知识归档文档，记录三路对比矩阵、证据来源与结论边界，
   可供后续实现阶段直接引用。
8. 后续实现预置验收已写入本 feature：
   迁移完成前启动路径不再触发当前崩溃前提；
   迁移后保持 chart contract 与 runtime/preview parity 通过。
9. `latest=1661`（非 200 整除）场景下，图表左侧点位不越界，
   刻度线/标签与折线随时间保持同速左移。
10. preview 运行时满足固定质数步长（19）与 190ms 推进；
    数据循环时 `timeStamp` 仍单调递增。

## Plan

1. 更新本 feature 的 Facts/Decision/Acceptance，完成后端路线锁定。
2. 新增调查知识归档，固化官方证据与本地复现实验。
3. 对齐 `ui-system` owner 规范，确保上层语义与本 feature 一致。
4. 复核 `chart-canvas` contract 是否冲突；若无冲突保持 contract 后端无关。
5. 为后续代码阶段预置迁移门槛与回归门槛，避免再次出现路线摇摆。

## Progress

- [x] 已完成 `QtCharts vs QtGraphs vs Canvas` 官方资料与本地实验调查。
- [x] 已将第一性原理、奥卡姆剃刀与苏格拉底假设挑战写入 Facts/Decision。
- [x] 已在本 feature 锁定“目标态/过渡态/禁止态”路线结论。
- [x] 已定义过渡态前置条件与退出触发条件。

## Todo

- [ ] 进入代码阶段前，把“启动路径崩溃前提消除”拆成独立执行子任务并补充回归测试。
- [ ] 进入迁移阶段前，逐条映射 `QtGraphs` 在目标版本下的 contract 覆盖率与差异处理策略。
- [ ] 过渡 `Canvas` 阶段补充高频刷新边界验证，避免性能风险突破既定上限。

## Assumptions

- 版本窗口短期维持 `PySide6 6.8.x`。
- `QtCharts` 在当前路线中被禁用，不作为过渡态或长期路线。
- `Canvas` 仅作为短期过渡态；进入目标态后不保留并行双轨。
