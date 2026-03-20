# Spec: Center Pane View

## Goal

定义 `src/temporal/qml/CenterPane.qml` 的中央内容区需求。该区域是实时数据页面的
视觉核心，负责承载俯仰角图、方位角图和 3D 声源球，并在预览模式下与右栏共享同
一场景数据。

## Component Responsibility

- 布局两张图表和一张 3D 声源位置视图。
- 在不同窗口宽度下保持标题、间距和视觉主次稳定。
- 消费 `appBridge` 提供的预览 series 和 3D 点位数据。

## Data Contract

### Inputs

- `sourcePositions`
- `previewMode`
- `previewScenarioKey`
- `appBridge.elevationSeries`
- `appBridge.azimuthSeries`
- `theme.chartHeight`
- `theme.sphereHeight`

### Rules

- `previewMode=true` 时，两张图表与 3D 点位必须来自同一活动预览场景。
- `previewMode=false` 时，图表保持运行态空占位，3D 继续消费运行态
  `sourcePositions`。
- 中栏不再从本地 QML fixture 脚本中读取预览数据。
- 中栏不负责决定哪些声源被选中，只负责消费 bridge 已裁剪后的数据。

## Visual Requirements

- 保持白色主内容面板和稳定垂直间距。
- 声源球区域应明显大于单张图表区域。
- 在较窄窗口下仍需保证标题、边距和边框可读。

## Interaction Requirements

- 中栏本身不提供场景切换控件。
- `previewScenarioKey` 仅用于向 `SourceSphereView` 转发预览兜底行为。
- 当右栏切换声源勾选状态时，中栏显示内容同步变化。

## Technical Constraints

- 图表绘制和 3D 渲染细节保留在子组件内部。
- 预览场景数据保留在 Python bridge 模块中。
- 预览基线场景保持为：
  - `referenceSingle`
  - `hemisphereSpread`
  - `equatorBoundary`
  - `emptyState`

## Non-Goals

- 不在该组件中实现预览能量过滤。
- 不在本阶段补充正式环境的 SST 历史绘制。

## Acceptance Criteria

1. 预览模式下，图表和 3D 数据始终来自同一活动场景。
2. 切换场景后，中栏与右栏同步刷新。
3. 取消勾选单个声源后，中栏对应图表曲线和 3D 点位同步消失。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/CenterPane.qml`
- 启动 `uv run temporal-preview`，确认中栏随场景切换和声源勾选同步变化。
