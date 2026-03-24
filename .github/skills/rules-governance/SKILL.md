---
name: rules-governance
description: "Repair governance rule violations by updating the correct owning layer with minimal changes. Keywords: governance repair, rule drift, rule ownership, RFC2119, 规则治理."
argument-hint: "governance gap or failure mode"
---

# Rules Governance Skill

## When To Use

Use when a rule violation has been identified and must be repaired.

## Goal

Restore rule system consistency with minimal changes.

## Core Principle

Each rule MUST have exactly one owning layer.

Other layers MAY reference the rule but MUST NOT redefine it.

## Owning Layers

- AGENTS.md — global agent behavior
- specs/contracts/** — system constraints (MUST NOT break)
- specs/features/** — task-specific constraints
- .github/** — tooling and repository constraints

## Procedure

1. Identify a single failure mode.
2. Classify gap type:
   - conflict
   - missing
   - overlap
   - weak-normative
   - unscoped
3. Determine owning layer.
4. Apply minimal repair to owning layer ONLY.
5. Remove or downgrade duplicated rules in other layers.

## Validation

After repair, the system MUST satisfy:

- rule is expressed using RFC 2119 keywords
- rule is located in the correct owning layer
- no conflicting rule exists
- no duplicated rule remains
- rule is testable or auditable

## Output

Return:

- `failure-mode`
- `gap-type`
- `owner-layer`
- `files-modified`
- `repair`
- `validation-result`
- `remaining-risk`

## Constraints

- Governance MUST NOT create new rules without clear ownership.
- Governance MUST NOT duplicate rules across layers.
- Governance MUST prefer modifying existing rules over adding new ones.
- Governance MUST ensure rules are normative (RFC 2119 compliant).
- Governance SHOULD minimize the number of files modified.
