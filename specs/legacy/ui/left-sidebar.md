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
- `appBridge.canToggleStreams`
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
- 监听按钮启用条件为 `appBridge.canToggleStreams`：
  - 启动监听要求 SSH 控制通道存活
  - 停止监听同样要求 SSH 控制通道存活
- 按下监听按钮时，只开启或关闭本地监听端口，不停止远端 odaslive，
  也不主动断开 SSH。
- 若远端 odaslive 在本地监听关闭后继续运行，界面允许其继续在日志区
  暴露连接失败信息，不追加额外联动。
- 状态区展示经过过滤的人类可读失败原因；
  原始 shell 路径和完整远端报错保留在日志区。
- 若失败原因来自远程控制通道初始化或恢复失败，
  状态区必须显示“远程控制通道…”类错误，
  不得误标成“SSH 连接失败”。

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

1. 左上日志区与左下控制区的整体比例接近参考图 `6:4`。
2. 控制区仅保留“启动/停止”和“监听/停止监听”两类主按钮。
3. 长日志与长错误路径在默认窗口下可通过自动换行直接阅读。
4. 状态面板显示人类可读的摘要原因，而不是原始 shell 细节。
5. 停止监听不会隐含停止远端 odaslive。
6. 停止监听不会隐含断开 SSH。
7. 监听按钮在 SSH 控制通道失活时禁用。
8. 监听按钮启用状态不得只依赖本地缓存的连接标记，必须反映当前 SSH 控制通道是否存活。
9. 停止远端时必须同时关闭启动 wrapper 和 `odaslive` 子进程，
   不能只停掉入口脚本后让真正的 `odaslive` 继续运行。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/LeftSidebar.qml`
