# Spec: App Action Button View

## Goal

定义 `src/temporal/qml/AppActionButton.qml` 的按钮组件需求。
该组件用于统一承载侧栏和内容区中的操作按钮风格，需要尽量接近 Windows 原生浅色按钮体验。

## Component Responsibility

- 渲染统一样式的操作按钮。
- 提供默认、悬停、按压、禁用四种视觉状态。

## Data Contract

### Inputs

- 按钮文字
- `enabled`
- `checked` 或等价状态
- `theme.buttonFill`
- `theme.buttonBorder`
- `theme.buttonText`

### Rules

- 按钮状态切换仅负责 UI 呈现，不在组件内部拼业务逻辑。

## Visual Requirements

- 外观接近 Windows 原生浅色按钮。
- 边框细、圆角小、背景浅。
- 禁用态文字和边框对比下降，但仍可辨认。

## Interaction Requirements

- 支持 hover、pressed、disabled 的状态反馈。
- 可用于“启动/停止”和“监听/停止监听”等切换按钮。

## Technical Constraints

- 样式参数统一从 `theme` 获取。

## Non-Goals

- 不承担复杂复合控件行为。

## Acceptance Criteria

1. 同类按钮在全页面视觉一致。
2. 禁用态和按压态反馈清晰可辨。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/AppActionButton.qml`
