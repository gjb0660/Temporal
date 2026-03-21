# Spec: Center Pane View

## Goal

定义 `src/temporal/qml/CenterPane.qml` 的中部内容区需求。
该区域是实时数据页面的视觉核心，
负责承载俯仰角图、方位角图和 3D 声源球，
并只消费 bridge 已整理好的图表 ticks、series 与点位数据。

## Component Responsibility

- 布局两张图表和一张 3D 声源位置视图。
- 在不同窗口宽度下保持标题、间距和视觉主次稳定。
- 消费 `appBridge` 提供的图表 series、横轴 ticks 和 3D 点位数据。

## Data Contract

### Inputs

- `appBridge.sourcePositionsModel`
- `appBridge.elevationSeriesModel`
- `appBridge.azimuthSeriesModel`
- `appBridge.chartXTicksModel`
- `theme.chartHeight`
- `theme.sphereHeight`

### Rules

- 两张图表与 3D 点位必须始终来自同一 bridge 数据源。
- preview 模式下，两张图表与 3D 点位必须共享同一
  `trackingFrames` 时间窗。
- 两张图表与 3D 点位必须共享同一当前可见声源集合。
- 右栏保留当前场景声源 row 及其勾选状态，
  中栏只消费勾选后的可见子集。
- 中栏不再从本地 QML fixture 脚本中读取预览数据。
- 中栏不负责决定哪些声源被选中，只负责消费 bridge 已裁剪后的数据。
- 中栏不在本地维护 preview 横轴 ticks 或运行态 ticks。
- 俯仰角归一化规则为 `(deg + 90) / 180`。
- 方位角归一化规则为 `(deg + 180) / 360`。

## Visual Requirements

- 保持白色主内容面板和稳定垂直间距。
- 声源球区域应明显大于单张图表区域。
- 在较窄窗口下仍需保证标题、边距和边框可读。

## Interaction Requirements

- 中栏本身不提供场景切换控件。
- 当右栏切换声源勾选状态时，中栏显示内容同步变化。
- 当监听开启或关闭时，中栏中的横轴、曲线和 3D 点位同步推进或同步暂停。
- preview 的时间轴滚动方式是：
  在固定的 `trackingFrames` 序列上移动 sample window，
  而不是临时生成新数据。

## Technical Constraints

- 图表绘制和 3D 渲染细节保留在子组件内部。
- 预览场景数据保留在 Python bridge 模块中。
- 中栏不根据 `previewMode` 本地推导图表数据、横轴 ticks 或
  3D 兜底点位。
- 预览基线场景保持为：
  - `referenceSingle`
  - `hemisphereSpread`
  - `equatorBoundary`
  - `emptyState`

## Non-Goals

- 不在该组件中实现 preview 能量过滤逻辑本身。
- 不在本阶段补充正式环境的 `SST` 历史绘制。

## Acceptance Criteria

1. Preview 模式下，图表和 3D 数据始终来自同一活动场景的同一
   `trackingFrames` 时间窗。
2. 切换场景后，中栏与右栏同步刷新。
3. 取消勾选单个声源后，中栏对应图表曲线和 3D 点位同步消失。
4. 监听开启后中栏推进，监听关闭后中栏暂停。
5. `CenterPane.qml` 不再包含本地 `previewMode` /
   `previewScenarioKey` 分支。

## Validation

- `uv run pyside6-qmllint src/temporal/qml/CenterPane.qml`
- 启动 `uv run temporal-preview`，确认中栏随场景切换、监听状态和
  声源勾选同步变化。
