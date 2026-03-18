# PRD: Phase A Project Skeleton

## Goal

Establish a runnable Temporal baseline with Python and QML.

## Scope

- Initialize Python project for version 3.10.
- Set up uv workflow and virtual environment usage.
- Create a minimal PySide6 application entry chain.
- Load Main.qml from Python startup path.

## Non-Goals

- ODAS network stream ingestion.
- SSH remote lifecycle control.
- Recording or visualization business logic.

## Functional Requirements

1. Provide a launchable main entrypoint.
2. Keep source tree as namespace packages.
3. Keep QML and backend wiring separated by appBridge.
4. Show a basic main window without runtime crash.

## Quality Requirements

- Keep pyright configuration enabled.
- Keep markdownlint clean for touched docs.
- Keep unittest discovery command executable.

## Acceptance Criteria

1. App starts from local environment with one command.
2. Main window renders successfully.
3. No __init__.py is added under src namespace tree.
