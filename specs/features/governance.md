---
title: governance
tracker: primary-feature
status: active
owner: copilot
updated: 2026-03-30
---

## Goal

建立最小 spec 治理闭环，使执行真源、规则 owner 与发现路径可以被稳定判定与复用。

## Non-Goals

- 不交付运行时产品能力。
- 不承担部署流水线或外部策略同步。

## Facts

- 仓库需要区分全局工作流、仓库质量门禁、feature 真源与领域指令的 owner。
- `AGENTS.md` 属于全局工作流 authority，不属于 `specs/` 执行真源。
- `.github/copilot-instructions.md` 与 `.github/instructions/**` 当前承接仓库级与领域级约束。
- `specs/index.md`、`specs/features/index.md` 与 `specs/contracts/index.md` 当前承接 spec 空间的结构与语义规则。
- 仓库中已存在 `rules-audit` 与 `rules-governance` 技能，用于审计和修复治理漂移。
- 历史治理曾依赖 phase、board 与 handoff 等旧语义入口。
- Primary Feature 与 Supporting Feature 已经成为当前 feature 结构中的稳定区分。

## Decision

- 将工作流行为收敛到 AGENTS 与相关技能体系中。
- 将仓库质量门禁收敛到 `.github/copilot-instructions.md` 与领域 instructions。
- 将 `specs/features/` 作为唯一执行真源，并以 `primary-feature` 明确主能力骨架。
- 审计 `AGENTS.md` 时按全局工作流层处理，不按普通 feature spec 语义处理。
- 通过命名规则、frontmatter 语义与 owner 分层维持 spec 治理的一致性。

## Acceptance

1. 全局工作流、仓库级约束、feature 真源与 contract 约束各自存在单一主 owner，不再互相重复定义同一规则。
2. agent 可按现有入口稳定发现 `AGENTS.md`、`.github/copilot-instructions.md`、`.github/instructions/**` 与 `specs/**`，无需依赖并行 dashboard。
3. `primary-feature`、`feature`、`bugfix`、`refactor`、`research`
   与 `status` 语义在 `specs/features/index.md` 中可直接判定，
   并能约束具体 feature frontmatter。

## Plan

1. 收敛治理文件层级与 owner 分工。
2. 固化 instructions、skills 与 prompts 的发现入口。
3. 固化 feature 命名、tracker、status 与执行真源规则。

## Progress

- [x] 已建立主要治理文件与领域指令入口。
- [x] 已落地治理审计与治理修复技能。
- [x] 已收敛文档语言、编码、格式与 feature 结构规则归属。
- [x] 已确认 active truth 层不再依赖旧 phase/board 作为执行入口。

## Todo

- [ ] 清理 legacy handoff 与设计文档中仍保留的旧 phase/board 历史表述，避免被误读为当前执行入口。
