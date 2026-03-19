# Spec: Left Sidebar View

## Goal

定义 `src/temporal/qml/LeftSidebar.qml` 的左侧栏需求。
该区域承载 ODAS 日志区和 ODAS 控制区，是操作员观察连接状态和执行远端控制的主入口。

## Component Responsibility

- 渲染左上日志卡片。
- 渲染左下 ODAS 控制卡片。
- 控制两张卡片的整体高度比例。

## Data Contract

### Inputs

- `appBridge.statusText`
- `appBridge.remoteConnected`
- `appBridge.odasRunning`
- `appBridge.streamsActive`

### Rules

- 左上日志区和左下控制区的整体高度比例接近 `6:4`。
- 控制区只提供两个按钮，不再暴露旧版复杂按钮矩阵。

## Visual Requirements

- 左栏背景采用浅绿色偏灰面板色。
- 日志卡片高度明显大于控制卡片。
- 卡片边框、圆角和阴影保持克制，贴近 Windows 原生浅色控件。

## Interaction Requirements

- 日志区支持滚动查看长文本。
- 控制区需要显示当前状态文本。
- 控制区按钮文案根据运行状态切换：
  - `启动` / `停止`
  - `监听` / `停止监听`

## Technical Constraints

- 业务动作必须调用 `appBridge.toggleRemoteOdas()` 和 `appBridge.toggleStreams()`。
- QML 不自行拼接远端状态机逻辑。

## Non-Goals

- 不在左侧栏内直接实现 SSH 或进程控制。

## Acceptance Criteria

1. 左上日志区和左下控制区整体比例接近参考图的 `6:4`。
2. 控制区只剩两个按钮。
3. 日志文本和状态文本在默认窗口下都具有可读高度。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/LeftSidebar.qml`
