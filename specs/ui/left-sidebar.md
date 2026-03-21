# Spec: Left Sidebar View

## Goal

定义 `src/temporal/qml/LeftSidebar.qml` 的左侧栏需求。
该区域承载远程 odaslive 日志区和 ODAS 控制区，
是操作员观察远端状态和执行控制的主入口。

## Component Responsibility

- 渲染左上远程 odaslive 日志卡片。
- 渲染左下 ODAS 控制卡片。
- 维持两张卡片约 `6:4` 的高度比例。

## Data Contract

### Inputs

- `appBridge.remoteLogLines`
- `appBridge.status`
- `appBridge.odasStarting`
- `appBridge.odasRunning`
- `appBridge.streamsActive`

### Rules

- 左上日志区和左下控制区的整体高度比例接近 `6:4`。
- 控制区只保留两个主操作按钮，不暴露旧版复杂按钮矩阵。
- 状态文本只读取 `appBridge.status`，QML 不自行拼接运行态。
- 远端 odaslive 与本地监听是两个独立资源：
  启动按钮控制远端 odaslive，监听按钮只控制本地监听端口。

## Visual Requirements

- 左栏背景采用浅绿色偏灰面板色。
- 日志卡片高度明显大于控制卡片。
- 卡片边框、圆角和阴影保持克制，贴近 Windows 浅色原生控件。
- 左上日志文本必须自动换行，不再强制依赖横向滚动查看长路径或长报错。

## Interaction Requirements

- 日志区支持纵向滚动浏览长文本。
- 日志区文本支持自动换行与鼠标选择复制。
- 控制区显示当前状态文本。
- 启动按钮文案按状态切换：
  - `启动`
  - `启动中`
  - `停止`
- `启动中` 时启动按钮禁用，防止重复点击。
- 监听按钮文案按状态切换：
  - `监听`
  - `停止监听`
- 按下启动按钮时，若 SSH 尚未连接，则先隐式建立 SSH 连接。
- 按下启动按钮时，若本地监听尚未启动，则先自动启动本地监听，
  再启动远端 odaslive。
- 按下停止按钮时，只停止远端 odaslive，不自动停止本地监听。
- 按下监听按钮时，只开启或关闭本地监听端口，不停止远端 odaslive，
  也不主动断开 SSH。
- 若远端 odaslive 在本地监听关闭后继续运行，界面允许其继续在日志区
  暴露连接失败信息，不追加额外联动。
- 状态区展示经过过滤的人类可读失败原因；
  原始 shell 路径和完整远端报错保留在日志区。

## Technical Constraints

- 所有业务动作必须调用 `appBridge.toggleRemoteOdas()`
  和 `appBridge.toggleStreams()`。
- QML 不自行实现 SSH、进程控制或错误分类逻辑。

## Non-Goals

- 不在左侧栏内直接实现 SSH 或进程控制。
- 不在左侧栏内保存或裁剪原始日志内容。

## Acceptance Criteria

1. 左上日志区与左下控制区的整体比例接近参考图 `6:4`。
2. 控制区仅保留“启动/停止”和“监听/停止监听”两类主按钮。
3. 长日志与长错误路径在默认窗口下可通过自动换行直接阅读。
4. 状态面板显示人类可读的摘要原因，而不是原始 shell 细节。
5. 停止监听不会隐含停止远端 odaslive。
6. 停止监听不会隐含断开 SSH。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/LeftSidebar.qml`
- `npx markdownlint specs/ui/left-sidebar.md`
