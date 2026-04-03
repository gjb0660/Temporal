#!/usr/bin/env python3
"""Run fast/full stage gate profiles and emit normalized reports."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CommandResult:
    command: str
    exit_code: int
    duration_sec: float
    stdout: str
    stderr: str


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def truncate(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]"


def load_profiles(commands_file: Path) -> dict[str, list[str]]:
    raw = json.loads(commands_file.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("commands file must be a JSON object")
    profiles: dict[str, list[str]] = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            raise ValueError("profile keys must be strings")
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ValueError(f"profile '{key}' must be a list of command strings")
        profiles[key] = value
    return profiles


def run_command(command: str, cwd: Path) -> CommandResult:
    start = time.perf_counter()
    proc = subprocess.run(  # noqa: S602
        command,
        shell=True,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    duration = time.perf_counter() - start
    return CommandResult(
        command=command,
        exit_code=proc.returncode,
        duration_sec=round(duration, 3),
        stdout=truncate(proc.stdout),
        stderr=truncate(proc.stderr),
    )


def build_report(
    profile: str,
    cwd: Path,
    started_at: str,
    ended_at: str,
    results: list[CommandResult],
) -> dict[str, Any]:
    passed = sum(1 for r in results if r.exit_code == 0)
    failed = len(results) - passed
    return {
        "profile": profile,
        "cwd": str(cwd),
        "started_at_utc": started_at,
        "ended_at_utc": ended_at,
        "total_commands": len(results),
        "passed_commands": passed,
        "failed_commands": failed,
        "pass": failed == 0,
        "results": [asdict(r) for r in results],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a gate profile and emit a normalized JSON report.",
    )
    parser.add_argument(
        "--profile",
        required=True,
        help="Profile to run, e.g. fast or full.",
    )
    parser.add_argument(
        "--commands-file",
        required=True,
        help='JSON file: {"fast": ["cmd1"], "full": ["cmd2"]}.',
    )
    parser.add_argument(
        "--report",
        required=True,
        help="Output JSON report path.",
    )
    parser.add_argument(
        "--cwd",
        default=".",
        help="Working directory for commands (default: current directory).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cwd = Path(args.cwd).resolve()
    commands_file = Path(args.commands_file).resolve()
    report_path = Path(args.report).resolve()

    profiles = load_profiles(commands_file)
    if args.profile not in profiles:
        print(f"[ERROR] Profile '{args.profile}' not found in {commands_file}")
        return 2

    commands = profiles[args.profile]
    if not commands:
        print(f"[ERROR] Profile '{args.profile}' has no commands.")
        return 2

    started_at = now_utc_iso()
    results = [run_command(cmd, cwd) for cmd in commands]
    ended_at = now_utc_iso()
    report = build_report(args.profile, cwd, started_at, ended_at, results)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(
        f"[INFO] Profile={report['profile']} pass={report['pass']} "
        f"passed={report['passed_commands']} failed={report['failed_commands']}"
    )
    print(f"[INFO] Report written to {report_path}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
