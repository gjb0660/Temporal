---
name: odas-workflow
description: "Use when: implementing or debugging ODAS stream ingestion, SSH lifecycle control, source visualization, and auto-recording in Temporal."
---

# ODAS Workflow Skill

## When To Use
Use this skill for tasks involving ODAS protocol handling, remote odaslive control, source lifecycle transitions, and recording correctness.

## Workflow
1. Validate remote control path (SSH key, host, command, status).
2. Validate SST/SSL framing and message schema parsing.
3. Validate source lifecycle transitions (appear, active, inactive, disappear).
4. Validate recorder transitions and output naming contract.
5. Validate UI update path from backend callbacks to QML bindings.

## Debug Checklist
- SSH connect/start/stop/status commands return explicit success or failure.
- SST stream includes src array and filters id 0 as invalid source.
- SSL stream filtering reacts to UI thresholds.
- Reconnect logic recovers after transient network failures.
- Recording files follow ODAS_{source_id}_{timestamp}_{sp|pf}.wav.

## Exit Criteria
- Remote lifecycle control works end-to-end.
- Visualization updates continuously for active sources.
- Auto recording starts and stops correctly by source lifecycle.
- Static checks and tests pass for touched modules.
