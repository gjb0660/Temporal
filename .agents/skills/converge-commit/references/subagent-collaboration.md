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
   - return findings and risk model
2. worker B:
   - apply Occam reduction proposals on staged scope
   - return minimalization diff and tradeoffs

## Supervisor Challenge Loop

Supervising agent responsibilities:

1. keep ownership boundaries explicit
2. run Socratic challenge on both workers' assumptions
3. resolve conflicts and preserve acceptance semantics
4. repeat multi-round convergence until high-risk items are closed
5. block commit when unresolved high-risk issue remains
6. execute one final atomic commit after gates pass

## Extended Output Contract

On top of the base output contract in `SKILL.md`, also return:

1. `assumption_challenges`
2. `round_closure`

## Completion Gate

Subagent mode is complete only when all are true:

1. no unresolved high-risk finding remains
2. required repository gates are all green
3. final delivery is one atomic commit
4. acceptance semantics remain aligned with active specs/contracts

If any condition fails, do not commit.

## Anti-Patterns

1. do not bypass delegated trigger checks
2. do not let one worker own both review-risk and reduction roles
3. do not skip Socratic challenge rounds
4. do not merge unresolved high-risk assumptions into final commit
5. do not emit multiple commits for one staged intent

## References

1. [minimal-espc delegated supervision](../../minimal-espc/references/delegated-tdd-supervision.md)
