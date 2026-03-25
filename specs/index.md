# Specs

## Purpose

`specs/` 是系统的唯一规范空间（Single Source of Truth）。

所有执行、决策与状态必须源自此目录。

## Index Rules

- 本文件仅定义结构与语义
- 本文件不包含执行状态
- 本文件不作为 dashboard 或控制面

## Structure

`specs/` 当前按以下语义组织：

- features/
- contracts/
- knowledge/
- legacy/
- ideas.md
- index.md

## Semantics

### features/

- 执行单元（Execution Units）
- MUST 是唯一执行真源
- 每个 feature MUST 对应一个且仅一个 spec 文件
- Agents MUST 仅在此目录执行任务

### contracts/

- 约束定义（Constraints）
- MUST 定义不可破坏的设计规则
- MUST NOT 包含执行逻辑或状态

### knowledge/

- 参考知识（Reference）
- MUST 为只读材料
- MUST NOT 包含执行状态（Plan / Progress / Todo）

### legacy/

- 历史归档（Archive）
- 仅保留过渡期历史材料
- MUST NOT 作为执行真源

### ideas.md

- 输入池（Inputs）
- MUST NOT 直接执行
- MUST 先转化为 feature

## Formats

所有 specs 内文件 MUST:

- 使用 UTF-8 编码
- 使用 LF 换行
- 使用 Markdown 格式
- 使用英文标题（# / ##）
- 正文使用本地语言（如中文）

所有 specs 内文件 MUST NOT:

- 混用中英文标题
- 使用非标准标题层级替代结构语义
- 滥用 MUST / SHOULD / MAY 等 RFC 2119 标记

**Template**:

```md
# Title
## Section
### 三级标题可以使用本地语言

正文说明（中文）
```
