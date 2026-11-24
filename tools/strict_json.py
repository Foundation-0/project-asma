"""Strict JSON parsing for repository-authored files; Python standard library only.

``json.loads`` keeps the last of two equal keys in one object, so a reader who scans
a file from the top sees one value while a checker silently uses another. It also
accepts the non-standard constants ``NaN``, ``Infinity`` and ``-Infinity``, and reads
an overflowing literal such as ``1e999`` as infinity. ``loads`` refuses all of these
with a ``ValueError`` that names the problem.

Use it for JSON this repository writes (registries, result manifests, certificates,
reports, audits, runtime records, test fixtures). Raw third-party responses kept
byte-identical under ``results/*/snapshot/`` are evidence, not repository-authored
files, and are not held to this rule.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _reject_constant(name: str) -> Any:
    raise ValueError(f"non-finite JSON number {name}")


def _finite_float(literal: str) -> float:
    value = float(literal)
    if not math.isfinite(value):
        raise ValueError(f"non-finite JSON number {literal}")
    return value


def loads(text: str) -> Any:
    """Parse ``text`` like ``json.loads``, refusing duplicate keys and non-finite numbers."""
    return json.loads(
        text,
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_constant,
        parse_float=_finite_float,
    )


def load_path(path: Path) -> Any:
    """Read UTF-8 JSON from ``path`` strictly; a parse error names the file."""
    try:
        return loads(Path(path).read_text(encoding="utf-8"))
    except ValueError as error:
        raise ValueError(f"{path}: {error}") from None
