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
from pilot001_first_run.allowlisted_fetch import AllowlistedFetchError, fetch_exact  # noqa: E402
from pilot001_first_run.config import InputPin, RunConfig, parse_attestation_ref  # noqa: E402
from pilot001_first_run.gates import toronto_today, validate_dropbox_flag, validate_real_run_gates  # noqa: E402
from pilot001_first_run.output_validator import validate_aggregate_document  # noqa: E402
from pilot001_first_run.preflight import run_linux_preflight, run_macos_preflight  # noqa: E402
from pilot001_first_run.runner import build_container_run_argv, resolve_image_tag  # noqa: E402
from pilot001_first_run.study_fetch import StudyFetchError, _verify_pin  # noqa: E402
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

    def test_linux_existing_output_skips_tmutil(self):
        calls = []

        def runner(command):
            calls.append(command)
            if "ulimit -c" in command[-1]:
                return subprocess.CompletedProcess(command, 0, "0\n", "")
            raise AssertionError(f"unexpected command: {command!r}")

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "nested"
            out.mkdir()
            report = run_linux_preflight(out, runner)
        self.assertTrue(report.passed)
        self.assertTrue(all("tmutil" not in " ".join(part for part in cmd) for cmd in calls))

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


class TestAllowlistedFetch(unittest.TestCase):
    def test_refuses_non_allowlisted_host(self):
        with self.assertRaises(AllowlistedFetchError) as ctx:
            fetch_exact("https://example.com/file.bin", expected_bytes=1)
        self.assertEqual(ctx.exception.code, codes.P001_FAIL_FETCH_HOST)


class TestManifestIntegrity(unittest.TestCase):
    def test_wrong_hash_fails(self):
        pin = InputPin("author_dropbox_member", "0" * 64, 3)
        with self.assertRaises(StudyFetchError) as ctx:
            _verify_pin(b"abc", pin)
        self.assertEqual(ctx.exception.code, codes.P001_FAIL_INPUT_INTEGRITY)


class TestRunnerDockerFlags(unittest.TestCase):
    def test_dry_run_uses_network_none(self):
        config = RunConfig(host="linux-ci", output_dir=Path("/tmp/out"), dry_run=True)
        with mock.patch(
            "pilot001_first_run.runner.inspect_image",
            return_value={"Id": "sha256:dead", "Architecture": "amd64"},
        ):
            argv = build_container_run_argv(
                config=config,
                image_tag="asma-synthetic:4.4.3",
                output_dir=Path("/tmp/out"),
                container_name="pilot001-run-test",
            )
        self.assertIn("--network=none", argv)
        self.assertIn("--dry-run", argv)
        self.assertNotIn("--network=bridge", argv)

    def test_real_run_uses_bridge_and_real_entry(self):
        config = RunConfig(
            host="macos",
            output_dir=Path("/tmp/out"),
            dry_run=False,
            gate0_signed=True,
            dropbox_cleared=True,
            gate0_attestation_ref="owner:2026-11-05",
        )
        with mock.patch(
            "pilot001_first_run.runner.inspect_image",
            return_value={"Id": "sha256:dead", "Architecture": "amd64"},
        ):
            argv = build_container_run_argv(
                config=config,
                image_tag="asma-synthetic:4.4.3",
                output_dir=Path("/tmp/out"),
                container_name="pilot001-run-test",
            )
        self.assertIn("--network=bridge", argv)
        self.assertIn("tools/pilot001_first_run/real_entry.py", argv)
        self.assertIn("PILOT001_OWNER_ATTESTATION_ID=owner", argv)
        self.assertNotIn("--network=none", argv)

    def test_real_resolves_source_adapter_image(self):
        config = RunConfig(host="macos", output_dir=Path("/tmp/out"), dry_run=False)
        self.assertEqual(
            resolve_image_tag(config, "asma-synthetic:4.4.3"),
            "asma-source-adapter:3.12.14-4.4.3",
        )


class TestRealPipelineWithoutEarlyStub(unittest.TestCase):
    @mock.patch("pilot001_first_run.runner.subprocess.run")
    @mock.patch("pilot001_first_run.runner.inspect_image")
    def test_gated_real_run_invokes_container(self, mock_inspect, mock_run):
        mock_inspect.return_value = {"Id": "sha256:abc", "Architecture": "amd64"}
        aggregate = {
            "schema_version": 1,
            "review_status": "exploratory_not_externally_reviewed",
            "configurations": [],
            "run_metadata": {},
        }
        mock_run.return_value = subprocess.CompletedProcess([], 0, json.dumps(aggregate), "")
        config = RunConfig(
            host="macos",
            output_dir=Path("/tmp/out"),
            dry_run=False,
            gate0_signed=True,
            dropbox_cleared=True,
            gate0_attestation_ref="owner:2026-11-05",
        )
        with tempfile.TemporaryDirectory() as tmp:
            status, detail = __import__(
                "pilot001_first_run.runner", fromlist=["run_container_pipeline"]
            ).run_container_pipeline(config, "asma-synthetic:4.4.3", Path(tmp))
        self.assertEqual(status, 0)
        self.assertNotEqual(detail, codes.P001_FAIL_GATE_REAL_FLAGS)
        docker_calls = [
            call
            for call in mock_run.call_args_list
            if call.args and call.args[0][:2] == ["docker", "--host=unix:///var/run/docker.sock"]
        ]
        self.assertTrue(docker_calls)
        self.assertIn("--network=bridge", docker_calls[0].args[0])


class TestSimulatedRealOutput(unittest.TestCase):
    def test_aggregate_only_shape(self):
        good = {
            "schema_version": 1,
            "review_status": "exploratory_not_externally_reviewed",
            "configurations": [{"label": "primary", "summary": {"patients": 158}}],
            "real_study_data_executed": True,
        }
        self.assertEqual(validate_aggregate_document(good), [])


if __name__ == "__main__":
    unittest.main()
