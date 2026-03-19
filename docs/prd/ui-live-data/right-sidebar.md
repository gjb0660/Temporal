# PRD: Right Sidebar View

## Goal

定义 `src/temporal/qml/RightSidebar.qml` 的右侧栏需求。
该区域用于展示声源列表、筛选器和录音会话信息，需要保持参考图中的紧凑信息面板风格。

## Component Responsibility

- 渲染声源列表区。
- 渲染筛选器区。
- 渲染录音会话区。

## Data Contract

### Inputs

- `sourceRows`
- `recordingSessions`

### Rules

- 无真实声源时仍显示占位声源行。
- 录音会话为空时显示空状态文案。

## Visual Requirements

- 右栏宽度较窄，布局应以纵向信息栈为主。
- 标题字号与左栏保持一致。
- 各区块之间使用轻量分隔线。

## Interaction Requirements

- 声源行支持勾选和点击反馈。
- 筛选器项支持开关状态。
- 录音会话区支持显示当前会话摘要。

## Technical Constraints

- 右栏的勾选操作必须通过 `appBridge` 或上层数据绑定更新。

## Non-Goals

- 不在右栏中直接实现录音存储和回放逻辑。

## Acceptance Criteria

1. 右栏默认尺寸下能完整显示三段内容。
2. 无数据时不出现空白断层。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/RightSidebar.qml`
