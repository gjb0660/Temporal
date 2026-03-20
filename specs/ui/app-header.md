# Spec: App Header View

## Goal

定义 `src/temporal/qml/AppHeader.qml` 的头部区域需求。该组件同时承载菜单条和绿
色品牌条，需要在保持品牌识别的同时，为预览模式提供顶部场景切换入口。

## Component Responsibility

- 渲染顶部菜单条。
- 渲染绿色品牌条。
- 显示产品名称 `Temporal Studio`。
- 在预览模式下渲染场景切换控件。
- 在正式模式下继续显示右侧静态导航入口。

## Data Contract

### Inputs

- `theme.menuHeight`
- `theme.brandHeight`
- `theme.brandFont`
- `theme.accentGreen`
- `appBridge.previewMode`
- `appBridge.previewScenarioKey`
- `appBridge.previewScenarioOptions`

### Rules

- 菜单项和品牌条基础文案由组件内部定义。
- 场景切换选项必须来自 `appBridge.previewScenarioOptions`，不能在 QML 中硬编码
  场景 key。
- `appBridge.previewMode == false` 时，不显示预览场景切换控件。

## Visual Requirements

- 菜单条为白底，分隔线轻量。
- 品牌条为绿色主色带。
- 预览场景切换控件位于品牌条右侧。
- 空间不足时，预览控件优先于静态导航占位。

## Interaction Requirements

- 菜单项保留 hover 和按压反馈。
- 预览模式下切换下拉框会调用 `appBridge.setPreviewScenario(key)`。
- 正式模式下不显示该控件，也不暴露预览操作入口。

## Technical Constraints

- 头部组件不直接持有预览场景状态。
- 场景切换只通过 `appBridge` 进行。
- 白色菜单行保持不变，不引入预览专用控制项。

## Non-Goals

- 不在该组件内实现菜单命令的实际分发。
- 不在该组件内实现预览数据过滤逻辑。

## Acceptance Criteria

1. 预览模式下，绿色头部右侧显示场景切换控件。
2. 正式模式下，头部继续显示静态导航文案，不显示预览下拉框。
3. 切换场景后，中栏和右栏的数据联动刷新。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/AppHeader.qml`
- 启动 `uv run temporal-preview`，确认头部只在预览模式下显示场景切换器。
