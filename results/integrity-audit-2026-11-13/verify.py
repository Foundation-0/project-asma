#!/usr/bin/env python3
"""Offline replay guard for the integrity-layer checker audit."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    completed = subprocess.run(
        [sys.executable, str(ROOT / "tools/audit_checkers.py"), "--check"],
        cwd=ROOT,
        check=False,
    )
    if completed.returncode != 0:
        print("FAIL: integrity audit verification", file=sys.stderr)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
