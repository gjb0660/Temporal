---
title: bootstrap
tracker: feature
status: done
owner: copilot
updated: 2026-03-26
---

## Goal

建立可运行的 Temporal bootstrap 基线，使 Python 启动链、QML 主窗口与 bridge 边界能够承载后续功能交付。

## Non-Goals

- 不覆盖 ODAS 网络接入、SSH 生命周期控制或录音语义。
- 不在本文件中扩展 UI 视觉系统或 preview 运行时。

## Facts

- 项目运行栈为 Python 3.10、PySide6 与 QML。
- Python 源码树采用 namespace package，不能新增 `__init__.py`。
- 主窗口必须由 Python 启动链加载共享 `Main.qml`。
- 该能力在本轮 feature 收敛中保持为已完成的 supporting baseline。

## Decision

- 使用 uv 作为本地运行与依赖入口。
- 由 Python 入口创建应用并注入 bridge，再加载共享 QML 主窗口。
- 保持 QML 与 backend 通过 bridge 隔离，避免在 bootstrap 层引入业务逻辑耦合。

## Acceptance

1. 本地环境可通过单一命令启动应用。
2. 主窗口可以稳定渲染，且不会因缺少业务功能而崩溃。
3. `src/temporal/**` 继续保持 namespace package 结构。

## Plan

1. 建立 Python 项目骨架与启动入口。
2. 接通最小 PySide6 应用链与 QML 加载路径。
3. 固化 bridge 隔离边界，作为后续功能前提。

## Progress

- [x] 已建立 Python 项目与 uv 工作流。
- [x] 已落地最小 PySide6 启动链并加载主 QML。
- [x] 已确认 namespace package 结构作为基础约束。

## Todo

- [ ] 后续若需补充启动期约束，转入对应 feature，不在本文件扩展范围。
