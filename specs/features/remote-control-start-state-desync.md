---
title: remote-control-start-state-desync
tracker: bugfix
status: done
owner: codex/core
updated: 2026-03-31
---

## Goal

修复实模式下“远端仍在运行但主按钮回退到启动”的误判，避免重复启动冲突。

## Non-Goals

- 不引入基于流数据的 running 推断。
- 不兼容 legacy “无 pid 自动接管”路径。
- 不改变左侧主按钮三态表达式与视觉样式。

## Facts

- 左侧主按钮文案由 `odasStarting/odasRunning` 直接驱动。
- 现场复现证据显示：`./build/bin/odaslive -c config/odas.cfg` 已运行，但 `odaslive.pid` 缺失。
- rootless 环境下 `/proc/$pid/cwd` 与 `/proc/$pid/exe` 不可作为可靠门控条件。
- 现有 `load_valid_pid` 依赖 `cmdline/cwd/exe/args` 身份匹配，易在 rootless 场景误判并清理 pid 文件。
- runtime 中日志读取异常（非断链）分支会提前返回，导致 `odasRunning` 收敛滞后。
- preview 复用同一份侧栏绑定，但 bridge 未暴露 `odasStarting`。

## Decision

- 采用 pid-only 真值模型（Occam 零兼容）：
  `running = (odaslive.pid 存在) and (pid 为纯数字) and (kill -0 pid 成功)`。
- 完全移除 `load_valid_pid` 对 `cmdline/cwd/exe/args` 的门控依赖。
- `temporal_start` 启动后必须写入 `odaslive.pid`，并进行回读一致性校验；失败显式返回非 0。
- `temporal_stop` 先尝试按进程组停止（`kill -TERM -- "-$pid"`），
  失败回退 `kill -TERM "$pid"`，确认停止后清理 pid 文件。
- runtime 在日志读取异常但控制通道未断时仍执行 `_sync_remote_odas_state(update_status=True)`。
- preview 补齐 `odasStarting` 只读属性（恒 `False`）与 notify，稳定共享绑定语义。

## Acceptance

1. `load_valid_pid` 仅由 pid 文件 + 数字校验 + `kill -0` 决定 running。
2. `temporal_start` 在 pid 文件写入失败或回读不一致时显式失败。
3. 日志读取异常（非断链）场景下，runtime 仍触发状态同步，按钮不误回退到“启动”。
4. preview/runtime 共享侧栏绑定表达式在 `odasStarting` 上无接口漂移。

## Plan

1. 先补测试覆盖 pid-only 判定、start 写 pid 失败分支、日志异常收敛与 preview `odasStarting`。
2. 重构 remote helper 的 pid 生命周期逻辑并移除 `/proc/cmdline/cwd/exe` 运行态门控。
3. 修改 runtime/preview bridge 后运行回归与门禁。

## Progress

- [x] 已确认现场证据：进程仍在运行但 `odaslive.pid` 缺失。
- [x] 已确认 rootless 下 `/proc/$pid/cwd`、`/proc/$pid/exe` 不可靠。
- [x] 已完成 pid-only helper 重构并移除 legacy 识别门控。
- [x] 已完成 bridge 兼容补强与测试更新。
- [x] 已通过 `tests.test_remote_odas`、`tests.test_app_bridge_integration`、
  `tests.test_preview_bridge` 与全量 `unittest discover`（112 tests）。
- [x] 已通过 `uv run ruff check src tests`、
  `uv run pyright --project pyproject.toml`（0 errors, 1 warning）、
  `npx markdownlint specs/features/remote-control-start-state-desync.md`。

## Todo

- [ ] 无。
