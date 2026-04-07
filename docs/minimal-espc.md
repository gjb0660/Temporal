# Minimal ESPC Specification

## 1. Overview

This project follows a **Minimal ESPC (Explorer → Spec → Plan → Code)** workflow.

Each task is represented as a **single evolving spec file**, which serves as:

* the source of truth
* the execution plan
* the progress tracker

Agents MUST operate directly on these spec files.

---

## 2. Core Principle

A spec file is a **closed execution loop**:

Goal → Non-Goals → Facts → Decision → Acceptance
→ Plan → Progress → (feedback → Facts) → Todo

Agents MUST keep this loop consistent and up to date.

---

## 3. Directory Structure

All work is organized under:

```text
specs/
├── features/
│   ├── auth.md
│   ├── payment.md
│
├── contracts/
│   └── ui/
│       └── left-sidebar.md
│
├── knowledge/
│   ├── architecture.md
│   ├── external-lib.md
│
├── ideas.md
└── index.md
```

### Semantics

* `features/`

  * **Execution units (核心工作单元)**
  * Each feature = exactly one spec file
  * The ONLY source of execution truth
  * Agents primarily operate here

* `contracts/`

  * **Non-breakable constraints (不可随意破坏的约束)**
  * Define design rules that the system MUST obey
  * The ONLY source of design constraints
  * Agents reference here for design guidance

* `knowledge/`

  * **Reusable background knowledge (可复用材料库)**
  * Can be referenced by features as supporting context
  * Stable, reference-only
  * MUST NOT contain execution state (no Plan/Progress)
  * SHOULD expose clear, directly referable conclusions

* `ideas.md`

  * **Candidate inputs / raw ideas**
  * Not executable until promoted to a feature
  * Lightweight, structured brainstorming

* `index.md`

  * **Self-description and entry page of `specs/`**
  * Explains how `specs/` is organized
  * Provides navigation to features, contracts, knowledge, and ideas
  * MUST NOT act as a dashboard, control plane, or execution state source

---

## 4. Spec File Format

Every feature spec MUST follow this structure:

```md
---
title: <feature-name>
tracker: primary-feature | feature | bugfix | refactor | research
status: exploring | active | blocked | done
owner: <agent-role> | <human-name>
updated: YYYY-MM-DD
---

## Goal
## Non-Goals

## Facts
## Decision

## Acceptance
1. <acceptance criteria 1>
2. <acceptance criteria 2>

## Plan
1. <step 1>
2. <step 2>

## Progress
- [ ] <current progress item>
- [x] <completed item>

## Todo
- [ ] <non-critical and deferred item>
```

---

## 5. Metadata (YAML Frontmatter)

### Rules

* Metadata is the **control plane**
* Body is the **execution plane**
* NEVER duplicate metadata inside the body

### Fields

* `title`: stable identifier (function/domain-based, not time-based)
* `tracker`:
  * `primary-feature`: defines a core capability, often with broad impact
  * `feature`: deliver new supporting capability
  * `bugfix`: fix incorrect behavior
  * `refactor`: improve existing structure
  * `research`: clarify unknowns
* `status`:
  * `exploring`: future state; boundaries are still being explored and not yet in the current execution loop
  * `active`: present state; currently in progress
  * `blocked`: present state; currently blocked and waiting for unblocking
  * `done`: past state; the execution loop has been completed
* `owner`: current responsible agent
* `updated`: last meaningful update (YYYY-MM-DD)

Agents MUST update `status`, `owner`, and `updated` when making changes.

---

## 6. Section Semantics

### 6.1 Goal

Defines **what success looks like**.

* MUST be stable
* MUST NOT include implementation details

### 6.2 Non-Goals

Defines **explicit boundaries**.

* What is intentionally NOT included
* Prevents scope creep

### 6.3 Facts (Explorer)

Stores **unavoidable realities and constraints**.

* Only verified or accepted facts
* No assumptions or plans

### 6.4 Decision (Spec)

Defines the **chosen approach**.

* Based on Goal + Facts
* Only current decision (not all options)

### 6.5 Acceptance (Spec)

Defines **verifiable acceptance criteria**.

* MUST be written as an **ordered list**
* Represents completion conditions of the feature
* SHOULD be testable (explicit or implicit test cases)
* Serves as the reference for TDD and validation

### 6.6 Plan (Plan)

Defines the **main execution path**.

* 3–7 ordered steps
* Critical path only
* Sequence matters

### 6.7 Progress (Code)

Represents **actual execution state**.

* Reflects real execution only (not future work)
* Tracks completed and in-progress items

### 6.8 Todo

Defines **non-critical or next-stage items**.

* NOT part of current Acceptance scope
* Includes:

  * next-phase work
  * consciously deferred items
* SHOULD remain short and discardable

---

## 7. Operating Rules

### 7.1 Single Source of Truth

* Each feature has exactly ONE spec file
* Files under `features/` are the ONLY authoritative execution source
* DO NOT create parallel documents

### 7.2 No Direct Execution Without Spec

Agents MUST NOT start coding unless:

* Goal is clear
* Decision exists
* Acceptance is defined
* Plan is defined

### 7.3 Controlled Evolution

When new information appears:

1. Update `Facts`
2. Adjust `Decision` if needed
3. Update `Acceptance` if scope changes
4. Update `Plan`
5. Continue execution

### 7.4 Boundary Discipline

* Do NOT expand scope beyond Goal
* Respect Non-Goals strictly
* Do NOT violate referenced contracts

### 7.5 Confusion Prevention

1. **Goal vs Acceptance**

    * Goal = direction / intent (where we want to go)
    * Acceptance = stopping condition (when we are done)

    Agents MUST ensure that all align with Goal.

2. **Facts vs Decision**

    * Facts = realities we must accept (what the world is)
    * Decision = choices we make based on those realities (how act within world)

    Agents MUST ensure that Decisions are dependent on Facts, not assumptions.

3. **Plan vs Todo**

    * Plan = critical execution path (current)
    * Todo = non-critical (future or deferred)

    Agents MUST NOT mix them.

4. **Non-Goal vs Todo**

    * Non-Goal = intentionally out of scope (excluded by design)
    * Todo = maybe in scope later (included but deferred)

    Agents MUST NOT confuse these. Non-Goals are boundaries, not future work.

### 7.6 Progress is Reality

* Progress reflects actual state only
* DO NOT write future actions here

### 7.8 Spec–Code Atomicity (Critical)

Spec and code MUST be updated in the **same atomic commit**.

* Every code change MUST correspond to a spec update
* Every spec Progress update MUST reflect real code changes
* NEVER commit code without updating the spec
* NEVER update spec Progress without corresponding code

This ensures:

* Spec and implementation are always consistent
* The spec remains a trustworthy execution source
* No drift between intention and reality

---

## 8. Lifecycle

Typical flow:

```text
ideas.md
→ feature (exploring)
→ feature (active)
→ feature (done)
```

Agents MUST update `status` accordingly.

---

## 9. Ideas Format (ideas.md)

The `ideas.md` file MUST follow a lightweight structured format:

```md
# Ideas

## Example

### 想法：<一句话描述>

动机：<为什么值得做>

1. <待确认问题 1>
2. <待确认问题 2>
```

**Example**:

```md id="a6nu84"
# Ideas

## Auth

### 支持 OAuth 登录（Google / GitHub）

减少注册成本，提高转化率

1. 是否需要绑定现有账号？
2. 是否支持多 provider？

## Payment

### 增加退款功能

提升用户信任

1. 是否全额退款？
2. 是否需要审批流程？
```

* Ideas are **inputs, not commitments**
* Keep each idea concise
* Focus on motivation and uncertainty
* DO NOT include implementation details
* Promote to `features/` only when Goal + Plan can be defined

---

## 10. Contract Guidelines (contracts/)

* Contract defines **constraints that must not be broken casually**
* Contracts describe **design rules**, not delivery steps
* Contracts SHOULD be stable and reusable
* Contracts MUST remain feature-agnostic
* Contracts MUST NOT encode execution state
* Contracts MUST NOT reference specific features

### Contract File Format

Each contract SHOULD follow this structure:

```md
---
title: <contract-name>
status: draft | active | deprecated
stability: strict | semi | flexible
version: <major>.<minor>
---

## Role

<what this contract is responsible for (semantic anchor)>

## Invariants

- <must always hold>

## Variation Space

- <allowed dimensions of change (NOT enumerating cases)>

## Rationale (Optional)

- <why these invariants exist>
- <design intent that constrains how variation space should be used>

## Anti-Patterns (Optional)

- <commonly misused or harmful patterns>
```

### Contract Metadata

* `status`:
  * `draft`: future state; still converging and not yet a stable reference
  * `active`: present state; current valid contract for normal references
  * `deprecated`: past state; historical contract that must not receive new references
* `stability`:
  * `strict`: must not change casually
  * `semi`: change allowed with explicit review
  * `flexible`: low-cost constraint, can evolve
* `version`: contract revision

### Contract Semantics

* Role defines **semantic responsibility**

  * MUST describe what the contract is and what it is responsible for
  * MUST NOT include constraints (use Invariants)
  * MUST NOT include explanations (use Rationale)
  * MUST NOT include allowed variations (use Variation Space)
  * SHOULD be concise (1–3 sentences)

* Invariants define **non-negotiable constraints**

  * MUST be minimal and stable
  * MUST NOT encode implementation details

* Variation Space defines **degrees of freedom**

  * MUST describe dimensions, NOT enumerate variants
  * MUST stay within boundaries implied by Invariants
  * SHOULD be minimal but sufficient for design exploration

* Rationale defines **causal explanation of Invariants**

  * MUST explain why Invariants exist
  * MUST NOT restate Variation Space
  * SHOULD provide design intent to guide use of Variation Space

* Anti-Patterns define **commonly incorrect solutions**

  * MUST be optional
  * MUST describe patterns that violate Invariants or Rationale
  * MUST NOT act as primary constraints
  * SHOULD help agents avoid incorrect implementations,
    not enumerate all invalid cases

### Feature–Contract Boundary

* Feature drives delivery; Contract drives constraints
* Feature = what to do
* Contract = what must not be broken
* Features MAY reference contracts, especially in `Facts`, `Decision`, or `Non-Goals`

---

## 11. Knowledge Guidelines (knowledge/)

* Knowledge acts as a **reference material library** for features
* Content is **loosely structured** (no fixed template required)
* MUST include **clearly extractable key conclusions**

  * e.g., `Key Points`, `Conclusions`, or equivalent sections
* SHOULD be **scannable and structured**

  * Prefer bullet points, sections, or short blocks
  * Avoid large unstructured text
* MAY be referenced by feature specs (especially in `Facts` or `Decision`)
* MUST remain **non-executable**

  * No Plan / Todo / Progress
* SUGGEST use Overview → Details → Summary structure for clarity

```md
# Knowledge Example

## 1. Overview

Key Points

## 2. ...

## N. Summary

Conclusions

## References
- [Source 1](url)
- [Source 2](url)
```

---

## 12. Anti-Patterns (Forbidden)

* ❌ Splitting spec into multiple files
* ❌ Mixing Facts / Decision / Plan
* ❌ Writing assumptions as Facts
* ❌ Expanding scope without updating Goal
* ❌ Using Todo as a second Plan
* ❌ Enumerating valid behaviors instead of defining Variation Space
* ❌ Using Notes as an unstructured container
* ❌ Using Anti-Patterns as hard constraints
* ❌ Writing execution state into knowledge/
* ❌ Writing feature-specific delivery logic into contracts/
* ❌ Using index.md as a dashboard
* ❌ Committing code without updating spec
* ❌ Spec drifting from actual implementation

---

## 13. Summary

* `features/` = execution units and the only source of truth

* `contracts/` = design constraints that guide and limit features

* `knowledge/` = reusable, scannable reference with key conclusions

* `ideas.md` = input pool (structured ideas)

* `index.md` = self-description and navigation entry

* One feature → one spec file

* Feature drives delivery; Contract drives constraints

* YAML controls state, Markdown drives execution

* Acceptance defines when to stop, Plan defines how to proceed

* Progress and Todo are checklist-based to prevent drift

* Spec and code evolve together atomically

ESPC is not a sequence, but a **continuous loop**.

Agents operate by **updating the spec, not bypassing it**.
