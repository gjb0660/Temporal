---
title: testing-refactor-suite-partition
tracker: refactor
status: done
owner: codex/core
updated: 2026-04-10
---

## Goal

在不改变生产行为语义的前提下，重构 `tests/test_*.py` 结构，
将高冲突混合文件按源码 owner-domain 拆分为可并行维护的执行单元。

## Non-Goals

- 不修改生产代码 public API、QML contract、运行时行为。
- 不引入新的功能断言或扩张测试范围。
- 不改变 unittest discover 入口与测试目录层级。

## Facts

- 拆分前存在 5 个高冲突混合文件：
  `test_app_bridge_integration.py`、`test_app_bridge_recording.py`、
  `test_chart_bridge_contract.py`、`test_preview_bridge.py`、`test_remote_odas.py`。
- 这些文件同时具备：高测试密度（15~38）、高提交热度、跨域语义混合。
- 历史重复点包含 `_ensure_app` / `_model_items` helper 与跨文件重复行为断言。
- 全量基线为 194 tests（拆分前可通过）。
- 分析证据见 `specs/knowledge/testing-source-analysis.md`。

## Decision

- 按源码所有权进行一次性全量拆分，不采用按 test 类型或按耗时拆分。
- 结构规则：一文件一 owner-domain；建议 6-12 个 tests，硬上限 15。
- 语义最小单元可低于 6（例如 entrypoint/qml contract 切片）。
- 允许“小修语义”：仅限测试命名/断言表达澄清，不新增功能断言。
- 对跨文件复用采取最小支持层：新增 domain `*_support.py` 承载稳定 helper/fake，
  保持 `tests/` 平铺并兼容 discovery。

本次落地拆分：

1. `test_app_bridge_integration` ->
   `test_app_bridge_remote_startup` /
   `test_app_bridge_remote_log` /
   `test_app_bridge_remote_stop` /
   `test_app_bridge_stream_recording_integration`
2. `test_app_bridge_recording` ->
   `test_app_bridge_recording_projection` /
   `test_app_bridge_recording_remote_control`
3. `test_chart_bridge_contract` ->
   `test_chart_bridge_runtime` /
   `test_chart_bridge_potential` /
   `test_chart_bridge_ingress` /
   `test_chart_bridge_parity` /
   `test_chart_bridge_qml_contract`
4. `test_preview_bridge` ->
   `test_preview_bridge_scenarios` /
   `test_preview_bridge_controls` /
   `test_preview_bridge_qml_contract` /
   `test_preview_bridge_entrypoint`
5. `test_remote_odas` ->
   `test_remote_odas_config` /
   `test_remote_odas_shell` /
   `test_remote_odas_lifecycle` /
   `test_remote_odas_log`

## Acceptance

1. 生产代码无变更，仅测试结构与 specs 变更。
2. 原 5 个热点混合文件从 `test_*.py` 集合移除，拆分文件落地并可被 discover。
3. 拆分前后全量测试总数保持 194，不丢用例。
4. 关键行为组语义等价：
   remote startup/stop、log poll/clear、preview scenario、chart parity、remote shell。
5. 迁移后门禁通过：
   - `uv run python -m unittest discover -s tests -p "test_*.py" -v`
   - `uv run ruff check tests`
   - `uv run pyright --project pyproject.toml`

## Plan

1. 固化知识基线与冲突根因（knowledge）。
2. 生成 owner-domain support 层并迁移 test methods 到新文件。
3. 删除原混合测试文件，保持 discover 兼容。
4. 运行 unittest / ruff / pyright 做语义等价与静态门禁验证。
5. 收口 spec（Facts/Decision/Acceptance/Progress 同步）。

## Progress

- [x] 完成 testing 基线调研并产出 knowledge。
- [x] 完成 5 个热点混合文件的全量拆分。
- [x] 完成 support 层收敛（`app_bridge_*`, `chart_bridge_*`, `preview_bridge_*`, `remote_odas_*`）。
- [x] 完成总用例数保持校验（194）。
- [x] 完成 unittest/ruff/pyright 全门禁通过。

## Todo

- [ ] 后续如新增测试，优先落到既有 owner-domain 文件，避免回流到“混合大文件”。
- [ ] 若 support helper 出现跨域耦合增长，另立 refactor 单元收敛边界。
