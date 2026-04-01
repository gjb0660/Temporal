# AppBridge Source Analysis

## 1. Overview

当前仓库中的 `AppBridge` 呈现“单类聚合多域职责”：

- `src/temporal/app.py` 同时承载 Qt bridge 对外接口、远端控制状态机、流监听生命周期、录音路由、UI 投影刷新与应用启动入口。
- `PreviewBridge` 通过继承 `AppBridge` 复用大量行为，形成 runtime/preview 双路径共享同一核心实现。
- QML 与测试均直接依赖 `temporal.app` 的对外语义，因此该文件的演进会放大跨层耦合与并行冲突概率。

本文件仅记录代码与仓库中的可验证事实，不包含执行决策与重构方案。

## 2. QML Binding Surface

QML 侧当前直接消费以下 bridge 字段与动作：

- 状态属性：`status`、`odasStarting`、`odasRunning`、`streamsActive`、`canToggleStreams`
- 数据模型：`sourceRowsModel`、`sourcePositionsModel`、`elevationSeriesModel`、`azimuthSeriesModel`、`recordingSessionsModel`
- 预览相关：`previewScenarioOptionsModel`、`previewScenarioKey`、`showPreviewScenarioSelector`
- 用户动作 slots：`toggleRemoteOdas()`、`toggleStreams()`、`setSourceSelected()`、`setSourcesEnabled()`、`setPotentialsEnabled()`、`setPotentialEnergyRange()`、`setPreviewScenario()`

绑定点分布在：

- `src/temporal/qml/Main.qml`
- `src/temporal/qml/LeftSidebar.qml`
- `src/temporal/qml/RightSidebar.qml`
- `src/temporal/qml/CenterPane.qml`
- `src/temporal/qml/AppHeader.qml`

## 3. Backend Dependency Surface

`AppBridge` 当前直接依赖并编排以下后端组件：

- 配置层：`load_config()`、`resolve_default_config_path()`
- 远端控制：`RemoteOdasController`
- 本地监听：`OdasClient`
- 录音：`AutoRecorder`
- 投影与解析：`ui_projection.py`、`odas_message_view.py`、`SourceColorAllocator`

核心耦合事实：

- 远端控制与本地监听在 `startRemoteOdas()` 链路上串联。
- SST/SSL 输入会触发 UI 投影刷新，同时驱动录音活跃 source 与会话快照。
- 运行态 chart 时间窗、source 颜色分配与筛选状态都在 bridge 内部维护，属于同一状态面。

补充代码事实（执行路径）：

- listener 线程创建位置在
  `src/temporal/core/network/odas_stream_client.py` 的 `threading.Thread(...)`。
- `OdasClient` 把 `on_sst/on_ssl/on_sep_audio/on_pf_audio` 回调注入 `AppBridge`
  的 `_on_*` 方法（`src/temporal/app.py` 构造器）。
- `AppBridge` 在 `_on_*` 链路与状态更新函数中调用
  `Signal.emit()` 与 `QmlListModel.replace()`。
- `AppBridge` 创建 `QTimer(self)` 并连接 `_poll_remote_log`、
  `_verify_odas_startup` 回调。

## 4. Test Constraints

测试代码中存在以下依赖事实：

- 现有测试广泛 `from temporal.app import AppBridge`。
- 现有测试广泛 patch `temporal.app.load_config`、`temporal.app.OdasClient`、`temporal.app.RemoteOdasController`、`temporal.app.AutoRecorder`。
- `PreviewBridge` 行为测试依赖 `AppBridge` 默认 preview 相关属性与 no-op 语义。

相关测试入口：

- `tests/test_app_bridge_integration.py`
- `tests/test_app_bridge_recording.py`
- `tests/test_preview_bridge.py`
- `tests/test_projection_parity.py`

公开接口引用概览（当前仓库）：

- QML 直接绑定主要集中在 model、状态布尔和控制 slots。
- tests 对 bridge 的直接引用覆盖远端控制状态、模型对象、preview 相关属性。
- `sourceItems/sourcePositions/sourceCount/recordingSessions` 与
  `setStatus/isSourceSelected` 在当前 QML 与 tests 中未发现直接引用。

## 5. Evolution Hotspots

基于 `git log -- src/temporal/app.py` 的近期演化，热点集中在：

- remote lifecycle（启动/停止/失败语义）
- runtime state machine（监听状态、控制通道断连恢复）
- projection parity（runtime/preview 共用投影逻辑）
- recording semantics（采样率识别与 fallback）

文件热点特征：

- 单文件长期作为跨 feature 交汇点。
- 多次提交在同一文件并发叠加，冲突风险高于普通模块。

## 6. Conflict Root Causes

基于当前代码与提交历史，可观察到以下并行冲突触发因素：

- 职责混合：UI 接口层与运行态编排层共处一个实现体。
- 写入面重叠：remote、recording、projection 任一变化都需改 `app.py`。
- 继承耦合：`PreviewBridge` 叠加重写时，容易与 `AppBridge` 同区块冲突。
- 测试 patch 锚点集中：`temporal.app.*` 路径改动会放大回归成本。

## References

- `src/temporal/app.py`
- `src/temporal/core/network/odas_client.py`
- `src/temporal/core/network/odas_stream_client.py`
- `src/temporal/preview_bridge.py`
- `src/temporal/qml/*.qml`
- `specs/contracts/app-bridge.md`
- `specs/contracts/preview-source.md`
- `specs/knowledge/app-bridge-execution-model.md`
- `tests/test_app_bridge_integration.py`
- `tests/test_app_bridge_recording.py`
- `tests/test_preview_bridge.py`
- `tests/test_projection_parity.py`
