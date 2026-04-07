---
title: app-bridge-refactor-modularization
tracker: refactor
status: done
owner: codex/core
updated: 2026-04-07
---

## Goal

在外部能力不扩张的前提下，完成 `AppBridge` backend 结构重构：
将高频变更实现拆分到 `src/temporal/app/` 子模块；
以 `temporal.app.bridge` 作为统一门面；允许修复已识别缺陷，
优先包含线程安全相关缺陷。

## Non-Goals

- 不改变 QML 侧 `appBridge` 的属性、slot、signal 契约。
- 不在本执行单元中扩张外部功能能力或新增业务语义。
- 不新增测试 case。
- 不修改任何 QML 文件。

## Facts

- `src/temporal/app/bridge.py` 当前作为统一门面，聚合 bridge 对外接口、装配与入口，仍是高频并发改动热点。
- `src/temporal/app/` 目录形态与 `temporal.app.bridge` 门面迁移已完成。
- `PreviewBridge` 当前通过继承复用 `AppBridge` 行为。
- listener 回调来自 `odas_stream_client` 线程（`threading.Thread`），
  并经 `OdasClient` 绑定到 `AppBridge._on_*`。
- `AppBridge` 当前 `_on_*` 与状态更新链路存在 `Signal.emit()` 与
  `QmlListModel.replace()` 写入点。
- `QTimer(self)` 当前驱动 `_poll_remote_log` 与 `_verify_odas_startup`。
- `specs/knowledge/app-bridge-source-analysis.md` 与
  `specs/knowledge/app-bridge-execution-model.md` 已提供事实证据。
- 主回归 tests 已迁移到 `temporal.app.bridge` 导入与
  `temporal.app.bridge.*` patch 锚点。
- 本执行单元约束：不改 QML；允许更新 tests 包名/patch 路径并删除冗余 case；
  绝对不允许新增测试 case。
- 阶段策略已冻结：Stage 1 拆分为 `1A/1B/1C`，且 `1A/1B` 允许因测试未迁移出现临时红，
  `1C` 必须恢复四套主回归可跑。

## Decision

- 重构目标改写为：外部能力不扩张，允许修复已识别缺陷（尤其线程安全）。
- 阶段顺序固定为：
  - Stage 1A：目录与门面切换
  - Stage 1B：业务域抽离
  - Stage 1C：调用方与测试迁移收口
  - Stage 2：Preview 组合化
  - Stage 3：线程安全收敛
  - Stage 4：接口瘦身
  - Stage 5：验收与收口
- Stage 1 迁移目标固定：在 `src/temporal/app/` 建立子域模块，
  门面固定为 `temporal.app.bridge`，并在 `1C` 完成调用方与测试迁移。
- 明确放弃旧导入兼容：不再承诺
  `from temporal.app import AppBridge, run, run_with_bridge`。
- 统一新导入路径：`from temporal.app.bridge import AppBridge, run, run_with_bridge`。
- 测试 patch 锚点统一迁移到 `temporal.app.bridge.*`
  （`load_config`、`OdasClient`、`RemoteOdasController`、`AutoRecorder`）。
- `PreviewBridge` 保持继承外观不变，对内改为组合化共享能力（逐阶段推进）。
- backend 模块边界固定为：
  - `remote lifecycle`
  - `stream/projection`
  - `recording/audio routing`
  - `status/state helpers`
- 线程收敛策略固定：listener 输入先通过 Qt queued signal 桥接回
  QObject 所在线程，再执行 Qt 对象状态写入。
- 接口瘦身候选固定为：`sourceItems`、`sourcePositions`、`sourceCount`、
  `recordingSessions`、`setStatus`、`isSourceSelected`。
- 瘦身硬约束：仅当“仓库静态引用（`src+tests+qml+specs`）零引用 + contract
  不要求”时，候选项才可移除或内部化。
- tests 策略固定：允许包名迁移与删除冗余 case；绝对不允许新增测试 case。
- `1A/1B` 可接受因旧测试导入与 patch 锚点未迁移导致的临时红；
  `1C` 起四套主回归必须恢复可跑并作为后续阶段输入门禁。
- 本执行单元固定约束：不改 QML。

## Acceptance

1. Stage 1A 退出门禁达成：`src/temporal/app/` 目录形态与 `bridge` 门面落位，
   新门面可导入，主运行路径可用。
2. 外部能力不扩张；允许落地线程安全相关缺陷修正。
3. `PreviewBridge` 继承外观与既有行为契约保持不变。
4. Stage 1B 退出门禁达成：四子域边界稳定，`bridge` 门面仅承担装配与委派，
   不承载业务编排。
5. Stage 1C 退出门禁达成：调用方导入与测试 import/patch 锚点已迁移到
   `temporal.app.bridge`，不再依赖旧导入路径。
6. Stage 2 退出门禁达成：Preview contract 不变，组合化共享路径生效。
7. Stage 3 退出门禁达成：不存在“后台线程直接触发任何 Qt 对象状态写入”的实现路径。
8. Stage 4 退出门禁达成：候选公开面仅在
   “仓库静态引用（`src+tests+qml+specs`）零引用 + contract 不要求”时才可移除或内部化，并有证据记录。
9. 回归测试通过：
   - `tests.test_app_bridge_integration`
   - `tests.test_app_bridge_recording`
   - `tests.test_preview_bridge`
   - `tests.test_ui_projection`
10. 允许更新测试包名/patch 路径并删除冗余 case，但绝对不允许新增测试 case。
11. 不修改任何 QML 文件。
12. 仓库既有门禁保持通过：pyright、ruff、qmllint、markdownlint、unittest。
13. 已在 specs 中具备三类调查产物：
    - 线程事件矩阵
    - 状态迁移表
    - 接口分级与候选清单

## Plan

1. Stage 0: Spec Baseline
   - 输入门禁：两份 knowledge 可引用；feature 约束一致；无未决冲突。
   - 任务：冻结 `temporal.app.bridge` 门面、测试迁移时点、阶段门禁文本。
   - 退出门禁：feature 含线程事件矩阵/状态迁移表/接口分级表引用，且无未决策略项。
2. Stage 1A: 目录与门面切换
   - 输入门禁：Stage 0 完成。
   - 任务：完成 `src/temporal/app/` 目录形态落位与 `bridge` 门面建立，运行入口改用新门面。
   - 禁止项：不改 QML；不做线程语义改写；不做接口瘦身。
   - 退出门禁：新门面可导入、主运行路径可用；允许旧测试导入导致临时红。
3. Stage 1B: 业务域抽离
   - 输入门禁：Stage 1A 完成。
   - 任务：将业务编排拆入四子域（`remote lifecycle`、`stream/projection`、
     `recording/audio routing`、`status/state helpers`），门面仅装配与委派。
   - 禁止项：不改 QML；不做线程收敛；不做测试迁移。
   - 退出门禁：四子域边界稳定、门面不承载业务编排；允许旧测试导入临时红。
4. Stage 1C: 调用方与测试迁移收口
   - 输入门禁：Stage 1B 完成。
   - 任务：调用方导入迁移到 `temporal.app.bridge`；tests 的 import/patch 锚点统一迁移；
     允许删除冗余测试 case。
   - 禁止项：绝对不新增测试 case；不改 QML。
   - 退出门禁：四套主回归恢复可跑；不再依赖旧导入与旧 patch 锚点。
5. Stage 2: Preview 组合化
   - 输入门禁：Stage 1C 完成且回归为绿。
   - 任务：保持 `PreviewBridge` 继承外观不变，对内完成组合化共享能力。
   - 禁止项：不改 QML；不做线程语义改写。
   - 退出门禁：Preview contract 不变；组合化路径生效。
6. Stage 3: 线程安全收敛
   - 输入门禁：Stage 2 完成。
   - 任务：listener 输入经 queued signal 回主线程；主线程执行所有 Qt 对象状态写入。
   - 禁止项：不改 QML；不新增测试 case。
   - 退出门禁：代码路径上不存在后台线程直接触发 Qt 对象状态写入的实现路径。
7. Stage 4: 接口瘦身
   - 输入门禁：Stage 3 完成；接口分级表已确认静态引用证据。
   - 任务：对候选接口执行移除或内部化，仅保留 contract 与静态引用所需公开面。
   - 禁止项：不改 QML；不新增测试 case。
   - 退出门禁：候选项逐项具备 `src+tests+qml+specs` 静态引用证据与 contract 对照记录。
8. Stage 5: 验收与收口
   - 输入门禁：Stage 2/3/4 全部完成。
   - 任务：运行四套主回归与仓库门禁，完成问题收口。
   - 退出门禁：四套主回归可跑通过，且未新增任何测试 case。

## Progress

- [x] 已完成 knowledge 去决策化修订，保留事实与证据边界。
- [x] 已完成执行模型事实补充（线程事件、状态迁移、接口引用统计）。
- [x] 已完成 feature 多阶段重排（Stage 0/1A/1B/1C/2/3/4/5）与阶段门禁固化。
- [x] 已完成导入策略决策：迁移到 `temporal.app.bridge`，不保留旧导入兼容。
- [x] Stage 1A：目录与门面切换（迁移到 `src/temporal/app/`）。
- [x] Stage 1B：业务域抽离（四子域边界稳定）。
- [x] Stage 1C：调用方与测试迁移收口（恢复四套主回归可跑）。
- [x] Stage 2：Preview 组合化（保持继承外观）。
- [x] Stage 3：线程安全收敛（queued signal 回主线程）。
- [x] Stage 4：接口瘦身收口（已移除 `sourceItems`、`sourcePositions`、`recordingSessions`、`isSourceSelected`；保留 `sourceCount`、`setStatus`，原因分别是状态汇总与状态写入仍被门面/状态链路使用）。
- [x] Stage 5：执行四套主回归与门禁验证（R1-R6 高风险模拟通过，未发现需修复缺陷；不新增测试 case，不改 QML）。
- [x] 收口增量：继续收敛 `bridge.py`，将残留业务逻辑下沉到子模块并固定 helper ownership，四套主回归保持通过。

## Todo

- [ ] 若任一阶段发现事实与当前决策冲突，先更新 Facts 再调整 Decision/Plan。
- [ ] 若后续需恢复旧导入兼容，需另立专题 feature 评估迁移成本与契约影响。
