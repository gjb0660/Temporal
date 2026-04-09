---
title: requirements
status: active
stability: semi
version: 0.2
---

## Role

定义 Temporal 的 Python 直接依赖版本治理约束，覆盖 runtime、dev、build 三类依赖。
该 Contract 负责统一“哪些包必须约束版本，哪些包保持无版本约束”的稳定边界。

## Invariants

- 依赖治理 MUST 以 `project.dependencies` 和 `project.optional-dependencies` 中**直接声明**的 package 为范围；MUST NOT 以传递依赖作为约束真源。
- runtime 依赖中的以下 package MUST 保持**版本约束**：
  - `pyside6~=6.10.0`
  - `paramiko>=3.5.0,<4.0.0`
  - `tomli>=2.2.0,<3.0.0`
- dev 的以下 package MUST 保持**无版本约束**：
  - `pyright`
  - `ruff`
- build 的以下 package MUST 在 `build-system.requires` 中被显式声明：
  - `setuptools>=68`
  - `wheel`

## Variation Space

- 允许在不改变 Invariants 的前提下调整具体安装版本（例如同一约束区间内升级到更新 patch 版本）。
- 允许新增或移除直接依赖包，但 MUST 同步更新本 Contract 的 package 清单与约束说明。
- 允许根据验证结果调整约束策略，但 MUST 保持“先改 spec，再改 pyproject”的顺序。

## Rationale

直接依赖 package 的约束状态与原因如下：

**runtime**:

- `pyside6` 对齐 Qt 6.10 迁移基线，为 `QtGraphs` 目标态提供依赖前提，并保持 `6.10.x` 小版本内稳定升级空间。
- `paramiko` 保持在 3.x 主线，避免 4.x 主版本语义变化对 SSH 行为造成不可控回归。
- `tomli`: 当前运行时为 Python 3.10，仍需第三方 TOML 解析库；固定 2.x 主线以确保兼容与稳定。

**dev**:

- `pyright` 静态检查工具发布频率高，保持无版本约束以持续获取最新规则与诊断修复。
- `ruff` 代码质量工具快速演进，保持无版本约束以减少规则滞后与工具链维护负担。

**build**:

- `setuptools` 维持既有构建下限，保障 `setuptools.build_meta` 构建路径可用，不新增额外上界策略。
- `wheel` 作为通用构建组件，当前无额外版本边界需求，维持开放以减少不必要锁定。

## Anti-Patterns

- 将 `pyright` 或 `ruff` 回退为固定版本，导致工具诊断能力长期滞后。
- 未更新 Contract 就直接修改 runtime 约束区间，造成 spec 与代码漂移。
- 把传递依赖版本直接写入本 Contract，导致维护面不受控并偏离“直接依赖真源”边界。
