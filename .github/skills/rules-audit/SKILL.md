---
name: rules-audit
description: "Detect governance rule violations, conflicts, gaps, overlap, and weak normative wording. Keywords: rules audit, governance audit, rule conflict, missing rule, RFC2119, 规则审计."
argument-hint: "audit scope or rule concern"
---

# Rules Audit Skill

## When To Use

Use when validating that governance rules are consistent, complete,
and mechanically enforceable.

## Goal

Detect violations in the rule system that can change agent behavior.

## Rule Model

A rule is valid only if it:

- uses RFC 2119 / RFC 8174 normative keywords (MUST, SHOULD, MAY)
- has a clear owning layer
- is mechanically testable

## Findings

Each finding MUST be classified as one of:

- `conflict` — two rules produce incompatible behavior
- `missing` — required rule is absent
- `overlap` — same rule defined in multiple layers
- `weak-normative` — missing or incorrect RFC2119 keyword
- `unscoped` — no clear ownership layer
- `unverifiable` — cannot be tested or audited

## Output

Return findings ordered by severity:

1. `critical` — behavior divergence or contract violation
2. `major` — incomplete or ambiguous governance
3. `minor` — clarity or redundancy issues

Each finding MUST include:

- `severity`
- `type`
- `file`
- `rule` (normative sentence)
- `violation` (what breaks)
- `impact`
- `minimal-fix`

## Constraints

- Audit MUST NOT introduce new rules.
- Audit MUST NOT modify files.
- Audit MUST rely only on existing rule sources:
  - AGENTS.md
  - specs/** (features + contracts)
  - .github/**
- Audit SHOULD ignore non-governance content.
- Audit MUST flag any rule that does not use RFC 2119 keywords.

## References

[RFC 2119 - Key words for use in RFCs to Indicate Requirement Levels](./references/rfc2119.md)
