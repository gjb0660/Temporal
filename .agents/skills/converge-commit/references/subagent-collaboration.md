# Subagent Collaboration (Optional)

## Entry Conditions

Use this path only when `mode=subagent`.
Enable it only when one of the following is true:

1. user explicitly requests subagent mode
2. delegated trigger from `$minimal-espc` passes

Delegated trigger must satisfy both:

1. cross-layer change exists
2. contract or Acceptance semantics are changing

## Topology

Use fixed 2-worker parallel topology:

1. worker A:
   - run first-principles review on staged changes
   - classify Chapter 3 smells in mandatory range
   - submit `input-fingerprint`, `proof-fingerprint` and `review-round`
   - submit mandatory `first-principles-proof`
   - return semantic and sustainability risk model
2. worker B:
   - apply Occam reduction proposals on staged scope
   - propose Chapter 6 micro-refactors for safe local cleanup
   - submit `input-fingerprint`, `proof-fingerprint` and `review-round`
   - submit mandatory `occam-reduction-proof`
   - return minimalization diff and tradeoffs

## Fingerprint Consistency Lock (Hard)

For every convergence round, worker A, worker B, and supervisor MUST use the
same `input-fingerprint`.

Hard mapping:

1. missing `input-fingerprint`, `proof-fingerprint`, or `review-round` in any
   role -> `semantic-gate=fail` and `pollution-gate=fail`
2. any worker `input-fingerprint` differs from supervisor `input-fingerprint` ->
   `semantic-gate=fail` and `pollution-gate=fail`
3. any role with `proof-fingerprint != input-fingerprint` -> `semantic-gate=fail`
   and `pollution-gate=fail`
4. staged fingerprint changes but any role misses `stale-proof-reset` with
   rewritten proofs -> `semantic-gate=fail` and `cleanup=fail`
5. if this lock fails, `round-closure=pass` is forbidden

## Socratic Challenge Lock (Hard)

This lock applies to `mode=subagent` only.

`assumption-challenges` is mandatory for every convergence round and must answer
all fixed questions:

1. removed assumption risk?
2. can fewer entities still satisfy active Acceptance semantics?
3. one to three iteration decay if deferred?

Hard mapping:

1. missing or empty `assumption-challenges` -> `semantic-gate=fail`
2. unanswered fixed questions -> `semantic-gate=fail`
3. if `semantic-gate=fail` from this lock, `round-closure=pass` is forbidden

## Supervisor Challenge Loop

Supervising agent responsibilities:

1. keep ownership boundaries explicit
2. enforce the Socratic Challenge Lock for each round before closure
3. enforce Fingerprint Consistency Lock and stale-proof invalidation before closure
4. enforce mandatory review range = touched plus one-hop
5. enforce two-layer policy:
   - safely fixable in mandatory range: clear all before exit
   - cross-boundary or large-scope: record `remaining-risk` and propose focused
     `refactor-plan-suggestions`
6. resolve conflicts and preserve acceptance semantics
7. repeat multi-round convergence until all hard gates are `pass`
8. block commit if any gate fails inside mandatory range
9. do not directly block on out-of-range historical failures; record risk
10. execute one final atomic commit after gates pass
11. do not close a round if either worker evidence is missing:
    missing worker A proof -> `semantic-gate=fail`
    missing worker B proof -> `pollution-gate=fail` and `cleanup=fail`

## Unified Output Contract

Always emit the same primary status keys as `SKILL.md`:

1. `source`
2. `category`
3. `stage`
4. `sync-risk`
5. `delegation`
6. `semantic-gate`
7. `pollution-gate`
8. `static-gate`
9. `atomic-submit`
10. `cleanup`

Subagent extension fields:

1. `assumption-challenges`
2. `round-closure`
3. `worker-verdicts`
4. `input-fingerprint`
5. `proof-fingerprint`
6. `review-round`
7. `first-principles-proof`
8. `occam-reduction-proof`

## Completion Gate

Subagent mode is complete only when all are true:

1. `semantic-gate=pass`
2. `pollution-gate=pass`
3. `static-gate=pass`
4. `atomic-submit=pass`
5. `cleanup=pass`
6. all safely fixable smells in mandatory range are cleared in this commit
7. final delivery is one atomic commit
8. acceptance semantics remain aligned with active specs/contracts
9. both worker proofs are present and non-empty for the final round
10. all role fingerprints match in the final round

If any condition fails, do not commit.

## Anti-Patterns

1. do not bypass delegated trigger checks
2. do not let one worker own both review-risk and reduction roles
3. do not skip Socratic challenge rounds
4. do not use unresolved high-risk-only checks as completion criterion
5. do not emit multiple commits for one staged intent

## References

1. [minimal-espc delegated supervision](../../minimal-espc/references/delegated-tdd-supervision.md)
