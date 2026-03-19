# Spec: Center Pane View

## Goal

定义 `src/temporal/qml/CenterPane.qml` 的中央内容区需求。
该区域负责承载俯仰角图、方位角图和活跃声源位置视图，是实时数据展示的视觉核心，并负责把开发期预览场景一致地分发给两张图表和 3D 视图。

## Component Responsibility

- 组织两张图表和一张 3D 声源位置视图。
- 维护三个内容块的标题、间距和相对视觉权重。
- 在开发期预览模式下，将同一组 fixture 同步提供给两张图表和 3D 视图。

## Data Contract

### Inputs

- `sourcePositions`
- `theme.chartHeight`
- `theme.sphereHeight`
- `previewMode`
- `previewScenarioKey`

### Rules

- 上方两张图表显示固定横轴样本范围。
- 下方声源位置区保持更强视觉权重，不能被压缩得过小。
- `previewMode=true` 时，两张图表和 3D 视图必须消费同一组预览场景。
- `previewMode=false` 时，3D 视图继续消费运行态 `sourcePositions`，图表保持占位/预览曲线。

## Visual Requirements

- 中栏背景为白色主内容区。
- 三个模块之间有稳定垂直间距。
- 声源位置区域需要明显大于单张图表高度。

## Interaction Requirements

- 当窗口变窄时，图表与球体区域仍需保持标题、内容和边距可读。
- 预览模式仅作为开发入口，不做用户可见开关。

## Technical Constraints

- 图表绘制和 3D 渲染细节由子组件负责。
- 预览场景至少包含：
  - `referenceSingle`
  - `hemisphereSpread`
  - `equatorBoundary`
  - `emptyState`

## Non-Goals

- 不在容器层实现后端数据采样和绘图算法。
- 不在该层引入新的业务逻辑或协议绑定。

## Acceptance Criteria

1. 默认窗口下两张图表和球体区域的层级接近参考图。
2. 球体区域在视觉上是中栏下半区主体。
3. 预览模式切换场景后，两张图表和 3D 视图的数据同步变化。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/CenterPane.qml`
- 逐个切换预览场景并截图，检查图表与 3D 是否一致
