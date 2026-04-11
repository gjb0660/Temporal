---
title: tracking-identity
status: active
stability: strict
version: 0.2
---

## Role

定义 tracking 层对 `sourceId` 与 `targetId` 身份关系的唯一约束真源。
该 Contract 约束空间目标连续性与身份映射边界，供 UI/bridge/recording 作为消费前提。

## Invariants

- tracking 输出的 `visible_targets` MUST 以 `targetId` 表达连续身份；下游 MUST 以 `targetId` 作为身份锚点。
- tracking MUST 先按 `sample` 降序、`sourceId` 升序对观测排序，并仅保留前 `8` 条进入可见身份匹配。
- 在同一帧的 `visible_targets` 中，`sourceId` 与 `targetId` MUST 分别保持一对一（无重复）。
- 连续性匹配 MUST 在连续性窗口（默认 `1600` samples）和角度阈值（默认 `20.0` 度）内进行。
- 连续性匹配目标 MUST 优先最大化匹配条数，再最小化角度代价；MUST NOT 为局部最小角度牺牲匹配覆盖率。
- 当目标在连续性窗口（默认 `1600` samples）内被匹配时，`targetId` MUST 保持连续；`sourceId` MAY 漂移。
- 当目标超出连续性窗口并重新出现时，tracking MAY 分配新 `targetId`。
- 当可见候选超过 palette 容量时，tracking MUST 在 `dropped_source_ids` 中记录被丢弃的 `sourceId`。
- 下游 consumer MUST NOT 重新定义 `sourceId` 复用冲突裁决；consumer 仅消费 tracking 输出。
- 若上游输入违背本 Contract 的身份前提，下游 consumer MAY 静默忽略异常映射；MUST NOT 因兼容而引入并行身份规则或抛错分支。

## Variation Space

- 连续性匹配算法、代价函数与阈值 MAY 演进，只要上述身份不变量保持。
- palette 分配与目标淘汰策略 MAY 调整，只要不破坏 `targetId` 身份锚点语义。
- 下游展示层 MAY 演进 `sourceId` 的呈现方式，但 MUST NOT 改写 tracking 的身份归属。

## Rationale

- 身份语义必须单源定义；否则 UI/bridge 与 tracking 并行裁决会造成状态漂移。
- 将冲突裁决留在 tracking owner，可以让消费层保持最小实现和稳定行为。

## Anti-Patterns

- 在 UI 或 bridge 层基于展示 `sourceId` 再推导一套身份映射。
- 为偶发违约输入在下游添加“第二套”冲突修复规则。
- 将 `sourceId` 当作跨帧稳定身份主键。
