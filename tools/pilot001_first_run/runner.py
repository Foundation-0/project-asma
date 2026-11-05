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
HANDOFF_VOLUME_PREFIX = "pilot001-handoff-"
HANDOFF_MOUNT = "/handoff"
REAL_FETCH_NETWORK = "bridge"
FETCH_CONTAINER_SCRIPT = "tools/pilot001_first_run/fetch_container.py"
ANALYZE_CONTAINER_SCRIPT = "tools/pilot001_first_run/analyze_container.py"


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


def _runtime_env(*, image_id: str, platform: str, config: RunConfig) -> list[str]:
    return [
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
        "--env",
        f"PILOT001_HANDOFF_DIR={HANDOFF_MOUNT}",
    ]


def _hardened_run_prefix(*, network: str) -> list[str]:
    return [
        "--rm",
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
        "--tmpfs=/tmp:rw,noexec,nosuid,size=2048m",
        "--mount",
        f"type=bind,src={ROOT},dst=/work,readonly",
        "-w",
        "/work",
    ]


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


def build_fetch_container_argv(
    *,
    config: RunConfig,
    image_tag: str,
    volume_name: str,
    container_name: str,
) -> list[str]:
    inspected = inspect_image(image_tag)
    image_id = inspected["Id"]
    platform = inspected.get("Architecture", "unknown")
    command = (
        docker_base()
        + ["run", "--name", container_name]
        + _hardened_run_prefix(network=REAL_FETCH_NETWORK)
        + ["--mount", f"type=volume,src={volume_name},dst={HANDOFF_MOUNT}"]
        + _runtime_env(image_id=image_id, platform=platform, config=config)
        + [
            image_tag,
            "/opt/python/bin/python3",
            "-I",
            "-B",
            FETCH_CONTAINER_SCRIPT,
        ]
    )
    return command


def build_analyze_container_argv(
    *,
    config: RunConfig,
    image_tag: str,
    output_dir: Path,
    volume_name: str,
    container_name: str,
) -> list[str]:
    inspected = inspect_image(image_tag)
    image_id = inspected["Id"]
    platform = inspected.get("Architecture", "unknown")
    command = (
        docker_base()
        + ["run", "--name", container_name]
        + _hardened_run_prefix(network="none")
        + [
            "--mount",
            f"type=volume,src={volume_name},dst={HANDOFF_MOUNT},readonly",
            "--mount",
            f"type=bind,src={output_dir.resolve()},dst=/output",
        ]
        + _runtime_env(image_id=image_id, platform=platform, config=config)
    )
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
    command.extend(
        [
            image_tag,
            "/opt/python/bin/python3",
            "-I",
            "-B",
            ANALYZE_CONTAINER_SCRIPT,
        ]
    )
    return command


def build_container_run_argv(
    *,
    config: RunConfig,
    image_tag: str,
    output_dir: Path,
    container_name: str,
) -> list[str]:
    return build_dry_run_argv(
        config=config,
        image_tag=image_tag,
        output_dir=output_dir,
        container_name=container_name,
    )


def build_container_create_argv(
    *,
    config: RunConfig,
    image_tag: str,
    output_dir: Path,
    container_name: str,
) -> list[str]:
    """Compatibility for tests: phase-1 fetch container uses bridge + handoff volume."""
    volume_name = f"{HANDOFF_VOLUME_PREFIX}test"
    return build_fetch_container_argv(
        config=config,
        image_tag=image_tag,
        volume_name=volume_name,
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


def _create_handoff_volume(name: str, environment: dict[str, str]) -> bool:
    completed = subprocess.run(
        docker_base() + ["volume", "create", name],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def _remove_handoff_volume(name: str, environment: dict[str, str]) -> None:
    subprocess.run(
        docker_base() + ["volume", "rm", "-f", name],
        env=environment,
        capture_output=True,
        check=False,
    )


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
    volume = HANDOFF_VOLUME_PREFIX + uuid.uuid4().hex
    if not _create_handoff_volume(volume, environment):
        return 1, codes.P001_FAIL_CONTAINER
    fetch_container = "pilot001-fetch-" + uuid.uuid4().hex
    analyze_container = "pilot001-analyze-" + uuid.uuid4().hex
    try:
        fetch_argv = build_fetch_container_argv(
            config=config,
            image_tag=image_tag,
            volume_name=volume,
            container_name=fetch_container,
        )
        fetch = _docker_run(fetch_argv, environment)
        if fetch.returncode != 0:
            return _failure_from_stdout(fetch.stdout)
        analyze_argv = build_analyze_container_argv(
            config=config,
            image_tag=image_tag,
            output_dir=output_dir,
            volume_name=volume,
            container_name=analyze_container,
        )
        analyze = _docker_run(analyze_argv, environment)
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
        _remove_handoff_volume(volume, environment)


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
        docker_base() + ["ps", "-a", "--filter", "name=pilot001-", "--format", "{{.ID}}"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if ps.stdout.strip():
        return codes.P001_FAIL_POSTFLIGHT
    volumes = subprocess.run(
        docker_base() + ["volume", "ls", "--filter", f"name={HANDOFF_VOLUME_PREFIX}", "-q"],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if volumes.stdout.strip():
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
