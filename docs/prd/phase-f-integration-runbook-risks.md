# PRD: Phase F Integration Runbook and Risks

## Goal

Close remaining Phase F gaps by adding integration validation,
operator runbook, and risk documentation.

## Scope

- Add integration tests for AppBridge SST/SSL/SSS flow.
- Add timeout recovery integration checks.
- Add operator runbook for local and remote ODAS operation.
- Add known-risks document with mitigation and fallback actions.

## Non-Goals

- CI platform onboarding.
- Packaging and installer delivery.
- Cloud storage and retention automation.

## Functional Requirements

1. Validate SST source lifecycle drives recorder start and stop.
2. Validate SSL payload updates potential counters correctly.
3. Validate SSS separated and post-filtered audio routing writes data.
4. Validate timeout stop and re-appear recovery create new sessions.
5. Provide reproducible runbook commands and troubleshooting steps.
6. Provide risk list with impact, mitigation, and operator fallback.

## Quality Requirements

- Keep integration tests deterministic and network-free.
- Reuse project unittest style and existing fixture patterns.
- Keep markdownlint clean for all new docs.
- Keep ruff, qmllint, pyright, and unittest green.

## Acceptance Criteria

1. New integration tests pass in local workspace.
2. docs/runbook.md covers setup, operation, and troubleshooting.
3. docs/risks.md covers key known limits and fallback actions.
4. Existing A-F tests remain green without regression.
