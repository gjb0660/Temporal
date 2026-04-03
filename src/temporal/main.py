from __future__ import annotations

# pyright: reportMissingImports=false
import sys
from typing import cast

from PySide6.QtGui import QGuiApplication

from temporal.app.bridge import run, run_with_bridge
from temporal.preview_bridge import PreviewBridge


def _ensure_app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is not None:
        return cast(QGuiApplication, app)
    return QGuiApplication(sys.argv)


def main() -> int:
    return run()


def preview_main() -> int:
    _ensure_app()
    return run_with_bridge(PreviewBridge())


if __name__ == "__main__":
    raise SystemExit(main())
