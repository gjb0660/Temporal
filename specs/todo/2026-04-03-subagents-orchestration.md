# AppBridge 3-Subagent Orchestration Pipeline

## 1. Objective

本文档定义 `app-bridge-refactor-modularization` 的时间顺序执行流水线。
目标是让 3 个子代理在固定 ownership 下并行开发，在严格串行门禁下收敛。

执行真源：`specs/features/app-bridge-refactor-modularization.md`

## 2. Global Execution Contract

### 2.1 Global Serial Segments

以下节点全局必须串行：

1. Stage 启动前冻结（目标、ownership、门禁、commit message）。
2. Stage 收敛评审（semantic gate + pollution gate）。
3. Stage 原子提交（仅 supervisor 提交）。
4. Stage 同步检查（stage-sync checkpoint）。
5. 下一 Stage 启动判定（仅在本 Stage 全门禁 pass 后）。

### 2.2 Intra-Stage Parallel Segments

并行窗口只在每个 Stage 的开发期开放：

1. Agent A/B/C 按固定 ownership 并行开发与自测。
2. 禁止跨 ownership 改动；发现冲突立即冻结冲突文件并转 supervisor 串行裁决。
3. 并行窗口关闭后，进入串行收敛，不允许继续新增改动。

### 2.3 Agent Lifecycle (Reused To End)

1. Agent A/B/C 在 Stage 1A 启动时创建。
2. 全阶段复用同一 agent + 同一 worktree（Stage 1A 到 Stage 5）。
3. 每阶段结束只做 `stage-sync checkpoint`，不关闭 agent。
4. 最终 Stage 5 全门禁通过后，统一关闭 agent 并清理 worktree。

## 3. Fixed Ownership

1. Agent A：门面与导入链路（`temporal.app.bridge`、运行入口、调用方导入）。
2. Agent B：`remote lifecycle` + `stream/projection`。
3. Agent C：`recording/audio routing` + `status/state helpers` + tests 迁移执行（Stage 1C）。

## 4. Timeline Pipeline

### Stage 0 (Spec Baseline, Serial Only)

进入条件：

1. feature/knowledge 无冲突。
2. 当前阶段目标与门禁文本冻结。

执行动作：

1. 固化 acceptance mapping（仅当前 Stage 条目）。
2. 固化 ownership 与文件边界。
3. 固化 commit 策略与本阶段 commit message（短英文）。

退出条件：

1. 无未决策略项。
2. Agent 创建前置条件满足。

---

### Stage 1 Cluster (1A + 1B + 1C, One Commit)

#### Stage 1A: 目录与门面切换

并行窗口任务：

1. A：目录形态与 `bridge` 门面落位，运行入口切换。
2. B：remote/stream 路径适配到新门面链路（仅本域）。
3. C：recording/status 路径适配到新门面链路（仅本域）。

子阶段收敛条件：

1. 新门面可导入。
2. 主运行路径可用。
3. 无 ownership 重叠。

#### Stage 1B: 业务域抽离

并行窗口任务：

1. B：抽离 remote+stream 业务编排。
2. C：抽离 recording+status 业务编排。
3. A：门面收敛为装配与委派，移除业务编排。

子阶段收敛条件：

1. 四子域边界稳定。
2. 门面不承载业务编排。
3. 无跨域文件污染。

#### Stage 1C: 调用方与测试迁移收口

并行窗口任务：

1. A：调用方 import 迁移到 `temporal.app.bridge`。
2. B：remote/stream 相关 tests import/patch 迁移。
3. C：recording/status 相关 tests import/patch 迁移并删除冗余 case。

子阶段收敛条件：

1. 四套主回归恢复可跑。
2. 不再依赖旧导入与旧 patch 锚点。
3. 未新增 test case。

#### Stage 1 Cluster 串行收口

1. supervisor 审核 1A/1B/1C 全量 diff（semantic + pollution）。
2. 仅在 1C 完成后提交 **Commit #1**（Stage 1A+1B+1C 一笔提交）。
3. 执行 stage-sync checkpoint（A/B/C 全部 rebase 到 Commit #1）。
4. 任一 agent 同步失败，回到 Stage 1 Cluster 修复，不得进入 Stage 2。

---

### Stage 2 (Preview 组合化, Commit #2)

并行窗口任务：

1. A：守住 Preview 外观契约。
2. B：组合化接入 remote/stream 共享能力。
3. C：组合化接入 recording/status 共享能力。

收敛条件：

1. Preview contract 不变。
2. 组合化路径生效。
3. 全门禁通过。

串行收口：

1. supervisor 提交 Commit #2。
2. 执行 stage-sync checkpoint。

---

### Stage 3 (线程安全收敛, Commit #3)

并行窗口任务：

1. B：listener 输入到 queued signal 桥接链路。
2. C：Qt 对象状态写入集中到 QObject 所在线程。
3. A：门面线程边界守卫与路径核验。

收敛条件（硬门禁）：

1. 不存在后台线程直接触发任何 Qt 对象状态写入路径。
2. 全门禁通过。

串行收口：

1. supervisor 提交 Commit #3。
2. 执行 stage-sync checkpoint。

---

### Stage 4 (接口瘦身, Commit #4)

并行窗口任务：

1. A：候选公开面移除/内部化实施。
2. B：`src+tests` 静态引用证据整理。
3. C：`qml+specs` 静态引用与 contract 对照证据整理。

收敛条件：

1. 每个候选项满足“静态零引用 + contract 不要求”。
2. 证据记录齐全，可复核。
3. 全门禁通过。

串行收口：

1. supervisor 提交 Commit #4。
2. 执行 stage-sync checkpoint。

---

### Stage 5 (Bugfix + High-Risk Simulation, Commit #5)

输入门禁：

1. Stage 2/3/4 已完成并提交。
2. 三代理 stage-sync checkpoint 已通过。

并行任务：

1. Agent A：门面与导入链路高风险操作模拟。
2. Agent B：remote/stream 事件与并发路径模拟。
3. Agent C：recording/status 与状态机一致性模拟。

可修复范围（硬约束）：

1. 仅线程与状态一致性相关缺陷。
2. 不引入新功能。
3. 不改 QML。
4. 不新增测试 case。

高风险模拟矩阵：

1. `R1` 远端快速切换：连续 `toggleRemoteOdas/toggleStreams` 高频交替。
2. `R2` 监听并发风暴：SST/SSL/PF/SEP 高频突发输入。
3. `R3` 启停竞争：`startRemoteOdas/stopRemoteOdas` 与 timer 回调重叠。
4. `R4` 预览切换竞争：Preview 切换与 runtime 更新并发。
5. `R5` 录音路由竞争：录音会话更新与 source 映射变化并发。
6. `R6` 断连恢复：remote disconnect/reconnect + stream restart。

每个 `R*` 必须记录：

1. trigger sequence
2. expected invariants
3. observed result
4. defect id（若失败）
5. fix commit reference（若有修复）

收敛条件：

1. 高风险模拟矩阵全部执行并记录。
2. 发现缺陷则修复并复验通过。
3. structured execution record 完整。
4. 全门禁通过。

串行收口：

1. supervisor 提交 Commit #5（bugfix commit）。
2. 统一关闭 A/B/C 三代理并清理 worktree。
3. 输出最终 gate 结果（semantic/pollution/atomic/cleanup）。

## 5. Mandatory Convergence Checklist

每个 Stage（或 Stage 1 Cluster）收敛时必须全部满足：

1. 每个代理提交当前阶段 `acceptance-mapping`。
2. 每个代理提交当前 ownership `pollution-check`。
3. supervisor 完成逐代理 diff 审核（无越界、无重叠）。
4. 全门禁通过（以当前 feature spec 为准）。
5. supervisor 完成当前阶段规定提交（Commit #1/#2/#3/#4/#5）。
6. stage-sync checkpoint 通过（3 代理均同步成功）。

任一失败处理：

1. 回退到当前 Stage 并行窗口修复，不得推进下一 Stage。
2. 若出现事实漂移，先更新 feature Facts，再继续本 Stage。

## 6. Gate Commands

每个 Stage 执行以下门禁（按 feature spec）：

1. `uv run pyright --project pyproject.toml`
2. `uv run ruff check src tests`
3. `uv run ruff format src tests`
4. `uv run pyside6-qmllint <qml-files>`
5. `npx markdownlint **/*.md .github/**/*.md`
6. `uv run python -m unittest discover -s tests -p "test_*.py" -v`

强制回归集：

1. `tests.test_app_bridge_integration`
2. `tests.test_app_bridge_recording`
3. `tests.test_preview_bridge`
4. `tests.test_projection_parity`

测试约束：

1. 可更新 tests import/patch 路径。
2. 可删除冗余 case。
3. 禁止新增 case。
4. `1A/1B` 允许临时红，`1C` 起必须恢复绿。

## 7. Commit Plan (Fixed)

1. Commit #1：`Stage 1A + 1B + 1C`
2. Commit #2：`Stage 2`
3. Commit #3：`Stage 3`
4. Commit #4：`Stage 4`
5. Commit #5：`Stage 5 bugfix`

## 8. Structured Execution Record Template

每个提交节点由 supervisor 记录：

1. `task-slice`
2. `red-findings`
3. `green-fixes`
4. `refactor-cleanups`
5. `acceptance-mapping`
6. `pollution-check`
7. `atomic-commit-summary`
8. `stage-sync-check`
9. `cleanup-check`
