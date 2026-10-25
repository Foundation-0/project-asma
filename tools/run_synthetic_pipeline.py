#!/usr/bin/env python3
"""Run only abstract fixtures in the isolated pinned R runtime."""

import argparse
import json
import os
import subprocess
import sys
import uuid

from build_synthetic_runtime import ROOT, local_docker_env


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="Include all 100 repetitions using the three actual model packages")
    args = parser.parse_args(argv)
    docker = ["docker", "--host=unix:///var/run/docker.sock"]
    environment = local_docker_env()
    image = "asma-synthetic:4.4.3"
    container = "asma-synthetic-" + uuid.uuid4().hex
    launched = False
    failed = False
    try:
        identity = subprocess.run(docker + ["image", "inspect", image, "--format", "{{.Id}}"],
                                  env=environment, check=True, capture_output=True, text=True).stdout.strip()
        if not identity.startswith("sha256:") or len(identity) != 71:
            raise ValueError("Invalid image identity")
        command = docker + [
            "run", "--name", container, "--rm", "--network=none", "--read-only", "--cap-drop=ALL",
            "--user", f"{os.getuid()}:{os.getgid()}",
            "--security-opt=no-new-privileges", "--ulimit=core=0", "--pids-limit=256",
            "--memory=8g", "--memory-swap=8g", "--cpus=2",
            "--tmpfs=/tmp:rw,noexec,nosuid,size=256m",
            "--mount", f"type=bind,src={ROOT},dst=/work,readonly", "-w", "/work",
            "--env", "ASMA_RUNTIME_IMAGE_ID=" + identity,
            identity, "Rscript", "--vanilla", "tools/run_synthetic_pipeline.R",
            "--full" if args.full else "--tests",
        ]
        launched = True
        result = subprocess.run(command, env=environment, check=True, capture_output=True,
                                text=True, timeout=7200)
        if result.stderr:
            raise ValueError("Unexpected runtime output")
        record = json.loads(result.stdout)
        if record.get("scope") != "Synthetic fixtures only; no source-study data or clinical performance result":
            raise ValueError("Unexpected result scope")
        record["execution_controls"] = {
            "network": "none", "root_filesystem": "read_only", "repository_mount": "read_only",
            "temporary_storage": "256 MiB tmpfs; noexec,nosuid", "memory_limit_gib": 8,
            "swap_limit_gib": 0, "cpu_limit": 2, "core_dump_limit": 0,
            "wall_time_limit_seconds": 7200, "no_new_privileges": True,
            "all_linux_capabilities_dropped": True,
            "note": "Recorded invocation controls; does not establish Canadian hosting or certified erasure.",
        }
    except Exception:
        failed = True
    finally:
        # Killing a timed-out Docker client does not stop its container. This
        # per-invocation UUID names only the temporary synthetic test container.
        if launched:
            try:
                subprocess.run(docker + ["rm", "--force", container], env=environment,
                               capture_output=True, timeout=30, check=False)
            except Exception:
                failed = True
    if failed:
        print("ERROR: isolated synthetic run failed; no row-level details emitted.", file=sys.stderr)
        return 1
    print(json.dumps(record, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
