# Spec: Right Sidebar View

## Goal

定义 `src/temporal/qml/RightSidebar.qml` 的右侧信息面板需求。
该区域负责展示声源列表、筛选器和录音会话，
并在 preview 模式下与活动预览场景保持一致。

## Component Responsibility

- 渲染声源列表区。
- 渲染筛选器区。
- 渲染录音会话区。
- 在 preview 模式下渲染真实的场景声源行，而不是静态占位。
- 在 preview 空场景下渲染稳定空态提示，而不是留下异常空白。

## Data Contract

### Inputs

- `appBridge.sourceRowsModel`
- `appBridge.recordingSessionsModel`
- `appBridge.sourcesEnabled`
- `appBridge.potentialsEnabled`
- `appBridge.potentialEnergyMin`
- `appBridge.potentialEnergyMax`

### Rules

- `appBridge.sourceRowsModel` 非空时，直接渲染 bridge 提供的行数据。
- `appBridge.sourceRowsModel` 为空时，统一显示空态提示文案。
- 行 badge 颜色必须使用数据中的 `badgeColor`。
- 右栏不在本地拼接 preview/runtime 占位行。
- 右栏 row 集合来自当前场景经过全局筛选后的 `sources` 元数据。
- 用户取消勾选后，对应 row 必须继续保留，只修改 `checked` 状态。
- 右栏 `暂无活动声源` 只在全局筛选后 row 数为零时出现，
  不因最后一个勾选被取消而触发。
- 右栏每一行右侧展示的动态数值
  必须跟随当前 frame 的 `energy` 变化，
  不能长期停留在静态 metadata。

## Visual Requirements

- 保持右栏较窄、纵向堆叠的布局。
- 标题字号与左栏保持一致。
- 各分区之间使用轻量分隔线。
- 声源 badge 颜色与图表和 3D 点位颜色一致。
- 空列表时显示 `暂无活动声源`，并保留稳定分隔结构。
- 筛选器区文案保持中文正式态：
  - `声源`
  - `候选点`
  - `候选声源能量范围`
- 录音会话为空时显示 `暂无活动录音会话`。

## Interaction Requirements

- 声源勾选框切换后调用
  `appBridge.setSourceSelected(sourceId, checked)`。
- 取消勾选后，对应 row 继续保留，仅勾选状态变化。
- 筛选器开关和能量滑杆继续绑定现有 `appBridge` 接口。
- 录音会话为空时仅显示空状态文案，不额外伪造列表项。

## Technical Constraints

- 右栏不在本地推导 badge 颜色或勾选状态。
- 场景切换控件不放在右栏，而放在头部。
- 右栏不根据 `previewMode` 或其他本地状态推导占位行和空态。
- 右栏不负责决定图表与 3D 的时序数据，只消费 bridge 输出的 row 状态。

## Non-Goals

- 不在右栏中实现录音存储或回放逻辑。
- 不在本阶段引入新的筛选器控件。

## Acceptance Criteria

1. Preview 模式下右栏声源列表来自当前场景的全局筛选结果，
   而不是静态占位。
2. 取消最后一个勾选 source 后，右栏 row 继续保留，
   图表和 3D 同时变空。
3. `emptyState` 下右栏不显示伪造声源行，
   并显示 `暂无活动声源`。
4. 右栏动态数值会随当前 frame 变化，
   可用于验证界面刷新逻辑。
5. 右栏筛选器与录音会话区文案保持中文正式态，
   不出现英文开发提示。
6. `RightSidebar.qml` 不再包含本地 preview/runtime 拼接逻辑。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/RightSidebar.qml`
- 启动 `uv run temporal-preview`，确认右栏与中栏和 3D 同步更新。
