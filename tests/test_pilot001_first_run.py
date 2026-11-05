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
from pilot001_first_run.allowlisted_fetch import (  # noqa: E402
    AllowlistedFetchError,
    _AllowlistedRedirectHandler,
    fetch_exact,
    host_allowed,
)
from pilot001_first_run.runner import (  # noqa: E402
    build_container_create_argv,
    build_container_run_argv,
    resolve_image_tag,
)
from pilot001_first_run.config import InputPin, RunConfig, parse_attestation_ref  # noqa: E402
from pilot001_first_run.gates import toronto_today, validate_dropbox_flag, validate_real_run_gates  # noqa: E402
from pilot001_first_run.output_validator import validate_aggregate_document  # noqa: E402
from pilot001_first_run.preflight import run_linux_preflight, run_macos_preflight  # noqa: E402
from pilot001_first_run.study_fetch import StudyFetchError, _archive_range_fetch, _verify_pin, fetch_to_tmpfs  # noqa: E402
import run_pilot001_first_run as entry  # noqa: E402
import urllib.request


def minimal_valid_aggregate(**overrides):
    payload = {
        "schema_version": 1,
        "review_status": "exploratory_not_externally_reviewed",
        "scope": "Pilot 001 first-run aggregate outputs; not externally reviewed",
        "input_mode": "synthetic_fixture",
        "real_study_data_executed": False,
        "amendment_1": {"A1": True, "A2": {"option_a": True, "option_b": True}, "A3": "strict"},
        "started_at_utc": "2026-11-05T00:00:00.000000Z",
        "finished_at_utc": "2026-11-05T00:00:00.000000Z",
        "elapsed_seconds": 1.0,
        "configurations": [
            {
                "label": "primary",
                "outer_seed_start": 1,
                "xgb_tree_method": "exact",
                "summary": {
                    "patients": 158,
                    "features": 64,
                    "repetitions": 5,
                    "outer_folds": 5,
                    "model_predictions": 100,
                    "ensemble_predictions": 100,
                    "final_scores": 100,
                    "complete_prediction_coverage": True,
                    "positive_negative_pairs": 10,
                    "auc": 0.5,
                    "rank_auc": 0.5,
                    "repetition_auc": 0.5,
                },
                "metric_formulations_agree": True,
            }
        ],
        "run_metadata": {
            "git_sha": "abc",
            "runtime_image_id": "id",
            "runtime_image_digest": "id",
            "container_platform": "amd64",
            "host_uname_m": "x86_64",
            "r_version": "4.4.3",
        },
        "limitations": ["Exploratory outputs only."],
    }
    payload.update(overrides)
    return payload


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
        bad = minimal_valid_aggregate()
        bad["scores"] = {"patient-001": 0.5}
        errors = validate_aggregate_document(bad)
        self.assertTrue(errors)

    def test_rejects_proof_review_cases(self):
        cases = [
            lambda p: p["configurations"][0]["summary"].update({"Scores": {"TCGA-04-1331": 0.5}}),
            lambda p: p["configurations"][0]["summary"].update(
                {f"k{index}": float(index) for index in range(300)}
            ),
            lambda p: p["configurations"][0]["summary"].update({"vector_leak": [0.1] * 60}),
            lambda p: p["configurations"][0]["summary"].update({"strings": [str(0.1)] * 500}),
            lambda p: p["limitations"].append("TCGA-04-1331-01A"),
            lambda p: p["configurations"][0]["summary"].update(
                {"late": [{f"nested_{i}": 1} for i in range(250)]}
            ),
        ]
        for mutate in cases:
            payload = minimal_valid_aggregate()
            mutate(payload)
            errors = validate_aggregate_document(payload)
            self.assertTrue(errors, msg=f"expected rejection after {mutate.__name__}")


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

    @mock.patch("pilot001_first_run.allowlisted_fetch._open")
    def test_redirect_off_allowlist_refused(self, mock_open):
        url = (
            "https://pmc-oa-opendata.s3.us-east-1.amazonaws.com/"
            "PMC10414761.1/NIHMS1918576-supplement-MMC1.xlsx"
        )

        def boom(request):
            raise AllowlistedFetchError(codes.P001_FAIL_FETCH_HOST)

        mock_open.side_effect = boom
        with self.assertRaises(AllowlistedFetchError) as ctx:
            fetch_exact(url, expected_bytes=1)
        self.assertEqual(ctx.exception.code, codes.P001_FAIL_FETCH_HOST)

    def test_dropbox_cdn_host_allowed(self):
        self.assertTrue(host_allowed("uc123456.dl.dropboxusercontent.com"))
        self.assertFalse(host_allowed("evil.dl.dropboxusercontent.com.evil.com"))

    def test_redirect_handler_checks_target_before_follow(self):
        handler = _AllowlistedRedirectHandler()
        request = urllib.request.Request("https://www.dropbox.com/s/x/file.zip")
        with self.assertRaises(AllowlistedFetchError):
            handler.redirect_request(request, None, 302, "", {}, "https://example.com/x")


class TestRealModeFetchPath(unittest.TestCase):
    @mock.patch("pilot001_first_run.study_fetch.fetch_byte_range")
    def test_study_fetch_refuses_non_allowlisted_host(self, mock_range):
        mock_range.side_effect = AllowlistedFetchError(codes.P001_FAIL_FETCH_HOST)
        with self.assertRaises(StudyFetchError) as ctx:
            _archive_range_fetch(0, 100)
        self.assertEqual(ctx.exception.code, codes.P001_FAIL_FETCH_HOST)

    @mock.patch("pilot001_first_run.study_fetch.fetch_byte_range")
    def test_study_fetch_refuses_redirect_off_allowlist(self, mock_range):
        mock_range.side_effect = AllowlistedFetchError(codes.P001_FAIL_FETCH_HOST)
        with self.assertRaises(StudyFetchError) as ctx:
            fetch_to_tmpfs(__import__("pilot001_first_run.config", fromlist=["default_input_manifest"]).default_input_manifest(), Path("/tmp/pilot001-test-fetch"))
        self.assertEqual(ctx.exception.code, codes.P001_FAIL_FETCH_HOST)

    @mock.patch.dict("os.environ", {"PILOT001_OWNER_ATTESTATION_ID": "owner"}, clear=False)
    @mock.patch("pilot001_first_run.real_entry.fetch_to_tmpfs")
    def test_real_entry_surfaces_fetch_host(self, mock_fetch):
        mock_fetch.side_effect = StudyFetchError(codes.P001_FAIL_FETCH_HOST)
        import io

        from pilot001_first_run import real_entry

        buffer = io.StringIO()
        with mock.patch("sys.stdout", buffer):
            code = real_entry.main(["--phase", "fetch"])
        self.assertEqual(code, 1)
        self.assertEqual(buffer.getvalue().strip(), codes.P001_FAIL_FETCH_HOST)


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

    def test_real_run_uses_bridge_for_fetch_container(self):
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
            argv = build_container_create_argv(
                config=config,
                image_tag="asma-synthetic:4.4.3",
                output_dir=Path("/tmp/out"),
                container_name="pilot001-run-test",
            )
        self.assertIn("--network=bridge", argv)
        self.assertIn("sleep", argv)
        self.assertIn("PILOT001_OWNER_ATTESTATION_ID=owner", argv)
        self.assertNotIn("--network=none", argv)

    def test_real_resolves_source_adapter_image(self):
        config = RunConfig(host="macos", output_dir=Path("/tmp/out"), dry_run=False)
        self.assertEqual(
            resolve_image_tag(config, "asma-synthetic:4.4.3"),
            "asma-source-adapter:3.12.14-4.4.3",
        )


class TestRealPipelineWithoutEarlyStub(unittest.TestCase):
    @mock.patch("pilot001_first_run.runner.git_sha", return_value="abc")
    @mock.patch("pilot001_first_run.runner.subprocess.run")
    @mock.patch("pilot001_first_run.runner.inspect_image")
    def test_gated_real_run_disconnects_before_analyze(self, mock_inspect, mock_run, _mock_git):
        mock_inspect.return_value = {"Id": "sha256:abc", "Architecture": "amd64"}
        aggregate = minimal_valid_aggregate()
        mock_run.side_effect = [
            subprocess.CompletedProcess([], 0, "container-id\n", ""),
            subprocess.CompletedProcess([], 0, "", ""),
            subprocess.CompletedProcess([], 0, "", ""),
            subprocess.CompletedProcess([], 0, json.dumps(aggregate), ""),
            subprocess.CompletedProcess([], 0, "", ""),
            subprocess.CompletedProcess([], 0, "", ""),
        ]
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
        disconnect = [
            call
            for call in mock_run.call_args_list
            if call.args
            and "network" in call.args[0]
            and "disconnect" in call.args[0]
        ]
        self.assertEqual(len(disconnect), 1)
        analyze = [
            call
            for call in mock_run.call_args_list
            if call.args and call.args[0][:3] == ["docker", "--host=unix:///var/run/docker.sock", "exec"]
            and "--phase" in call.args[0]
            and "analyze" in call.args[0]
        ]
        self.assertEqual(len(analyze), 1)


class TestSimulatedRealOutput(unittest.TestCase):
    def test_aggregate_only_shape(self):
        good = minimal_valid_aggregate(real_study_data_executed=True)
        self.assertEqual(validate_aggregate_document(good), [])


if __name__ == "__main__":
    unittest.main()
