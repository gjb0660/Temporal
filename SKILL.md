# Temporal ODAS Skill

## Purpose
Reusable playbook for ODAS client development in Temporal.

## Scenarios
- Add/adjust ODAS stream parser.
- Diagnose remote odaslive control failures.
- Debug source tracking and auto-recording mismatch.
- Tune QML visualization updates.

## Workflow
1. Confirm remote connectivity (SSH key, host, command).
2. Validate SST/SSL framing and message schema.
3. Map source lifecycle events to recorder state transitions.
4. Verify UI update path from core callback to QML binding.

## Debug Checklist
- SSH status command returns running odaslive process.
- SST stream contains `src` array and non-zero ids.
- SSL filter thresholds match UI slider values.
- WAV files appear with expected naming contract.

## Exit Criteria
- Remote control works end-to-end.
- Visualization updates continuously for active sources.
- Auto recording starts/stops correctly by source lifecycle.
