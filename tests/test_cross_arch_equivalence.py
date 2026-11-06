"""Unit tests for synthetic cross-architecture aggregate equivalence."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from pilot001_first_run import failure_codes as codes  # noqa: E402
from pilot001_first_run.cross_arch_equivalence import (  # noqa: E402
    FAILURE_CODE,
    PASS_SCHEMA_VERSION,
    build_pass_record,
    compare_synthetic_records,
    git_sha_matches_head,
    load_pass_record,
    pass_record_matches_images,
    verify_pass_record_payload,
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
        self.assertEqual(len(record["metrics"]), len(record["compared_paths"]))
        for item in record["metrics"]:
            self.assertIn("difference", item)
            self.assertTrue(item["within_tolerance"])

    def test_pass_record_binds_image_ids(self):
        record = self.valid_pass_record()
        self.assertTrue(verify_pass_record_payload(record))
        self.assertTrue(
            pass_record_matches_images(
                record,
                amd64_image_id=record["amd64_synthetic_image_id"],
                arm64_image_id=record["arm64_synthetic_image_id"],
            )
        )

    def test_deadbeef_git_sha_fails_gate(self):
        record = dict(self.valid_pass_record(), git_sha="deadbeef")
        self.assertFalse(verify_pass_record_payload(record))
        self.assertFalse(git_sha_matches_head(record["git_sha"], HEAD_SHA))
        self.assertEqual(
            validate_cross_arch_equivalence_for_real_run(
                machine_arch="arm64",
                real_mode=True,
                head_git_sha=HEAD_SHA,
                amd64_image_id=record["amd64_synthetic_image_id"],
                arm64_image_id=record["arm64_synthetic_image_id"],
                arm64_image_architecture="arm64",
                pass_record=record,
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
                amd64_image_id=record["amd64_synthetic_image_id"],
                arm64_image_id=record["arm64_synthetic_image_id"],
                arm64_image_architecture="amd64",
                pass_record=record,
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
                amd64_image_id=record["amd64_synthetic_image_id"],
                arm64_image_id=record["arm64_synthetic_image_id"],
                arm64_image_architecture="arm64",
                pass_record=record,
            )
        )

    def test_arm64_lockfile_pins_platform_digest(self):
        lock = json.loads((ROOT / "runtime/synthetic-packages-arm64.json").read_text())
        amd = json.loads((ROOT / "runtime/synthetic-packages.json").read_text())
        self.assertEqual(lock["platform"], "linux/arm64")
        self.assertEqual(lock["base_image"], amd["base_image"])

    def test_arm64_adapter_lock_pins_base_image_id(self):
        lock = json.loads((ROOT / "runtime/source-adapter-python-arm64.json").read_text())
        prior = json.loads((ROOT / "registries/pilot-001-synthetic-validation-arm64.json").read_text())
        self.assertTrue(lock["base_image_id"].startswith("sha256:"))
        self.assertEqual(lock["base_image_id"], prior["environment"]["runtime_image_id"])

    def test_builder_selects_lock_by_platform(self):
        self.assertEqual(builder.lock_path("linux/arm64").name, "synthetic-packages-arm64.json")
        self.assertEqual(builder.DEFAULT_TAGS["linux/arm64"], "asma-synthetic:4.4.3-arm64")


if __name__ == "__main__":
    unittest.main()
