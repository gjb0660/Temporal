# Spec: Phase H Preview Filtering and Validation

## Goal

将 preview 模式收口为可重复的 UI 验证入口，
并明确过滤语义、空态语义和监听门控语义，
避免历史上的“取消最后一个勾选后错误显示暂无活动声源”等回归。

## Scope

- 定义 preview 下声源过滤、候选过滤和勾选过滤的职责边界。
- 统一右栏空态、图表空态和 3D 空态的判定方式。
- 将 `temporal-preview` 固化为 preview 手工验收入口。
- 明确逐帧动态 energy 对右栏和筛选逻辑的驱动关系。

## Non-Goals

- 不重做生产态过滤语义。
- 不建设自动截图对比基础设施。
- 不引入新的图表交互特性。
- 不在本阶段覆盖异常预览场景。

## Filter Semantics

- `sourcesEnabled=false`：右栏 row、图表和 3D 全部清空。
- `potentialsEnabled=false`：不应用 energy 范围过滤。
- `potentialsEnabled=true`：`potentialEnergyMin` 和 `potentialEnergyMax`
  作用于当前场景数据。
- 用户勾选通过 `setSourceSelected(sourceId, selected)` 控制，
  仅影响图表和 3D 的可见子集。
- 当最后一个已勾选 source 被取消勾选时：
  - 右栏 row 继续保留
  - 图表与 3D 清空
  - 不触发“暂无活动声源”空态
- 右栏“暂无活动声源”只由全局筛选结果为零决定，
  而不由用户勾选结果决定。
- 右栏 row 的动态数值应以当前 frame 的 `energy` 为准，
  以便测试数值刷新和筛选联动逻辑。

## Filtering Scope

当前 preview 过滤语义覆盖以下区域：

- 右栏 source rows
- 中部俯仰角图
- 中部方位角图
- 3D source positions

其中：

- 全局筛选同时影响右栏 row 集合和可见 source 候选集。
- 勾选筛选只影响图表和 3D 的最终显示集合。
- 图表和 3D 都从 `trackingFrames` 派生，
  不允许分别保留独立过滤逻辑。
- 右栏动态数字、图表和 3D 必须共享同一当前 frame。

## Functional Requirements

1. Preview 继续复用现有右栏过滤控件，不新增页面控件。
2. `toggleStreams()` 可独立启停本地监听，不依赖远端运行状态。
3. `toggleStreams()` 在本地 listener 启动失败时必须吸收异常，
   保持 `streamsActive=false`，并写入明确失败状态文案。
4. `toggleRemoteOdas()` 启动时若本地未监听，必须先补开监听，
   再启动远端 `odaslive`。
5. 主按钮停止时必须按“先停监听，再停远端，不断 SSH”的顺序执行。
6. runtime bridge 必须公开以下运行态观测属性：
   - `odasStarting`
   - `remoteLogLines`
   - `remoteLogText`
7. `remoteLogLines` 为日志真源，
   `remoteLogText` 仅为字符串投影。
8. preview 默认进入静态首帧；监听开启后才推进 sample window
   和 current frame。
9. `advancePreviewTick()` 必须同时更新：
   - `chartXTicksModel`
   - `elevationSeriesModel`
   - `azimuthSeriesModel`
   - `sourcePositionsModel`
   - 右栏当前 frame 动态数值
10. `emptyState` 场景必须使用真实空数据，
   不生成占位 row 或占位点位。
11. runtime bridge 的 `_poll_remote_log()`
   在非启动中状态下必须同步 remote health，
   避免 `odasRunning` 残留为脏状态。
12. runtime bridge 的 startup verify timer
   必须在启动成功、启动失败、SSH 断开和手动停止路径中统一取消。

## Validation Workflow

1. 启动 `uv run temporal-preview`。
2. 依次验证四个基线场景：
   - `referenceSingle`
   - `hemisphereSpread`
   - `equatorBoundary`
   - `emptyState`
3. 对每个非空场景执行以下操作：
   - 观察初始首帧静态画面
   - 点击“监听”，确认图表、右栏动态数值和 3D 同步推进
   - 调整声源勾选，确认右栏 row 不消失
   - 开启候选过滤并调整 energy 范围
   - 单独点击“停止监听”，确认动画暂停但远端状态不被连带停止
4. 执行主按钮启动和停止流程，确认自动补监听与停止顺序正确。

## Quality Requirements

- preview 过滤语义必须明确、可复现、文档化。
- 空态语义必须稳定，避免因局部可见集为空而误触发右栏空态。
- preview 数据可以是固定场景，但页面滚动必须来自 sample window
  在固定帧序列上的滑动窗口推进。
- runtime 状态机必须以单一内部状态为真源，
  不允许通过 `_status` 文案隐式表达中间态。
- 验证流程不得依赖修改 QML 或手动注入 fixture 数据。

## Acceptance Criteria

1. 右栏空态只在全局筛选后 row 数为零时出现。
2. 取消最后一个勾选 source 后，`sourceRowsModel.count` 保持不变。
3. 监听开启后，横轴、图表、右栏动态数值和 3D 同步推进；
   监听关闭后同步暂停。
4. 主按钮启动会自动补开监听，主按钮停止保持先停监听再停远端。
5. `temporal-preview` 可作为标准 preview 验收入口重复执行，
   不需要再修改源代码。
6. runtime 回归中，listener 启动失败不会再继续启动远端，
   且不会向 UI/QML 外抛异常。
