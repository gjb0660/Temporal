# PRD: Chart Canvas View

## Goal

定义 `src/temporal/qml/ChartCanvas.qml` 的图表组件需求。
该组件用于绘制俯仰角和方位角折线图，输出风格需要接近参考图中的原始 ODAS 曲线图。

## Component Responsibility

- 绘制坐标网格。
- 绘制横轴、纵轴刻度和标题。
- 绘制一条或多条折线数据。

## Data Contract

### Inputs

- 图表标题
- Y 轴范围和刻度
- 样本横轴范围
- 一组或多组折线数据

### Rules

- 横轴默认展示固定样本范围，当前基线为 `0-1600`。
- 无真实数据时允许显示空网格或占位曲线。

## Visual Requirements

- 网格颜色轻量，不能压过折线。
- 折线颜色与参考图保持一致风格，主要使用青色和紫色。
- 坐标文本采用紧凑浅灰样式。

## Interaction Requirements

- 图表当前无需支持缩放和平移。

## Technical Constraints

- 使用 QML Canvas 或等效轻量绘制方式。
- 绘制逻辑需保证窗口缩放后仍然清晰。

## Non-Goals

- 不实现复杂交互式数据分析能力。

## Acceptance Criteria

1. 两张图表都能稳定显示网格、坐标轴和折线。
2. 横轴范围与参考图要求一致。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/ChartCanvas.qml`
