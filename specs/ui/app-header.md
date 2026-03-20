# Spec: App Header View

## Goal

定义 `src/temporal/qml/AppHeader.qml` 的头部区域需求。该组件同时承载菜单条和绿
色品牌条，需要在保持品牌识别的同时，仅通过 bridge 提供的可见性和文案数据决定
右侧显示场景切换器还是静态导航。

## Component Responsibility

- 渲染顶部菜单条。
- 渲染绿色品牌条。
- 显示产品名称 `Temporal Studio`。
- 在 bridge 要求时渲染场景切换控件。
- 在 bridge 提供导航标签时渲染右侧静态导航入口。

## Data Contract

### Inputs

- `theme.menuHeight`
- `theme.brandHeight`
- `theme.brandFont`
- `theme.accentGreen`
- `appBridge.previewScenarioKey`
- `appBridge.previewScenarioOptions`
- `appBridge.showPreviewScenarioSelector`
- `appBridge.headerNavLabels`

### Rules

- 菜单项和品牌条基础文案由组件内部定义。
- 场景切换选项必须来自 `appBridge.previewScenarioOptions`，不能在 QML 中硬编码
  场景 key。
- `appBridge.showPreviewScenarioSelector == true` 时显示预览场景切换控件。
- `appBridge.headerNavLabels` 非空时显示右侧静态导航。
- 预览模式下场景切换器替换静态导航，不与 `配置 / 录制 / 相机` 同时显示。

## Visual Requirements

- 菜单条为白底，分隔线轻量。
- 品牌条为绿色主色带。
- 预览场景切换控件位于品牌条右侧。
- 场景切换器与静态导航不并存。

## Interaction Requirements

- 菜单项保留 hover 和按压反馈。
- 预览模式下切换下拉框会调用 `appBridge.setPreviewScenario(key)`。
- 组件不自行根据 `previewMode` 推导显示策略。

## Technical Constraints

- 头部组件不直接持有预览场景状态。
- 场景切换只通过 `appBridge` 进行。
- 白色菜单行保持不变，不引入预览专用控制项。
- 头部不在本地硬编码右侧静态导航与场景切换器的互斥逻辑之外的预览分支。

## Non-Goals

- 不在该组件内实现菜单命令的实际分发。
- 不在该组件内实现预览数据过滤逻辑。

## Acceptance Criteria

1. 预览模式下，绿色头部右侧显示场景切换控件。
2. 正式模式下，头部继续显示静态导航文案，不显示预览下拉框。
3. 切换场景后，中栏和右栏的数据联动刷新。
4. QML 不再直接依赖 `previewMode` 决定头部右侧显示内容。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/AppHeader.qml`
- 启动 `uv run temporal-preview`，确认头部只在预览模式下显示场景切换器。
