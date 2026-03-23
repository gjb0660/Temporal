# Spec: Phase F Validation and Delivery

## Goal

Provide release-grade validation for protocol flow, recording safety,
and user operation path.

## Scope

- Run static checks and unit tests.
- Verify remote control and stream reconnection behavior.
- Verify source-driven recording contract end to end.
- Produce concise runbook and troubleshooting notes.

## Non-Goals

- Full CI platform onboarding.
- Cross-platform packaging matrix.
- Performance benchmark campaign.

## Functional Requirements

1. Execute pyright, qmllint, markdownlint, and unittest before merge.
2. Verify SST, SSL, SSS, and recorder behavior in an integration scenario.
3. Document known risks and fallback operations.
4. Keep operator workflow reproducible.

## Quality Requirements

- Keep all checks green for touched scope.
- Keep issue triage notes linked to reproducible steps.

## Acceptance Criteria

1. All quality gates pass in local workspace.
2. Remote odaslive lifecycle can be operated from Temporal UI.
3. Recording files are generated according to contract in live run.
