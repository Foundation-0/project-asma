"""Offline evidence checks; no Docker, study data or external calls required."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import probe_execution_conditions as probe


class ExecutionConditionTests(unittest.TestCase):
    def test_missing_observations_fail_closed_as_unknown(self):
        checks = probe.evaluate_checks({}, {})
        self.assertTrue(checks)
        self.assertTrue(all(item["status"] == "UNKNOWN" for item in checks.values()))
        self.assertNotEqual(probe.observed_status(None), "PASS")

    def test_false_or_wrong_type_is_not_success(self):
        self.assertEqual(probe.observed_status(False), "FAIL")
        self.assertEqual(probe.observed_status(1), "FAIL")
        self.assertEqual(probe.observed_status("true"), "FAIL")
        self.assertEqual(probe.observed_status(True), "PASS")
        self.assertEqual(probe.observed_status(True, 1), "FAIL")

    def test_numeric_control_observations_do_not_allow_bool_or_unlimited(self):
        checks = probe.evaluate_checks({"memory_limit_bytes": "max", "swap_limit_bytes": False,
                                        "cpu_limit": 2.0}, {})
        self.assertEqual(checks["memory_limit_bytes"]["status"], "FAIL")
        self.assertEqual(checks["swap_limit_bytes"]["status"], "FAIL")
        self.assertEqual(checks["cpu_limit"]["status"], "PASS")

    def test_configuration_without_kernel_evidence_does_not_pass(self):
        checks = probe.evaluate_checks({}, {"docker_memory_bytes": probe.MEMORY_BYTES})
        self.assertEqual(checks["docker_memory_bytes"]["status"], "PASS")
        self.assertEqual(checks["memory_limit_bytes"]["status"], "UNKNOWN")
        self.assertEqual(checks["cgroup_v2"]["status"], "UNKNOWN")

    def test_docker_inspection_discards_environment_paths_and_identifiers(self):
        inspected = {"Id": "PRIVATE_TEST_SENTINEL", "Config": {
            "User": "1000:1000", "Env": ["SECRET=PRIVATE_TEST_SENTINEL"]},
            "Mounts": [{"Destination": "/work", "Source": "PRIVATE_TEST_SENTINEL", "RW": False, "Type": "bind"}],
            "HostConfig": {"NetworkMode": "none", "LogConfig": {"Type": "none"},
                           "ReadonlyRootfs": True, "CapDrop": ["ALL"],
                           "SecurityOpt": ["no-new-privileges:true"],
                           "Ulimits": [{"Name": "core", "Soft": 0, "Hard": 0}]}}
        observed = probe.inspect_controls(inspected, "1000:1000")
        self.assertNotIn("PRIVATE_TEST_SENTINEL", json.dumps(observed))
        self.assertTrue(observed["docker_log_driver_none"])
        self.assertTrue(observed["docker_checkout_read_only"])
        self.assertTrue(observed["docker_no_new_privileges"])
        inspected["Mounts"][0]["RW"] = True
        self.assertFalse(probe.inspect_controls(inspected, "1000:1000")["docker_checkout_read_only"])
        inspected["HostConfig"]["LogConfig"]["Type"] = "json-file"
        self.assertFalse(probe.inspect_controls(inspected, "1000:1000")["docker_log_driver_none"])

    def test_no_new_privileges_requires_enabled_configuration_value(self):
        for value, expected in (("no-new-privileges", True),
                                ("no-new-privileges:true", True),
                                ("no-new-privileges:false", False),
                                ("no-new-privileges:invalid", False)):
            with self.subTest(value=value):
                observed = probe.inspect_controls({"HostConfig": {"SecurityOpt": [value]}}, "1000:1000")
                self.assertEqual(observed["docker_no_new_privileges"], expected)

    def test_executor_observation_reports_unknowns_without_inventing_no_swap(self):
        with tempfile.TemporaryDirectory() as directory:
            result = probe.executor_observations(Path(directory))
        self.assertIsNone(result["kernel_visible_swap_devices"])
        self.assertIsNone(result["memory.swap.max"])

    def test_executor_observation_counts_devices_without_disclosing_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "proc").mkdir()
            (root / "proc/swaps").write_text("Filename Type Size Used Priority\nPRIVATE_TEST_SENTINEL file 1 0 -2\n")
            cgroup = root / "sys/fs/cgroup"
            cgroup.mkdir(parents=True)
            (cgroup / "memory.max").write_text("17179869184\n")
            (cgroup / "memory.swap.max").write_text("max\n")
            (cgroup / "cpu.max").write_text("PRIVATE_TEST_SENTINEL\n")
            result = probe.executor_observations(root)
        self.assertEqual(result["kernel_visible_swap_devices"], 1)
        self.assertEqual(result["memory.swap.max"], "max")
        self.assertIsNone(result["cpu.max"])
        self.assertNotIn("PRIVATE_TEST_SENTINEL", json.dumps(result))

    def test_options_keep_execution_offline_and_disable_persistent_docker_logs(self):
        options = probe.execution_options(root=Path("/abstract"), uid=123, gid=456)
        for flag in ("--network=none", "--read-only", "--cap-drop=ALL", "--log-driver=none",
                     "--memory=8g", "--memory-swap=8g", "--ulimit=core=0"):
            self.assertIn(flag, options)
        self.assertEqual(options[options.index("--user") + 1], "123:456")
        self.assertIn("type=bind,src=/abstract,dst=/work,readonly", options)
        self.assertNotIn("--privileged", options)

    def test_timeout_removes_only_its_owned_container_and_sanitizes_error(self):
        identity = "sha256:" + "a" * 64
        responses = [subprocess.CompletedProcess([], 0, identity, ""),
                     subprocess.CompletedProcess([], 0, "internal-id", ""),
                     subprocess.TimeoutExpired(["PRIVATE_TEST_SENTINEL"], 60),
                     subprocess.CompletedProcess([], 0, "removed", "")]
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(Path, "read_text", return_value=json.dumps({"environment": {"runtime_image_id": identity}})), \
                mock.patch.object(probe.subprocess, "run", side_effect=responses) as run, \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(probe.main([]), 1)
        create = run.call_args_list[1].args[0]
        name = create[create.index("--name") + 1]
        self.assertTrue(name.startswith("asma-condition-probe-"))
        self.assertEqual(run.call_args_list[-1].args[0][-3:], ["rm", "--force", name])
        self.assertEqual(out.getvalue(), "")
        self.assertEqual(err.getvalue(), probe.FAILURE + "\n")

    def test_report_exit_status_distinguishes_failed_unknown_and_passed_controls(self):
        for status, code in (("FAIL", 2), ("UNKNOWN", 2), ("PASS", 0)):
            with mock.patch.object(probe, "run_probe", return_value={"technical_checks_status": status}), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(probe.main([]), code)

    def test_cli_accepts_no_data_or_clearance_override(self):
        for option in ("--data", "--approve", "--country"):
            with mock.patch.object(probe, "run_probe") as run, \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                probe.main([option, "abstract"])
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
