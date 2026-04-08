# Worker Execution Card

Use this card when executing as a subagent in a stage pipeline.

## Required Input Bundle

Do not start execution unless all are provided:

1. objective for current stage slice
2. ownership boundary (files/modules you own)
3. constraints (non-goals, forbidden edits, contract limits)
4. gate profile to run (`fast` or `full`, if required in-stage)
5. expected output format

## Hard Prohibitions

1. Do not edit outside ownership boundary.
2. Do not silently change contracts or acceptance semantics.
3. Do not run uncontrolled retry loops after repeated gate failure.
4. Do not revert other agents' edits.
5. Do not bypass stated gate requirements.

## Execution Pattern

1. Restate acceptance mapping for your slice.
2. Implement only inside ownership.
3. Run required gate profile for your slice.
4. Report evidence and residual risks.

## Mandatory Output Schema

Return exactly these sections:

1. `acceptance-mapping`
2. `pollution-check`
3. `ownership-check`
4. `remaining-risk`
5. `evidence-summary`

Recommended minimal content:

- `acceptance-mapping`: criterion -> proof
- `pollution-check`: pass/fail + delta summary
- `ownership-check`: pass/fail + overlap notes
- `remaining-risk`: none or concise list
- `evidence-summary`: changed files + gate/test outcomes

## Escalation Trigger

Stop and escalate to supervisor when:

1. ownership overlap is required to continue
2. acceptance criteria conflict with observed facts
3. repeated gate failure shows no net progress
