---
name: spec-code-alignment
description: 'Audit drift between specs/features and implementation,
  generate a specs/todo scan report, and realign feature specs to
  current code reality. Use for spec/code drift, feature truth
  alignment, todo report generation, spec backfill, and governance-safe
  spec updates.'
argument-hint: 'feature scope or drift concern to audit'
user-invocable: true
disable-model-invocation: false
---

# Spec Code Alignment

## When to Use

Use this skill when you need to:

- audit drift between `specs/features/*.md` and `src/temporal/**`
- check whether feature facts or decisions overstate current implementation
- generate a repair report under `specs/todo/`
- realign feature specs to current code reality before fixing code
- separate true code/spec drift from stale docs or legacy history

Typical trigger phrases:

- spec/code drift
- feature alignment
- scan current codebase against specs
- generate todo report for drift
- update feature specs to match implementation

## Goal

Keep `specs/features/` as the execution truth by:

1. auditing actual implementation against active feature specs
2. recording actionable drift in a report under `specs/todo/`
3. updating feature specs to match verified code facts without inventing future behavior

## Guardrails

- Treat active feature specs as the only execution truth; ignore
  `legacy/` unless the user explicitly asks for history review.
- Distinguish three outcomes:
  - code matches spec
  - spec overstates code
  - code has moved beyond spec
- Do not rewrite `Goal`, `Non-Goals`, or `Acceptance` unless the user
  explicitly asks for behavior redefinition.
- For alignment-only work, prefer updating:
  - `Facts`
  - `Decision`
  - `Plan`
  - `Progress`
  - `Todo`
- Do not convert intended architecture into current fact unless code and
  tests already prove it.
- If drift is really a docs-only simplification that the user allows,
  record that and move on.
- If a rule conflict exists, update the owning layer only.

## Procedure

### 1. Load the current truth sources

Read, at minimum:

- `specs/features/index.md`
- relevant `specs/features/*.md`
- relevant code in `src/temporal/**`
- relevant tests in `tests/**`

If governance or naming rules are involved, also read:

- `docs/specs-filename.md`
- `docs/feature-design-and-evolution.md`
- relevant governance skills or instructions

### 2. Audit by capability, not by file order

For each active feature in scope:

1. extract the promised behavior from the feature spec
2. locate the actual implementation entrypoints
3. locate the tests that freeze the current behavior
4. compare promised behavior vs actual behavior

Focus on high-coupling areas first:

- bridge and projection layers
- runtime state machines
- routing and recording boundaries
- preview/runtime parity
- remote-control lifecycle and failure paths

### 3. Classify each finding

Classify drift into one of these buckets:

- `aligned`: spec and code agree
- `spec-overstates-code`: spec promises more than code delivers
- `code-exceeds-spec`: code behavior exists but spec does not record it
- `owner-drift`: behavior is implemented under the wrong feature
  boundary
- `docs-only`: non-owning docs are stale, but active feature truth is
  acceptable

Use severity pragmatically:

- `major`: affects execution truth or future implementation decisions
- `minor`: wording drift, examples, or non-owning docs

### 4. Produce a scan report under `specs/todo/`

Create a dated report file, for example:

- `specs/todo/2026-03-27-spec-code-alignment-scan.md`

Recommended sections:

1. `Goal`
2. `Scope`
3. `Summary`
4. `Findings`
5. `Aligned Areas`
6. `Next Actions`
7. `Remaining Risk`

Each finding should include:

- severity
- type
- file
- violation
- impact
- code evidence
- minimal fix

### 5. Realign feature specs to code reality

For each feature that truly drifts:

1. update `updated`
2. revise `Facts` so they describe verified current behavior
3. revise `Decision` so it reflects the current implemented posture
4. revise `Plan` so unfinished work is explicitly the remaining gap
5. revise `Progress` to separate completed behavior from missing parity
6. revise `Todo` to capture deferred or next repair work

Do not smuggle future architecture into `Facts`.

Examples:

- If runtime charts are not implemented, do not claim chart parity is
  complete.
- If preview still owns local projection logic, do not claim it already
  consumes a shared layer.
- If tests already freeze a behavior that the spec omitted, add that
  fact to the spec.

### 6. Validate

After updates:

1. run diagnostics on changed markdown files
2. run `markdownlint` on the report and updated feature specs
3. confirm the report and feature specs do not contradict each other

If the task includes code changes later, that is a separate phase.

## Decision Points

### When should you update the spec now?

Update now when:

- the current code behavior is clearly implemented
- tests confirm the behavior
- the spec currently overstates or misstates the code

### When should you only report drift?

Report only when:

- behavior is ambiguous or insufficiently verified
- the user asked for audit only
- the gap implies a product decision rather than a factual correction

### When should you ignore a mismatch?

Ignore it when:

- it lives in `legacy/`
- it is a non-owning doc the user explicitly allows to be simplified
- it does not change execution truth

## Completion Checks

The skill is complete when all of the following are true:

1. a `specs/todo/` scan report exists for the audited scope
2. each real drift finding is classified and justified with code evidence
3. changed feature specs describe current code reality rather than
  intended architecture
4. no updated feature spec overclaims behavior that code does not
  implement
5. markdown diagnostics and `markdownlint` pass for changed markdown files

## Output Expectations

When using this skill, the final response should summarize:

- what was scanned
- which features were truly out of alignment
- where the report was written
- which feature specs were updated
- what remains for the later code-fix phase

## Example Prompts

- Audit current `specs/features/*.md` against the runtime code and write
  a todo report.
- Check whether preview-mode and ui-system specs still match the
  implementation, then backfill the specs to current reality.
- Scan recording, routing-session, and remote-control for spec drift and
  document only actionable gaps.
- Generate a `specs/todo/` alignment report before we start code fixes.
