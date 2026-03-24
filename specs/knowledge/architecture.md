# Temporal Architecture

## 1. Overview

Temporal 是一个 Python + QML 的 ODAS 上位机客户端。
其主要职责包括：

- SSH 私钥的远程 `odaslive` 生命周期控制
- SSL / SST / SSS 的实时可视化
- Sound source 的自动录音

## 2. Technology Stack

当前技术栈包括：

- Python 3.10 + PySide6 + QML
- uv, with pyproject.toml and venv
- unittest, not pytest

## 3. Design Principles

- Python 负责协议、SSH、录音与状态管理。
- QML 负责展示与交互，不承载协议语义。
- Python 和 QML 通过 bridge 进行通信，保持层次分离。

## 4. Decisions

- Python 源码采用 `src` layout。
- Python 源码树采用 PEP 420 namespace packages, No __init__.py

## 5. Layout Structure

- Python backend 位于 `src/temporal/core`
  - `network`：ODAS stream client 与解析
  - `ssh`：远程 `odaslive` 生命周期控制
  - `recording`：source 驱动录音状态与文件写入
- bridge 与启动入口位于 `src/temporal/app.py`、`src/temporal/main.py`
- QML 展示层位于 `src/temporal/qml`

## 6. Summary

- Temporal 的主边界是 Python backend / bridge / QML 三层。
- `src` layout + PEP 420 是当前仓库的稳定组织事实。
