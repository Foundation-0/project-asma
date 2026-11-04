#!/usr/bin/env python3
"""Run offline pinned-runtime checks in CI; synthetic repository inputs only."""

import json
import os
import re
import subprocess
import sys

from build_synthetic_runtime import ROOT, local_docker_env
from probe_execution_conditions import execution_options

FAILURE = "ERROR: offline pinned-runtime checks failed."


def docker_run(image, *command, extra_env=(), extra_volumes=()):
    arguments = (["docker", "--host=unix:///var/run/docker.sock", "run", "--rm"]
                 + execution_options(log_driver_none=False)
                 + list(extra_volumes) + list(extra_env) + [image] + list(command))
    completed = subprocess.run(arguments, env=local_docker_env(), check=False,
                               capture_output=True, text=True)
    if completed.stdout:
        sys.stdout.write(completed.stdout)
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    return completed


def assert_unittest_count(output, expected):
    match = re.search(r"^Ran (\d+) tests", output, re.MULTILINE)
    if not match:
        raise SystemExit(f"{FAILURE} missing unittest count line")
    observed = int(match.group(1))
    if observed != expected:
        raise SystemExit(f"{FAILURE} expected {expected} tests, observed {observed}")


def image_id(tag):
    completed = subprocess.run(
        ["docker", "--host=unix:///var/run/docker.sock", "image", "inspect", tag, "--format", "{{.Id}}"],
        env=local_docker_env(), check=True, capture_output=True, text=True)
    identity = completed.stdout.strip()
    if not identity.startswith("sha256:"):
        raise SystemExit(FAILURE)
    return identity


def git_bind_mounts():
    if os.environ.get("CI") != "true":
        return []
    mounts = []
    for path in ("/usr/bin/git", "/usr/lib/git-core", "/usr/share/git-core"):
        if os.path.exists(path):
            mounts.extend(["--volume", f"{path}:{path}:ro"])
    return mounts


def main(argv=None):
    adapter = os.environ.get("ADAPTER_IMAGE", "").strip()
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", adapter):
        raise SystemExit(FAILURE)

    validate = docker_run(adapter, "/opt/python/bin/python3", "-I", "-B", "tools/validate.py",
                        extra_volumes=git_bind_mounts())
    if validate.returncode != 0 or not re.search(r"^PASS:", validate.stdout, re.MULTILINE):
        raise SystemExit(FAILURE)

    suite = docker_run(adapter, "/opt/python/bin/python3", "-I", "-B", "-m", "unittest",
                       "discover", "-s", "tests", "-v")
    if suite.returncode != 0:
        raise SystemExit(FAILURE)
    assert_unittest_count(suite.stdout + suite.stderr, 207)
    print("Python suite count: Ran 207 tests")

    adapter_tests = docker_run(adapter, "/opt/python/bin/python3", "-I", "-B", "-m", "unittest",
                               "discover", "-s", "tests", "-p", "test_source_data_adapter.py", "-v")
    if adapter_tests.returncode != 0:
        raise SystemExit(FAILURE)
    assert_unittest_count(adapter_tests.stdout + adapter_tests.stderr, 30)
    print("Adapter suite count: Ran 30 tests")

    synthetic = image_id(os.environ.get("SYNTHETIC_TAG", "asma-synthetic:4.4.3"))
    r_run = docker_run(
        synthetic, "Rscript", "--vanilla", "tools/run_synthetic_pipeline.R", "--tests",
        extra_env=["--env", f"ASMA_RUNTIME_IMAGE_ID={synthetic}"])
    if r_run.returncode != 0:
        raise SystemExit(FAILURE)
    try:
        record = json.loads(r_run.stdout)
    except json.JSONDecodeError as error:
        raise SystemExit(FAILURE) from error
    total = record.get("assertions", {}).get("total")
    if total != 179:
        raise SystemExit(f"{FAILURE} expected 179 R assertions, observed {total!r}")
    print("R assertion total: 179")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
