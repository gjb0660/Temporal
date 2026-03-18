# Temporal Repository Instructions

## Project Intent
Temporal is a Python + QML ODAS upper-computer client focused on:
- SSH private-key based remote odaslive lifecycle control.
- Real-time SSL/SST/SSS visualization.
- Source-driven automatic recording.

## Technical Stack
- Python 3.10
- PySide6 + QML
- uv + venv

## Architecture Boundaries
- Python backend layer: src/temporal/core
  - network: ODAS stream clients and parsing
  - ssh: remote odaslive lifecycle control
  - recording: source-driven recorder state and file writing
- Bridge and startup: src/temporal/app.py, src/temporal/main.py
- QML presentation: src/temporal/ui/qml

QML must not open sockets directly. All service actions go through appBridge slots/signals.

## ODAS Protocol Constraints
- SST tracked JSON stream: port 9000
- SSL potential JSON stream: port 9001
- SSS separated PCM stream: port 10000
- SSS post-filtered PCM stream: port 10010

Keep stream handlers tolerant to chunk boundaries, malformed lines, and reconnect scenarios.

## Recording Contract
- Filename format: ODAS_{source_id}_{timestamp}_{sp|pf}.wav
- Recording lifecycle: source appears -> start; source disappears/inactive timeout -> stop

## Quality Gates
Run these checks before merge:
- pyright
- ruff check src tests
- pytest

## Additional Rules
- Python source tree uses namespace packages; do not add __init__.py files.
- Keep Pyright enabled and aligned with pyproject.toml settings.

## Collaboration Rules
- Ask via vscode_askQuestions whenever requirements are ambiguous.
- Run markdownlint for markdown changes and fix syntax violations.
- Write AI-facing docs and code comments in concise English imperative style.
- Write human-facing docs and chat responses in concise Chinese technical style.
- Deliver or update a PRD before implementing a feature.
- Follow Explore -> Plan -> Approval -> Code before implementation.
- After each bug fix, record a local lesson-learned rule.
- Only use git add and git commit; never rewrite or delete git history.
- Never modify or delete files outside the current workspace.
