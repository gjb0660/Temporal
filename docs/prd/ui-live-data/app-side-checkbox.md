# PRD: App Side Checkbox View

## Goal

定义 `src/temporal/qml/AppSideCheckBox.qml` 的侧栏复选框组件需求。
该组件服务于右侧栏声源和筛选器列表，需要提供简洁、轻量且贴近系统风格的勾选控件。

## Component Responsibility

- 渲染复选框框体、勾选标记和标签文字。
- 支持可选的徽标数字或标签附加信息。

## Data Contract

### Inputs

- 标签文案
- `checked`
- `enabled`
- 可选徽标值

### Rules

- 勾选状态由外部数据驱动。
- 当 `enabled` 为 `false` 时，组件仅作为展示占位。

## Visual Requirements

- 复选框尺寸紧凑，适合侧栏密集排布。
- 勾选框与标签垂直居中。
- 徽标样式需要克制，不抢主层级。

## Interaction Requirements

- 支持点击切换。
- 支持 hover 反馈。

## Technical Constraints

- 不在组件内部保存业务源数据。

## Non-Goals

- 不扩展为树形选择器或多级筛选控件。

## Acceptance Criteria

1. 右栏复选项行高和对齐稳定。
2. 占位数据与真实数据都能正常显示。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/AppSideCheckBox.qml`
