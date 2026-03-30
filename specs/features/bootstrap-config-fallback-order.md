---
title: bootstrap-config-fallback-order
tracker: bugfix
status: done
owner: codex/core
updated: 2026-03-30
---

## Goal

修正启动期配置选择顺序，确保运行时默认读取真实配置，而不是误用示例配置。

## Non-Goals

- 不修改 `odas.toml` 与 `odas.example.toml` 的字段语义。
- 不调整 remote、streams 配置解析规则。

## Facts

- `AppBridge` 启动时此前固定读取 `config/odas.example.toml`。
- 仓库中同时存在 `config/odas.toml` 与 `config/odas.example.toml`。
- 示例配置仅适合作为缺省 fallback 与测试输入，不应覆盖真实运行配置。

## Decision

- 启动链配置路径解析改为：
  1. 优先使用 `config/odas.toml`
  2. 当且仅当其不存在时回退 `config/odas.example.toml`
- 用单元测试固定该优先级，避免后续回归。

## Acceptance

1. 启动链默认路径解析在存在 `config/odas.toml` 时返回该文件。
2. 当 `config/odas.toml` 缺失时，启动链回退到 `config/odas.example.toml`。
3. 现有 `config_loader` 与 `AppBridge` 相关测试保持通过。

## Plan

1. 先新增失败测试覆盖默认路径优先级。
2. 最小实现默认路径解析函数并接入 `AppBridge`。
3. 运行 targeted unittest 验证回归。

## Progress

- [x] 已新增默认路径优先级测试（`tests/test_config_loader.py`）。
- [x] 已实现 `resolve_default_config_path` 并接入 `AppBridge`。
- [x] 已验证 `tests.test_config_loader` 与 `tests.test_app_bridge_recording` 通过。

## Todo

- [ ] 若后续引入 CLI 配置参数覆盖策略，需新增独立 feature 明确优先级层次。
