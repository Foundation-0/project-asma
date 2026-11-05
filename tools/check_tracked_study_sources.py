#!/usr/bin/env python3
"""Fail if git tracks pinned study source file patterns."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = (
    re.compile(r"NIHMS1918576-supplement-MMC[14]\.xlsx$"),
    re.compile(r"\.RData$"),
    re.compile(r"discovery_matrix"),
    re.compile(r"/pilot-001-scratch/"),
    re.compile(r"PDC00035[7-9]\.tsv$"),
    re.compile(r"PDC00036[0-2]\.tsv$"),
)


def tracked_paths() -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return []
    return [line for line in completed.stdout.splitlines() if line.strip()]


def main() -> int:
    violations = []
    for path in tracked_paths():
        for pattern in PATTERNS:
            if pattern.search(path):
                violations.append(path)
                break
    if violations:
        print("FAIL: tracked study source or scratch paths detected:")
        for item in sorted(violations):
            print(item)
        return 1
    print("PASS: no tracked study source paths")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
