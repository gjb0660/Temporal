# Spec: Source Sphere View

## Goal

定义 `src/temporal/qml/SourceSphereView.qml` 的三维声源位置视图需求。
该组件用于展示活跃声源在球面空间中的位置，
默认观感、轴语义、网壳配色和交互方式均以参考图
`ODAS_Studio.png` 为最终视觉真值。

## Component Responsibility

- 渲染更接近 ODAS Studio 的球体网壳近似，而不是简单经纬线球。
- 渲染上下半球双色网壳、绿色水平盘和黑色核心体。
- 渲染主场景坐标轴和与当前旋转方向一致的左下角缩略坐标框。
- 渲染活跃声源点位并保持同一 source id 的颜色稳定。

## Data Contract

### Inputs

- `sourcePositionsModel`
- `theme.axisBlue`
- `theme.axisOrange`
- `theme.axisGreen`

### Rules

- `sourcePositionsModel` 允许为空或未定义，组件必须安全渲染空球体，
  且不能产生运行时警告。
- 主场景轴语义固定为：
  - X 轴为橙色
  - Z 轴为蓝色
  - Y 轴为绿色
- ODAS 坐标映射固定为 `ODAS(x, y, z) -> QtQuick3D(x, z, y)`。
- 左下角缩略坐标框必须随当前 yaw/pitch 实时更新。
- Preview 模式下，输入点位只能来自当前 frame 的
  `trackingFrames[*].sources` 派生结果。
- 右栏取消勾选后，对应点位必须消失，但右栏 row 不因此被删除。
- 3D 点位与中栏图表必须共享同一当前 frame 和同一可见 source 集合。
- production `AppBridge` 在非 preview 下允许输出空点位 model，
  但不得输出伪造 preview 点位。

## Visual Requirements

- 球体必须占据该区域主要视觉面积，不能下沉到底部。
- 上半球网壳为蓝色，下半球网壳为橙色。
- 球体中部存在半透明绿色水平盘。
- 水平盘中心存在黑色方柱体。
- 点位大小、颜色和球体构图需在默认窗口尺寸下清晰可见。

## Interaction Requirements

- 支持鼠标左键拖拽旋转视角。
- 默认视角无需交互也能呈现接近参考图的空间结构。
- 不实现 hover、点选或联动筛选。

## Technical Constraints

- 使用 `QtQuick3D` 实现，不退化为静态 2D 图。
- 鼠标事件处理使用显式函数参数形式，避免 QML 废弃警告。
- 以轻量近似方式实现球壳，不引入自定义 3D Geometry。
- 组件不在本地合成 preview fallback 点位，所有点位均来自 bridge 输入。
- 3D 点位必须与中栏图表共享同一时序源，
  不允许单独生成动画轨迹。

## Non-Goals

- 不实现自由缩放和复杂相机动画。
- 不实现声源轨迹历史回放。
- 不在该组件内接入后端真实历史曲线数据。

## Acceptance Criteria

1. 默认尺寸下球体、双色网壳、绿色水平盘、黑色核心和三轴都清晰可见。
2. 左下角存在完整的 `X / Y / Z` 缩略坐标框，
   且方向与主场景一致。
3. 组件启动时没有 `undefined` 属性访问错误和废弃信号参数警告。
4. 同一 source id 在重复刷新时颜色保持稳定。
5. 空输入时不显示伪造点位，且不反向触发右栏空态。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/SourceSphereView.qml`
- 使用预览场景 `referenceSingle`、`hemisphereSpread`、
  `equatorBoundary`、`emptyState` 进行本地截图比对
- `uv run temporal`
