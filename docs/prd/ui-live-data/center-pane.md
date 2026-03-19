# PRD: Center Pane View

## Goal

定义 `src/temporal/qml/CenterPane.qml` 的中央内容区需求。
该区域负责承载俯仰角图、方位角图和活跃声源位置视图，是实时数据展示的视觉核心。

## Component Responsibility

- 组织两张图表和一张 3D 声源位置视图。
- 维护三个内容块的标题与间距。
- 为声源球体区域提供足够的展示高度。

## Data Contract

### Inputs

- `sourcePositions`
- `theme.chartHeight`
- `theme.sphereHeight`

### Rules

- 上方两张图表显示固定的横轴样本范围。
- 下方声源位置区保持更强视觉权重，不能被压缩得过小。

## Visual Requirements

- 中栏背景为白色主内容区。
- 三个模块之间有稳定垂直间距。
- “Active sources locations” 区域需要明显大于单张图表高度。

## Interaction Requirements

- 当窗口变窄时，图表与球体区域仍需保持标题、内容和边距可读。

## Technical Constraints

- 图表绘制和 3D 渲染细节由子组件负责。

## Non-Goals

- 不在容器层实现数据采样和绘图算法。

## Acceptance Criteria

1. 默认窗口下两张图表和球体区域的层级接近参考图。
2. 球体区域在视觉上是中栏下半区主体。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/CenterPane.qml`
