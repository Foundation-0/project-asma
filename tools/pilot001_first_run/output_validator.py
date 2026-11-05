"""Validate aggregate-only first-run outputs."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

IDENTIFIER_LIKE = re.compile(
    r"(patient|sample|specimen|aliquot|mrn|uuid|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
    re.I,
)
ROW_LEVEL_KEYS = frozenset(
    {
        "scores",
        "repetition_scores",
        "patient_ids",
        "sample_ids",
        "row_names",
        "values",
        "x",
        "y",
        "keys",
    }
)


def _walk(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ROW_LEVEL_KEYS:
                errors.append(f"forbidden_key:{path}.{key}")
                continue
            _walk(item, f"{path}.{key}", errors)
        return
    if isinstance(value, list):
        if len(value) > 64 and all(isinstance(x, (int, float)) for x in value[: min(len(value), 128)]):
            errors.append(f"suspected_vector:{path}")
        for index, item in enumerate(value[:200]):
            _walk(item, f"{path}[{index}]", errors)
        return
    if isinstance(value, str):
        if len(value) > 120 and IDENTIFIER_LIKE.search(value):
            errors.append(f"suspected_identifier:{path}")
        if IDENTIFIER_LIKE.search(value) and len(value.split()) == 1 and len(value) > 12:
            errors.append(f"suspected_identifier:{path}")


def validate_aggregate_document(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != 1:
        errors.append("schema_version")
    if payload.get("review_status") != "exploratory_not_externally_reviewed":
        errors.append("review_status")
    _walk(payload, "root", errors)
    return errors


def validate_output_dir(output_dir: Path, declared_files: frozenset[str]) -> list[str]:
    errors: list[str] = []
    if not output_dir.is_dir():
        return ["missing_output_dir"]
    seen = {path.name for path in output_dir.iterdir() if path.is_file()}
    extra = seen - set(declared_files)
    missing = set(declared_files) - seen
    if extra:
        errors.append(f"unexpected_files:{','.join(sorted(extra))}")
    if missing:
        errors.append(f"missing_files:{','.join(sorted(missing))}")
    aggregate_name = "pilot001-first-run-aggregate.json"
    for name in declared_files:
        if name not in seen:
            continue
        try:
            payload = json.loads((output_dir / name).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            errors.append(f"invalid_json:{name}")
            continue
        if name == aggregate_name:
            errors.extend(f"{name}:{item}" for item in validate_aggregate_document(payload))
    return errors
