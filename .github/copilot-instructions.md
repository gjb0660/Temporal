# Temporal Repository Instructions

## Ownership

- This file defines repository-wide technical constraints and quality gates.
- Keep agent workflow, role handoff, and execution process in AGENTS.md.

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
- QML presentation: src/temporal/qml (flat QML layout)

Prefer src layout with PEP 420 namespace packages for Python source tree.

QML must not open sockets directly. All service actions go through appBridge slots/signals.

## ODAS Protocol Constraints

- SST tracked JSON stream: port 9000
- SSL potential JSON stream: port 9001
- SSS separated PCM stream: port 10000
- SSS post-filtered PCM stream: port 10010

Keep stream handlers tolerant to chunk boundaries, malformed lines,
and reconnect scenarios.

## Recording Contract

- Filename format: ODAS_{source_id}_{timestamp}_{sp|pf}.wav
- Recording lifecycle: source appears -> start;
  source disappears/inactive timeout -> stop

## Quality Gates

Run these checks before merge:

- `uv run pyright`
- `uv run pyside6-qmllint src/temporal/qml/Main.qml`
- `npx markdownlint AGENTS.md docs/**/*.md .github/**/*.md specs/**/*.md`
- `uv run ruff check src tests`
- `uv run python -m unittest discover -s tests -p "test_*.py" -v`

## Additional Rules

- Python source tree uses PEP 420 namespace packages; do not add __init__.py files.
- Keep Python modules under src layout (src/temporal/**).
- Keep QML files under flat layout (src/temporal/qml/**).
- Keep Pyright enabled and aligned with pyproject.toml settings.

## Collaboration Rules

- Keep agent workflow rules in `AGENTS.md`; do not duplicate them here.
- Run markdownlint for touched Markdown files and fix all violations
  before merge.
- Write AI-facing docs and code comments in concise English imperative style.
- Write human-facing docs and chat responses in concise Chinese technical style.
- Only use git add and git commit; never rewrite or delete git history.
- Never modify or delete files outside the current workspace.
