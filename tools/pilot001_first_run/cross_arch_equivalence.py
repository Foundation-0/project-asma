"""Compare synthetic pipeline aggregates across linux/amd64 and linux/arm64."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TOLERANCE = ROOT / "registries/pilot-001-cross-arch-equivalence-tolerance.json"
PASS_FILENAME = "pilot001-cross-arch-equivalence-pass.json"
FAILURE_CODE = "P001-FAIL-CROSS-ARCH-EQUIVALENCE"
GATE_FAILURE_CODE = "P001-FAIL-GATE-CROSS-ARCH-EQUIVALENCE"
IMAGE_ID = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass
class MetricDelta:
    path: str
    amd64: Any
    arm64: Any
    allowed: float
    observed: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "amd64": self.amd64,
            "arm64": self.arm64,
            "allowed_delta": self.allowed,
            "observed_delta": self.observed,
        }


@dataclass
class ComparisonResult:
    passed: bool
    failure_code: str | None = None
    deltas: list[MetricDelta] = field(default_factory=list)
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"passed": self.passed}
        if self.failure_code:
            payload["failure_code"] = self.failure_code
        if self.message:
            payload["message"] = self.message
        if self.deltas:
            payload["deltas"] = [item.to_dict() for item in self.deltas]
        return payload


def load_tolerance(path: Path | None = None) -> dict[str, Any]:
    data = json.loads((path or TOLERANCE).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("invalid tolerance registry")
    return data


def _resolve_path(payload: dict[str, Any], dotted: str) -> Any:
    current: Any = payload
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            raise KeyError(dotted)
        current = current[part]
    return current


def _allowed_delta(reference: float, tolerance: dict[str, Any]) -> float:
    absolute = float(tolerance["absolute_tolerance"])
    relative = float(tolerance["relative_tolerance"])
    return max(absolute, abs(reference) * relative)


def compare_synthetic_records(
    amd64_record: dict[str, Any],
    arm64_record: dict[str, Any],
    *,
    tolerance: dict[str, Any] | None = None,
) -> ComparisonResult:
    tolerance = tolerance or load_tolerance()
    for record, label in ((amd64_record, "amd64"), (arm64_record, "arm64")):
        if record.get("scope") != "Synthetic fixtures only; no source-study data or clinical performance result":
            return ComparisonResult(False, FAILURE_CODE, message=f"unexpected scope on {label}")
        integration = record.get("integration") or {}
        if not integration.get("executed"):
            return ComparisonResult(False, FAILURE_CODE, message=f"integration not executed on {label}")

    deltas: list[MetricDelta] = []
    for path in tolerance["integer_paths"]:
        left = _resolve_path(amd64_record, path)
        right = _resolve_path(arm64_record, path)
        if left != right:
            deltas.append(MetricDelta(path, left, right, 0, abs(float(left) - float(right))))
    for path in tolerance["float_paths"]:
        left = float(_resolve_path(amd64_record, path))
        right = float(_resolve_path(arm64_record, path))
        allowed = _allowed_delta(left, tolerance)
        observed = abs(left - right)
        if observed > allowed:
            deltas.append(MetricDelta(path, left, right, allowed, observed))
    if deltas:
        return ComparisonResult(False, FAILURE_CODE, deltas=deltas)
    return ComparisonResult(True)


def build_pass_record(
    *,
    amd64_record: dict[str, Any],
    arm64_record: dict[str, Any],
    comparison: ComparisonResult,
    git_sha: str | None = None,
    tolerance_path: Path | None = None,
) -> dict[str, Any]:
    tolerance = load_tolerance(tolerance_path)
    amd64_image = amd64_record.get("environment", {}).get("runtime_image_id")
    arm64_image = arm64_record.get("environment", {}).get("runtime_image_id")
    if not isinstance(amd64_image, str) or not IMAGE_ID.fullmatch(amd64_image):
        raise ValueError("amd64 runtime_image_id missing")
    if not isinstance(arm64_image, str) or not IMAGE_ID.fullmatch(arm64_image):
        raise ValueError("arm64 runtime_image_id missing")
    return {
        "schema_version": 1,
        "passed": comparison.passed,
        "failure_code": comparison.failure_code,
        "git_sha": git_sha,
        "amd64_synthetic_image_id": amd64_image,
        "arm64_synthetic_image_id": arm64_image,
        "tolerance_registry": "registries/pilot-001-cross-arch-equivalence-tolerance.json",
        "absolute_tolerance": tolerance["absolute_tolerance"],
        "relative_tolerance": tolerance["relative_tolerance"],
        "compared_paths": tolerance["integer_paths"] + tolerance["float_paths"],
        "amd64_finished_at_utc": amd64_record.get("finished_at_utc"),
        "arm64_finished_at_utc": arm64_record.get("finished_at_utc"),
    }


def load_pass_record(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if data.get("schema_version") != 1 or data.get("passed") is not True:
        return None
    for key in ("amd64_synthetic_image_id", "arm64_synthetic_image_id"):
        value = data.get(key)
        if not isinstance(value, str) or not IMAGE_ID.fullmatch(value):
            return None
    return data


def pass_record_matches_images(
    record: dict[str, Any],
    *,
    amd64_image_id: str,
    arm64_image_id: str,
) -> bool:
    return (
        record.get("amd64_synthetic_image_id") == amd64_image_id
        and record.get("arm64_synthetic_image_id") == arm64_image_id
    )


def validate_macos_arm64_equivalence(
    *,
    machine_arch: str,
    real_mode: bool,
    equivalence_record: Path,
    amd64_image_id: str,
    arm64_image_id: str,
) -> str | None:
    if machine_arch != "arm64" or not real_mode:
        return None
    record = load_pass_record(equivalence_record)
    if record is None:
        return GATE_FAILURE_CODE
    if not pass_record_matches_images(
        record, amd64_image_id=amd64_image_id, arm64_image_id=arm64_image_id
    ):
        return GATE_FAILURE_CODE
    return None
