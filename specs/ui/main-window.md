# Spec: Main Window

## Goal

定义 `src/temporal/qml/Main.qml` 的主窗口需求。该窗口是实时数据应用的页面级外
壳，负责组织布局、主题 token 和顶层组件组合，并通过 `appBridge` 统一接收业
务状态。

## Component Responsibility

- 作为应用主窗口。
- 定义全局主题 token，并向子组件透传。
- 组装左侧栏、中间内容区和右侧栏。
- 维持窗口级尺寸、最小尺寸和整体背景。

## Data Contract

### Inputs

- `appBridge.sourceIds`
- `appBridge.sourcePositions`
- `appBridge.recordingSessions`
- `appBridge.isSourceSelected(sourceId)`
- `appBridge.previewMode`
- `appBridge.previewScenarioKey`

### Rules

- 页面本身不直接实现后端业务逻辑。
- 当没有真实声源数据时，页面仍需显示稳定占位内容。
- 子组件统一通过 `theme` 获取视觉参数。
- 预览状态由 `appBridge` 持有，而不是本地 QML 属性。

## Visual Requirements

- 默认窗口尺寸为 `1188x794`。
- 最小窗口尺寸为 `940x640`。
- 页面采用三栏结构：
  - 左栏为日志和 ODAS 控制。
  - 中栏为两张图表和声源位置视图。
  - 右栏为声源、筛选器和录音会话。
- 顶部包含原生风格菜单条和绿色品牌条。
- 整体风格接近 Windows 原生浅色界面，保留绿色品牌识别。

## Interaction Requirements

- 窗口缩放时，三栏布局保持稳定，不出现重叠和裁切。
- 中栏优先获得剩余宽度。
- 左栏和右栏保持可读的最小宽度。

## Technical Constraints

- QML 不能直接访问 SSH、socket 或文件系统。
- 所有业务动作都通过 `appBridge` 进入后端。
- 预览态向中栏的传递必须使用 `appBridge.previewMode` 和
  `appBridge.previewScenarioKey`。

## Non-Goals

- 不在主窗口组件内实现图表绘制细节。
- 不在主窗口组件内实现声源球体的 3D 几何细节。
- 不在本阶段于主窗口内实现预览场景切换控件。

## Acceptance Criteria

1. 正式入口和预览入口都可以稳定显示完整的主界面框架。
2. 默认尺寸下三栏比例与参考图接近。
3. 中栏通过 `appBridge` 接收预览状态，不再由本地 QML 持有预览开关。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/Main.qml`
- `uv run temporal`
- `uv run temporal-preview`
