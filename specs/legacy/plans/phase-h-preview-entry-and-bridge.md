# Spec: Phase H Preview Entry and Bridge

## Goal

将 preview 模式从本地 QML 开关提升为标准应用入口，
并通过 `uv run temporal-preview` 暴露出来。

## Scope

- 增加独立的 preview 启动脚本。
- 提供以 `appBridge` 注入的 `PreviewBridge`。
- 保持 preview 和 production 继续共享同一份 `Main.qml`。
- 定义现有左栏、中栏和右栏所需的最小 preview bridge API。

## Implemented Shape

- `pyproject.toml` 暴露：
  - `temporal = "temporal.main:main"`
  - `temporal-preview = "temporal.preview_main:main"`
- `src/temporal/app.py` 暴露共享的 `run_with_bridge()` 启动辅助函数。
- `src/temporal/preview_main.py` 通过
  `run_with_bridge(PreviewBridge())` 启动 `Main.qml`。
- `src/temporal/preview_bridge.py` 负责 preview 状态与 preview-safe 控制行为。
- `src/temporal/preview_data.py` 是 preview 场景的 Python 真源。

## Non-Goals

- 不在本阶段完成右栏的完整 preview 数据联动。
- 不在本阶段完成 UI 内的 preview 场景切换控件。
- 不在本阶段完成候选能量范围的完整 preview 过滤语义。
- 不引入新的 production 传输或录音行为。

## Functional Requirements

1. `uv run temporal-preview` 必须在无需手改 QML 的前提下，
   启动现有主窗口布局。
2. Preview 模式使用 `PreviewBridge`，而 `uv run temporal`
   继续使用 `AppBridge`。
3. 两个 bridge 都必须以 `appBridge` 名称暴露给 QML。
4. `PreviewBridge` 必须为当前 QML 实际使用到的所有方法和属性
   提供安全实现，包括：
   - 左栏控制与状态文本
   - 中栏图表和 3D 绑定
   - 右栏声源与筛选控件
5. Preview 左栏动作只能切换本地 preview 状态，
   不得启动 SSH、socket 或真实 ODAS 数据流。

## Interface Additions

- `previewMode: bool`
- `previewScenarioKey: str`
- `previewScenarioKeys: list[str]`
- `setPreviewScenario(key: str)`
- `elevationSeries: list[dict]`
- `azimuthSeries: list[dict]`

Production bridge returns safe empty defaults for preview-only properties so
QML can bind the same interface in both entrypoints.
Production bridge 需要为 preview-only 属性返回安全空默认值，
以便 QML 在两个入口下绑定同一套接口。

## Quality Requirements

- 保持 `Main.qml` 在 preview 和 production 之间共享。
- 保持 preview bridge 行为确定、可复现且仅限本地。
- 不要求 QML 按 bridge 对象名分支。
- 将 preview fixture 数据保留在 Python 中，而不是本地 QML JavaScript。

## Acceptance Criteria

1. `uv run temporal-preview` 能成功启动主 UI。
2. `uv run temporal` 的行为保持不变。
3. 进入 preview 模式不需要修改任何 QML 文件。
4. 现有页面区域能使用 preview bridge 数据与 no-op 控制正常渲染，
   不出现运行时错误。
5. `CenterPane.qml` 不再导入本地 preview fixture 脚本。

## Validation Workflow

- `uv run pyside6-qmllint src/temporal/qml/Main.qml`
- `uv run pyside6-qmllint src/temporal/qml/CenterPane.qml`
- `uv run pyside6-qmllint src/temporal/qml/RightSidebar.qml`
- `uv run ruff check src tests`
- `uv run python -m unittest discover -s tests -p "test_*.py" -v`
- 启动 `uv run temporal-preview` 并验证：
  - 主布局无需编辑 QML 即可渲染
  - 中栏显示 preview 图表和 3D 数据
  - 右栏在本阶段仍显示占位 source rows
  - 左栏动作只改变本地 preview 状态
