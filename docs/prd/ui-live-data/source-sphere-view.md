# PRD: Source Sphere View

## Goal

定义 `src/temporal/qml/SourceSphereView.qml` 的三维声源位置视图需求。
该组件用于展示活跃声源在球面空间中的位置，需要在默认姿态、网格配色、坐标轴和交互方式上尽量贴近参考版 ODAS Studio。

## Component Responsibility

- 渲染球体线框网格。
- 渲染上下半球的双色网格。
- 渲染绿色水平面和黑色核心体。
- 渲染主场景坐标轴和左下角缩略坐标框。
- 渲染活跃声源点位。

## Data Contract

### Inputs

- `sourcePositions`
- `theme.axisBlue`
- `theme.axisOrange`
- `theme.axisGreen`

### Rules

- `sourcePositions` 必须允许为空或未定义，组件需回退到稳定的预览数据。
- 默认姿态要接近参考图的俯视角观察效果。
- 小坐标框必须显示 `X / Y / Z` 三轴。

## Visual Requirements

- 球体需要占据该区域的主要视觉面积，不能缩在底部。
- 上半球网格为蓝色，下半球网格为棕色。
- 球体中间存在绿色水平面。
- 水平面中心存在黑色核心体，形态接近黑色方芯。
- 主场景三轴颜色区分明确：
  - X 轴偏橙色
  - Y 轴偏蓝色
  - Z 轴偏绿色
- 左下角缩略坐标框与主场景轴向一致。

## Interaction Requirements

- 支持鼠标拖拽旋转视角。
- 默认视角无需用户交互也能呈现出与参考图接近的空间结构。

## Technical Constraints

- 使用 `QtQuick3D` 实现，不退化为静态 2D 图。
- 组件不得因为 `sourcePositions` 为 `undefined` 而产生运行时警告。
- 鼠标事件处理需采用显式函数参数形式，避免 QML 废弃警告。

## Non-Goals

- 不实现自由缩放和复杂相机动画。
- 不实现声源轨迹历史回放。

## Acceptance Criteria

1. 默认尺寸下球体、绿色平面、黑色核心和三轴都清晰可见。
2. 左下角存在完整的 `X / Y / Z` 缩略坐标框。
3. 组件启动时没有 `undefined` 属性访问错误和废弃信号参数警告。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/SourceSphereView.qml`
- `uv run temporal`
