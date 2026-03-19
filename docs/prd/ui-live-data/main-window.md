# PRD: Main Window

## Goal

定义 `src/temporal/qml/Main.qml` 的页面级需求。
该窗口是 Temporal 的实时数据主界面，需要统一承载菜单、品牌头部、底栏和三栏主内容区域，并在布局比例、视觉层级和可操作性上接近参考版 ODAS Studio。

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

### Rules

- 页面本身不直接实现业务控制逻辑。
- 当没有真实数据时，页面仍需显示稳定的占位内容。
- 子组件统一从 `theme` 读取视觉参数。

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

## Non-Goals

- 不在主窗口组件内实现图表绘制细节。
- 不在主窗口组件内实现声源球体的 3D 几何细节。

## Acceptance Criteria

1. 启动应用后可以稳定显示完整的主界面框架。
2. 默认尺寸下三栏比例与参考图接近。
3. 在无数据场景下右栏和中栏仍有合理占位内容。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/Main.qml`
- `uv run temporal`
