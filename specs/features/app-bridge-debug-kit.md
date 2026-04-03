---
title: app-bridge-fake-runtime
tracker: feature
status: active
owner: codex/core
updated: 2026-04-04
---

## Goal

建立 AppBridge 调试与测试的单一替身入口，消除重复编写 fake 组件与配置构造的结构性浪费，并让临时 debug 脚本与测试共享同一组基础组件。

## Non-Goals

- 不改变 `AppBridge`、QML、Remote 控制、录音生命周期的外部行为语义。
- 不覆盖 AppBridge 之外的测试域（例如 `remote_odas` 专属 fake）。
- 不引入“一键创建 AppBridge”的高耦合工厂。
- 不新增自动化 lint/scan 门禁（本执行单元采用文档约束）。

## Facts

- `AppBridge.__init__` 已支持 `cfg/remote/client/recorder` 依赖注入，重复 patch 不是技术必需。
- `tests/test_app_bridge_recording.py`、`tests/test_chart_bridge_contract.py`、`tests/test_preview_bridge.py` 都存在同构的 `_FakeRecorder/_FakeClient/_FakeRemote/_fake_config`。
- `tests/test_app_bridge_integration.py` 也重复定义 `_fake_config` 与近似 remote/client fake。
- 仓库当前不存在 `tests/helpers` 或统一 fixtures 层，导致每个测试文件重复造轮子。
- 用户临时 debug 脚本也重复同一套 fake 与 patch 上下文，问题已超出单个测试文件。
- 最新暂存实现已新增 `src/temporal/app/fake_runtime.py`，并在四个 AppBridge 测试文件切换到统一 import。
- 最新暂存实现采用 `FakeRecorder/FakeClient/FakeRemote/fake_config` 命名，不再使用 `_FakeXxx/_fake_config` 作为共享模块导出名。
- `tests/test_app_bridge_recording.py` 与 `tests/test_app_bridge_integration.py` 保留场景特化本地子类，仅承载行为差异。
- reviewer 指出当前共享 `FakeRemote` 承载了测试特化状态机与故障注入字段，公共层耦合过重。
- 当前高耦合字段集中在启动序列、异常注入、停止失败模拟等 integration 专属语义，不属于公共最小能力。

## Decision

- 新增 `src/temporal/app/fake_runtime.py` 作为 AppBridge 域唯一 debug 基础组件模块。
- 模块只提供最小原子 API：
  - `FakeRecorder`
  - `FakeClient`
  - `FakeRemote`
  - `fake_config()`
- 该模块保持 runtime-neutral：不被主运行路径自动导入，仅供测试与手动 debug 复用。
- AppBridge 域测试迁移到 `from temporal.app.fake_runtime import ...` 路径，去除通用 fake 重复定义。
- 公共 `FakeRecorder/FakeRemote` 仅保留最小 no-op + 基础计数能力，不承载测试特化状态机或故障注入。
- `tests/test_app_bridge_recording.py` 与 `tests/test_app_bridge_integration.py` 承担本地特化 fake 行为，不把特化字段回灌公共层。
- 约束通过 feature 文档治理，不新增自动化扫描门禁。

## Acceptance

1. `src/temporal/app/fake_runtime.py` 存在并导出 `FakeRecorder/FakeClient/FakeRemote/fake_config`。
2. `tests/test_app_bridge_recording.py`、`tests/test_chart_bridge_contract.py`、
   `tests/test_preview_bridge.py`、`tests/test_app_bridge_integration.py`
   已统一从 `temporal.app.fake_runtime` 导入通用 fake/config。
3. 上述四个文件不再重复定义通用 fake/config，仅允许保留场景特化本地子类。
4. AppBridge 域四套回归测试通过，且外部行为无变化。
5. `src/temporal/app/fake_runtime.py` 不含测试特化字段：`start_status_sequence`、`status_sequence`、`keep_running_after_stop`、`status_exception`、`log_exception`、`_AUTO_STATUS*`。

## Plan

1. 在 `specs/features/` 落地本 feature，并冻结范围与验收口径。
2. 在 `src/temporal/app/` 新增 `fake_runtime.py`，实现最小原子 debug 组件。
3. 迁移 AppBridge 域测试到统一 debug 组件，删除通用重复 fake/config 定义。
4. 运行 AppBridge 域回归并验证行为一致性。
5. 在 spec 的 Progress/Todo 中记录迁移完成状态与残留风险。

## Progress

- [x] 已确认重复问题存在于 AppBridge 测试域与临时 debug 脚本。
- [x] 已确认 `AppBridge` 具备注入能力，可支撑去 patch 化迁移。
- [x] 已完成范围收敛：仅 AppBridge 域。
- [x] 已完成策略收敛：`src/temporal/app/fake_runtime.py` + 最小原子 API + 文档约束。
- [x] 已完成四个 AppBridge 测试文件的共享 fake/config 迁移。
- [x] 已完成 AppBridge 域四套回归测试（60 tests）。
- [x] 已完成公共 fake 解耦重写：特化状态机与故障注入逻辑回归测试本地类。

## Todo

- [ ] 若后续扩展共享 fake，先通过“公共最小能力”审查，禁止把测试专属语义回灌公共模块。
