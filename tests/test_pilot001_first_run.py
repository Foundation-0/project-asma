"""Tests for Pilot 001 first-run orchestration."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from pilot001_first_run import failure_codes as codes  # noqa: E402
from pilot001_first_run.config import RunConfig, parse_attestation_ref  # noqa: E402
from pilot001_first_run.gates import toronto_today, validate_dropbox_flag, validate_real_run_gates  # noqa: E402
from pilot001_first_run.output_validator import validate_aggregate_document  # noqa: E402
from pilot001_first_run.preflight import run_linux_preflight, run_macos_preflight  # noqa: E402
import run_pilot001_first_run as entry  # noqa: E402


class TestAttestationAndGates(unittest.TestCase):
    def test_attestation_ref_requires_date(self):
        self.assertIsNone(parse_attestation_ref("missing-date"))
        self.assertEqual(parse_attestation_ref("gate0:2026-11-05"), ("gate0", "2026-11-05"))

    def test_dropbox_refused_on_linux_ci(self):
        config = RunConfig(
            host="linux-ci",
            output_dir=Path("/tmp/out"),
            dropbox_cleared=True,
        )
        self.assertEqual(
            validate_dropbox_flag(config, preflight_passed=True),
            codes.P001_FAIL_GATE_DROPBOX_HOST,
        )

    def test_dropbox_requires_preflight_on_macos(self):
        config = RunConfig(host="macos", output_dir=Path("/tmp/out"), dropbox_cleared=True)
        self.assertEqual(
            validate_dropbox_flag(config, preflight_passed=False),
            codes.P001_FAIL_GATE_DROPBOX_PREFLIGHT,
        )

    def test_real_run_requires_both_flags(self):
        config = RunConfig(host="macos", output_dir=Path("/tmp/out"), dry_run=False)
        self.assertEqual(
            validate_real_run_gates(config, preflight_passed=True),
            codes.P001_FAIL_GATE_REAL_FLAGS,
        )

    @mock.patch("pilot001_first_run.gates.toronto_today", return_value=date(2026, 11, 5))
    def test_stale_attestation_date_refused(self, _mock_today):
        config = RunConfig(
            host="macos",
            output_dir=Path("/tmp/out"),
            dry_run=False,
            gate0_signed=True,
            dropbox_cleared=True,
            gate0_attestation_ref="owner:2026-11-04",
        )
        self.assertEqual(
            validate_real_run_gates(config, preflight_passed=True),
            codes.P001_FAIL_GATE_ATTESTATION_DATE,
        )

    @mock.patch("pilot001_first_run.gates.toronto_today", return_value=date(2026, 11, 5))
    def test_attestation_date_matches_toronto_today(self, _mock_today):
        config = RunConfig(
            host="macos",
            output_dir=Path("/tmp/out"),
            dry_run=False,
            gate0_signed=True,
            dropbox_cleared=True,
            gate0_attestation_ref="owner:2026-11-05",
        )
        self.assertIsNone(validate_real_run_gates(config, preflight_passed=True))


class TestPreflight(unittest.TestCase):
    def test_linux_ulimit_core_mock(self):
        def runner(command):
            if "ulimit -c" in command[-1]:
                return subprocess.CompletedProcess(command, 0, "0\n", "")
            return subprocess.CompletedProcess(command, 0, "[Excluded]  /tmp/out\n", "")

        report = run_linux_preflight(Path("/tmp/out"), runner)
        self.assertTrue(report.passed)

    def test_macos_docker_swap_mock(self):
        def runner(command):
            if "ulimit -c" in command[-1]:
                return subprocess.CompletedProcess(command, 0, "0\n", "")
            return subprocess.CompletedProcess(command, 0, "ok\n", "")

        report = run_macos_preflight(Path("/tmp/out"), runner, docker_desktop_swap=1)
        self.assertFalse(report.passed)
        self.assertIn("docker_desktop_swap", report.checks)


class TestOutputValidator(unittest.TestCase):
    def test_rejects_row_level_payload(self):
        bad = {
            "schema_version": 1,
            "review_status": "exploratory_not_externally_reviewed",
            "scores": {"patient-001": 0.5},
        }
        errors = validate_aggregate_document(bad)
        self.assertTrue(any("forbidden_key" in item for item in errors))


class TestEntrypointFailureOutput(unittest.TestCase):
    @mock.patch("run_pilot001_first_run.run_container_pipeline", return_value=(1, codes.P001_FAIL_CONTAINER))
    @mock.patch("run_pilot001_first_run.run_preflight")
    def test_failure_prints_only_aggregate_code(self, mock_preflight, _mock_run):
        from pilot001_first_run.preflight import PreflightReport
        import io

        mock_preflight.return_value = PreflightReport("linux-ci", True, {"ulimit_core": "PASS"})
        with tempfile.TemporaryDirectory() as tmp:
            buffer = io.StringIO()
            with mock.patch("sys.stdout", buffer):
                code = entry.main(["--host", "linux-ci", "--output-dir", tmp])
        lines = [line for line in buffer.getvalue().splitlines() if line.strip()]
        self.assertEqual(code, 1)
        self.assertEqual(lines, [codes.P001_FAIL_CONTAINER])


class TestTrackedStudySources(unittest.TestCase):
    def test_no_tracked_sources(self):
        completed = subprocess.run(
            [sys.executable, str(TOOLS / "check_tracked_study_sources.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, msg=completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
