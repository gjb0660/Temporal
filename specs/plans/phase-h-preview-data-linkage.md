# Spec: Phase H Preview Data Linkage

## Goal

收口 preview 的数据主模型，确保右栏、图表和 3D
都消费同一份 bridge 派生结果。
本阶段不再允许图表和 3D 各自维护独立假数据，
也不允许 QML 在本地拼装 preview fallback。

## Scope

- 将 preview 场景主模型收口为 `sources`、`trackingFrames`
  和 `sampleWindow`。
- 保持现有 QML 契约名称不变，由 bridge 输出最终可渲染结果。
- 让右栏 row、图表序列和 3D 点位围绕同一份
  tracking timeline 同步变化。
- 将 `odas_web` 的三条参考结论固化为仓库约束：
  - 图表与 3D 必须共享同一份 tracking 时序源。
  - 勾选只影响可见性，不改写 source row 集合。
  - 主按钮启动时先补监听，再起远端。

## Non-Goals

- 不把 runtime 的 `Tcp*Subscriber`
  重构为 `odas_web` 风格的本地 server/listener 架构。
- 不引入逐帧动态 energy。
- 不处理 source appear/disappear 的复杂生命周期。
- 不改变现有 QML 对外属性名和主页面布局。

## Data Model

每个 preview 场景定义统一数据结构：

- `key`
- `displayName`
- `sources[{id, color, energy}]`
- `trackingFrames[{sample, sources[{id, x, y, z}]}]`
- `sampleWindow{sampleStart, sampleStep, windowSize, tickCount, tickStride,`
  `advancePerTick, timerIntervalMs}`
- 可选 `status`
- 可选 `remoteLogLines`

基线场景保持为：

- `referenceSingle`
- `hemisphereSpread`
- `equatorBoundary`
- `emptyState`

其中：

- `sources` 只承载右栏元数据和筛选条件。
- `trackingFrames` 是图表与 3D 的唯一时序真源。
- `sampleWindow` 决定横轴标签、预览窗口大小和定时推进步长。

## Functional Requirements

1. Preview 场景数据存放在共享 Python 模型中，
   由 `PreviewBridge` 统一消费。
2. `PreviewBridge`
   在不改变现有 QML 属性名的前提下，继续输出：
   - `sourceRowsModel`
   - `sourcePositionsModel`
   - `elevationSeriesModel`
   - `azimuthSeriesModel`
   - `chartXTicksModel`
   - `odasRunning`
   - `streamsActive`
3. `sourceRowsModel` 从 `sources` 派生，
   只表示当前场景在全局筛选后的 row。
4. `sourcePositionsModel`
   从当前 frame 的 `trackingFrames[*].sources` 派生。
5. `elevationSeriesModel` 与 `azimuthSeriesModel`
   从当前 sample window 内的 xyz 序列派生，
   不再维护独立假数据数组。
6. 场景切换后，右栏、图表、3D 和横轴标签
   必须在同一 bridge 刷新周期内同步更新。
7. 新场景切换后，默认重置为
   “该场景的全部 source 已勾选，sample window 回到起点”。
8. preview 默认只渲染首帧静态结果，不自动滚动；
   只有监听开启后才推进。
9. 监听关闭后，preview 停在当前结果；
   再次开启时从场景起点重新开始。

## Rules

- 图表与 3D 必须共享同一 `trackingFrames` 时间窗。
- `checked` 只控制图表和 3D 的可见子集，不删除右栏 row。
- 当最后一个已勾选 source 被取消勾选时，
  `sourceRowsModel.count` 保持不变。
- 右栏空态只在当前场景经过全局筛选后
  确实没有任何 row 时出现。
- `emptyState`
  必须是真正的空数据场景，不生成伪造 row 或伪造点位。
- 俯仰角归一化规则为 `(deg + 90) / 180`。
- 方位角归一化规则为 `(deg + 180) / 360`。
- QML 不根据 `previewMode` 本地推导图表数据、
  横轴 ticks 或 3D fallback 点位。

## Interface Additions

本阶段不新增页面契约名，继续沿用现有 bridge/QML 接口：

- `sourceRowsModel`
- `sourcePositionsModel`
- `elevationSeriesModel`
- `azimuthSeriesModel`
- `chartXTicksModel`
- `odasRunning`
- `streamsActive`

同时明确其语义更新为：

- `toggleRemoteOdas()`
  启动时，若本地未监听，先启动监听，再启动远端 `odaslive`。
- `toggleStreams()` 可独立开启或关闭本地监听，
  不要求远端已运行。
- 主按钮停止时保持“先停监听，再停远端，不断 SSH”的顺序。

生产态 `AppBridge` 继续提供安全默认值：

- preview 相关选项模型为空
- header 导航标签保持 runtime 默认值
- chart x 轴 ticks 保持 runtime 默认值

## Quality Requirements

- preview 派生逻辑必须确定、可重复、与实时 ODAS 消息解耦。
- 场景切换和勾选变化必须是无副作用的纯 bridge 状态变更。
- 图表、3D、右栏和日志文案必须避免再次引入乱码。
- 同一 source id 在右栏 badge、图表曲线和 3D
  点位中的颜色必须保持稳定。

## Acceptance Criteria

1. 右栏 row 来自 `sources`，图表与 3D 来自 `trackingFrames`，
   三者在场景切换和 tick 推进时保持同步。
2. 取消最后一个勾选 source 后，
   右栏 row 继续保留，只让图表和 3D 变空。
3. preview 启动时不再出现 Qt timer 相关告警。
4. 主按钮启动会自动补开监听，
   主按钮停止会先停监听再停远端。
5. `emptyState` 不显示伪造声源行和伪造点位。

## Validation Workflow

- `uv run pyside6-qmllint src/temporal/qml/Main.qml`
- `uv run ruff check src tests`
- `uv run python -m unittest discover -s tests -p "test_*.py" -v`
- 启动 `uv run temporal-preview` 并验证：
  - 初始为首帧静态结果
  - 点击“监听”后图表、横轴和 3D 同步推进
  - 单独点击“停止监听”后动画暂停但远端状态不被强制停止
  - 点击主按钮“启动”会自动补开监听
  - 点击主按钮“停止”会先停监听再停远端
  - `referenceSingle`、`hemisphereSpread`、`equatorBoundary`、
    `emptyState` 均可稳定复现
