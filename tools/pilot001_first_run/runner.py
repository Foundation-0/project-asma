"""Container orchestration for Pilot 001 first-run."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

from build_synthetic_runtime import ROOT, local_docker_env
from pilot001_first_run import failure_codes as codes
from pilot001_first_run.config import RunConfig
from pilot001_first_run.output_validator import validate_output_dir

AGGREGATE_FILENAME = "pilot001-first-run-aggregate.json"
PREFLIGHT_FILENAME = "pilot001-preflight-report.json"


def git_sha() -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def docker_base() -> list[str]:
    return ["docker", "--host=unix:///var/run/docker.sock"]


def inspect_image(tag: str) -> dict:
    completed = subprocess.run(
        docker_base() + ["image", "inspect", tag],
        env=local_docker_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(completed.stdout)[0]


def run_container_pipeline(
    config: RunConfig,
    image_tag: str,
    output_dir: Path,
) -> tuple[int, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    inspected = inspect_image(image_tag)
    image_id = inspected["Id"]
    platform = inspected.get("Architecture", "unknown")
    digest = image_id
    environment = local_docker_env()
    container = "pilot001-run-" + uuid.uuid4().hex
    command = docker_base() + [
        "run",
        "--name",
        container,
        "--rm",
        "--network=none",
        "--read-only",
        "--log-driver=none",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--ulimit=core=0",
        "--pids-limit=512",
        "--memory=8g",
        "--memory-swap=8g",
        "--cpus=2",
        "--tmpfs=/tmp:rw,noexec,nosuid,size=512m",
        "--tmpfs=/work/scratch:rw,noexec,nosuid,size=512m",
        "--mount",
        f"type=bind,src={ROOT},dst=/work,readonly",
        "--mount",
        f"type=bind,src={output_dir.resolve()},dst=/output,rw",
        "-w",
        "/work",
        "--env",
        "HOME=/tmp",
        "--env",
        "R_HISTFILE=",
        "--env",
        "XDG_CACHE_HOME=/tmp/asma-cache",
        "--env",
        "R_USER_CACHE_DIR=/tmp/asma-cache",
        "--env",
        f"ASMA_RUNTIME_IMAGE_ID={image_id}",
        "--env",
        f"PILOT001_GIT_SHA={config.git_sha or git_sha()}",
        "--env",
        f"PILOT001_IMAGE_PLATFORM={platform}",
        "--env",
        f"PILOT001_UNAME_M={os.uname().machine}",
        image_tag,
        "Rscript",
        "--vanilla",
        "tools/run_pilot001_reconstruction.R",
        "--dry-run",
        "--repetitions=5",
    ]
    if not config.dry_run:
        return 1, codes.P001_FAIL_GATE_REAL_FLAGS
    try:
        completed = subprocess.run(
            command,
            env=environment,
            capture_output=True,
            text=True,
            timeout=7200,
            check=False,
        )
    finally:
        subprocess.run(
            docker_base() + ["rm", "--force", container],
            env=environment,
            capture_output=True,
            check=False,
        )
    stdout = completed.stdout.strip()
    if completed.returncode != 0:
        if completed.stderr:
            sys.stderr.write(completed.stderr)
        line = stdout.splitlines()[0] if stdout else codes.P001_FAIL_CONTAINER
        if codes.is_aggregate_failure_line(line):
            return completed.returncode, line
        return completed.returncode, codes.P001_FAIL_CONTAINER
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return 1, codes.P001_FAIL_CONTAINER
    payload.setdefault("run_metadata", {})
    payload["run_metadata"].update(
        {
            "git_sha": config.git_sha or git_sha(),
            "runtime_image_id": image_id,
            "runtime_image_digest": digest,
            "container_platform": platform,
        }
    )
    (output_dir / AGGREGATE_FILENAME).write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return 0, stdout


def postflight() -> str | None:
    environment = local_docker_env()
    ps = subprocess.run(
        docker_base() + ["ps", "-a", "--filter", "name=pilot001-run-", "--format", "{{.ID}}"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if ps.stdout.strip():
        return codes.P001_FAIL_POSTFLIGHT
    return None


def emit_success_summary(output_dir: Path, peak_rss_kib: int | None = None) -> None:
    aggregate_path = output_dir / AGGREGATE_FILENAME
    payload = json.loads(aggregate_path.read_text(encoding="utf-8"))
    summary = {
        "status": "PASS",
        "output_dir": str(output_dir),
        "configurations": len(payload.get("configurations", [])),
        "elapsed_seconds": payload.get("elapsed_seconds"),
        "runtime_image_id": payload.get("run_metadata", {}).get("runtime_image_id"),
        "git_sha": payload.get("run_metadata", {}).get("git_sha"),
    }
    if peak_rss_kib is not None:
        summary["peak_rss_kib"] = peak_rss_kib
    print(json.dumps(summary, sort_keys=True))


def emit_failure(code: str) -> None:
    sys.stdout.write(code + "\n")
    sys.stdout.flush()
