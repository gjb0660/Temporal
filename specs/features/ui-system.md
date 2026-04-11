---
title: ui-system
tracker: primary-feature
status: active
owner: codex/ui
updated: 2026-04-10
---

## Goal

完成主界面的视觉层级、操作布局与共享展示语义收口，使三栏结构、控制区、图表与 3D 视图具备统一的操作与阅读体验。

## Non-Goals

- 不拥有 preview-mode 入口与 PreviewBridge 启动职责。
- 不拥有远端控制、录音状态机或 SSS 路由真源。

## Facts

- 主界面当前是三栏结构，并已形成控制区、图表区、3D 区的稳定信息层级。
- `preview-mode` 与 production 共享同名 `appBridge` 契约与同一投影实现层。
- runtime 已稳定投影 `sourceRowsModel`、`sourcePositionsModel`、`elevationChartSeriesModel`、`azimuthChartSeriesModel` 与筛选状态。
- runtime/preview 的语义分工已固定：preview 负责 scenario 数据推进，runtime 负责 SST 输入与窗口维护；展示投影共享。
- 当前可视化语义已固定：row/3D 基于 current frame，chart 基于共享时间窗，三者共享同一过滤语义。
- 图表固定窗口、主刻度与颜色一致性等稳定约束已由 `specs/contracts/ui/chart-canvas.md` 承接。
- potential 叠加层的过滤、节流、色阶与层级语义已由 `specs/contracts/potential-overlay.md` 单一拥有。
- 图表后端路线结论已由 `ui-system-refactor-chart-canvas` 承接，`ui-system` 只消费其上层展示边界。
- row 的对象目录语义与可见过滤语义已解耦：row 可保留共享历史窗口内的历史 source，chart/3D 仅消费当前可见子集。
- tracking 身份映射约束由 `specs/contracts/tracking-identity.md` 单一拥有；`ui-system` 仅消费 `targetId` 身份输出。
- runtime 已收口性能策略：SST 高频摄取与 chart 模型提交解耦，默认 20Hz 提交；row/3D 仍按当前帧实时投影。
- source 颜色由 bridge 输出并按空间目标连续性保持稳定映射，row/3D/chart 共享同一映射；颜色身份主键为 `targetId`。
- `sourceId` 在输入侧可作为短期跟踪标识展示，但不再作为展示身份主键。
- bridge 已稳定输出历史行保留、颜色稳定与按活跃优先/最新历史优先裁剪所需的共享 row 语义，供右栏与跨视图展示一致消费。
- 运行态下 row 会随 SST/tick 高频刷新；若刷新链路持续整表重建，右栏 checkbox 单击会与刷新竞争并出现“点不动/回弹”体感。

## Decision

- `ui-system` 继续作为共享展示语义 owner，统一维护布局、投影、过滤、空态与时序展示边界。
- QML 只消费 bridge 输出，不复制业务推导；runtime/preview 继续在同一 projection 层演进。
- row/chart/3D 的过滤与空态契约保持冻结，后续演进只能走 shared projection 单路径收敛。
- 颜色语义与图表时间窗只通过共享 bridge/projection 输出消费，不在 QML 或下游 feature 中复制业务语义。
- potential 语义只通过共享 bridge/projection 输出消费，并统一引用 `specs/contracts/potential-overlay.md`。
- 颜色语义由 bridge 颜色账本单一路径维护；MUST NOT 在 projection/QML 引入并行颜色业务语义或业务 fallback。
- `sourceId` 漂移与 `targetId` 连续性语义由 `specs/contracts/tracking-identity.md` 拥有；`ui-system` 仅定义展示消费行为。
- 行状态（`active`/灰态）由 `targetId` 判定；MUST NOT 按展示 `sourceId` 推导。
- 右栏勾选交互写入路径以 `targetId` 为唯一身份锚点；MUST NOT 再以 `sourceId` 作为交互主键。
- runtime 在 bridge 层保持单一行为真源；MUST NOT 并行维护两套筛选、模型刷新与状态推导逻辑。
- 模型刷新必须保持用户单击原子性：无数据变化的刷新 MUST NOT 触发整表 reset。
- 图表后端路线与迁移门槛由 `ui-system-refactor-chart-canvas` 单独拥有；`ui-system` 不重复承载其实现裁决。

## Acceptance

1. 三栏布局在默认尺寸与较窄窗口下保持稳定层级。
2. 左侧控制区只呈现必要的操作按钮与对应状态。
3. 3D 声源区、标题层级与整体主题满足既定视觉目标。
4. 右栏 row 与 3D 共享 current frame 语义，chart 使用共享时间窗序列，三者共享同一过滤语义。
5. 取消最后一个勾选 source 后，row 集合保持稳定，只有图表与 3D 变空。
6. 关闭“筛选器-声源”总开关后，row 集合保持稳定且可继续勾选，只有图表与 3D 变空。
7. row 的历史保留语义与 chart / 3D 的当前可见集保持分离；source 在当前帧消失后，row 与 chart 点迹在共享历史窗口内继续保留，超出窗口后自动移除。
8. chart 在连接首帧显示 `0`，发生重连后重新从 `0` 起算。
9. chart 行为持续满足 `specs/contracts/ui/chart-canvas.md`，且 `ui-system` 不再复写其中的稳定约束。
10. 同一目标短时重现且 `sourceId` 漂移时，row / chart / 3D 颜色保持稳定并与 runtime / preview 一致。
11. 历史窗口内列表行颜色不重复；当历史目标超过调色板容量时，行集合按“活跃优先 + 最新历史优先”裁剪并与 runtime / preview 一致。
12. `ui-system` 与 `ui-system-refactor-chart-canvas` 的 owner 边界保持一致，不出现路线冲突或重复裁决。
13. 运行态（含 preview tick 连续推进）下右栏 checkbox 单击一次即可稳定生效，不因高频刷新出现“点不动/自动回弹”。
14. 当同一空间目标在连续性窗口内发生 `sourceId` 漂移时，勾选状态随 `targetId` 连续保持，不因展示 `sourceId` 变化丢失。

## Plan

1. 收敛页面结构、卡片比例与视觉层级。
2. 收敛控制区的按钮布局与文案。
3. 收敛 3D 视图强调与整体主题风格。
4. 补齐 production bridge 的图表序列投影，使其与 row/3D 的过滤语义一致。
5. 为 runtime 与 preview 的展示 parity 建立可重复验证入口。

## Progress

- [x] 已完成三栏结构与布局节奏调整。
- [x] 已收敛左侧按钮区与日志区比例。
- [x] 已完成 3D 区域强调与整体主题方向收口。
- [x] 已识别共享 bridge 契约与数据投影属于 ui-system owner。
- [x] 已冻结 row 稳定、3D 过滤与空态判定的首批行为语义。
- [x] 已在 runtime `AppBridge` 收口 elevation/azimuth chart series 投影。
- [x] 已抽离 shared projection layer，并由 runtime 与 preview 共同消费。
- [x] 已同步 chart 后端路线 owner 边界，`ui-system` 不再重复裁决实现路线。
- [x] 已将右栏 checkbox 写入路径收口为 `targetId` 单一路径，并消除无变化刷新触发的整表 reset。

## Todo

- [ ] 若后续新增展示轴或筛选维度，需先在 shared projection layer 扩展后再进入 bridge 层。
