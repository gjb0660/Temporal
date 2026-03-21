# Spec: Phase H Preview Data Linkage

## Goal

收口 preview 的数据主模型，确保右栏、图表和 3D
都消费同一份标准化 tracking 数据，而不是各自维护独立假数据。
本阶段的目标是先把 preview 打造成稳定演示入口，
同时提前与真实运行时的数据模型方向对齐。

## Scope

- 将 preview 场景主模型收口为 `sources`、`trackingFrames`
  和 `sampleWindow`。
- 保持现有 QML 契约名称不变，由 bridge 输出最终可渲染结果。
- 让右栏 row、图表序列和 3D 点位围绕同一份
  tracking timeline 同步变化。
- 将以下结论固化为仓库约束：
  - 图表与 3D 必须共享同一份 tracking 时序源。
  - 勾选只影响可见性，不改写 source row 集合。
  - 主按钮启动时先补监听，再起远端。
- 为下一阶段与真实运行时彻底统一模型预留结构，
  包括逐帧动态 energy。

## Non-Goals

- 不把 runtime 的 `Tcp*Subscriber`
  重构为本地 server/listener 传输架构。
- 不覆盖异常场景，例如丢帧、source 消失重现、ID 跳变。
- 不改变现有 QML 对外属性名和主页面布局。
- 不在本阶段引入真实录包回放。

## Data Model

每个 preview 场景定义统一数据结构：

- `key`
- `displayName`
- `sources[{id, color}]`
- `trackingFrames[{sample, sources[{id, x, y, z, energy}]}]`
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

- `sources` 负责右栏稳定 row 的元数据，
  不再承载用于图表和 3D 的时序值。
- `trackingFrames` 是图表、3D 和右栏动态数值的唯一时序真源。
- `sampleWindow` 决定横轴标签、预览窗口大小和定时推进步长。
- `energy` 需要进入逐帧 `trackingFrames[*].sources[*]`，
  用于驱动右栏数值、筛选逻辑和界面回归测试。

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
   表示当前场景经全局筛选后的稳定 row 集合。
4. `sourceRowsModel` 中 row 的右侧动态数值
   必须从当前 frame 对应 source 的 `energy` 刷新，
   而不是长期停留在静态 metadata。
5. `sourcePositionsModel`
   从当前 frame 的 `trackingFrames[*].sources` 派生。
6. `elevationSeriesModel` 与 `azimuthSeriesModel`
   从当前 sample window 内的 xyz 序列派生，
   不再维护独立假数据数组。
7. 场景切换后，右栏、图表、3D 和横轴标签
   必须在同一 bridge 刷新周期内同步更新。
8. 新场景切换后，默认重置为
   “该场景的全部 source 已勾选，sample window 回到起点”。
9. preview 默认只渲染首帧静态结果，不自动滚动；
   只有监听开启后才推进。
10. 监听关闭后，preview 停在当前结果；
    再次开启时从场景起点重新开始。

## Rules

- 图表与 3D 必须共享同一 `trackingFrames` 时间窗。
- 右栏动态数值与图表/3D 当前帧必须来自同一 frame。
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
  横轴 ticks、动态 energy 或 3D fallback 点位。
- preview 数据可以是稳定演示数据，
  但结构必须朝真实运行时统一模型收口。

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
- preview 现在优先保证 UI 和状态机一致性，
  不追求模拟异常链路。
- 图表、3D、右栏和日志文案必须避免再次引入乱码。
- 同一 source id 在右栏 badge、图表曲线和 3D
  点位中的颜色必须保持稳定。

## Acceptance Criteria

1. 右栏 row 来自 `sources`，图表与 3D 来自 `trackingFrames`，
   三者在场景切换和 tick 推进时保持同步。
2. 右栏显示的动态数值会随当前 frame 变化，
   不再只显示静态 energy。
3. 取消最后一个勾选 source 后，
   右栏 row 继续保留，只让图表和 3D 变空。
4. preview 启动时不再出现 Qt timer 相关告警。
5. 主按钮启动会自动补开监听，
   主按钮停止会先停监听再停远端。
6. `emptyState` 不显示伪造声源行和伪造点位。

## Validation Workflow

- `uv run pyside6-qmllint src/temporal/qml/Main.qml`
- `uv run ruff check src tests`
- `uv run python -m unittest discover -s tests -p "test_*.py" -v`
- 启动 `uv run temporal-preview` 并验证：
  - 初始为首帧静态结果
  - 点击“监听”后图表、横轴、右栏动态数值和 3D 同步推进
  - 单独点击“停止监听”后动画暂停但远端状态不被强制停止
  - 点击主按钮“启动”会自动补开监听
  - 点击主按钮“停止”会先停监听再停远端
  - `referenceSingle`、`hemisphereSpread`、`equatorBoundary`、
    `emptyState` 均可稳定复现
