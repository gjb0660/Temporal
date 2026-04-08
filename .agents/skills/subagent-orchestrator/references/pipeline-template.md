# Pipeline Template

用于在 `specs/todo/` 下编写时间顺序的多代理编排文档。
例如：

- `specs/todo/2026-04-03-subagents-orchestration.md`

## Goal

说明这份编排文档存在的目的、目标 feature、以及期望的收敛结果。

- feature 真源：`<feature-spec-path>`
- 本文档产出目标：`<一句中文目标>`

## Inputs

列出执行前冻结的输入条件。

- 参与代理数量：`<N>`
- ownership 切片原则：`<按文件/模块/子域>`
- 约束：`<例如 不改QML/不新增测试/仅backend>`
- 阶段门禁来源：`<feature/specs/contracts>`
- delegation 准入快照：`source/category/stage/sync-risk/delegation`

## Global Contract

描述全局不变规则（适用于全部阶段）。

### Serial Segments

以下节点必须串行：

1. 阶段启动前冻结（目标、ownership、门禁、提交策略）。
2. 阶段收敛评审（semantic + pollution）。
3. 通过 `$converge-commit` 完成 stage close 原子提交。
4. stage-sync checkpoint。
5. 下一阶段准入判定。

### Parallel Segments

以下规则仅在阶段内部并行窗口生效：

1. 并行只在阶段开发窗口内开启。
2. 每个代理仅在自身 ownership 内改动。
3. 出现越界或重叠改动时，立即冻结并转串行裁决。
4. 收敛窗口关闭后，不允许继续新增改动。

### Agent Lifecycle

说明代理生命周期策略：

1. 在 `<start-stage>` 创建代理。
2. 在各阶段之间复用同一代理（及其工作分支/工作树）。
3. 仅在最终门禁通过后统一关闭代理。

## Stage Plan

先列阶段清单，再按模板展开每个阶段。阶段数量不设上限，不要求固定命名。
每个阶段收口都必须填写 lookahead 记录（可写 `none` 并给理由）。

### Stage List

按时间顺序填写阶段清单：

1. `<Stage-ID>: <Stage-Name>`
2. `<Stage-ID>: <Stage-Name>`
3. `<Stage-ID>: <Stage-Name>`

### Stage Block Template

对每个阶段使用以下模板。

#### Stage `<Stage-ID>`: `<Stage-Name>`

- 类型：`main | cluster-substage | optional`

Entry Gates：

1. `<进入条件1>`
2. `<进入条件2>`

Parallel Tasks (A/B/C... ownership)：

1. Agent A: `<任务 + ownership>`
2. Agent B: `<任务 + ownership>`
3. Agent C: `<任务 + ownership>`

说明：可按需要扩展为 `A/B/C/D/...`，不代表固定三代理上限。

Convergence Gates：

1. `<收敛条件1>`
2. `<收敛条件2>`
3. `<收敛条件3>`

Serial Close：

1. `<串行收口动作1>`
2. `<串行收口动作2>`

Exit Criteria：

1. `<退出门禁1>`
2. `<退出门禁2>`
3. `lookahead: <read-only prep list | none with reason>`

### Cluster Block Template (Optional)

当多个子阶段必须合并为一次提交时使用。

#### Cluster `<Cluster-ID>`: `<Cluster-Name>`

- 子阶段：`<Stage-A>, <Stage-B>, <Stage-C>`
- 提交策略：`cluster close 时一笔提交`

Cluster Close Gates：

1. 子阶段门禁全部通过。
2. 不得绕过 cluster-level full gate。
3. 不得绕过 cluster-level stage-sync。

### Lookahead Block (Required At Stage Close)

每个阶段收口都必须填写。若无安全只读任务，显式记录 `none` 并给出理由。

#### Lookahead `<From-Stage>` -> `<Next-Stage>`

只读准备任务：

1. Agent `<X>`: `<read-only prep task>`
2. Agent `<Y>`: `<read-only prep task>`

约束：

1. 只允许只读分析与证据整理。
2. 不得修改当前阶段 ownership 文件。
3. 不得绕过当前阶段关闭门禁。
4. 若 `lookahead=none`，必须写明理由。

## Gates

列出本任务的门禁与判定口径。

Required Gates：

1. `<gate command or check>`
2. `<gate command or check>`
3. `<gate command or check>`

Mandatory Convergence Checklist：

1. 每个代理提交 acceptance-mapping。
2. 每个代理提交 pollution-check。
3. supervisor 完成 ownership overlap 审核。
4. supervisor 完成 semantic 审核。
5. stage-sync checkpoint 通过。

Failure Handling：

1. 任一门禁失败，回到当前阶段并行窗口修复。
2. 未满足退出门禁时，禁止推进下一阶段。

## Commit Policy

使用规则式提交策略，不固定提交笔数。

- 主阶段策略：`main stage close must converge through $converge-commit before atomic submit`
- 集群阶段策略：`approved cluster close must converge through $converge-commit before atomic submit`

Commit Mapping（按实际阶段填写）：

| Stage/Cluster | Commit Message |
| --- | --- |
| `<Stage-ID or Cluster-ID>` | `<short english message>` |
| `<Stage-ID or Cluster-ID>` | `<short english message>` |

## Execution Record

定义阶段收口记录模板；按阶段数量重复填写。

### Stage Record Template

主契约块（required）：

1. `source`
2. `category`
3. `stage`
4. `sync-risk`
5. `delegation`
6. `semantic-gate`
7. `pollution-gate`
8. `static-gate`
9. `atomic-submit`
10. `cleanup`

附录块（required）：

1. `task-slice`
2. `acceptance-mapping`
3. `pollution-check`
4. `ownership-check`
5. `atomic-commit-summary`
6. `stage-sync`
7. `remaining-risk`
8. `divergence-events`
9. `lookahead`

可选执行痕迹（optional）：

1. `red-findings`
2. `green-fixes`
3. `refactor-cleanups`

### High-Risk Simulation (Mandatory Final Round)

在最后一轮收口阶段必须填写：

| scenario-id | trigger-sequence | expected-invariants | observed-result | defect-id | fix-commit-reference |
| --- | --- | --- | --- | --- | --- |
| `<R*>` | `<...>` | `<...>` | `pass/fail` | `<id/none>` | `<sha/n-a>` |

### Final Close Record (Mandatory At Final Close)

最终收口必须填写：

主契约块（required）：

1. `source`
2. `category`
3. `stage`
4. `sync-risk`
5. `delegation`
6. `semantic-gate`
7. `pollution-gate`
8. `static-gate`
9. `atomic-submit`
10. `cleanup`

附录块（required）：

1. `stability-slo-window-minutes`
2. `uncontrolled-drift-events`
3. `final-pollution-delta`
4. `stage-sync`
5. `remaining-risk`
6. `hardening-result: pass|fail`
7. `hardening-fail-action`（当 `hardening-result=fail` 必填）

关闭规则：

1. `hardening-result=fail` 时，默认阻断 final close。
2. 必须执行修复或降级处理并复验后，才能关闭。
