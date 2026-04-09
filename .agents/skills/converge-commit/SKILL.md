---
name: converge-commit
description: Review staged changes and prepare one atomic commit by first-principles cleanup and Occam-style reduction. Use when the task is commit-time review, pre-commit refactor convergence, staged diff quality checks, or "提交前审查/复查". Supports `mode=single|subagent`, defaults to single, and enables subagent mode only on delegated trigger conditions.
---

# Converge Commit

## Step 0: Freshness and Proof Lock (Hard)

Before any gate/check/commit, fill core freshness and both proof fields for the current round:

1. `input-fingerprint`
2. `proof-fingerprint`
3. `review-round`
4. `first-principles-proof`
5. `occam-reduction-proof`

fingerprint is derived from current staged snapshot by `git write-tree`

Hard mapping:

1. missing `input-fingerprint`, `proof-fingerprint`, or `review-round` ->
   `semantic-gate=fail` and `pollution-gate=fail`
2. `proof-fingerprint != input-fingerprint` -> `semantic-gate=fail` and `pollution-gate=fail`
3. missing `first-principles-proof` -> `semantic-gate=fail`
4. missing `occam-reduction-proof` -> `pollution-gate=fail` and `cleanup=fail`

If Freshness Lock fails or any required proof field is missing or empty,
restart from Step 0.
Do not run quick gate, full gate, or commit.

## Output Template (Fill First)

Primary status keys (fixed):
`source`, `category`, `stage`, `sync-risk`, `delegation`, `semantic-gate`,
`pollution-gate`, `static-gate`, `atomic-submit`, `cleanup`.

Required evidence keys (mandatory):

1. `input-fingerprint`: staged snapshot fingerprint for this round
2. `proof-fingerprint`: fingerprint the proof is bound to; equals `input-fingerprint`
3. `review-round`: integer round index, starts at `1`, increments per convergence round
4. `first-principles-proof`: invalidated assumption, preserved semantic invariants, one to three iteration decay risk
5. `occam-reduction-proof`: removed or merged entities, or explicit "no safe reduction" proof in mandatory range
6. `findings`
7. `reduction-decisions`
8. `remaining-risk`
9. `refactor-plan-suggestions`
10. `final-commit-subject`

## Core Contract

1. review staged changes only
2. mandatory range = touched files plus one-hop neighbors
3. first-principles review before Occam reduction
4. every review round MUST bind proof to current staged fingerprint
5. empty staged delta fails closed (`atomic-submit=fail`, `cleanup=fail`)
6. allow one final atomic commit only after all gates are `pass`

## Scope Gate

1. use `git diff --cached --name-only` and `git diff --cached`
2. expand to touched plus one-hop neighbors (callers/callees, coupled contracts, immediate tests)
3. failures in mandatory range block exit and commit
4. out-of-range failures go to `remaining-risk`

## Six-Step Loop

Repeat steps 1-4 until convergence, then run step 5. Step 6 is allowed only
when all gates are `pass`.

1. first-principles review and smell classification (see refactoring reference)
2. Occam reduction to remove dead or redundant entities
3. mandatory smell closure: safe fixes now, unsafe or cross-boundary to risk fields
4. quick gate: `pyright`, `ruff`, `qmllint` on mandatory range
5. full gate: repository required checks before commit
6. atomic commit: one valid subject, commit exactly once

## Unified Sustainability Gates (Only Decision Source)

1. `semantic-gate`: acceptance semantics, assumptions, and freshness locks are aligned
2. `pollution-gate`: no mandatory-range dead paths, unresolved safely-fixable smells, or freshness mismatches
3. `static-gate`: mandatory-range and repository required checks are green
4. `atomic-submit`: one intent, one commit action, valid subject format
5. `cleanup`: no unresolved TODO/FIXME/HACK for this intent and diff is minimal

Any failed gate blocks loop exit and commit.

## Reference Routing

Trigger signals and subagent mode routing:
[subagent-collaboration.md](./references/subagent-collaboration.md)

Commit subject policy:
[commit-log-spec.md](./references/commit-log-spec.md)

Smell closure and micro-refactor policy:
[refactoring-required-elective.md](./references/refactoring-required-elective.md)
