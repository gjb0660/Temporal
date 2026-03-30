# Repository Instructions

## Scope

Defines repository-level facts, constraints, layout, and quality checks.

Read `AGENTS.md` for workflow and execution rules.

## Source of Truth

- [specs/knowledge/architecture.md](../specs/knowledge/architecture.md)

## Repository Layout

- Python code MUST stay under `src/temporal/**`
- QML code MUST stay under `src/temporal/qml/**`
- Tests MUST stay under `tests/**`
- Python SHOULD NOT include `__init__.py` in namespace packages
- Docs SHOULD be human-readable export from specs.

## Writing Rules

- MUST use UTF-8 + LF
- SHOULD use English for code,  AGENTS.md, and `.github` files
- SHOULD use bilingual (e.g. Chinese + English headings) for specs and docs

## Git Rules

- MUST NOT rewrite or delete history
- MUST NOT modify files outside workspace scope

## Repository Checks

Before commit, MUST pass:

- `uv run pyright --project pyproject.toml`
- `uv run ruff check src tests`
- `uv run ruff format src tests`

- `uv run pyside6-qmllint <qml-files>`
- `uv run pyside6-qmlformat -i <qml-files>`

- `npx markdownlint **/*.md .github/**/*.md`

- `uv run python -m unittest discover -s tests -p "test_*.py" -v`
