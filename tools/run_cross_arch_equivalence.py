#!/usr/bin/env python3
"""Run or compare linux/amd64 vs linux/arm64 synthetic aggregate equivalence."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build_synthetic_runtime import DEFAULT_TAGS, ROOT as REPO_ROOT, local_docker_env  # noqa: E402
from pilot001_first_run.cross_arch_equivalence import (  # noqa: E402
    FAILURE_CODE,
    PASS_FILENAME,
    build_pass_record,
    compare_synthetic_records,
    normalize_git_sha,
)
from pilot001_first_run.runner import git_sha  # noqa: E402


def load_record(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_pipeline(image: str, platform: str) -> dict:
    docker = ["docker", "--host=unix:///var/run/docker.sock"]
    env = local_docker_env()
    identity = subprocess.run(
        docker + ["image", "inspect", image, "--format", "{{.Id}}"],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    container = "asma-cross-arch-" + uuid.uuid4().hex
    command = docker + [
        "run",
        "--name",
        container,
        "--rm",
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--platform=" + platform,
        "--user",
        f"{os.getuid()}:{os.getgid()}",
        "--security-opt=no-new-privileges",
        "--ulimit=core=0",
        "--pids-limit=256",
        "--memory=8g",
        "--memory-swap=8g",
        "--cpus=2",
        "--tmpfs=/tmp:rw,noexec,nosuid,size=256m",
        "--mount",
        f"type=bind,src={REPO_ROOT},dst=/work,readonly",
        "-w",
        "/work",
        "--env",
        "ASMA_RUNTIME_IMAGE_ID=" + identity,
        identity,
        "Rscript",
        "--vanilla",
        "tools/run_synthetic_pipeline.R",
        "--full",
    ]
    try:
        completed = subprocess.run(command, env=env, capture_output=True, text=True, timeout=7200)
    finally:
        subprocess.run(docker + ["rm", "--force", container], env=env, capture_output=True, check=False)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(f"synthetic pipeline failed on {platform}: {detail[:500]}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"synthetic pipeline returned non-JSON on {platform}: {exc}") from exc


def build_platform_image(platform: str, source_cache: Path | None) -> None:
    tag = DEFAULT_TAGS[platform]
    command = [
        sys.executable,
        str(ROOT / "tools/build_synthetic_runtime.py"),
        "--platform",
        platform,
        "--tag",
        tag,
    ]
    if source_cache is not None:
        command.extend(["--source-cache", str(source_cache)])
    subprocess.run(command, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--amd64-record", type=Path, help="Existing amd64 synthetic pipeline JSON")
    parser.add_argument("--arm64-record", type=Path, help="Existing arm64 synthetic pipeline JSON")
    parser.add_argument(
        "--platform",
        choices=sorted(DEFAULT_TAGS),
        help="Build (optional) and run synthetic --full on one platform; write with --write-record",
    )
    parser.add_argument("--skip-build", action="store_true", help="With --platform, skip image build")
    parser.add_argument("--source-cache", type=Path, help="Optional package cache for --platform builds")
    parser.add_argument("--image", help="Override image tag for --platform (default from lock)")
    parser.add_argument("--write-record", type=Path, help="Write synthetic pipeline JSON for --platform")
    parser.add_argument("--git-sha", help="Recorded git commit for pass artifact (default: HEAD)")
    parser.add_argument(
        "--write-pass",
        type=Path,
        help=f"Write {PASS_FILENAME} on successful compare",
    )
    args = parser.parse_args(argv)

    if args.platform:
        if args.write_record is None:
            parser.error("--platform requires --write-record")
        tag = args.image or DEFAULT_TAGS[args.platform]
        if not args.skip_build:
            build_platform_image(args.platform, args.source_cache)
        record = run_pipeline(tag, args.platform)
        write_json(args.write_record, record)
        return 0

    if args.amd64_record and args.arm64_record:
        amd64_record = load_record(args.amd64_record)
        arm64_record = load_record(args.arm64_record)
    else:
        parser.error("Provide --platform --write-record or both --amd64-record and --arm64-record")

    comparison = compare_synthetic_records(amd64_record, arm64_record)
    if not comparison.passed:
        print(comparison.failure_code or FAILURE_CODE)
        if comparison.deltas:
            print(json.dumps(comparison.to_dict(), indent=2, sort_keys=True))
        return 1

    recorded_sha = normalize_git_sha(args.git_sha) or normalize_git_sha(git_sha())
    if recorded_sha is None:
        print("ERROR: git sha must be a full 40-character commit hash", file=sys.stderr)
        return 1
    pass_record = build_pass_record(
        amd64_record=amd64_record,
        arm64_record=arm64_record,
        comparison=comparison,
        git_sha=recorded_sha,
    )
    payload = json.dumps(pass_record, indent=2, sort_keys=True)
    if args.write_pass is not None:
        write_json(args.write_pass, pass_record)
    print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
