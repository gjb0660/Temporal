# Execution Flow

## Stage Entry

- Enter Explorer when facts are insufficient
- Enter Spec when Goal and Acceptance can be defined
- Enter Plan when Decision is clear
- Enter Code only when Plan and Acceptance exist
- Enter Review when implementation is complete enough for verification

## Stage Exit

- Exit Explorer when facts are sufficient
- Exit Spec when Acceptance is testable and bounded
- Exit Plan when the critical path is explicit and minimal
- Exit Code only when code, tests, and spec are consistent
- Exit Review only when no unresolved high-risk issue remains

## Code Loop

When in Code:

Red → Green → Refactor → Commit

- Each step must be verifiable
- Refactor must preserve behavior
- Do not accumulate large unverified changes

## Anti-Patterns

- Do not expand scope without updating the spec
- Do not infer behavior from code without spec
- Do not continue execution when spec drift is detected
- Do not create parallel sources of truth
