# ESPC + Knowledge AI Spec System

## 0. Core Idea

- ESPC = Explorer → Spec → Plan → Code（逻辑层，不是文件层）
- 每个 feature 用一个主文件承载（默认单文件）
- 结构按复杂度“生长”，不是预先设计

## 1. Directory Structure

AGENTS.md                # 仓库级 AI 行为入口

specs/                   # 面向 AI 文档
  index.md               # specs 路由入口
  knowledge/             # 知识层（多源）
  feature-a.md           # 简单需求（单文件）
  feature-b/             # 复杂需求（多文件）

docs/                    # 人类文档（非执行）

## 2. Layer Responsibilities

AGENTS.md

- 定义 AI 如何工作
- 指定读取顺序与修改规则

specs/index.md

- 当前 specs 导航
- 活跃 feature 状态
- 阅读路径

knowledge/

- 外部知识（upstream/domain）
- 项目决策（decisions）

feature.md

- 唯一执行单元（承载 ESPC）

## 3. Feature File (Single File ESPC)

```markdown
# Feature: xxx

status: exploring | specified | planned | implementing | done

## Context (Explorer)

- 问题、背景、约束
- 不涉及实现

## Definition (Spec)

- 行为、输入输出、边界、验收标准
- 不涉及任务拆解

## Execution (Plan)

- 实现步骤、模块、测试
- 不改变 Spec

## Notes (optional)

- 偏差、决策、后续优化
```

## 4. Complexity Upgrade Rules

从 feature.md → 目录，当满足任一：

- 文件过长（~300-500行）
- 出现子 feature
- Plan 明显复杂（多模块/多人）
- 需要长期维护/历史记录

升级后：

feature-x/
  feature.md
  sub-features/
  notes.md (optional)

只允许升级，不允许降级

## 5. Knowledge Rules

- 使用 `knowledge/`（不是 context.md）
- 必须有 index.md 作为路由
- 分类按“来源”，不是用途：

  upstream/   # 外部库
  domain/     # 领域知识
  decisions/  # 项目决策（最重要）

## 6. AI Execution Protocol

默认输入：

1. AGENTS.md
2. specs/index.md
3. knowledge/index.md
4. target feature.md

规则：

- 不跳过 Spec 直接写 Code
- Plan 必须基于 Spec
- Code 必须对应 Spec
- 不擅自扩展范围

## 7. Key Principles

- 逻辑分层（ESPC），物理最简（单文件优先）
- feature 是最小单位（不是阶段）
- 知识 / 规格 / 执行 三层分离
- index = 路由，不是内容仓库
- 优先减少文件数量，而不是增加结构

## 8. One-line Summary

ESPC = 一个 feature 在“问题 → 定义 → 实现 → 运行”中的状态演进，
用单文件承载，用知识层支撑，用索引层导航。
