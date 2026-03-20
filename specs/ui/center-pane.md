# Spec: Center Pane View

## Goal

定义 `src/temporal/qml/CenterPane.qml` 的中央内容区需求。
该区域负责承载俯仰角图、方位角图和活跃声源位置视图，是实时数据展示的视觉核心，并负责把开发期预览场景一致地分发给两张图表和 3D 视图。

## Component Responsibility

- 组织两张图表和一张 3D 声源位置视图。
- 维护三个内容块的标题、间距和相对视觉权重。
- 在预览模式下仅通过 `appBridge` 消费预览数据。

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

- 上方两张图表显示固定横轴样本范围。
- 下方声源位置区保持更强视觉权重，不能被压缩得过小。
- `previewMode=true` 时，两张图表和 3D 视图必须消费同一组预览场景。
- `previewMode=false` 时，3D 视图继续消费运行态 `sourcePositions`，图表保持占位/预览曲线。
- 预览 fixture 数据不得保留在本地 QML JavaScript 中。

## Visual Requirements

- 中栏背景为白色主内容区。
- 三个模块之间有稳定垂直间距。
- 声源位置区域需要明显大于单张图表高度。

## Interaction Requirements

- 当窗口变窄时，图表与球体区域仍需保持标题、内容和边距可读。
- 预览行为属于开发/测试模式，不是用户可见开关。
- 中栏本身不持有场景切换状态。
- `previewScenarioKey` 仅用于向 `SourceSphereView` 转发预览兜底行为。

## Technical Constraints

- 图表绘制和 3D 渲染细节由子组件负责。
- 预览场景数据保留在 Python bridge 模块中。
- 预览基线场景保持为：
  - `referenceSingle`
  - `hemisphereSpread`
  - `equatorBoundary`
  - `emptyState`

## Non-Goals

- 不在该组件中实现预览声源行联动。
- 不在该组件中实现预览能量过滤。
- 不在本阶段补充正式环境的 SST 历史绘制。

## Acceptance Criteria

1. 默认窗口尺寸下，两张图表和 3D 球体维持既定的视觉层级。
2. 预览模式下，图表和 3D 数据来自同一个活动预览场景。
3. 运行模式下，即使没有实时历史数据，图表也保持稳定空态。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/CenterPane.qml`
- 启动 `uv run temporal-preview`，确认中栏在不依赖本地 QML fixture 的前提
  下渲染出预览图表和预览 3D 数据。
