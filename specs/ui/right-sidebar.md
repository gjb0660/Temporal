# Spec: Right Sidebar View

## Goal

定义 `src/temporal/qml/RightSidebar.qml` 的右侧信息面板需求。该区域负责展示声源
列表、筛选器和录音会话，并在预览模式下与活动预览场景保持一致。

## Component Responsibility

- 渲染声源列表区。
- 渲染筛选器区。
- 渲染录音会话区。
- 在预览模式下渲染真实的场景声源行，而不是静态占位。
- 在预览空场景下渲染稳定空态提示，而不是留下异常空白。

## Data Contract

### Inputs

- `appBridge.sourceRows`
- `appBridge.recordingSessions`
- `appBridge.sourcesEnabled`
- `appBridge.potentialsEnabled`
- `appBridge.potentialEnergyMin`
- `appBridge.potentialEnergyMax`

### Rules

- `appBridge.sourceRows` 非空时，直接渲染桥接层提供的行数据。
- `appBridge.sourceRows` 为空时，统一显示空态提示文案。
- 行 badge 颜色必须使用数据中的 `badgeColor`。
- 右栏不在本地拼接预览/正式模式占位行。
- `appBridge.sourceRows` 表示当前场景在全局筛选后的声源行，并保留
  可逆的勾选状态。

## Visual Requirements

- 保持右栏较窄、纵向堆叠的布局。
- 标题字号与左栏保持一致。
- 各分区之间使用轻量分隔线。
- 声源 badge 颜色与图表和 3D 点位颜色一致。
- 空列表时显示 `暂无活动声源`，并保留稳定分隔结构。
- 筛选器区文案保持中文正式态:
  - `声源`
  - `候选点`
  - `候选声源能量范围:`
- 录音会话为空时显示 `暂无活跃录音会话`。

## Interaction Requirements

- 声源勾选框切换后调用 `appBridge.setSourceSelected(sourceId, checked)`。
- 取消勾选后，对应 row 继续保留，仅勾选状态变化。
- 筛选器开关和能量滑杆继续绑定现有 `appBridge` 接口。
- 录音会话为空时仅显示空状态文案，不额外伪造列表项。

## Technical Constraints

- 右栏不在本地推导 badge 颜色或勾选状态。
- 场景切换控件不放在右栏，而放在头部。
- 本阶段不在右栏内实现能量过滤后的裁剪逻辑。
- 右栏不根据 `previewMode` 或其他本地状态推导占位行和空态。

## Non-Goals

- 不在右栏中实现录音存储或回放逻辑。
- 不在本阶段实现能量过滤联动。

## Acceptance Criteria

1. 预览模式下右栏声源列表来自当前场景的筛选结果，而不是静态占位。
2. 勾选单个声源后，右栏状态与图表、3D 数据保持一致。
3. `emptyState` 下右栏不显示伪造的声源行，并显示 `暂无活动声源`。
4. 右栏筛选器与录音会话区文案保持中文正式态，不出现英文开发提示。
5. `RightSidebar.qml` 不再包含本地 preview/runtime 拼接逻辑。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/RightSidebar.qml`
- 启动 `uv run temporal-preview`，确认右栏与中栏和 3D 同步更新。
