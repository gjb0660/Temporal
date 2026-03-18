# PRD: copilot-to-codex Skill

## 目标

创建一个全局 Codex 技能，用于把当前仓库中的 GitHub Copilot 自定义内容迁移为仓库内 `.codex/skills/` 结构。

## 范围

- 保留全局技能 `copilot-to-codex`。
- 默认扫描以下来源：
  - `AGENTS.md`
  - `.github/copilot-instructions.md`
  - `.github/instructions/**/*.instructions.md`
  - `.github/skills/**`
- 生成或更新仓库下的 `.codex/skills/`。
- 生成同步清单并支持重复执行。

## 非目标

- 不再生成 `.codex/AGENTS.md`。
- 不再生成 `.codex/instructions/*`。
- 不处理 `.github/agents/*.agent.md`。
- 不处理 `.github/prompts/*.prompt.md`。
- 不处理 `.github/hooks/*`。

## 功能需求

1. 生成总技能 `.codex/skills/github-instructions/`。
2. 将 `AGENTS.md` 与 `.github/copilot-instructions.md` 收纳为总技能的 workspace 参考文档。
3. 将 `.github/instructions/*.instructions.md` 的 frontmatter 元数据提取到总技能 `SKILL.md`。
4. 将 `.github/instructions/*.instructions.md` 的正文拆分到总技能 `references/` 下对应文件。
5. 将 `.github/skills/<name>/` 逐个迁移到 `.codex/skills/<name>/`，保持独立技能目录。
6. 对源技能 `SKILL.md` 在迁移时仅保留 Codex 兼容 frontmatter 字段 `name` 与 `description`，正文与资源目录保持不变。
7. 在 `.codex/.gitignore` 中写入忽略规则：
   ```gitignore
   *
   !.gitignore
   ```
8. 生成 `.codex/copilot-sync-manifest.json`，记录受管文件、哈希、模式与文本基线。
9. 对旧版 `.codex/AGENTS.md` 和 `.codex/instructions/*`：
   - 若由旧 manifest 管理且未被人工修改，则自动删除。
   - 若无法安全判断，则在输出中显式标记为 stale。

## 质量要求

- `copilot-to-codex` 技能结构通过 `quick_validate.py`。
- 生成的 `github-instructions` 技能通过 `quick_validate.py`。
- 迁移后的源技能目录尽可能通过 `quick_validate.py`。
- 重复运行在无源变更时保持幂等。
- 对文本文件仍支持基于 manifest 的三方合并。

## 验收标准

1. 当前仓库运行脚本后，`.codex/skills/github-instructions/` 存在且包含：
   - `SKILL.md`
   - `references/workspace-agents.md`
   - `references/workspace-copilot-instructions.md`
   - 每个 `.github/instructions/*` 对应的 reference 文件
2. `.github/instructions/*` 的 `description`、`applyTo` 等元数据出现在 `github-instructions/SKILL.md` 中。
3. `.github/skills/odas-workflow` 与 `.github/skills/session-handoff` 被迁移到 `.codex/skills/` 下独立目录。
4. 新版本同步后，不再新增 `.codex/AGENTS.md` 或 `.codex/instructions/*`。
5. 旧版受管 `.codex/AGENTS.md` 和 `.codex/instructions/*` 被清理或显式标记为 stale。
