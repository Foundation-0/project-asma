"""Unit tests for synthetic cross-architecture aggregate equivalence."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from pilot001_first_run import failure_codes as codes  # noqa: E402
from pilot001_first_run.cross_arch_equivalence import (  # noqa: E402
    FAILURE_CODE,
    build_pass_record,
    compare_synthetic_records,
    load_pass_record,
    pass_record_matches_images,
    validate_macos_arm64_equivalence,
)
import build_synthetic_runtime as builder  # noqa: E402

FIXTURES = ROOT / "tests/fixtures"


class CrossArchEquivalenceTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def test_identical_fixtures_pass(self):
        result = compare_synthetic_records(
            self.load("cross_arch_amd64_record.json"),
            self.load("cross_arch_arm64_record.json"),
        )
        self.assertTrue(result.passed)
        self.assertIsNone(result.failure_code)

    def test_planted_divergence_fails_with_code(self):
        result = compare_synthetic_records(
            self.load("cross_arch_amd64_record.json"),
            self.load("cross_arch_arm64_diverged_record.json"),
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.failure_code, FAILURE_CODE)
        self.assertTrue(result.deltas)

    def test_pass_record_binds_image_ids(self):
        amd64 = self.load("cross_arch_amd64_record.json")
        arm64 = self.load("cross_arch_arm64_record.json")
        comparison = compare_synthetic_records(amd64, arm64)
        record = build_pass_record(amd64_record=amd64, arm64_record=arm64, comparison=comparison)
        self.assertTrue(record["passed"])
        loaded = load_pass_record(FIXTURES / "cross_arch_equivalence_pass.json")
        self.assertIsNotNone(loaded)
        self.assertTrue(
            pass_record_matches_images(
                loaded,
                amd64_image_id=record["amd64_synthetic_image_id"],
                arm64_image_id=record["arm64_synthetic_image_id"],
            )
        )

    def test_macos_arm64_real_mode_requires_pass_record(self):
        amd64_id = "sha256:" + "1" * 64
        arm64_id = "sha256:" + "2" * 64
        self.assertEqual(
            validate_macos_arm64_equivalence(
                machine_arch="arm64",
                real_mode=True,
                equivalence_record=Path("/nonexistent/pass.json"),
                amd64_image_id=amd64_id,
                arm64_image_id=arm64_id,
            ),
            codes.P001_FAIL_GATE_CROSS_ARCH_EQUIVALENCE,
        )
        self.assertIsNone(
            validate_macos_arm64_equivalence(
                machine_arch="x86_64",
                real_mode=True,
                equivalence_record=FIXTURES / "cross_arch_equivalence_pass.json",
                amd64_image_id=amd64_id,
                arm64_image_id=arm64_id,
            )
        )

    def test_arm64_lockfile_pins_platform_digest(self):
        lock = json.loads((ROOT / "runtime/synthetic-packages-arm64.json").read_text())
        self.assertEqual(lock["platform"], "linux/arm64")
        self.assertIn("0792a280", lock["base_image"])
        amd = json.loads((ROOT / "runtime/synthetic-packages.json").read_text())
        self.assertEqual(
            [item["version"] for item in lock["packages_in_install_order"]],
            [item["version"] for item in amd["packages_in_install_order"]],
        )

    def test_builder_selects_lock_by_platform(self):
        self.assertEqual(builder.lock_path("linux/arm64").name, "synthetic-packages-arm64.json")
        self.assertEqual(builder.DEFAULT_TAGS["linux/arm64"], "asma-synthetic:4.4.3-arm64")


if __name__ == "__main__":
    unittest.main()
