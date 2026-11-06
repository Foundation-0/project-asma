"""Compare synthetic pipeline aggregates across linux/amd64 and linux/arm64."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
TOLERANCE = ROOT / "registries/pilot-001-cross-arch-equivalence-tolerance.json"
SYNTHETIC_LOCKS = {
    "linux/amd64": ROOT / "runtime/synthetic-packages.json",
    "linux/arm64": ROOT / "runtime/synthetic-packages-arm64.json",
}
# R sources that define synthetic fixture assembly and integration aggregates (--full).
SYNTHETIC_AGGREGATE_R_SOURCES: tuple[str, ...] = (
    "R/asma_input.R",
    "R/asma_core.R",
    "R/asma_models.R",
    "tools/run_synthetic_pipeline.R",
    "tests/r/synthetic_fixture.R",
)
PASS_FILENAME = "pilot001-cross-arch-equivalence-pass.json"
PASS_ARTIFACT_NAME = "pilot001-cross-arch-equivalence-pass"
WORKFLOW_FILE = "cross-arch-equivalence.yml"
PASS_SCHEMA_VERSION = 3
FAILURE_CODE = "P001-FAIL-CROSS-ARCH-EQUIVALENCE"
GATE_FAILURE_CODE = "P001-FAIL-GATE-CROSS-ARCH-EQUIVALENCE"
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


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tolerance(path: Path | None = None) -> dict[str, Any]:
    data = json.loads((path or TOLERANCE).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("invalid tolerance registry")
    return data


def compared_paths(tolerance: dict[str, Any] | None = None) -> list[str]:
    tolerance = tolerance or load_tolerance()
    return list(tolerance["integer_paths"]) + list(tolerance["float_paths"])


def compute_synthetic_build_identity(platform: str) -> dict[str, str]:
    lock_path = SYNTHETIC_LOCKS[platform]
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    dockerfile = ROOT / "runtime/Dockerfile.synthetic"
    install_r = ROOT / "runtime/install.R"
    package_hasher = hashlib.sha256()
    for record in lock["packages_in_install_order"]:
        package_hasher.update(record["sha256"].encode("ascii"))
    return {
        "platform": platform,
        "base_image_pin": lock["base_image"],
        "synthetic_lock_sha256": file_sha256(lock_path),
        "dockerfile_synthetic_sha256": file_sha256(dockerfile),
        "install_r_sha256": file_sha256(install_r),
        "package_sources_sha256": package_hasher.hexdigest(),
    }


def compute_synthetic_r_sources_sha256() -> dict[str, str]:
    return {relative: file_sha256(ROOT / relative) for relative in SYNTHETIC_AGGREGATE_R_SOURCES}


def compute_synthetic_stack_identity() -> dict[str, Any]:
    return {
        "schema_version": 2,
        "amd64": compute_synthetic_build_identity("linux/amd64"),
        "arm64": compute_synthetic_build_identity("linux/arm64"),
        "tolerance_registry_sha256": file_sha256(TOLERANCE),
        "synthetic_r_sources_sha256": compute_synthetic_r_sources_sha256(),
    }


def stack_identities_match(recorded: Any, local: dict[str, Any]) -> bool:
    return isinstance(recorded, dict) and recorded == local


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


def recompute_pass_record_metrics(record: dict[str, Any]) -> bool:
    """Recompute tolerance from stored amd64/arm64 values; ignore file verdict fields."""
    tolerance = load_tolerance()
    paths = compared_paths(tolerance)
    metrics = record.get("metrics")
    if not isinstance(metrics, list):
        return False
    by_path: dict[str, dict[str, Any]] = {}
    for item in metrics:
        if not isinstance(item, dict) or "path" not in item:
            return False
        by_path[str(item["path"])] = item
    if set(by_path) != set(paths):
        return False
    for path in paths:
        item = by_path[path]
        if "amd64" not in item or "arm64" not in item:
            return False
        if path in tolerance["integer_paths"]:
            left = item["amd64"]
            right = item["arm64"]
            if left != right:
                return False
            continue
        left = float(item["amd64"])
        right = float(item["arm64"])
        if abs(left - right) > _allowed_delta(left, tolerance):
            return False
    return True


def pass_record_has_required_shape(data: dict[str, Any]) -> bool:
    if data.get("schema_version") != PASS_SCHEMA_VERSION:
        return False
    if normalize_git_sha(data.get("git_sha")) is None:
        return False
    stack = data.get("synthetic_stack_identity")
    if not isinstance(stack, dict) or stack.get("schema_version") != 2:
        return False
    r_sources = stack.get("synthetic_r_sources_sha256")
    if not isinstance(r_sources, dict) or set(r_sources) != set(SYNTHETIC_AGGREGATE_R_SOURCES):
        return False
    metrics = data.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        return False
    for item in metrics:
        if not isinstance(item, dict):
            return False
        for field in ("path", "amd64", "arm64"):
            if field not in item:
                return False
    return True


def build_pass_record(
    *,
    amd64_record: dict[str, Any],
    arm64_record: dict[str, Any],
    comparison: ComparisonResult,
    git_sha: str | None = None,
    tolerance_path: Path | None = None,
) -> dict[str, Any]:
    if not comparison.passed:
        raise ValueError("refusing to write pass record for failed comparison")
    tolerance = load_tolerance(tolerance_path)
    if git_sha is not None and not GIT_SHA.fullmatch(git_sha):
        raise ValueError("git_sha must be a full 40-character commit hash")
    metrics = comparison.metrics or collect_metric_audits(amd64_record, arm64_record, tolerance=tolerance)
    stack_identity = compute_synthetic_stack_identity()
    return {
        "schema_version": PASS_SCHEMA_VERSION,
        "git_sha": git_sha,
        "synthetic_stack_identity": stack_identity,
        "tolerance_registry": "registries/pilot-001-cross-arch-equivalence-tolerance.json",
        "absolute_tolerance": tolerance["absolute_tolerance"],
        "relative_tolerance": tolerance["relative_tolerance"],
        "compared_paths": compared_paths(tolerance),
        "metrics": metrics,
        "amd64_finished_at_utc": amd64_record.get("finished_at_utc"),
        "arm64_finished_at_utc": arm64_record.get("finished_at_utc"),
        "ci_reference": {
            "amd64_runtime_image_id": amd64_record.get("environment", {}).get("runtime_image_id"),
            "arm64_runtime_image_id": arm64_record.get("environment", {}).get("runtime_image_id"),
        },
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


def validate_pass_record_for_gate(
    record: dict[str, Any] | None,
    *,
    head_git_sha: str,
    local_stack_identity: dict[str, Any],
) -> bool:
    if record is None or not pass_record_has_required_shape(record):
        return False
    if not git_sha_matches_head(record.get("git_sha"), head_git_sha):
        return False
    if not stack_identities_match(record.get("synthetic_stack_identity"), local_stack_identity):
        return False
    if not recompute_pass_record_metrics(record):
        return False
    return True


def parse_pass_record_file(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def load_pass_record(path: Path) -> dict[str, Any] | None:
    data = parse_pass_record_file(path)
    if data is None or not pass_record_has_required_shape(data):
        return None
    return data


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
        return parse_pass_record_file(candidate)
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
