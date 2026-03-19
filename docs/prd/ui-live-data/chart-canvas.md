# PRD: Chart Canvas View

## Goal

定义 `src/temporal/qml/ChartCanvas.qml` 的图表组件需求。
该组件用于绘制俯仰角和方位角折线图，输出风格需要接近参考图中的原始 ODAS 曲线图，并支持多条按 source id 稳定配色的折线。

## Component Responsibility

- 绘制坐标网格。
- 绘制横轴、纵轴刻度和标题。
- 循环绘制 `seriesList` 中的一条或多条折线数据。

## Data Contract

### Inputs

- `xTicks`
- `yTicks`
- `xAxisLabel`
- `seriesList`

### Rules

- `seriesList` 每项结构固定为 `{ sourceId, values, color }`。
- 横轴默认展示固定样本范围。
- 无真实数据时允许显示空网格，不强制显示占位曲线。

## Visual Requirements

- 网格颜色轻量，不能压过折线。
- 折线颜色与参考图保持一致风格，并允许扩展到多 source 颜色。
- 坐标文本采用紧凑浅灰样式。

## Interaction Requirements

- 图表当前无需支持缩放和平移。

## Technical Constraints

- 使用 QML Canvas 或等效轻量绘制方式。
- 绘制逻辑需保证窗口缩放后仍然清晰。

## Non-Goals

- 不实现复杂交互式数据分析能力。

## Acceptance Criteria

1. 两张图表都能稳定显示网格、坐标轴和多条折线。
2. `seriesList` 为空时仍能稳定显示空网格。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/ChartCanvas.qml`
