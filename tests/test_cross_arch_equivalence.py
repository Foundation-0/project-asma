"""Unit tests for synthetic cross-architecture aggregate equivalence."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from pilot001_first_run import failure_codes as codes  # noqa: E402
from pilot001_first_run.cross_arch_equivalence import (  # noqa: E402
    FAILURE_CODE,
    PASS_SCHEMA_VERSION,
    SYNTHETIC_AGGREGATE_R_SOURCES,
    build_pass_record,
    compare_synthetic_records,
    compute_synthetic_r_sources_sha256,
    compute_synthetic_stack_identity,
    git_sha_matches_head,
    load_pass_record,
    pass_record_has_required_shape,
    recompute_pass_record_metrics,
    validate_pass_record_for_gate,
)
from pilot001_first_run.gates import validate_cross_arch_equivalence_for_real_run  # noqa: E402
import build_synthetic_runtime as builder  # noqa: E402

FIXTURES = ROOT / "tests/fixtures"
HEAD_SHA = "a" * 40


class CrossArchEquivalenceTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def valid_pass_record(self) -> dict:
        return self.load("cross_arch_equivalence_pass.json")

    def local_stack(self) -> dict:
        return compute_synthetic_stack_identity()

    def test_identical_fixtures_pass(self):
        result = compare_synthetic_records(
            self.load("cross_arch_amd64_record.json"),
            self.load("cross_arch_arm64_record.json"),
        )
        self.assertTrue(result.passed)
        self.assertTrue(result.metrics)

    def test_planted_divergence_fails_with_code(self):
        result = compare_synthetic_records(
            self.load("cross_arch_amd64_record.json"),
            self.load("cross_arch_arm64_diverged_record.json"),
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.failure_code, FAILURE_CODE)
        self.assertTrue(result.deltas)

    def test_stack_identity_hashes_documented_r_sources(self):
        stack = self.local_stack()
        self.assertEqual(stack["schema_version"], 2)
        self.assertEqual(stack["synthetic_r_sources_sha256"], compute_synthetic_r_sources_sha256())
        self.assertEqual(set(stack["synthetic_r_sources_sha256"]), set(SYNTHETIC_AGGREGATE_R_SOURCES))

    def test_pass_record_includes_auditable_metrics(self):
        amd64 = self.load("cross_arch_amd64_record.json")
        arm64 = self.load("cross_arch_arm64_record.json")
        comparison = compare_synthetic_records(amd64, arm64)
        record = build_pass_record(
            amd64_record=amd64,
            arm64_record=arm64,
            comparison=comparison,
            git_sha=HEAD_SHA,
        )
        self.assertEqual(record["schema_version"], PASS_SCHEMA_VERSION)
        self.assertEqual(record["synthetic_stack_identity"], self.local_stack())
        self.assertEqual(len(record["metrics"]), len(record["compared_paths"]))
        for item in record["metrics"]:
            self.assertIn("difference", item)
            self.assertTrue(item["within_tolerance"])

    def test_pass_record_binds_stack_identity_not_image_ids(self):
        record = self.valid_pass_record()
        self.assertTrue(pass_record_has_required_shape(record))
        self.assertEqual(record["synthetic_stack_identity"], self.local_stack())
        self.assertIn("ci_reference", record)
        self.assertNotIn("amd64_synthetic_image_id", record)

    def _forged_float_metric(self, record: dict) -> dict:
        record = copy.deepcopy(record)
        record["passed"] = True
        target = next(item for item in record["metrics"] if item["path"] == "integration.auc")
        target["within_tolerance"] = True
        target["difference"] = 0.0
        target["arm64"] = float(target["amd64"]) + 1.0
        return record

    def test_forged_metric_verdict_fails_recompute(self):
        record = self._forged_float_metric(self.valid_pass_record())
        self.assertFalse(recompute_pass_record_metrics(record))

    def test_forged_passed_true_still_fails_gate(self):
        record = self._forged_float_metric(self.valid_pass_record())
        self.assertEqual(
            validate_cross_arch_equivalence_for_real_run(
                machine_arch="arm64",
                real_mode=True,
                head_git_sha=HEAD_SHA,
                arm64_image_architecture="arm64",
                pass_record=record,
                local_stack_identity=self.local_stack(),
            ),
            codes.P001_FAIL_GATE_CROSS_ARCH_EQUIVALENCE,
        )

    def test_deadbeef_git_sha_fails_gate(self):
        record = dict(self.valid_pass_record(), git_sha="deadbeef")
        self.assertFalse(git_sha_matches_head(record["git_sha"], HEAD_SHA))
        self.assertEqual(
            validate_cross_arch_equivalence_for_real_run(
                machine_arch="arm64",
                real_mode=True,
                head_git_sha=HEAD_SHA,
                arm64_image_architecture="arm64",
                pass_record=record,
                local_stack_identity=self.local_stack(),
            ),
            codes.P001_FAIL_GATE_CROSS_ARCH_EQUIVALENCE,
        )

    def test_stack_identity_mismatch_fails_gate(self):
        record = copy.deepcopy(self.valid_pass_record())
        record["synthetic_stack_identity"] = dict(record["synthetic_stack_identity"])
        record["synthetic_stack_identity"]["amd64"]["synthetic_lock_sha256"] = "0" * 64
        self.assertEqual(
            validate_cross_arch_equivalence_for_real_run(
                machine_arch="arm64",
                real_mode=True,
                head_git_sha=HEAD_SHA,
                arm64_image_architecture="arm64",
                pass_record=record,
                local_stack_identity=self.local_stack(),
            ),
            codes.P001_FAIL_GATE_CROSS_ARCH_EQUIVALENCE,
        )

    def test_arm64_architecture_mismatch_fails_gate(self):
        record = self.valid_pass_record()
        self.assertEqual(
            validate_cross_arch_equivalence_for_real_run(
                machine_arch="arm64",
                real_mode=True,
                head_git_sha=HEAD_SHA,
                arm64_image_architecture="amd64",
                pass_record=record,
                local_stack_identity=self.local_stack(),
            ),
            codes.P001_FAIL_GATE_CROSS_ARCH_EQUIVALENCE,
        )

    def test_valid_record_passes_gate(self):
        record = self.valid_pass_record()
        self.assertIsNone(
            validate_cross_arch_equivalence_for_real_run(
                machine_arch="arm64",
                real_mode=True,
                head_git_sha=HEAD_SHA,
                arm64_image_architecture="arm64",
                pass_record=record,
                local_stack_identity=self.local_stack(),
            )
        )

    def test_validate_pass_record_for_gate_requires_all_tolerance_paths(self):
        record = copy.deepcopy(self.valid_pass_record())
        record["metrics"] = record["metrics"][:-1]
        self.assertFalse(
            validate_pass_record_for_gate(
                record,
                head_git_sha=HEAD_SHA,
                local_stack_identity=self.local_stack(),
            )
        )

    def test_load_pass_record_rejects_malformed_git_sha(self):
        path = FIXTURES / "cross_arch_equivalence_pass.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["git_sha"] = "not-a-sha"
        broken = FIXTURES / "_broken_pass.json"
        broken.write_text(json.dumps(data), encoding="utf-8")
        try:
            self.assertIsNone(load_pass_record(broken))
        finally:
            broken.unlink(missing_ok=True)

    def test_arm64_lockfile_pins_platform_digest(self):
        lock = json.loads((ROOT / "runtime/synthetic-packages-arm64.json").read_text())
        amd = json.loads((ROOT / "runtime/synthetic-packages.json").read_text())
        self.assertEqual(lock["platform"], "linux/arm64")
        self.assertEqual(lock["base_image"], amd["base_image"])

    def test_arm64_adapter_lock_pins_synthetic_build_identity(self):
        lock = json.loads((ROOT / "runtime/source-adapter-python-arm64.json").read_text())
        prior = json.loads((ROOT / "registries/pilot-001-synthetic-validation-arm64.json").read_text())
        identity = lock["base_synthetic_build_identity"]
        self.assertEqual(identity, prior["synthetic_build_identity"])
        self.assertNotIn("base_image_id", lock)

    def test_builder_selects_lock_by_platform(self):
        self.assertEqual(builder.lock_path("linux/arm64").name, "synthetic-packages-arm64.json")
        self.assertEqual(builder.DEFAULT_TAGS["linux/arm64"], "asma-synthetic:4.4.3-arm64")


if __name__ == "__main__":
    unittest.main()
