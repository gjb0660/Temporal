---
title: governance
tracker: primary-feature
status: active
owner: copilot
updated: 2026-03-26
---

## Goal

建立一个可持续收敛的 spec 治理能力，使 Temporal 仓库内的执行真源、规则 owner 与发现路径保持稳定一致。

## Non-Goals

- 不交付运行时产品能力。
- 不承担部署流水线或外部策略同步。

## Facts

- 仓库需要区分全局工作流、仓库质量门禁、feature 真源与领域指令的 owner。
- 历史治理曾依赖 phase、board 与 handoff 等旧语义入口。
- Primary Feature 与 Supporting Feature 已经成为当前 feature 结构中的稳定区分。
- 该能力在本轮 feature 收敛中已经形成稳定边界。

## Decision

- 将工作流行为收敛到 AGENTS 与相关技能体系中。
- 将仓库质量门禁收敛到 `.github/copilot-instructions.md` 与领域 instructions。
- 将 `specs/features/` 作为唯一执行真源，并以 `primary-feature` 明确主能力骨架。
- 通过命名规则、frontmatter 语义与 owner 分层维持 spec 治理的一致性。

## Acceptance

1. 主要治理文件的 owner 边界清晰，不再互相重复定义同一规则。
2. 规则可被 agent 加载并用于实际执行。
3. Primary Feature、Supporting Feature 与 tracker 语义有稳定归属。

## Plan

1. 收敛治理文件层级与 owner 分工。
2. 固化 instructions、skills 与 prompts 的发现入口。
3. 固化 feature 命名、tracker 与执行真源规则。

## Progress

- [x] 已建立主要治理文件与领域指令入口。
- [x] 已落地治理审计与治理修复技能。
- [x] 已收敛文档语言、编码、格式与 feature 结构规则归属。

## Todo

- [ ] 清理仍引用旧 phase/board 语义的遗留材料，避免治理层残留并行真源。
