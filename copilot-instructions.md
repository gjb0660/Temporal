# Temporal Repository Instructions

## Project Intent
Temporal is a Python + QML ODAS upper-computer client focused on:
- SSH private-key based remote odaslive lifecycle control.
- Real-time SSL/SST/SSS visualization.
- Source-driven automatic recording.

## Architecture Boundaries
- Python service layer lives under `src/temporal/core`.
- QML presentation layer lives under `src/temporal/ui/qml`.
- QML must call Python through explicit bridge slots/signals only.
- Keep ODAS protocol parsing in core/network; do not parse JSON in QML.

## Coding Rules
- Python uses namespace packages; do not add `__init__.py`.
- Keep Python 3.10 compatibility.
- Use dataclass for protocol DTOs and config models.
- Network workers must support reconnect and malformed message tolerance.
- Recording filenames must follow `ODAS_{source_id}_{timestamp}_{sp|pf}.wav`.

## Quality Gates
- Run static checks before merging:
  - Pyright (configured in `pyproject.toml`)
  - Ruff
- Add tests for:
  - JSON stream framing
  - source lifecycle to recording state transitions
  - config parsing defaults and overrides

## UX Direction
- Follow ODAS Studio structure:
  - left monitor/control cards
  - center elevation/azimut charts + 3D source view
  - right source/filter panel
  - bottom status strip
- Prefer deterministic, low-latency updates over heavy visual effects.
