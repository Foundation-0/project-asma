"""Validate aggregate-only first-run outputs (strict allowlist schema, fail closed)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pilot001_first_run.config import DRY_REPETITIONS, REAL_REPETITIONS

TCGA_BARCODE = re.compile(
    r"TCGA-[0-9A-Z]{2}-[0-9A-Z0-9]{4}(?:-[0-9A-Z0-9]{2,})*",
    re.I,
)
TCGA_DASHLESS = re.compile(r"TCGA[0-9A-Z]{6,}", re.I)
UNICODE_HYPHENS = frozenset("\u2010\u2011\u2012\u2013\u2014\u2212\ufe58\ufe63\uff0d")
NUMERIC_STRING = re.compile(r"^[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?$")
UUID_LIKE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.I,
)
BASE64_LIKE = re.compile(r"^[A-Za-z0-9+/]+=*$")

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
METADATA_KEYS = frozenset(
    {"git_sha", "runtime_image_id", "runtime_image_digest", "container_platform", "host_uname_m", "r_version"}
)
AMENDMENT_KEYS = frozenset({"A1", "A2", "A3"})
A2_KEYS = frozenset({"option_a", "option_b"})

ALLOWED_CONFIG_LABELS = frozenset(
    {
        "primary",
        "sensitivity_xgb_hist",
        "sensitivity_seed_block_101_200",
    }
)
ALLOWED_XGB_TREE_METHODS = frozenset({"exact", "hist"})
ALLOWED_INPUT_MODES = frozenset({"synthetic_fixture", "pinned_real_sources"})
REVIEW_STATUS = "exploratory_not_externally_reviewed"
AMENDMENT_A3_VALUE = "strict"

MAX_NUMERIC_VECTOR = 31
MAX_SCORELIKE_DICT = 20
MAX_CONFIGURATIONS = 8
MAX_STRING_FIELD = 512
MAX_LIMITATIONS = 12
MIN_OUTER_SEED = 1
MAX_OUTER_SEED = 10_000

PROFILE_DRY = "dry"
PROFILE_REAL = "real"
PROFILES = frozenset({PROFILE_DRY, PROFILE_REAL})

# Frozen protocol configuration set: (label, outer_seed_start, xgb_tree_method).
REAL_CONFIGURATIONS = (
    ("primary", 1, "exact"),
    ("sensitivity_xgb_hist", 1, "hist"),
    ("sensitivity_seed_block_101_200", 101, "exact"),
)
REAL_PATIENTS = 135
REAL_FEATURES = 64
REAL_POSITIVE_NEGATIVE_PAIRS = 4316

SUMMARY_INT_FIELDS = frozenset(
    {
        "patients",
        "features",
        "repetitions",
        "outer_folds",
        "model_predictions",
        "ensemble_predictions",
        "final_scores",
        "positive_negative_pairs",
    }
)
SUMMARY_FLOAT_FIELDS = frozenset({"auc", "rank_auc"})
SUMMARY_BOOL_FIELDS = frozenset({"complete_prediction_coverage"})
REPETITION_AUC_KEYS = frozenset(
    {"count", "minimum", "lower_quartile", "median", "upper_quartile", "maximum", "mean"}
)
REPETITION_AUC_FLOAT_KEYS = frozenset(
    {"minimum", "lower_quartile", "median", "upper_quartile", "maximum", "mean"}
)


def _exact_keys(value: dict[str, Any], allowed: frozenset[str], path: str, errors: list[str]) -> bool:
    extra = set(value) - allowed
    missing = allowed - set(value)
    if extra:
        errors.append(f"unexpected_keys:{path}:{','.join(sorted(extra))}")
    if missing:
        errors.append(f"missing_keys:{path}:{','.join(sorted(missing))}")
    return not extra and not missing


def _forbidden_key(name: str) -> bool:
    lowered = name.lower()
    if lowered in FORBIDDEN_KEY_TOKENS:
        return True
    return any(token in lowered for token in ("patient_id", "sample_id", "row_name"))


def _looks_like_base64_payload(value: str) -> bool:
    if len(value) < 48:
        return False
    if not BASE64_LIKE.match(value):
        return False
    return len(value) % 4 == 0 or value.endswith("=")


def _suspicious_string(value: str, path: str, errors: list[str]) -> None:
    if TCGA_BARCODE.search(value):
        errors.append(f"suspected_identifier:{path}")
    if "TCGA" in value.upper():
        if TCGA_DASHLESS.search(value):
            errors.append(f"suspected_identifier:{path}")
        if any(character in value for character in UNICODE_HYPHENS):
            errors.append(f"suspected_identifier:{path}")
    if UUID_LIKE.search(value) and len(value) <= 80:
        errors.append(f"suspected_identifier:{path}")


def _check_bounded_string(value: str, path: str, errors: list[str], *, check_base64: bool) -> None:
    if len(value) > MAX_STRING_FIELD:
        errors.append(f"string_too_long:{path}")
    _suspicious_string(value, path, errors)
    if check_base64 and _looks_like_base64_payload(value):
        errors.append(f"suspected_base64:{path}")


def _require_string(value: Any, path: str, errors: list[str], *, check_base64: bool = False) -> None:
    if not isinstance(value, str):
        errors.append(f"type:{path}")
        return
    _check_bounded_string(value, path, errors, check_base64=check_base64)


def _require_bool(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, bool):
        errors.append(f"type:{path}")


def _require_int(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, int) or isinstance(value, bool):
        errors.append(f"type:{path}")


def _require_number(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        errors.append(f"type:{path}")


def _validate_repetition_auc(item: Any, path: str, errors: list[str], profile: str) -> None:
    if isinstance(item, list):
        if len(item) > MAX_NUMERIC_VECTOR and all(
            isinstance(x, (int, float)) and not isinstance(x, bool) for x in item
        ):
            errors.append(f"suspected_vector:{path}")
        errors.append(f"type:{path}")
        return
    if not isinstance(item, dict):
        errors.append(f"type:{path}")
        return
    if not _exact_keys(item, REPETITION_AUC_KEYS, path, errors):
        return
    _require_int(item["count"], f"{path}.count", errors)
    if profile == PROFILE_REAL:
        count = item["count"]
        if isinstance(count, int) and not isinstance(count, bool) and count != REAL_REPETITIONS:
            errors.append(f"repetitions:{path}.count")
    for key in REPETITION_AUC_FLOAT_KEYS:
        _require_number(item[key], f"{path}.{key}", errors)


def _validate_summary(value: Any, path: str, errors: list[str], profile: str) -> None:
    if not isinstance(value, dict):
        errors.append(f"schema:{path}")
        return
    if not _exact_keys(value, SUMMARY_KEYS, path, errors):
        return
    for key, item in value.items():
        if _forbidden_key(key):
            errors.append(f"forbidden_key:{path}.{key}")
            continue
        if key in SUMMARY_FLOAT_FIELDS:
            _require_number(item, f"{path}.{key}", errors)
        elif key == "repetition_auc":
            _validate_repetition_auc(item, f"{path}.repetition_auc", errors, profile)
        elif key in SUMMARY_INT_FIELDS:
            _require_int(item, f"{path}.{key}", errors)
        elif key in SUMMARY_BOOL_FIELDS:
            _require_bool(item, f"{path}.{key}", errors)
    expected_repetitions = REAL_REPETITIONS if profile == PROFILE_REAL else DRY_REPETITIONS
    repetitions = value["repetitions"]
    if (
        isinstance(repetitions, int)
        and not isinstance(repetitions, bool)
        and repetitions != expected_repetitions
    ):
        errors.append(f"repetitions:{path}.repetitions")
    if profile == PROFILE_REAL:
        for key, expected in (
            ("patients", REAL_PATIENTS),
            ("features", REAL_FEATURES),
            ("positive_negative_pairs", REAL_POSITIVE_NEGATIVE_PAIRS),
        ):
            actual = value[key]
            if isinstance(actual, int) and not isinstance(actual, bool) and actual != expected:
                errors.append(f"denominator:{path}.{key}")


def _validate_configuration(value: Any, path: str, errors: list[str], profile: str) -> None:
    if not isinstance(value, dict):
        errors.append(f"schema:{path}")
        return
    if not _exact_keys(value, CONFIG_KEYS, path, errors):
        return
    label = value["label"]
    _require_string(label, f"{path}.label", errors)
    if isinstance(label, str):
        if label not in ALLOWED_CONFIG_LABELS:
            errors.append(f"label:{path}.label")
        if NUMERIC_STRING.match(label):
            errors.append(f"label:{path}.label")
    _require_int(value["outer_seed_start"], f"{path}.outer_seed_start", errors)
    if isinstance(value["outer_seed_start"], int) and not isinstance(value["outer_seed_start"], bool):
        seed = value["outer_seed_start"]
        if seed < MIN_OUTER_SEED or seed > MAX_OUTER_SEED:
            errors.append(f"range:{path}.outer_seed_start")
    method = value["xgb_tree_method"]
    if not isinstance(method, str) or method not in ALLOWED_XGB_TREE_METHODS:
        errors.append(f"type:{path}.xgb_tree_method")
    _require_bool(value["metric_formulations_agree"], f"{path}.metric_formulations_agree", errors)
    _validate_summary(value["summary"], f"{path}.summary", errors, profile)


def _validate_metadata(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"schema:{path}")
        return
    if not _exact_keys(value, METADATA_KEYS, path, errors):
        return
    for key in METADATA_KEYS:
        item = value[key]
        check_b64 = key == "r_version"
        _require_string(item, f"{path}.{key}", errors, check_base64=check_b64)


def _validate_amendment(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"schema:{path}")
        return
    if not _exact_keys(value, AMENDMENT_KEYS, path, errors):
        return
    _require_bool(value["A1"], f"{path}.A1", errors)
    a2 = value["A2"]
    if not isinstance(a2, dict):
        errors.append(f"type:{path}.A2")
    elif not _exact_keys(a2, A2_KEYS, f"{path}.A2", errors):
        pass
    else:
        _require_bool(a2["option_a"], f"{path}.A2.option_a", errors)
        _require_bool(a2["option_b"], f"{path}.A2.option_b", errors)
    a3 = value["A3"]
    if not isinstance(a3, str) or a3 != AMENDMENT_A3_VALUE:
        errors.append(f"type:{path}.A3")


def _validate_root(payload: dict[str, Any], errors: list[str], profile: str) -> None:
    path = "root"
    if not _exact_keys(payload, ROOT_KEYS, path, errors):
        return
    if payload["schema_version"] != 1:
        errors.append("schema_version")
    if payload["review_status"] != REVIEW_STATUS:
        errors.append("review_status")
    _require_string(payload["scope"], f"{path}.scope", errors, check_base64=True)
    input_mode = payload["input_mode"]
    if not isinstance(input_mode, str) or input_mode not in ALLOWED_INPUT_MODES:
        errors.append(f"type:{path}.input_mode")
    _require_bool(payload["real_study_data_executed"], f"{path}.real_study_data_executed", errors)
    _require_string(payload["started_at_utc"], f"{path}.started_at_utc", errors)
    _require_string(payload["finished_at_utc"], f"{path}.finished_at_utc", errors)
    _require_number(payload["elapsed_seconds"], f"{path}.elapsed_seconds", errors)
    limitations = payload["limitations"]
    if not isinstance(limitations, list):
        errors.append(f"type:{path}.limitations")
    elif len(limitations) > MAX_LIMITATIONS:
        errors.append(f"limitations_count:{path}")
    else:
        for index, entry in enumerate(limitations):
            _require_string(entry, f"{path}.limitations[{index}]", errors, check_base64=True)
    configurations = payload["configurations"]
    if not isinstance(configurations, list):
        errors.append(f"type:{path}.configurations")
    elif len(configurations) > MAX_CONFIGURATIONS or len(configurations) < 1:
        errors.append(f"configurations_count:{path}")
    else:
        for index, cfg in enumerate(configurations):
            _validate_configuration(cfg, f"{path}.configurations[{index}]", errors, profile)
        if profile == PROFILE_REAL:
            actual = [
                (cfg.get("label"), cfg.get("outer_seed_start"), cfg.get("xgb_tree_method"))
                if isinstance(cfg, dict)
                else None
                for cfg in configurations
            ]
            if actual != list(REAL_CONFIGURATIONS):
                errors.append(f"configurations_profile:{path}.configurations")
    _validate_metadata(payload["run_metadata"], f"{path}.run_metadata", errors)
    _validate_amendment(payload["amendment_1"], f"{path}.amendment_1", errors)


def _check_numeric_vector(items: list[Any], path: str, errors: list[str]) -> None:
    if len(items) <= MAX_NUMERIC_VECTOR:
        return
    if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in items):
        errors.append(f"suspected_vector:{path}")
        return
    if all(isinstance(x, str) and NUMERIC_STRING.match(x) for x in items):
        errors.append(f"suspected_vector:{path}")


def _check_scorelike_dict(value: dict[str, Any], path: str, errors: list[str]) -> None:
    if len(value) <= MAX_SCORELIKE_DICT:
        return
    if all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in value.values()):
        errors.append(f"suspected_row_map:{path}")


def _check_nested_score_blocks(value: dict[str, Any], path: str, errors: list[str]) -> None:
    if len(value) < 10:
        return
    nested = [item for item in value.values() if isinstance(item, dict)]
    if len(nested) < 10:
        return
    if all(
        len(sub) >= 15
        and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in sub.values())
        for sub in nested
    ):
        errors.append(f"suspected_nested_scores:{path}")


def _deep_leak_scan(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        _check_scorelike_dict(value, path, errors)
        _check_nested_score_blocks(value, path, errors)
        for key, item in value.items():
            if _forbidden_key(str(key)):
                errors.append(f"forbidden_key:{path}.{key}")
            _deep_leak_scan(item, f"{path}.{key}", errors)
        return
    if isinstance(value, list):
        _check_numeric_vector(value, path, errors)
        for index, item in enumerate(value):
            _deep_leak_scan(item, f"{path}[{index}]", errors)
        return
    if isinstance(value, str):
        _suspicious_string(value, path, errors)


def validate_aggregate_document(payload: dict[str, Any], profile: str) -> list[str]:
    if profile not in PROFILES:
        return ["profile:root"]
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["schema:root"]
    _validate_root(payload, errors, profile)
    _deep_leak_scan(payload, "root", errors)
    return errors


def validate_output_dir(
    output_dir: Path, declared_files: frozenset[str], profile: str
) -> list[str]:
    if profile not in PROFILES:
        return ["profile:root"]
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
            errors.extend(
                f"{name}:{item}" for item in validate_aggregate_document(payload, profile)
            )
    return errors
