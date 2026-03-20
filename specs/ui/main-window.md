# Spec: Main Window

## Goal

定义 `src/temporal/qml/Main.qml` 的主窗口需求。该窗口是实时数据应用的页面级外
壳，负责主题、布局和顶层组件组装，并通过 `appBridge` 统一承接正式态和预览态
数据。

## Component Responsibility

- 作为应用主窗口外壳。
- 定义共享主题 token 并透传给子组件。
- 组装左侧栏、中栏和右侧栏。
- 将 `appBridge` 的顶层数据直接绑定到各区域组件。

## Data Contract

### Inputs

- `appBridge.sourcePositions`
- `appBridge.sourceRows`
- `appBridge.recordingSessions`
- `appBridge.previewMode`
- `appBridge.previewScenarioKey`

### Rules

- 主窗口不再在本地 QML 中组装 `sourceRows()`。
- 右栏数据直接来自 `appBridge.sourceRows`。
- 中栏预览状态直接来自 `appBridge.previewMode` 和
  `appBridge.previewScenarioKey`。
- 页面本身不直接实现后端业务逻辑。

## Visual Requirements

- 默认窗口尺寸为 `1188x794`。
- 最小窗口尺寸为 `940x640`。
- 页面保持三栏布局：
  - 左栏为日志和 ODAS 控制
  - 中栏为图表和声源球
  - 右栏为声源、筛选器和录音会话

## Interaction Requirements

- 窗口缩放时，三栏布局保持可读且不重叠。
- 中栏优先获得剩余宽度。
- 右栏在预览模式和正式模式下都保持稳定结构。

## Technical Constraints

- QML 不得直接访问 SSH、socket 或文件系统。
- 所有业务动作都通过 `appBridge` 路由。
- 主窗口只负责绑定，不负责重新塑形预览场景数据。

## Non-Goals

- 不在主窗口中实现图表绘制细节。
- 不在主窗口中实现 3D 球体几何细节。
- 不在主窗口中实现能量过滤逻辑。

## Acceptance Criteria

1. 主窗口不再包含本地 `sourceRows()` 逻辑。
2. 预览模式下右栏和中栏都从 `appBridge` 获取统一场景数据。
3. 正式模式下页面仍保持稳定空态和占位结构。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/Main.qml`
- `uv run temporal-preview`
