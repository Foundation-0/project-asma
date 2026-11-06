"""Compare synthetic pipeline aggregates across linux/amd64 and linux/arm64."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TOLERANCE = ROOT / "registries/pilot-001-cross-arch-equivalence-tolerance.json"
PASS_FILENAME = "pilot001-cross-arch-equivalence-pass.json"
PASS_ARTIFACT_NAME = "pilot001-cross-arch-equivalence-pass"
WORKFLOW_FILE = "cross-arch-equivalence.yml"
PASS_SCHEMA_VERSION = 2
FAILURE_CODE = "P001-FAIL-CROSS-ARCH-EQUIVALENCE"
GATE_FAILURE_CODE = "P001-FAIL-GATE-CROSS-ARCH-EQUIVALENCE"
IMAGE_ID = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
NATIVE_ARM64_ARCH = frozenset({"arm64", "aarch64"})


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
    metrics: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"passed": self.passed}
        if self.failure_code:
            payload["failure_code"] = self.failure_code
        if self.message:
            payload["message"] = self.message
        if self.deltas:
            payload["deltas"] = [item.to_dict() for item in self.deltas]
        if self.metrics:
            payload["metrics"] = self.metrics
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


def collect_metric_audits(
    amd64_record: dict[str, Any],
    arm64_record: dict[str, Any],
    *,
    tolerance: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    tolerance = tolerance or load_tolerance()
    audits: list[dict[str, Any]] = []
    for path in tolerance["integer_paths"]:
        left = _resolve_path(amd64_record, path)
        right = _resolve_path(arm64_record, path)
        difference = abs(float(left) - float(right))
        audits.append(
            {
                "path": path,
                "amd64": left,
                "arm64": right,
                "difference": difference,
                "allowed_delta": 0,
                "within_tolerance": left == right,
            }
        )
    for path in tolerance["float_paths"]:
        left = float(_resolve_path(amd64_record, path))
        right = float(_resolve_path(arm64_record, path))
        difference = abs(left - right)
        allowed = _allowed_delta(left, tolerance)
        audits.append(
            {
                "path": path,
                "amd64": left,
                "arm64": right,
                "difference": difference,
                "allowed_delta": allowed,
                "within_tolerance": difference <= allowed,
            }
        )
    return audits


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

    metrics = collect_metric_audits(amd64_record, arm64_record, tolerance=tolerance)
    deltas: list[MetricDelta] = []
    for item in metrics:
        if item["within_tolerance"]:
            continue
        deltas.append(
            MetricDelta(
                item["path"],
                item["amd64"],
                item["arm64"],
                float(item["allowed_delta"]),
                float(item["difference"]),
            )
        )
    if deltas:
        return ComparisonResult(False, FAILURE_CODE, deltas=deltas, metrics=metrics)
    return ComparisonResult(True, metrics=metrics)


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
    if git_sha is not None and not GIT_SHA.fullmatch(git_sha):
        raise ValueError("git_sha must be a full 40-character commit hash")
    metrics = comparison.metrics or collect_metric_audits(amd64_record, arm64_record, tolerance=tolerance)
    return {
        "schema_version": PASS_SCHEMA_VERSION,
        "passed": comparison.passed,
        "failure_code": comparison.failure_code,
        "git_sha": git_sha,
        "amd64_synthetic_image_id": amd64_image,
        "arm64_synthetic_image_id": arm64_image,
        "tolerance_registry": "registries/pilot-001-cross-arch-equivalence-tolerance.json",
        "absolute_tolerance": tolerance["absolute_tolerance"],
        "relative_tolerance": tolerance["relative_tolerance"],
        "compared_paths": tolerance["integer_paths"] + tolerance["float_paths"],
        "metrics": metrics,
        "amd64_finished_at_utc": amd64_record.get("finished_at_utc"),
        "arm64_finished_at_utc": arm64_record.get("finished_at_utc"),
    }


def normalize_git_sha(value: str | None) -> str | None:
    if not isinstance(value, str):
        return None
    lowered = value.strip().lower()
    if GIT_SHA.fullmatch(lowered):
        return lowered
    return None


def git_sha_matches_head(record_sha: str | None, head_sha: str | None) -> bool:
    record = normalize_git_sha(record_sha)
    head = normalize_git_sha(head_sha)
    if not record or not head:
        return False
    return record == head


def verify_pass_record_payload(data: dict[str, Any]) -> bool:
    if data.get("schema_version") != PASS_SCHEMA_VERSION or data.get("passed") is not True:
        return False
    if normalize_git_sha(data.get("git_sha")) is None:
        return False
    for key in ("amd64_synthetic_image_id", "arm64_synthetic_image_id"):
        value = data.get(key)
        if not isinstance(value, str) or not IMAGE_ID.fullmatch(value):
            return False
    metrics = data.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        return False
    for item in metrics:
        if not isinstance(item, dict):
            return False
        for field in ("path", "amd64", "arm64", "difference", "allowed_delta", "within_tolerance"):
            if field not in item:
                return False
    return True


def load_pass_record(path: Path, *, require_git_sha: str | None = None) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not verify_pass_record_payload(data):
        return None
    if require_git_sha is not None and not git_sha_matches_head(data.get("git_sha"), require_git_sha):
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


def try_download_pass_record_from_ci(*, git_sha: str, dest_dir: Path) -> dict[str, Any] | None:
    head = normalize_git_sha(git_sha)
    if not head:
        return None
    try:
        listed = subprocess.run(
            [
                "gh",
                "run",
                "list",
                "--repo",
                _github_repo_slug(),
                "--workflow",
                WORKFLOW_FILE,
                "--commit",
                head,
                "--json",
                "databaseId,conclusion",
                "--limit",
                "1",
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        if listed.returncode != 0 or not listed.stdout.strip():
            return None
        runs = json.loads(listed.stdout)
        if not runs or runs[0].get("conclusion") != "success":
            return None
        run_id = str(runs[0]["databaseId"])
        dest_dir.mkdir(parents=True, exist_ok=True)
        downloaded = subprocess.run(
            [
                "gh",
                "run",
                "download",
                run_id,
                "--repo",
                _github_repo_slug(),
                "-n",
                PASS_ARTIFACT_NAME,
                "-D",
                str(dest_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        if downloaded.returncode != 0:
            return None
        candidate = dest_dir / PASS_FILENAME
        if not candidate.is_file():
            matches = list(dest_dir.glob(f"**/{PASS_FILENAME}"))
            candidate = matches[0] if matches else candidate
        return load_pass_record(candidate, require_git_sha=head)
    except (OSError, ValueError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def _github_repo_slug() -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(ROOT), "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        url = completed.stdout.strip()
        if url.endswith(".git"):
            url = url[:-4]
        if "github.com:" in url:
            return url.split("github.com:", 1)[1]
        if "github.com/" in url:
            return url.split("github.com/", 1)[1]
    except (subprocess.CalledProcessError, OSError, IndexError):
        pass
    return "Foundation-0/project-asma"
