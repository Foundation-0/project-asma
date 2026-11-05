#!/usr/bin/env python3
"""CI dry run for Pilot 001 first-run orchestration (synthetic path only)."""

import json
import os
import resource
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_synthetic_runtime import local_docker_env  # noqa: E402


def main() -> int:
    if not os.path.exists("/var/run/docker.sock"):
        if os.environ.get("CI") == "true":
            print("FAIL: docker required for Pilot 001 dry run", file=sys.stderr)
            return 1
        print("SKIP: docker unavailable", file=sys.stderr)
        return 0
    env = local_docker_env()
    inspect = subprocess.run(
        ["docker", "--host=unix:///var/run/docker.sock", "image", "inspect", "asma-synthetic:4.4.3"],
        env=env,
        capture_output=True,
        check=False,
    )
    if inspect.returncode != 0:
        subprocess.run(
            [sys.executable, str(ROOT / "tools/build_synthetic_runtime.py")],
            cwd=ROOT,
            check=True,
            env=env,
        )
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    with tempfile.TemporaryDirectory(prefix="pilot001-dry-") as tmp:
        output = Path(tmp) / "out"
        output.mkdir()
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/run_pilot001_first_run.py"),
                "--host",
                "linux-ci",
                "--output-dir",
                str(output),
                "--image",
                "asma-synthetic:4.4.3",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
        peak_rss = max(usage_after.ru_maxrss, usage_before.ru_maxrss)
        if completed.returncode != 0:
            if completed.stderr:
                sys.stdout.write(completed.stderr)
            sys.stdout.write(completed.stdout)
            if completed.stderr:
                sys.stderr.write(completed.stderr)
            return completed.returncode
        summary = json.loads(completed.stdout.strip().splitlines()[-1])
        summary["peak_rss_kib"] = peak_rss
        print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
