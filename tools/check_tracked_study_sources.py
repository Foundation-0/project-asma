#!/usr/bin/env python3
"""Fail if git tracks pinned study source file patterns.

Exit codes: 0 when git lists this tree's files and none matches; 1 when git
tracks or stages a matching path; 2 when the tree was not checked, because an
unchecked tree must not pass: git cannot list tracked files (no git, not a
checkout, or a git error), or git lists none (a fresh repository, or a tree
inside a repository that does not track it).
"""

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
    # git ls-files prints repository-relative paths with no leading slash, so the
    # top-level scratch folder that .gitignore reserves must match at the start.
    re.compile(r"(^|/)pilot-001-scratch/"),
    re.compile(r"PDC00035[7-9]\.tsv$"),
    re.compile(r"PDC00036[0-2]\.tsv$"),
)
UNLISTED = "cannot list tracked files with git, so the tree was not checked"


class GitListingError(RuntimeError):
    """git did not list this tree's tracked files, so the tree was not checked."""


def tracked_paths() -> list[str]:
    # -z prints each path verbatim; without it git quotes and escapes unusual
    # names (non-ASCII, tabs, quotes), and the anchored patterns would miss them.
    try:
        completed = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise GitListingError(f"{UNLISTED} (git: {error})") from None
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", "replace").strip().splitlines()
        reason = detail[0] if detail else f"git exited {completed.returncode}"
        raise GitListingError(f"{UNLISTED} (git: {reason})")
    paths = [path for path in completed.stdout.decode("utf-8", "replace").split("\0") if path]
    if not paths:
        # Git ran but examined nothing here; an empty listing is not a clean tree.
        raise GitListingError("git lists no tracked files in this tree, so the tree was not checked")
    return paths


def main() -> int:
    try:
        paths = tracked_paths()
    except GitListingError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    violations = []
    for path in paths:
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
