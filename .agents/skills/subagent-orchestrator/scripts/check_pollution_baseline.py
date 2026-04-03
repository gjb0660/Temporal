#!/usr/bin/env python3
"""Capture and compare git pollution baselines for stage gates."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_git_status(cwd: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git status failed")
    return [line for line in proc.stdout.splitlines() if line.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Capture stage-entry pollution baseline or compare current status "
            "against a baseline to block incremental pollution."
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--capture", action="store_true", help="Capture baseline.")
    mode.add_argument("--compare", action="store_true", help="Compare with baseline.")
    parser.add_argument(
        "--baseline",
        required=True,
        help="Baseline JSON path.",
    )
    parser.add_argument(
        "--report",
        help="Optional compare report JSON path.",
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="Git working directory (default: current directory).",
    )
    return parser.parse_args()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def capture_mode(cwd: Path, baseline_path: Path) -> int:
    entries = run_git_status(cwd)
    payload = {
        "captured_at_utc": now_utc_iso(),
        "cwd": str(cwd),
        "entries": entries,
    }
    write_json(baseline_path, payload)
    print(f"[INFO] Baseline captured: {baseline_path} entries={len(entries)}")
    return 0


def compare_mode(cwd: Path, baseline_path: Path, report_path: Path | None) -> int:
    baseline_raw = json.loads(baseline_path.read_text(encoding="utf-8"))
    baseline_entries = set(baseline_raw.get("entries", []))
    current_entries = set(run_git_status(cwd))

    introduced = sorted(current_entries - baseline_entries)
    resolved = sorted(baseline_entries - current_entries)
    passed = len(introduced) == 0

    report = {
        "checked_at_utc": now_utc_iso(),
        "cwd": str(cwd),
        "baseline_path": str(baseline_path),
        "baseline_entries_count": len(baseline_entries),
        "current_entries_count": len(current_entries),
        "introduced_entries_count": len(introduced),
        "resolved_entries_count": len(resolved),
        "introduced_entries": introduced,
        "resolved_entries": resolved,
        "pass": passed,
    }

    if report_path is not None:
        write_json(report_path, report)
        print(f"[INFO] Compare report written: {report_path}")

    if passed:
        print("[INFO] Pollution check pass: no incremental pollution.")
        return 0

    print("[ERROR] Pollution check fail: incremental pollution detected.")
    for entry in introduced:
        print(f"  + {entry}")
    return 1


def main() -> int:
    args = parse_args()
    cwd = Path(args.cwd).resolve()
    baseline_path = Path(args.baseline).resolve()
    report_path = Path(args.report).resolve() if args.report else None

    try:
        if args.capture:
            return capture_mode(cwd, baseline_path)
        return compare_mode(cwd, baseline_path, report_path)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
