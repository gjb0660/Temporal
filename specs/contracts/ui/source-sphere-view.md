---
title: source-sphere-view
status: active
stability: flexible
version: 0.2
---

## Role

定义三维声源球作为空间位置感知锚点。
该 Contract 约束球面网壳、坐标语义、点位身份和旋转观察的稳定体验。

## Invariants

- 声源球 MUST 在默认状态下持续呈现球体网壳、水平盘、核心体和 `X / Y / Z` 方向提示；MUST NOT 退化为无方向感的普通点云。
- 坐标轴语义 MUST 保持 `X=橙色`、`Y=绿色`、`Z=蓝色`，且主场景轴 MUST 只显示正半轴。
- ODAS 坐标到视图坐标的映射 MUST 保持 `Z-up` 语义下的右手空间一致性；MUST NOT 因实现重构改变用户对空间方向的理解。
- 组件 MUST 支持 tracked 与 potential 双层叠加。
- tracked 点位颜色 MUST 保持与 source 身份稳定对应，并只渲染当前可见 tracked 子集。
- potential 叠加层 MUST 与 tracked 身份语义分离；MUST NOT 伪造 potential 稳定身份 id。
- potential 点位的色阶、大小、尾迹、层级、材质与颜色格式规则 MUST 引用 `specs/contracts/potential-overlay.md`；组件 MUST NOT 并行定义。
- 组件 MUST NOT 本地生成 preview fallback 点位或并行业务真源轨迹。
- 空模型或缺失模型 MUST 仍能安全渲染空球体；MUST NOT 产生运行时警告或伪造数据。
- 鼠标左键拖拽旋转 MUST 保持可用，且缩略坐标框 MUST 随当前朝向同步更新。
- 在转到背面后，上下拖拽语义 MUST 继续稳定；MUST NOT 出现 pitch 方向反转。
- 经线与纬线 MUST 保持均匀角度划分，MUST NOT 出现手工不等距分段。
- 水平盘 MUST 继续表达赤道参考面语义，且 MUST NOT 让背面的网壳和点位完全失去可辨认性。
- 核心体 MUST 保持为可辨认的黑色方形薄芯片语义；MUST NOT 退化为难以辨识方向层次的厚块堆叠。

## Variation Space

- 球壳密度、材质、相机参数和点位大小 MAY 演进，只要整体空间语义仍然清晰。
- 默认视角和拖拽灵敏度 MAY 调整，但不得破坏方向映射的一致性。
- 视觉近似方式 MAY 重写，但上半球、下半球、水平盘和核心体的层次语义 MUST 保持可辨认。

## Rationale

- 三维球体承担的是空间方向感，而不是单纯装饰；坐标轴和稳定颜色是用户建立空间记忆的关键。
- 空模型安全渲染可以让用户区分“当前没有可见声源”和“视图自身损坏”。

## Anti-Patterns

- 改变轴颜色或坐标映射却不保留同等清晰的方向语义。
- 在没有 bridge 数据时本地伪造点位或轨迹。
- 把球体简化成无法表达方向关系的二维占位图。
- 让水平盘完全遮挡背面点位与网壳。
- 把 potential 强行映射到 tracked source 行身份，造成身份语义污染。
