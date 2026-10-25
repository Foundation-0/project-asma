"""Integrity tests for public package acquisition; no Docker or network needed."""

import hashlib
import io
import json
import contextlib
from pathlib import Path
import sys
import tempfile
import subprocess
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_synthetic_runtime as builder
import run_synthetic_pipeline as runner


class SyntheticRuntimeChecks(unittest.TestCase):
    def record(self):
        return {"package": "abstract", "version": "1.0", "bytes": 4,
                "sha256": hashlib.sha256(b"test").hexdigest(),
                "url": "https://cran.r-project.org/src/contrib/abstract_1.0.tar.gz"}

    def test_cached_source_requires_exact_size_and_hash_before_build(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            source = cache / "abstract_1.0.tar.gz"
            source.write_bytes(b"test")
            self.assertEqual(builder.checked_archive(self.record(), cache)[1], b"test")
            for invalid in (b"fail", b"testx"):
                source.write_bytes(invalid)
                with self.assertRaises(ValueError):
                    builder.checked_archive(self.record(), cache)

    def test_network_read_is_bounded_and_checked(self):
        for payload in (b"test", b"testx", b"tes", b"fail"):
            response = io.BytesIO(payload)
            response.geturl = lambda: self.record()["url"]
            with mock.patch.object(builder.urllib.request, "urlopen", return_value=response):
                if payload == b"test":
                    self.assertEqual(builder.checked_archive(self.record())[1], payload)
                else:
                    with self.assertRaises(ValueError):
                        builder.checked_archive(self.record())

    def test_rejects_unexpected_source_hosts_or_paths(self):
        for changed in ({"url": "http://cran.r-project.org/source"},
                        {"url": "https://example.invalid/source"},
                        {"package": "../abstract"}):
            with self.assertRaises(ValueError):
                builder.checked_archive(dict(self.record(), **changed))

    def test_local_daemon_selection_preserves_proxy_and_registry_configuration(self):
        values = {"DOCKER_HOST": "abstract-endpoint", "DOCKER_CONTEXT": "abstract-context",
                  "DOCKER_TLS_VERIFY": "1", "DOCKER_CONFIG": "abstract-config", "HTTPS_PROXY": "abstract-proxy"}
        with mock.patch.dict(builder.os.environ, values, clear=True):
            selected = builder.local_docker_env()
        self.assertNotIn("DOCKER_HOST", selected)
        self.assertNotIn("DOCKER_CONTEXT", selected)
        self.assertNotIn("DOCKER_TLS_VERIFY", selected)
        self.assertEqual(selected["DOCKER_CONFIG"], values["DOCKER_CONFIG"])
        self.assertEqual(selected["HTTPS_PROXY"], values["HTTPS_PROXY"])

    def test_synthetic_runner_uses_isolation_and_records_only_expected_scope(self):
        identity = "sha256:" + "a" * 64
        payload = {"scope": "Synthetic fixtures only; no source-study data or clinical performance result"}
        responses = [subprocess.CompletedProcess([], 0, identity + "\n", ""),
                     subprocess.CompletedProcess([], 0, json.dumps(payload), ""),
                     subprocess.CompletedProcess([], 1, "", "already removed")]
        out = io.StringIO()
        with mock.patch.object(runner.subprocess, "run", side_effect=responses) as run, \
                contextlib.redirect_stdout(out):
            self.assertEqual(runner.main(["--full"]), 0)
        command = run.call_args_list[1].args[0]
        for flag in ("--network=none", "--read-only", "--cap-drop=ALL", "--ulimit=core=0",
                     "--memory=8g", "--memory-swap=8g", "--cpus=2"):
            self.assertIn(flag, command)
        self.assertEqual(command[-1], "--full")
        self.assertEqual(command[command.index("--user") + 1],
                         f"{runner.os.getuid()}:{runner.os.getgid()}")
        self.assertIn(identity, command)
        self.assertEqual(json.loads(out.getvalue())["execution_controls"]["network"], "none")

    def test_timeout_stops_only_the_named_synthetic_container_and_sanitizes_failure(self):
        identity = "sha256:" + "a" * 64
        responses = [subprocess.CompletedProcess([], 0, identity + "\n", ""),
                     subprocess.TimeoutExpired(["private-marker"], 7200),
                     subprocess.CompletedProcess([], 0, "", "")]
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(runner.subprocess, "run", side_effect=responses) as run, \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(runner.main([]), 1)
        invocation = run.call_args_list[1].args[0]
        owned_name = invocation[invocation.index("--name") + 1]
        self.assertTrue(owned_name.startswith("asma-synthetic-"))
        self.assertEqual(run.call_args_list[2].args[0][-3:], ["rm", "--force", owned_name])
        self.assertEqual(out.getvalue(), "")
        self.assertNotIn("private-marker", err.getvalue())

    def test_synthetic_runner_has_no_dataset_path_or_url_argument(self):
        with mock.patch.object(runner.subprocess, "run") as run, \
                contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            runner.main(["--data", "abstract-source"])
        run.assert_not_called()

    def test_cleanup_failure_is_sanitized_and_does_not_publish_success(self):
        identity = "sha256:" + "a" * 64
        payload = {"scope": "Synthetic fixtures only; no source-study data or clinical performance result"}
        responses = [subprocess.CompletedProcess([], 0, identity + "\n", ""),
                     subprocess.CompletedProcess([], 0, json.dumps(payload), ""),
                     subprocess.TimeoutExpired(["private-marker"], 30)]
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(runner.subprocess, "run", side_effect=responses), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(runner.main([]), 1)
        self.assertEqual(out.getvalue(), "")
        self.assertNotIn("private-marker", err.getvalue())


if __name__ == "__main__":
    unittest.main()
