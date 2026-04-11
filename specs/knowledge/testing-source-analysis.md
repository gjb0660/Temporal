# Testing Source Analysis

## 1. Overview

本文件记录本次 refactor 之前 `tests/test_*.py` 的源码事实基线，
用于解释冲突根因并约束拆分策略。

分析目标不是覆盖率，而是并行协作下的冲突概率与变更耦合度。

## 2. Baseline Inventory

基线时间：2026-04-10（拆分前）。

| File | Tests | Size(bytes) | Git Hotness(commits) | Primary Domain |
| --- | ---: | ---: | ---: | --- |
| test_chart_bridge_contract.py | 38 | 34859 | 13 | app bridge + chart + qml contract |
| test_app_bridge_integration.py | 29 | 32688 | 17 | app bridge remote lifecycle + recording |
| test_remote_odas.py | 25 | 28397 | 13 | remote odas ssh/shell/lifecycle |
| test_preview_bridge.py | 22 | 24763 | 27 | preview runtime + qml + entrypoint |
| test_app_bridge_recording.py | 15 | 14735 | 22 | app bridge recording + remote control |
| test_source_tracking_semantics.py | 10 | 9066 | 5 | source tracking semantics |
| test_config_loader.py | 9 | 9243 | 5 | config loading |
| test_auto_recorder.py | 11 | 7334 | 6 | auto recorder |
| test_chart_window_semantics.py | 7 | 5032 | 3 | chart window model |
| test_odas_stream_client.py | 5 | 5226 | 5 | socket listeners |
| test_odas_message_view.py | 13 | 4426 | 5 | odas message projection |
| test_ui_projection.py | 4 | 3351 | 6 | ui projection model |
| test_json_stream.py | 5 | 2580 | 3 | json stream buffer |
| test_qml_list_model.py | 1 | 1161 | 1 | qml list model |

## 3. Coverage Matrix

### 3.1 模块重叠事实

高重叠模块（同一生产模块被 2+ 测试文件覆盖）：

- `temporal.app.bridge` <- `test_app_bridge_integration.py`, `test_app_bridge_recording.py`,
  `test_chart_bridge_contract.py`, `test_preview_bridge.py`
- `temporal.app.fake_runtime` <- 5 个文件共用
- `temporal.preview_data` <- `test_chart_bridge_contract.py`, `test_preview_bridge.py`, `test_source_tracking_semantics.py`
- `temporal.core.ssh.remote_odas` <- `test_app_bridge_integration.py`, `test_remote_odas.py`
- `temporal.core.recording.auto_recorder` <- `test_auto_recorder.py`, `test_app_bridge_integration.py`

### 3.2 重复 helper / 重复语义

- 重复 helper：`_ensure_app`、`_model_items` 同时存在于 chart/preview 两个大文件。
- 重复行为断言：`test_unchecked_last_source_keeps_rows_but_clears_visible_outputs` 同时存在于 `test_app_bridge_recording.py` 与 `test_preview_bridge.py`。

## 4. Conflict Root Causes

基于第一性原理，冲突的最小充分原因不是“文件数量少”，而是“单文件承载多 owner-domain 语义”。

可验证根因：

1. 大文件混合多个责任域（remote lifecycle、log poll、recording、qml contract）并共享同一 fake/runtime 前置。
2. 高频演进点（`AppBridge`、`PreviewBridge`、`RemoteOdasController`）在测试层也聚集到同一文件，放大并行改动重叠。
3. 测试边界与生产模块 ownership 不一致，导致 reviewer 需要跨域理解单个 diff。

## 5. Socratic Findings

关键反问与结论：

- 问：冲突是否主要由“测试太多”导致？
  结论：否。核心是多责任聚合，而不是总用例数。
- 问：是否应优先按 unit/integration 分类？
  结论：不优先。冲突发生在 ownership 交叉，先按源码所有权拆分更直接降低冲突。
- 问：是否需要在本轮引入新测试范式？
  结论：不需要。遵循奥卡姆剃刀，先完成结构解耦与语义等价迁移。

## 6. Refactor Design Inputs

本次执行单元采用以下输入约束：

- 一文件一 owner-domain。
- 全量覆盖热点混合文件，不做局部试点。
- 允许结构重排 + 小修语义表达，不引入新功能断言。
- 迁移后维持 discover 规则：`python -m unittest discover -s tests -p "test_*.py"`。

## 7. Historical Hotspots

`git log -- tests` 基线统计（含 `tests/test_*.py`，共 64 次触达 commit）：

| Rank | File | Touches |
| --- | --- | ---: |
| 1 | test_preview_bridge.py | 27 |
| 2 | test_app_bridge_recording.py | 22 |
| 3 | test_app_bridge_integration.py | 17 |
| 4 | test_chart_bridge_contract.py | 13 |
| 5 | test_remote_odas.py | 13 |

高共改（co-change）对：

1. `test_app_bridge_recording.py` <-> `test_preview_bridge.py`（10）
2. `test_app_bridge_integration.py` <-> `test_remote_odas.py`（9）
3. `test_app_bridge_integration.py` <-> `test_app_bridge_recording.py`（8）
4. `test_chart_bridge_contract.py` <-> `test_preview_bridge.py`（7）
5. `test_app_bridge_recording.py` <-> `test_chart_bridge_contract.py`（5）

结论：热点由“跨域共改中心性”主导，而非单纯文件大小。

## 8. Summary

拆分前风险来自“高热度 + 多责任 + 单文件聚合”。

拆分策略必须直接对齐 owner-domain，
否则即使补充 helper 抽象，冲突热点仍会停留在大文件上。

## References

- [testing.md](./testing.md)
- [app-bridge-source-analysis.md](./app-bridge-source-analysis.md)
- [app-bridge-refactor-modularization.md](../features/app-bridge-refactor-modularization.md)
- `uv run python -m unittest discover -s tests -p "test_*.py" -v`
- `uv run ruff check tests`
- `git log -- tests`
- `git log --pretty=format: --name-only -- tests | group by tests/test_*.py`
- `git log --pretty=format:%H --name-only -- tests` + pairwise co-change统计脚本
