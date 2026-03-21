# Spec: Left Sidebar View

## Goal

定义 `src/temporal/qml/LeftSidebar.qml` 的左侧栏需求。
该区域承载 ODAS 日志区和 ODAS 控制区，
是操作员观察连接状态和执行远端控制的主入口。

## Component Responsibility

- 渲染左上日志卡片。
- 渲染左下 ODAS 控制卡片。
- 控制两张卡片的整体高度比例。
- 在 preview 与 runtime 中统一承载主按钮和监听按钮的状态机入口。

## Data Contract

### Inputs

- `appBridge.status`
- `appBridge.remoteConnected`
- `appBridge.odasStarting`
- `appBridge.odasRunning`
- `appBridge.streamsActive`
- `appBridge.remoteLogText`

### Rules

- 左上日志区和左下控制区的整体高度比例接近 `6:4`。
- 控制区只提供两个按钮，不再暴露旧版复杂按钮矩阵。
- 主按钮 `启动/停止` 直接绑定 `appBridge.toggleRemoteOdas()`。
- 监听按钮 `监听/停止监听` 直接绑定 `appBridge.toggleStreams()`。
- 主按钮启动时，若本地未监听，bridge 必须先补开监听，
  再启动远端 `odaslive`。
- 主按钮停止时，bridge 必须先停监听，再停远端，
  且不主动断开 SSH。
- 监听按钮允许在远端未运行时单独开启本地 listener。
- preview 的动画推进只能由监听状态触发，
  左栏控制语义必须与运行时状态机一致。
- 主按钮在 `odasStarting=true` 时显示 `启动中`，
  并处于禁用状态，避免重复触发启动。

## Visual Requirements

- 左栏背景采用浅绿色偏灰面板色。
- 日志卡片高度明显大于控制卡片。
- 卡片边框、圆角和阴影保持克制，贴近 Windows 原生浅色控件。
- 按钮文案保持中文正式态：
  - `启动` / `停止`
  - `监听` / `停止监听`

## Interaction Requirements

- 日志区支持滚动查看长文本。
- 控制区需要显示当前状态文本。
- 日志文案应清晰区分以下状态：
  - 等待远端连接
  - 本地 listener 已开启，等待远端接入
  - 本地 listener 启动失败
  - 远程 `odaslive` 启动中
  - 正在监听 `SST/SSL/SSS` 数据流
  - 远程 `odaslive` 已启动
  - 远程 `odaslive` 已停止

## Technical Constraints

- 业务动作必须调用 `appBridge.toggleRemoteOdas()` 和
  `appBridge.toggleStreams()`。
- QML 不自行拼接远端状态机逻辑。
- QML 不限制监听按钮必须依赖远端运行态。
- QML 直接消费 `odasStarting`，
  不本地推导“启动中”状态。

## Non-Goals

- 不在左侧栏内直接实现 SSH 或进程控制。

## Acceptance Criteria

1. 左上日志区和左下控制区整体比例接近参考图的 `6:4`。
2. 控制区只剩两个按钮。
3. 监听按钮可独立启停本地 listener。
4. 主按钮启动会自动补开监听，主按钮停止顺序正确。
5. 日志文本和状态文本在默认窗口下都具有可读高度，
   且不出现乱码。
6. 主按钮在启动验证窗口内显示 `启动中` 且不可重复点击。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/LeftSidebar.qml`
