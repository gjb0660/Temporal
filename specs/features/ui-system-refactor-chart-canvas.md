---
title: ui-system-refactor-chart-canvas
tracker: refactor
status: exploring
owner: codex/ui
updated: 2026-04-01
---

## Goal

重写 `ChartCanvas`，并显式移除 chart 子系统的历史兼容包袱。
以第一性原理收敛“时间窗语义、颜色语义、缺口语义、渲染职责边界”，
形成可直接验收的零兼容实现基线。

## Non-Goals

- 不在本执行单元引入缩放、平移、悬停分析等交互能力。
- 不在本执行单元扩展 potential 点云图层或新增第三张图。
- 不重构 `SourceSphereView`、左/右侧边栏或录音链路。
- 不改变 `specs/contracts/ui/chart-canvas.md` 已冻结的只读趋势图契约。

## Facts

- `specs/contracts/ui/chart-canvas.md` 已冻结图表不变量：双轴趋势图、空网格安全、
  source 颜色一致、只读语义、`0.01s` 横轴、`1600` 固定窗口与 `200` 主刻度。
- 当前 `ChartCanvas.qml` 在 `onPaint` 内解析 `valuesJson`，渲染层承担数据解码职责。
- 当前 shared projection `build_chart_series(...)` 对 source 缺帧不补位；
  series 长度由“出现过多少帧”决定，而非“窗口帧长度”决定。
- `odas_web` 的 `graph.js` 在 source inactive 时写入 `y: null`，
  其语义是“保留时间轴位置并显示断点”。
- runtime 与 preview 当前已经共享 `ui_projection` 路径，
  可作为单一路径收敛新输入契约。
- 本次先完成了 `specs/knowledge/references/odas-web-chart-canvas-analysis.md`，
  明确了可迁移事实与边界。
- 当前实现方案参数已经锁定：backend 为 `QtCharts`、scope 为 tracked-only 双图、
  source scale 上限 `<=8`、刷新节流固定 `20 FPS`。
- 窗口与刻度参数已经锁定：滚动窗区间 `[latest-1600, latest]`，负刻度可见，
  且窗口内所有 `sample % 200 == 0` 的刻度均需绘制刻度线与标签。
- 实际会话观测显示同一说话人连续发言时可能触发 `sourceId` 递增，
  `sourceId` 不再适合作为颜色身份主键。
- 当前 `ui-system` 是展示语义 owner，`preview-mode` 只应适配共享展示语义，
  不应反向约束 `ui-system` 的设计收敛。
- 苏格拉底式假设挑战 1：我们真正要保护的是“视觉像旧版”，
  还是“行为语义可验证且可长期演进”？
- 苏格拉底式假设挑战 2：让 QML 解析业务 JSON 是否真是最简方案，
  还是把复杂度错误放在了最难测的层？
- 苏格拉底式假设挑战 3：source 缺帧时自动压缩为连续线，
  是否掩盖了真实数据不连续性？

## Decision

- 采用奥卡姆剃刀：`ChartCanvas` 仅负责绘制，不再承担业务推导或 JSON 解码。
- 渲染后端采用 `QtCharts`，并保持 tracked-only 双图（elevation / azimuth）。
- 建立单一输入契约：bridge/projection 输出“已对齐时间窗”的结构化点列，
  其中 `x` 为数值 sample，`y` 为角度值，缺帧以可空值表达 gap；
  不再保留 `valuesJson + chartXTicksModel(string)` 旧接口形状。
- 新接口命名固定为：
  `chartWindowModel`、`elevationChartSeriesModel`、`azimuthChartSeriesModel`。
- 缺帧表达显式化：source 在某窗口帧无数据时，必须以 gap 语义传递到渲染层，
  并通过分段折线保持断点可见，不允许静默索引压缩或跨 gap 连线。
- 刷新采用固定 `20 FPS` 节流；source 并发展示能力按 `<=8` 路收口。
- source 超过 8 路时，先执行 Top8 选择，再应用勾选过滤：
  Top8 规则为“空间目标最近出现时间降序”，并列按当前帧 `sourceId` 升序。
- X 轴窗口采用硬约束：固定长度 `1600`，滚动区间 `[latest-1600, latest]`，
  负刻度必须显示，且窗口内所有 `200` 整除刻度都要绘制刻度线与标签。
- latest 刻度必须始终标注；当 latest 本身可被 `200` 整除时，禁止重复刻度线/标签。
- 颜色语义采用“空间目标连续映射 + 分配池分配”：
  单连接会话内同一空间目标颜色稳定；重连后全量重置映射。
- 空间目标关联算法固定为：方位角 + 仰角 + 最近时间特征，
  全局最小角距匹配，角距阈值 `<=20°`，连续性窗口 `2` 秒。
- 颜色分配策略固定为：匹配成功继承历史颜色；
  无匹配新目标优先复用释放池，否则按固定调色池顺序分配颜色。
- 默认配置要求调色池长度覆盖可见上限（`>=8`）；
  若异常配置导致颜色槽位不足，先执行 Top8 选择再进行颜色分配，
  槽位耗尽后可丢弃超限目标并发出告警。
- 颜色分配只依赖“空间目标映射 + 分配序号”，不依赖 `sourceId` 数值范围。
- `preview-mode` 必须适配 `ui-system` 的共享展示语义：
  移除 `sampleWindow.tickCount/windowSize/tickStride` 对 chart 语义的配置入口。
- 缺失 `timeStamp` 的帧视为无效帧并直接丢弃：
  不入窗口、不推进 sample、不更新 latest，且不保留 sample fallback 兼容路径。
- 视觉风格以 `odas_web` 为基线，优先保证趋势可读性与状态稳定感。
- 保持 contract 行为边界不变：不新增交互，不改变双图结构，不改变时钟语义。
- runtime 与 preview 同步切换到同一新契约，禁止并行双轨实现。

## Acceptance

1. 新 `ChartCanvas` 不再在 `onPaint` 中解析 `valuesJson`，渲染输入为直接可绘制结构。
2. 同一时间窗内，points 必须与窗口帧长度对齐；
   不要求与 ticks 同长度，source 缺帧时可观察到 gap，而非线段压缩。
3. 颜色语义继续由 bridge 单一路径输出，row/3D/chart 保持一致。
4. `0.01s`、固定 `1600` 滚动窗口、`200` 整除主刻度、latest 去重标注、
   重连归零语义全部保持不变。
5. runtime 与 preview 对同一场景输入的 chart 行为保持 parity。
6. 相关单元测试覆盖新契约边界，且现有 chart 行为回归测试通过。
7. `latest=350` 时窗口含负刻度，`...,-200,0,200` 的刻度线与标签可见。
8. `latest=1660` 时窗口覆盖多个 `200` 整除点，主刻度完整可见。
9. `latest=1600` 时 latest 与主刻度重合，不出现重复刻度线或重复标签。
10. source 缺帧场景中折线断点可见，不跨 gap 连线。
11. 单连接会话内同一空间目标颜色保持稳定，且当前可见 `<=8` 路不撞色。
12. 默认配置下可见 `<=8` 路颜色槽位充足且映射稳定；
    异常小调色池配置下先执行 Top8，再在槽位耗尽时丢弃超限目标并发出告警。
13. source 超过 8 路时，按“空间目标最近出现时间降序 + 当前帧 `sourceId` 升序平局”选前 8。
14. `preview-mode` 不再通过 `sampleWindow.tickCount/windowSize/tickStride` 配置 chart 语义，
    且其展示语义与 `ui-system` 保持一致。
15. 缺失 `timeStamp` 帧不会触发 chart sample fallback 递增。
16. 连续讲话导致 `sourceId` 变化时，若空间目标匹配仍成立，颜色保持不变。
17. 目标静默时间 `<=2.0` 秒后恢复时优先复用原颜色；
    超过 `2.0` 秒窗口时允许复用原色或分配新色。

## Plan

1. 定义并冻结 ChartCanvas 新输入契约（含 gap 表达、长度对齐规则）。
2. 重构 shared projection 与 bridge 输出，移除渲染层 JSON 解码依赖。
3. 迁移 `ChartCanvas` 到 `QtCharts` 并落地分段折线 gap 渲染。
4. 重写 `src/temporal/qml/ChartCanvas.qml`，仅保留绘制职责与 `20 FPS` 节流刷新。
5. 校验 `CenterPane.qml` 绑定与 contract 一致性，避免行为漂移。
6. 增补/调整测试，冻结以下场景：`latest=350`、`latest=1660`、
   `latest=1600` 去重、source gap 断点与 runtime/preview parity。
7. 将颜色映射、Top8 选择、无 `timeStamp` 处理改为零兼容行为，
   并删除旧接口形状相关断言。
8. 增加空间目标连续映射测试：分段讲话换 `sourceId` 保色、
   双目标交错不串色、静默窗口内外恢复策略。

## Progress

- [x] 已完成 `odas_web` 图表实现调研并提取可迁移事实。
- [x] 已完成第一性原理与奥卡姆剃刀约束收敛。
- [x] 已将“假设挑战”落入本 feature 的 Facts 与 Decision。
- [ ] 尚未进入代码实现阶段。

## Todo

- [ ] 在实现前补充一份最小输入契约示例（含正常帧、缺帧、重连归零三组样例）。
- [ ] 在进入编码前对照 `specs/contracts/ui/chart-canvas.md` 做一次逐条不变量复核。
