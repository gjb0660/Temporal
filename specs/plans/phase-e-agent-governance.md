# Spec: Phase E Agent Governance and Collaboration

## Goal

把 Temporal 交付中稳定的 Copilot 协作规则固化下来。

## Scope

- 定义仓库级编码与安全规则。
- 定义 backend、qml、tests 的领域指令文件。
- 定义 agent 交接契约与 review 关注顺序。
- 定义用于重复实施质量控制的 ODAS workflow skill。
- 定义用于重复规则维护的治理修复与治理审计 skills。
- 定义用于推进下一步工作的 push prompt，覆盖 spec 更新、
  test-first 执行与最终 commit 纪律。
- 定义用于第一性原理修复的 root-cause-fix prompt，覆盖
  探索阶段澄清、spec 更新、闭环测试，以及显式拒绝
  symptom-only patch。
- 定义文档语言、编码与换行规则，并明确这些规则在治理文件中的归属边界。

## Non-Goals

- 运行时应用功能。
- 部署流水线自动化。
- 外部策略同步。

## Functional Requirements

1. 让 instruction files 在 .github 层级下可被发现。
2. 保持规则表述可执行且简洁。
3. 保持 `AGENTS.md` 作为执行顺序、code entry、code exit 与 git
   安全行为的工作流权威。
4. 保持 `specs/index.md` 作为静态契约入口。
5. 保持 `specs/in-progress.md` 作为动态路由与状态来源。
6. 仅在 `specs/index.md` 中持有 handoff contract。
7. 保持治理修复流程位于 `.github/skills/rules-governance/`。
8. 保持治理审计流程位于 `.github/skills/rules-audit/`，而不是 prompt。
9. 保持 next-step progression prompt 位于
   `.github/prompts/push.prompt.md`。
10. 保持 root-cause-first repair prompt 位于
    `.github/prompts/root-cause-fix.prompt.md`。
11. 保持 `specs/index.md` 作为新建 `specs/**/*.md` 与
    `specs/handoffs/**/*.md` 文件的语言契约。
12. 保持 `.github/copilot-instructions.md` 作为新建 `docs/**/*.md`、
    source code comments、git commit messages，以及仓库编码与换行
    策略的语言契约。
13. 将保留的英文历史 specs、docs 与 handoffs 作为 audit
    observations 或 statistics 处理，而不是单独 findings。
14. 在计划批次中统一规范历史 handoff 的语言，而不是在顺手改动时处理。
15. 在 implementation work 期间，冻结 `specs/**/*.md`、
    `docs/**/*.md`、`.github/**/*.md` 与 `AGENTS.md` 中现有的
    `#` 与 `##` 标题。
16. Heading freeze 的例外仅限 `rules-governance` 工作、
    新建 Markdown 文件，或用户明确要求的文档结构重构。
17. 对这些既有 Markdown 做本地化时，保留现有英文 `#` 与 `##` 标题，
    仅翻译正文，除非落在上述例外范围内。

## Quality Requirements

- 保持所有治理文件 markdownlint clean。
- 在 instruction system 需要时保持 frontmatter 有效。
- 保持 skill 名称、文件夹名称与 description 对 discovery 一致。
- 保持 prompt description 足够具体，便于 discovery。
- 通过 repo config 保持仓库编码与换行策略可执行。
- 保持 heading-freeze 表述足够明确，便于 audit。
- 保持 Markdown 本地化规则足够明确，避免把英文标题误译为中文。

## Acceptance Criteria

1. Agent 能在没有歧义的情况下加载并应用这些规则。
2. 规则文件反映当前仓库约定。
3. Review agent 的优先级覆盖 regression 与 data-loss risks。
4. Governance audit 与 repair workflow 可作为 skills 被发现。
5. Next-step progression workflow 可作为 prompt 被发现。
6. Root-cause-first repair workflow 可作为 prompt 被发现。
7. 语言与编码规则被分配到明确的治理 owner，且没有歧义。
8. Markdown heading-freeze 的范围与例外足够明确，便于 audit。
9. 现有 Markdown 的本地化操作不会把既有英文标题误改为中文。
