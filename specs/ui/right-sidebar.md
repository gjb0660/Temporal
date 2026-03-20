# Spec: Right Sidebar View

## Goal

定义 `src/temporal/qml/RightSidebar.qml` 的右侧信息面板需求。该区域负责展示声源
列表、筛选器和录音会话，并在预览模式下与活动预览场景保持一致。

## Component Responsibility

- 渲染声源列表区。
- 渲染筛选器区。
- 渲染录音会话区。
- 在预览模式下渲染真实的场景声源行，而不是静态占位。

## Data Contract

### Inputs

- `sourceRows`
- `recordingSessions`
- `appBridge.previewMode`

### Rules

- `sourceRows` 非空时，直接渲染桥接层提供的行数据。
- 正式模式且 `sourceRows` 为空时，显示占位声源行。
- 预览模式且场景为空时，不伪造占位声源行。
- 行 badge 颜色必须使用数据中的 `badgeColor`。

## Visual Requirements

- 保持右栏较窄、纵向堆叠的布局。
- 标题字号与左栏保持一致。
- 各分区之间使用轻量分隔线。
- 声源 badge 颜色与图表和 3D 点位颜色一致。

## Interaction Requirements

- 声源勾选框切换后调用 `appBridge.setSourceSelected(sourceId, checked)`。
- 筛选器开关和能量滑杆继续绑定现有 `appBridge` 接口。
- 录音会话为空时显示空状态文案。

## Technical Constraints

- 右栏不在本地推导 badge 颜色或勾选状态。
- 预览模式下的场景切换控件不放在右栏，而放在头部。
- 本阶段不在右栏内实现能量过滤后的裁剪逻辑。

## Non-Goals

- 不在右栏中实现录音存储或回放逻辑。
- 不在本阶段实现能量过滤联动。

## Acceptance Criteria

1. 预览模式下右栏声源列表来自当前场景，而不是静态占位。
2. 勾选单个声源后，右栏状态与图表、3D 数据保持一致。
3. `emptyState` 下右栏不显示伪造的声源行。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/RightSidebar.qml`
- 启动 `uv run temporal-preview`，确认右栏与中栏和 3D 同步更新。
