# Repository Instructions

## Scope

Defines repository-wide facts, engineering constraints, and quality gates.

- Agent workflow MUST follow AGENTS.md.
- Specs are the single source of truth.
- Docs are human-readable export from specs.

## Source of Truth

- [specs/knowledge/architecture.md](../specs/knowledge/architecture.md)

## Repository Rules

- Python code MUST stay under src/temporal/**
- QML code MUST stay under src/temporal/qml/**
- Tests case MUST stay under tests/**
- Python MUST NOT __init__.py in namespace packages

### 1. Writing Rules

- MUST ONLY be UTF-8 + LF
- SHOULD English for code/github, bilingual for docs

### 2. Git Rules

- MUST NOT rewrite or delete history
- MUST NOT modify files outside workspace

## Repository Checks

Before commit, MUST pass:

- `uv run pyright --project pyproject.toml`
- `uv run ruff check src tests`
- `uv run ruff format src tests`

- `uv run pyside6-qmllint <qml-files>`
- `uv run pyside6-qmlformat -i <qml-files>`

- `npx markdownlint **/*.md .github/**/*.md`

- `uv run python -m unittest discover -s tests -p "test_*.py" -v`