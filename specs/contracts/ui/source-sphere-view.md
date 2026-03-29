---
title: source-sphere-view
status: active
stability: flexible
version: 0.1
---

## Role

定义三维声源球作为空间位置感知锚点。
该 Contract 约束球面网壳、坐标语义、点位身份和旋转观察的稳定体验。

## Invariants

- 声源球 MUST 在默认状态下持续呈现球体网壳、水平盘、核心体和
  `X / Y / Z` 方向提示，MUST NOT 退化为无方向感的普通点云。
- 坐标轴语义 MUST 保持 `X=橙色`、`Y=绿色`、`Z=蓝色`。
- ODAS 坐标到视图坐标的映射 MUST 保持 `ODAS(x, y, z) ->
  QtQuick3D(x, z, -y)`，以维持 `Z-up` 语义下的右手坐标系；实现重构
  MUST NOT 改变用户对空间方向的理解。
- 点位颜色 MUST 保持与 source 身份稳定对应；组件 MUST 只渲染当前可见
  source 子集，MUST NOT 本地生成 preview fallback 点位或历史轨迹。
- 空模型或缺失模型 MUST 仍能安全渲染空球体，MUST NOT 产生运行时警告
  或伪造数据。
- 鼠标左键拖拽旋转 MUST 保持可用，且缩略坐标框 MUST 随当前朝向同步更新。
- 在转到背面后，上下拖拽语义 MUST 继续稳定，MUST NOT 出现 pitch
  方向反转。
- 经线与纬线 MUST 按均匀角度划分，MUST NOT 出现手工不等距分段。
- 水平盘 MUST 与赤道大圆重合，MUST NOT 明显缩小一圈。
- 水平盘的透明度与深度写入策略 MUST 保证背面的网壳和点位仍可辨认，
  MUST NOT 被完全遮挡。
- 默认窗口尺寸下，球体与缩略坐标框 MUST 保持在组件边界内，MUST NOT
  从底边溢出。

## Variation Space

- 球壳密度、材质、相机参数和点位大小 MAY 演进，只要整体空间语义仍然
  清晰。
- 默认视角和拖拽灵敏度 MAY 调整，但不得破坏方向映射的一致性。
- 视觉近似方式 MAY 重写，但上半球、下半球、水平盘和核心体的层次语义
  MUST 保持可辨认。

## Rationale

- 三维球体承担的是空间方向感，而不是单纯装饰；坐标轴和稳定颜色是用户
  建立空间记忆的关键。
- 空模型安全渲染可以让用户区分“当前没有可见声源”和“视图自身损坏”。

## Anti-Patterns

- 改变轴颜色或坐标映射却不保留同等清晰的方向语义。
- 在没有 bridge 数据时本地伪造点位或轨迹。
- 把球体简化成无法表达方向关系的二维占位图。
