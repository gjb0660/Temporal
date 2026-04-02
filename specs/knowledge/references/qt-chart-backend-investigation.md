# Qt Chart Backend Investigation

## 1. Overview

本文用于归档 `QtCharts vs QtGraphs vs Canvas` 的调查结论，作为
`ui-system-refactor-chart-canvas` 的证据基础。

调查时间：2026-04-02
调查范围：官方文档事实 + 当前仓库本地复现实验
调查目标：锁定 chart 后端长期路线，避免路线反复摇摆。

## 2. Environment Snapshot

- OS: Windows（本地开发环境）
- Python: `3.10`
- PySide6: `6.8.3`
- 当前 UI 图表实现：`src/temporal/qml/ChartCanvas.qml` 使用 `QtCharts` + `ChartView`
- 当前入口：`src/temporal/main.py` 与 `src/temporal/app.py` 使用 `QGuiApplication`

## 3. First-Principles Frame

- 不可谈判目标 1：启动稳定性（不崩溃）
- 不可谈判目标 2：contract 语义稳定（时间窗、gap、颜色一致性）
- 不可谈判目标 3：生命周期可持续（避免被弃用路径锁死）
- 奥卡姆剃刀约束：优先选择“最少额外假设且长期可维护”的方案

## 4. Official Evidence

- `Qt Charts` 文档标注自 Qt 6.10 起 deprecated，并建议新项目使用 `Qt Graphs`。
- 同页标注：Qt Quick 模板默认 `QGuiApplication` 需要替换为 `QApplication`，才能满足 `Qt Charts` 渲染前提。
- `Qt Graphs Migration from Qt Charts` 提供了明确迁移路径，但指出了 6.8 代际差异，例如标题、图例等缺口仍需按实际需求核对。
- `Canvas` 文档明确提示：对 `Canvas.Image` 路径应避免“大画布 + 频繁更新 + 动画”，且建议优先考虑 `QQuickPaintedItem`（C++/QPainter）而非 JS/Context2D。

## 5. Local Reproduction Evidence

2026-04-02 在当前仓库进行最小复现：

- 路径 A：`QGuiApplication` + `Main.qml`（含 `QtCharts`）
  - 结果：复现 `Windows fatal exception: access violation`
  - 进程退出码：`-1073741819`
- 路径 B：`QApplication` + 同一加载路径
  - 结果：可完成加载（`roots=1`），未复现上述崩溃

结论：当前优先级最高的一阶问题是“启动前提不满足”而非“图表视觉差异”。

## 6. Option Comparison Matrix

### QtCharts

- 生命周期信号是官方已 deprecated（Qt 6.10+）。
- contract 拟合高，当前已落地。
- 稳定性风险中到高，当前入口前提可触发崩溃。
- 工程成本低到中。
- 结论：禁用。

### QtGraphs

- 生命周期信号是官方推荐替代路线。
- contract 拟合中到高，但需要迁移与回归。
- 稳定性风险中等，且需要处理版本差异。
- 工程成本中等。
- 结论：长期目标态。

### Canvas (QML/JS)

- 生命周期信号是未弃用，但官方有高频更新警示。
- contract 拟合中等，可实现但易把复杂度放入 JS 渲染。
- 稳定性风险中到高，高频更新路径不占优。
- 工程成本中到高。
- 结论：短期过渡态（受限使用）。

### QQuickPaintedItem (C++)

- 生命周期信号是可行，但属自研渲染路径。
- contract 拟合中等，需要自建绘制与桥接。
- 稳定性风险中等，性能与线程细节需精细控制。
- 工程成本高。
- 结论：非当前优先项。

## 7. Decision Boundaries

- 路线锁定：
  - 目标态：`QtGraphs`
  - 过渡态：`Canvas`（仅风险控制用途）
  - 禁止态：`QtCharts`
- 过渡态退出触发（全部满足）：
  1. 版本窗口允许进入 Qt 6.10+ 策略
  2. `QtGraphs` 满足 chart contract 语义回归
  3. runtime/preview parity 回归通过
- 重新评估 `Canvas` 的唯一入口是出现新的可验证反证数据，且该数据能够推翻本调查中的官方与实验事实。

## 8. References

- [Qt Charts C++ Classes (Qt 6.11)](https://doc.qt.io/qt-6/qtcharts-module-qtcharts-obsolete.html)
- [Qt Graphs Migration from Qt Charts (Qt 6.11)](https://doc.qt.io/qt-6/qtgraphs-migration-guide-2d.html)
- [Canvas QML Type (Qt 6.11)](https://doc.qt.io/qt-6/qml-qtquick-canvas.html)
- [QQuickPaintedItem Class (Qt 6.11)](https://doc.qt.io/qt-6/qquickpainteditem.html)
- [What's New in Qt 6.8](https://doc.qt.io/qt-6.8/whatsnew68.html)
