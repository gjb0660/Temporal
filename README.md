# Temporal

Temporal is an ODAS-oriented array speech upper-computer client built with Python + QML.

## Stack
- Python 3.10
- uv + venv
- PySide6 (QML)

## Quick Start
```powershell
uv venv --python 3.10
.\.venv\Scripts\Activate.ps1
uv sync
uv run temporal
```

## MVP Scope
- SSH private-key based remote ODAS lifecycle control
- SST/SSL/SSS data pipeline scaffolding
- Source Elevation and Azimut chart placeholders
- 3D source sphere placeholder + source/filter side panel
- Auto recording state machine skeleton

## Structure
- src/temporal: application code
- src/temporal/ui/qml: QML pages and components
- src/temporal/core: SSH/network/recording services
- .github/instructions: agent-scoped instructions
