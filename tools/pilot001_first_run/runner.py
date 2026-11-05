"""Container orchestration for Pilot 001 first-run."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

from build_synthetic_runtime import ROOT, local_docker_env
from pilot001_first_run import failure_codes as codes
from pilot001_first_run.config import RunConfig, parse_attestation_ref
from pilot001_first_run.output_validator import validate_aggregate_document

AGGREGATE_FILENAME = "pilot001-first-run-aggregate.json"
PREFLIGHT_FILENAME = "pilot001-preflight-report.json"
STAGING_AGGREGATE = ".pilot001-first-run-aggregate.staging.json"
DEFAULT_SYNTHETIC_IMAGE = "asma-synthetic:4.4.3"
DEFAULT_REAL_IMAGE = "asma-source-adapter:3.12.14-4.4.3"
OWNER_ATTESTATIONS = ROOT / "registries/pilot-001-owner-attestations.json"
STUDY_TMPFS = "/tmp/pilot001-study"
REAL_FETCH_NETWORK = "bridge"
IDLE_COMMAND = ["sleep", "7200"]


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


def resolve_image_tag(config: RunConfig, cli_image: str) -> str:
    if cli_image != DEFAULT_SYNTHETIC_IMAGE:
        return cli_image
    return DEFAULT_SYNTHETIC_IMAGE if config.dry_run else DEFAULT_REAL_IMAGE


def inspect_image(tag: str) -> dict:
    completed = subprocess.run(
        docker_base() + ["image", "inspect", tag],
        env=local_docker_env(),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(completed.stdout)[0]


def _container_create_argv(
    *,
    config: RunConfig,
    image_tag: str,
    output_dir: Path,
    container_name: str,
    network: str,
) -> list[str]:
    inspected = inspect_image(image_tag)
    image_id = inspected["Id"]
    platform = inspected.get("Architecture", "unknown")
    tmpfs_main = "512m" if config.dry_run else "2048m"
    command = docker_base() + [
        "run",
        "-d",
        "--name",
        container_name,
        f"--network={network}",
        "--read-only",
        "--log-driver=none",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--ulimit=core=0",
        "--pids-limit=512",
        "--memory=8g",
        "--memory-swap=8g",
        "--cpus=2",
        f"--tmpfs=/tmp:rw,noexec,nosuid,size={tmpfs_main}",
        f"--tmpfs={STUDY_TMPFS}:rw,noexec,nosuid,size=512m",
        "--mount",
        f"type=bind,src={ROOT},dst=/work,readonly",
        "--mount",
        f"type=bind,src={output_dir.resolve()},dst=/output",
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
    ]
    if not config.dry_run:
        parsed = parse_attestation_ref(config.gate0_attestation_ref)
        if parsed:
            att_id, _att_date = parsed
            command.extend(["--env", f"PILOT001_OWNER_ATTESTATION_ID={att_id}"])
        if OWNER_ATTESTATIONS.is_file():
            command.extend(
                [
                    "--mount",
                    f"type=bind,src={OWNER_ATTESTATIONS.resolve()},dst=/work/registries/pilot-001-owner-attestations.json,readonly",
                ]
            )
    command.append(image_tag)
    command.extend(IDLE_COMMAND)
    return command


def build_dry_run_argv(
    *,
    config: RunConfig,
    image_tag: str,
    output_dir: Path,
    container_name: str,
) -> list[str]:
    inspected = inspect_image(image_tag)
    image_id = inspected["Id"]
    platform = inspected.get("Architecture", "unknown")
    return docker_base() + [
        "run",
        "--name",
        container_name,
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
        "--mount",
        f"type=bind,src={ROOT},dst=/work,readonly",
        "--mount",
        f"type=bind,src={output_dir.resolve()},dst=/output",
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


def build_container_create_argv(
    *,
    config: RunConfig,
    image_tag: str,
    output_dir: Path,
    container_name: str,
) -> list[str]:
    return _container_create_argv(
        config=config,
        image_tag=image_tag,
        output_dir=output_dir,
        container_name=container_name,
        network=REAL_FETCH_NETWORK,
    )


def build_container_run_argv(
    *,
    config: RunConfig,
    image_tag: str,
    output_dir: Path,
    container_name: str,
) -> list[str]:
    if config.dry_run:
        return build_dry_run_argv(
            config=config,
            image_tag=image_tag,
            output_dir=output_dir,
            container_name=container_name,
        )
    return build_container_create_argv(
        config=config,
        image_tag=image_tag,
        output_dir=output_dir,
        container_name=container_name,
    )


def _docker_run(argv: list[str], environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        env=environment,
        capture_output=True,
        text=True,
        timeout=7200,
        check=False,
    )


def _docker_exec(
    container: str,
    exec_argv: list[str],
    environment: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        docker_base() + ["exec", container] + exec_argv,
        env=environment,
        capture_output=True,
        text=True,
        timeout=7200,
        check=False,
    )


def _failure_from_stdout(stdout: str) -> tuple[int, str]:
    line = stdout.strip().splitlines()[0] if stdout.strip() else codes.P001_FAIL_CONTAINER
    if codes.is_aggregate_failure_line(line):
        return 1, line
    return 1, codes.P001_FAIL_CONTAINER


def _finalize_aggregate_payload(
    payload: dict,
    *,
    config: RunConfig,
    image_id: str,
    platform: str,
    digest: str,
) -> dict:
    payload.setdefault("run_metadata", {})
    payload["run_metadata"].update(
        {
            "git_sha": config.git_sha or git_sha(),
            "runtime_image_id": image_id,
            "runtime_image_digest": digest,
            "container_platform": platform,
        }
    )
    return payload


def _promote_aggregate(output_dir: Path, payload: dict) -> None:
    validation_errors = validate_aggregate_document(payload)
    if validation_errors:
        raise ValueError(codes.P001_FAIL_OUTPUT_VALIDATION)
    staging = output_dir / STAGING_AGGREGATE
    final = output_dir / AGGREGATE_FILENAME
    staging.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    staging.replace(final)


def run_dry_container_pipeline(
    config: RunConfig,
    image_tag: str,
    output_dir: Path,
) -> tuple[int, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    image_tag = resolve_image_tag(config, image_tag)
    inspected = inspect_image(image_tag)
    image_id = inspected["Id"]
    platform = inspected.get("Architecture", "unknown")
    environment = local_docker_env()
    container = "pilot001-run-" + uuid.uuid4().hex
    command = build_container_run_argv(
        config=config,
        image_tag=image_tag,
        output_dir=output_dir,
        container_name=container,
    )
    try:
        completed = _docker_run(command, environment)
    finally:
        subprocess.run(
            docker_base() + ["rm", "--force", container],
            env=environment,
            capture_output=True,
            check=False,
        )
    if completed.returncode != 0:
        return _failure_from_stdout(completed.stdout)
    try:
        payload = json.loads(completed.stdout.strip())
    except json.JSONDecodeError:
        return 1, codes.P001_FAIL_CONTAINER
    payload = _finalize_aggregate_payload(
        payload,
        config=config,
        image_id=image_id,
        platform=platform,
        digest=image_id,
    )
    try:
        _promote_aggregate(output_dir, payload)
    except ValueError as error:
        return 1, str(error)
    return 0, completed.stdout.strip()


def run_real_container_pipeline(
    config: RunConfig,
    image_tag: str,
    output_dir: Path,
) -> tuple[int, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    image_tag = resolve_image_tag(config, image_tag)
    inspected = inspect_image(image_tag)
    image_id = inspected["Id"]
    platform = inspected.get("Architecture", "unknown")
    environment = local_docker_env()
    container = "pilot001-run-" + uuid.uuid4().hex
    create_argv = build_container_create_argv(
        config=config,
        image_tag=image_tag,
        output_dir=output_dir,
        container_name=container,
    )
    try:
        created = _docker_run(create_argv, environment)
        if created.returncode != 0 or not created.stdout.strip():
            return 1, codes.P001_FAIL_CONTAINER
        fetch = _docker_exec(
            container,
            [
                "/opt/python/bin/python3",
                "-I",
                "-B",
                "tools/pilot001_first_run/real_entry.py",
                "--phase",
                "fetch",
            ],
            environment,
        )
        if fetch.returncode != 0:
            return _failure_from_stdout(fetch.stdout)
        disconnected = subprocess.run(
            docker_base() + ["network", "disconnect", REAL_FETCH_NETWORK, container],
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        if disconnected.returncode != 0:
            return 1, codes.P001_FAIL_CONTAINER
        analyze = _docker_exec(
            container,
            [
                "/opt/python/bin/python3",
                "-I",
                "-B",
                "tools/pilot001_first_run/real_entry.py",
                "--phase",
                "analyze",
            ],
            environment,
        )
        if analyze.returncode != 0:
            return _failure_from_stdout(analyze.stdout)
        try:
            payload = json.loads(analyze.stdout.strip())
        except json.JSONDecodeError:
            return 1, codes.P001_FAIL_CONTAINER
        payload = _finalize_aggregate_payload(
            payload,
            config=config,
            image_id=image_id,
            platform=platform,
            digest=image_id,
        )
        try:
            _promote_aggregate(output_dir, payload)
        except ValueError as error:
            return 1, str(error)
        return 0, analyze.stdout.strip()
    finally:
        subprocess.run(
            docker_base() + ["rm", "--force", container],
            env=environment,
            capture_output=True,
            check=False,
        )


def run_container_pipeline(
    config: RunConfig,
    image_tag: str,
    output_dir: Path,
) -> tuple[int, str]:
    if config.dry_run:
        return run_dry_container_pipeline(config, image_tag, output_dir)
    return run_real_container_pipeline(config, image_tag, output_dir)


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
