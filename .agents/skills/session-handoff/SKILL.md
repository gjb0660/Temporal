---
name: session-handoff
description: "Use when ending a work session to ensure spec is synchronized, perform self-audit against ESPC principles, and optionally produce a minimal handoff artifact. Keywords: session handoff, closeout, self-audit, progress sync, 会话交接."
argument-hint: "active work item or session scope"
---

# Session Handoff Skill

## When To Use

Use this skill when a work session is ending and continuity
or correctness must be ensured.

## Goal

Ensure the system state is consistent, auditable, and resumable
WITHOUT introducing a parallel execution source.

## Core Principle

- The active feature spec MUST remain the single source of execution truth.
- Any handoff artifact MUST be treated as a derived, non-authoritative summary.

## Required Identification

The skill MUST identify:

- the active execution source (feature spec)
- work completed in this session (verified only)
- validation actually performed
- unresolved risks or blockers
- the next concrete continuation point

## Procedure

1. Locate the active execution source.
2. Update the source BEFORE any summary is produced.
3. Perform a self-audit against ESPC principles.
4. Capture only verified session facts.
5. Optionally generate a handoff artifact if required.
6. Return a minimal continuation summary.

## Self-Audit (Mandatory)

The following checks MUST be performed:

### Spec Consistency

- The active feature spec MUST be updated if execution changed.
- `Progress` MUST reflect only completed work.
- `Todo` MUST NOT duplicate `Plan`.
- `Facts` MUST NOT contain assumptions.
- `Decision` MUST be consistent with `Facts`.

### Boundary Discipline

- Work MUST NOT exceed `Goal`.
- `Non-Goals` MUST NOT be violated.
- Applicable contracts MUST NOT be violated.

### Source Integrity

- No parallel execution source MUST be created.
- No execution state MUST be written outside the spec.
- Knowledge files MUST remain non-executable.

### Validation Integrity

- Validation MUST be recorded ONLY if actually executed.
- If validation was not executed, it MUST be explicitly stated as "not run".

## Handoff Artifact (Optional)

A handoff file MAY be created ONLY IF:

- repository rules require it, OR
- session continuity would otherwise be degraded

If created:

- It MUST be written under `.tmp/handoffs/`
- It MUST be treated as a derived artifact
- It MUST NOT act as an execution source
- It SHOULD remain concise and directly actionable
- It MAY be deleted after recovery

## Handoff Content Requirements

If a handoff file is created, it MUST include:

- active execution source
- completed work (verified only)
- validation status (executed or not run)
- unresolved risks or blockers
- next continuation step

It MUST NOT:

- duplicate full spec content
- introduce new plans or decisions
- contradict the active spec

## Output

The skill MUST return:

- `active-source`
- `spec-updated` (yes/no)
- `validation-status`
- `open-risks`
- `next-step`

## Exit Criteria

- The active spec reflects the true session state
- All self-audit checks pass
- No parallel state source has been introduced
- The next session has a clear starting point

## Constraints

- The skill MUST NOT introduce new rules.
- The skill MUST NOT modify contracts or governance structure.
- The skill MUST prioritize spec correctness over summary completeness.
- The skill SHOULD minimize output size.
- The skill MAY skip artifact creation if unnecessary.
