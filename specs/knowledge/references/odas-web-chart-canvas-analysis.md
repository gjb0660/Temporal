# ODAS Web Chart Canvas Analysis

## 1. Research Objective

本文件仅记录 `D:\Workspace\odas_web` 中图表画布相关设计的源码事实，
用于沉淀独立可引用的证据层材料。

## 2. Source Scope

Source level: direct source fact

本次分析限定以下文件：

- `views/live_data.html`
- `resources/js/graph.js`
- `resources/js/interface.js`
- `resources/js/tcp_link.js`
- `resources/js/odas_launcher.js`

## 3. Direct Source Facts

### 3.1 Canvas Host And Script Wiring

Source level: direct source fact

`views/live_data.html` 在 center layout 放置两张 `<canvas class="graph">`：

- `Source Elevation`
- `Source Azimut`

同页脚本顺序中，`Chart.bundle.min.js` 与 `graph.js` 在 sphere 与其他模块前后
独立加载，图表绘制逻辑由 `graph.js` 驱动。

### 3.2 Chart Instance Model

Source level: direct source fact

`graph.js` 定义 `ChartBundle`，每个 bundle 内包含：

- `datasets`（tracked source 曲线）
- `pdatasets`（potential source 点集）
- 对应数据容器 `cdata` 与 `pdata`

页面中每个 `.graph` canvas 初始化一个 `ChartBundle` 和一个 Chart.js `line` 图。

### 3.3 Window And Refresh Policy

Source level: direct source fact

`graph.js` 使用固定窗口参数：

- `totalFrames`: desktop 为 80，mobile 为 40
- `refreshFrame`: 20
- `dataMin/dataMax`: x 轴可见区间

tracked 数据追加后，当数组长度超过 `totalFrames` 会执行 `shift()`，
从而维持固定窗口。

### 3.4 Axis And Visual Configuration

Source level: direct source fact

图表配置包含以下稳定项：

- `type: "line"`
- `xAxes[0].type: "linear"`
- `xAxes[0].scaleLabel.labelString: "Sample"`
- y 轴范围：elevation `[-90, 90]`，azimuth `[-180, 180]`
- y 轴步长：elevation `30`，azimuth `60`
- `animation: false`
- `tooltips.enabled: false`
- `legend.display: false`
- `responsive: true`
- `maintainAspectRatio: false`

### 3.5 Tracking Event Update

Source level: direct source fact

`document` 的 `tracking` 事件驱动 tracked 更新：

- 每 `refreshFrame` 次事件执行一次图表写入
- source active 时写入角度值
- source inactive 时写入 `{x: timestamp, y: null}`
- 更新时间窗后触发 `request-chart`

### 3.6 Potential Event Update

Source level: direct source fact

`potential` 事件驱动 potential 点集更新：

- 根据 `energyIsInRange` 过滤后写入 `pdata`
- `pdatasets` 使用 `showLines: false`，以散点呈现
- 无 potential 命中时写入 `y: null` 占位

### 3.7 Selection And Visibility

Source level: direct source fact

`update-selection` 与 `potential-visibility` 事件分别控制：

- tracked datasets 的 `hidden`
- potential pdatasets 的 `hidden`

图表重绘通过统一 `request-chart` 事件触发。

### 3.8 Reset And Idle Cleanup

Source level: direct source fact

清空语义由 `clearChart` 事件统一执行：

- tracked/potential 数据数组清零
- tracking 与 potential 各自维护 10 秒 watchdog；
  超时触发清空并取消对应 timer

`odas_launcher.js` 在连接切换后也会异步触发 `clearChart`。

## 4. Source-Based Inferences

Source level: inference from source

1. `odas_web` 的图表层是事件驱动模型，`tracking/potential` 事件是主时序入口。
2. 图表窗口语义是“固定容量滑动窗”，不是无限累计历史。
3. tracked 与 potential 共用同一坐标系统，但在视觉通道上区分为线与点。
4. `y: null` 在 tracked/potential 两条路径都被用作缺口占位语义。
5. 清空策略是“显式事件 + 超时 watchdog”双保险。

## 5. Summary

`odas_web` 图表实现可归纳为：

- 两张线性时间轴图（elevation / azimuth）
- tracked 线 + potential 点的双通道叠加
- 固定窗口滚动与显式清空机制
- 事件驱动的数据更新与可见性控制

以上结论均来自 `odas_web` 源码，不包含跨项目映射结论。

## References

- `D:/Workspace/odas_web/views/live_data.html`
- `D:/Workspace/odas_web/resources/js/graph.js`
- `D:/Workspace/odas_web/resources/js/interface.js`
- `D:/Workspace/odas_web/resources/js/tcp_link.js`
- `D:/Workspace/odas_web/resources/js/odas_launcher.js`
