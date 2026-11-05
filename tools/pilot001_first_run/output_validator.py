"""Validate aggregate-only first-run outputs (allowlist schema, fail closed)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

TCGA_BARCODE = re.compile(r"TCGA-[0-9A-Z]{2}-[0-9A-Z0-9]{4}", re.I)
NUMERIC_STRING = re.compile(r"^[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?$")
UUID_LIKE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.I,
)

FORBIDDEN_KEY_TOKENS = frozenset(
    {
        "scores",
        "repetition_scores",
        "patient_ids",
        "sample_ids",
        "row_names",
        "values",
        "keys",
        "x",
        "y",
        "patient",
        "sample",
        "specimen",
        "aliquot",
        "mrn",
    }
)

ROOT_KEYS = frozenset(
    {
        "schema_version",
        "review_status",
        "scope",
        "input_mode",
        "real_study_data_executed",
        "amendment_1",
        "started_at_utc",
        "finished_at_utc",
        "elapsed_seconds",
        "configurations",
        "run_metadata",
        "limitations",
    }
)

SUMMARY_KEYS = frozenset(
    {
        "patients",
        "features",
        "repetitions",
        "outer_folds",
        "model_predictions",
        "ensemble_predictions",
        "final_scores",
        "complete_prediction_coverage",
        "positive_negative_pairs",
        "auc",
        "rank_auc",
        "repetition_auc",
    }
)

CONFIG_KEYS = frozenset({"label", "outer_seed_start", "xgb_tree_method", "summary", "metric_formulations_agree"})
METADATA_KEYS = frozenset({"git_sha", "runtime_image_id", "runtime_image_digest", "container_platform", "host_uname_m", "r_version"})
AMENDMENT_KEYS = frozenset({"A1", "A2", "A3"})
A2_KEYS = frozenset({"option_a", "option_b"})

MAX_NUMERIC_VECTOR = 31
MAX_NUMERIC_STRING_VECTOR = 31
MAX_SCORELIKE_DICT = 20


def _forbidden_key(name: str) -> bool:
    lowered = name.lower()
    if lowered in FORBIDDEN_KEY_TOKENS:
        return True
    return any(token in lowered for token in ("patient_id", "sample_id", "row_name"))


def _suspicious_string(value: str, path: str, errors: list[str]) -> None:
    if TCGA_BARCODE.search(value):
        errors.append(f"suspected_identifier:{path}")
    if UUID_LIKE.search(value) and len(value) <= 80:
        errors.append(f"suspected_identifier:{path}")
    if len(value.split()) == 1 and len(value) > 12 and value.isalnum() and any(c.isdigit() for c in value):
        if TCGA_BARCODE.search(value) or value.count("-") >= 2:
            errors.append(f"suspected_identifier:{path}")


def _check_numeric_vector(items: list[Any], path: str, errors: list[str]) -> None:
    if len(items) <= MAX_NUMERIC_VECTOR:
        return
    if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in items):
        errors.append(f"suspected_vector:{path}")
        return
    if len(items) > MAX_NUMERIC_STRING_VECTOR and all(
        isinstance(x, str) and NUMERIC_STRING.match(x) for x in items
    ):
        errors.append(f"suspected_vector:{path}")


def _check_scorelike_dict(value: dict[str, Any], path: str, errors: list[str]) -> None:
    if len(value) <= MAX_SCORELIKE_DICT:
        return
    if all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value.values()):
        errors.append(f"suspected_row_map:{path}")


def _walk_allowed(value: Any, path: str, errors: list[str], *, schema: str) -> None:
    if schema == "root":
        if not isinstance(value, dict):
            errors.append(f"schema:{path}")
            return
        extra = set(value) - ROOT_KEYS
        missing = ROOT_KEYS - set(value)
        if extra:
            errors.append(f"unexpected_keys:{path}:{','.join(sorted(extra))}")
        if missing:
            errors.append(f"missing_keys:{path}:{','.join(sorted(missing))}")
        for key, item in value.items():
            if _forbidden_key(key):
                errors.append(f"forbidden_key:{path}.{key}")
                continue
            if key == "schema_version" and item != 1:
                errors.append("schema_version")
            if key == "review_status" and item != "exploratory_not_externally_reviewed":
                errors.append("review_status")
            if key == "limitations" and isinstance(item, list):
                for index, entry in enumerate(item):
                    if isinstance(entry, str):
                        _suspicious_string(entry, f"{path}.limitations[{index}]", errors)
            if key == "configurations":
                if not isinstance(item, list):
                    errors.append(f"type:{path}.configurations")
                else:
                    for index, cfg in enumerate(item):
                        _walk_allowed(cfg, f"{path}.configurations[{index}]", errors, schema="configuration")
            if key == "run_metadata":
                _walk_allowed(item, f"{path}.run_metadata", errors, schema="metadata")
            if key == "amendment_1":
                _walk_allowed(item, f"{path}.amendment_1", errors, schema="amendment")
        return

    if schema == "configuration":
        if not isinstance(value, dict):
            errors.append(f"schema:{path}")
            return
        if set(value) - CONFIG_KEYS:
            errors.append(f"unexpected_keys:{path}")
        summary = value.get("summary")
        if summary is not None:
            _walk_allowed(summary, f"{path}.summary", errors, schema="summary")
        for key, item in value.items():
            if _forbidden_key(key):
                errors.append(f"forbidden_key:{path}.{key}")
            if isinstance(item, str):
                _suspicious_string(item, f"{path}.{key}", errors)
        return

    if schema == "summary":
        if not isinstance(value, dict):
            errors.append(f"schema:{path}")
            return
        if set(value) - SUMMARY_KEYS:
            errors.append(f"unexpected_keys:{path}")
        _check_scorelike_dict(value, path, errors)
        for key, item in value.items():
            if _forbidden_key(key):
                errors.append(f"forbidden_key:{path}.{key}")
            if isinstance(item, (int, float)) and key.endswith("auc") and not isinstance(item, bool):
                continue
            if isinstance(item, dict):
                _check_scorelike_dict(item, f"{path}.{key}", errors)
        return

    if schema == "metadata":
        if not isinstance(value, dict):
            errors.append(f"schema:{path}")
            return
        if set(value) - METADATA_KEYS:
            errors.append(f"unexpected_keys:{path}")
        for key, item in value.items():
            if isinstance(item, str):
                _suspicious_string(item, f"{path}.{key}", errors)
        return

    if schema == "amendment":
        if not isinstance(value, dict) or set(value) - AMENDMENT_KEYS:
            errors.append(f"schema:{path}")
            return
        a2 = value.get("A2")
        if isinstance(a2, dict) and set(a2) - A2_KEYS:
            errors.append(f"unexpected_keys:{path}.A2")


def validate_aggregate_document(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    _walk_allowed(payload, "root", errors, schema="root")
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
