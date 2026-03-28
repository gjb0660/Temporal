---
name: odas-workflow
description: "Execute ODAS integration and debugging with correct sequencing, stream handling, and separation of ODAS-domain vs downstream issues."
---

# ODAS Workflow Skill

## Role

This skill defines the **execution procedure** for integrating and debugging ODAS.

It MUST orchestrate actions using:

- ODAS domain knowledge (see `specs/knowledge/odas.md`)
- ODAS domain constraints (see `specs/contracts/odas-integration.md`)

It MUST NOT redefine knowledge or constraints.

## When To Use

Use this skill when the task involves:

- ODAS integration (odaslive / odascore)
- ODAS configuration validation
- SSL / SST / SSS stream debugging
- Socket data consumption
- Sound source localization / tracking issues
- Audio separation pipeline validation

## Required Inputs

Before execution, the agent MUST identify:

- ODAS execution mode (local process / container / remote)
- Active config file (single source of truth)
- Enabled sinks (SSL / SST / SSS)
- Target host and ports
- Downstream consumer (parser / recorder / UI / pipeline)

If any of the above is unknown, the agent MUST resolve it before proceeding.

## Execution Workflow

### 1. Validate Execution Source

- The agent MUST confirm which binary is used (`odaslive`, `odascore`, or wrapper)
- The agent MUST confirm the exact config file path
- The agent MUST NOT assume defaults

### 2. Validate Configuration

- The agent MUST verify that enabled sinks match intended outputs
- The agent MUST verify:
  - interface type (tcp / file / etc.)
  - IP / port
  - format (json / raw / audio)
- The agent SHOULD detect unused or conflicting sections

### 3. Validate Transport Layer

- The agent MUST verify socket connectivity
- In remote setups:
  - The listening side MUST be started before ODAS
- The agent MUST verify:
  - bind address correctness
  - firewall / network reachability

### 4. Validate Stream Framing

- The agent MUST treat socket data as a **byte stream**, not message boundaries
- The agent MUST:
  - support multiple messages per read
  - support partial message reconstruction
- The agent MUST NOT assume `recv()` == one JSON message

### 5. Validate Semantic Interpretation

- The agent MUST distinguish:
  - SSL → localization candidates
  - SST → tracked sources
  - SSS → audio streams
- The agent MUST NOT infer lifecycle semantics without contract definition
- Placeholder / zero-value entries MUST be handled via explicit rules

### 6. Isolate ODAS vs Downstream Issues

The agent MUST separate:

| Layer | Responsibility |
| ------ | ------ |
| ODAS | produces streams |
| Consumer | parses streams |
| Product | interprets meaning |

The agent MUST NOT attribute downstream bugs to ODAS without evidence.

### 7. Verify Downstream via Contracts

If behavior involves:

- source lifecycle
- recording rules
- UI updates
- naming conventions

The agent MUST validate against `specs/contracts/**`.

The agent MUST NOT infer or invent such rules.

## Debug Checklist

The agent MUST verify:

- ODAS process runs with correct config
- Each sink has a reachable consumer
- Stream parsing handles concatenation and fragmentation
- SSL / SST / SSS are not confused
- Startup order is correct
- Audio parameters match expectations
- All non-ODAS behavior is backed by contracts

## Exit Criteria

This skill is complete ONLY when:

- ODAS behavior is explained by verified facts
- Stream transport and parsing are correct
- Semantic interpretation is explicitly defined
- ODAS issues are isolated from downstream issues
- No implicit assumptions remain
