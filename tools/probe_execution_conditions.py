#!/usr/bin/env python3
"""Observe technical controls without study data; never grant research clearance."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

from build_synthetic_runtime import ROOT, local_docker_env

FAILURE = "ERROR: execution-condition probe failed; no environment details emitted."
IMAGE_RECORD = ROOT / "registries/pilot-001-source-adapter-runtime.json"
MEMORY_BYTES = 8 * 1024**3


def execution_options(root=ROOT, uid=None, gid=None):
    """Controls for a local, offline process; no data or secrets in arguments."""
    uid = os.getuid() if uid is None else uid
    gid = os.getgid() if gid is None else gid
    return ["--network=none", "--read-only", "--cap-drop=ALL", "--log-driver=none",
            "--user", f"{uid}:{gid}", "--security-opt=no-new-privileges",
            "--ulimit=core=0", "--pids-limit=256", "--memory=8g", "--memory-swap=8g",
            "--cpus=2", "--tmpfs=/tmp:rw,noexec,nosuid,size=256m",
            "--mount", f"type=bind,src={root},dst=/work,readonly", "-w", "/work",
            "--env", "R_HISTFILE=/dev/null", "--env", "XDG_CACHE_HOME=/tmp/asma-cache",
            "--env", "R_USER_CACHE_DIR=/tmp/asma-cache"]


def observed_status(value, expected=True):
    """Unavailable evidence never becomes a successful control check."""
    return "UNKNOWN" if value is None else "PASS" if type(value) is type(expected) and value == expected else "FAIL"


def inspect_controls(inspected, owner):
    """Extract an allowlist, never return Docker environment/host paths/IDs."""
    host = inspected.get("HostConfig", {})
    config = inspected.get("Config", {})
    mount = [item for item in inspected.get("Mounts", []) if item.get("Destination") == "/work"]
    limits = [item for item in host.get("Ulimits", []) if item.get("Name") == "core"]
    return {
        "docker_network_none": host.get("NetworkMode") == "none" if "NetworkMode" in host else None,
        "docker_root_read_only": host.get("ReadonlyRootfs"),
        "docker_checkout_read_only": (len(mount) == 1 and mount[0].get("RW") is False and
                                      mount[0].get("Type") == "bind") if "Mounts" in inspected else None,
        "docker_log_driver_none": host.get("LogConfig", {}).get("Type") == "none" if "LogConfig" in host else None,
        "docker_capabilities_dropped": host.get("CapDrop") == ["ALL"] if "CapDrop" in host else None,
        "docker_no_new_privileges": any(item in ("no-new-privileges", "no-new-privileges:true")
                                        for item in host.get("SecurityOpt", [])) if "SecurityOpt" in host else None,
        "docker_checkout_owner": config.get("User") == owner if "User" in config else None,
        "docker_core_zero": (len(limits) == 1 and limits[0].get("Soft") == 0 and limits[0].get("Hard") == 0)
                            if "Ulimits" in host else None,
        "docker_memory_bytes": host.get("Memory"),
        "docker_memory_plus_swap_bytes": host.get("MemorySwap"),
        "docker_nanocpus": host.get("NanoCpus"), "docker_pids_limit": host.get("PidsLimit"),
    }


def evaluate_checks(observation, docker):
    expected = {
        "root_read_only": True, "checkout_read_only": True,
        "network_interfaces_loopback_only": True, "ipv4_route_table_empty": True,
        "capabilities_all_zero": True, "no_new_privileges": True,
        "runs_as_checkout_owner": True, "core_dump_soft_and_hard_zero": True,
        "cgroup_v2": True, "memory_limit_bytes": MEMORY_BYTES, "swap_limit_bytes": 0,
        "cpu_limit": 2, "pids_limit": 256, "tmpfs_noexec_nosuid": True,
        "tmpfs_limit_256_mib": True, "r_tempdir_on_tmpfs": True,
        "artificial_tmpfs_write_removed": True, "vanilla_startup": True,
        "workspace_save_restore_disabled": True, "history_disabled": True,
        "cache_destinations_on_tmpfs": True,
        "python_version": "3.12.14", "python_isolated_mode": True,
        "python_user_site_disabled": True, "python_bytecode_writes_disabled": True,
        "python_shares_cgroup": True, "python_shares_mount_namespace": True,
        "python_shares_network_namespace": True,
    }
    expected_docker = {key: True for key in (
        "docker_network_none", "docker_root_read_only", "docker_checkout_read_only",
        "docker_log_driver_none", "docker_capabilities_dropped", "docker_no_new_privileges",
        "docker_checkout_owner", "docker_core_zero")}
    expected_docker.update(docker_memory_bytes=MEMORY_BYTES,
                           docker_memory_plus_swap_bytes=MEMORY_BYTES,
                           docker_nanocpus=2_000_000_000, docker_pids_limit=256)
    checks = {}
    for values, requirements in ((observation, expected), (docker, expected_docker)):
        for name, wanted in requirements.items():
            value = values.get(name)
            # JSON numbers are numeric; reject booleans pretending to be limits.
            if type(wanted) is int and type(value) is float and value.is_integer():
                value = int(value)
            checks[name] = {"status": observed_status(value, wanted), "observed": value, "expected": wanted}
    return checks


def executor_observations(root=Path("/")):
    """Report only kernel-visible aggregate constraints, not provider guarantees."""
    def read(relative):
        try:
            return (root / relative).read_text().strip()
        except (OSError, UnicodeError):
            return None
    swaps = read("proc/swaps")
    result = {"kernel_visible_swap_devices": None if swaps is None else max(0, len(swaps.splitlines()) - 1)}
    for name in ("memory.max", "memory.swap.max", "cpu.max", "pids.max"):
        value = read("sys/fs/cgroup/" + name)
        result[name] = value if value is not None and re.fullmatch(r"(?:max|[0-9]+)(?: [0-9]+)?", value) else None
    result["scope"] = "Current executor view; unseen ancestor limits and provider memory/storage policies are not verified."
    return result


def run_probe():
    docker = ["docker", "--host=unix:///var/run/docker.sock"]
    environment = local_docker_env()
    pinned = json.loads(IMAGE_RECORD.read_text())["environment"]["runtime_image_id"]
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", pinned):
        raise ValueError(FAILURE)
    def command(arguments, timeout=60):
        result = subprocess.run(docker + arguments, env=environment, check=True,
                                capture_output=True, text=True, timeout=timeout)
        if result.stderr:
            raise ValueError(FAILURE)
        return result.stdout
    identity = command(["image", "inspect", pinned, "--format", "{{.Id}}"])
    if identity.strip() != pinned:
        raise ValueError(FAILURE)
    name = "asma-condition-probe-" + uuid.uuid4().hex
    started = datetime.now(timezone.utc).isoformat()
    created = False
    try:
        created = True
        command(["create", "--name", name] + execution_options() +
                ["--env", f"ASMA_PROBE_UID={os.getuid()}", pinned,
                 "Rscript", "--vanilla", "--no-save", "--no-restore", "tools/probe_execution_conditions.R"])
        observation = json.loads(command(["start", "--attach", name]))
        inspected = json.loads(command(["inspect", name]))
        if not isinstance(observation, dict) or observation.get("schema_version") != 1 or len(inspected) != 1:
            raise ValueError(FAILURE)
        container = inspected[0]
        if container.get("State", {}).get("ExitCode") != 0:
            raise ValueError(FAILURE)
        checks = evaluate_checks(observation, inspect_controls(container, f"{os.getuid()}:{os.getgid()}"))
        states = [item["status"] for item in checks.values()]
        return {
            "schema_version": 1, "scope": "Technical runtime probe only; no study data or research clearance",
            "started_at_utc": started, "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime_image_id": pinned,
            "technical_checks_status": "FAIL" if "FAIL" in states else "UNKNOWN" if "UNKNOWN" in states else "PASS",
            "checks": checks, "executor_observations": executor_observations(),
            "unverified_context": {name: "UNKNOWN" for name in (
                "actual_processing_country", "operator_research_location", "provider_terms_and_retention",
                "applicable_institutional_or_funding_obligations", "applicable_privacy_and_research_use_basis")},
            "limitations": [
                "A passing technical probe does not authorize data use or establish any legal or ethics determination.",
                "The no-log driver prevents Docker log persistence for this probe, not provider monitoring or retention.",
                "No study bytes were downloaded or processed; only an artificial temporary marker was written and removed.",
                "No external network connection was attempted; network isolation is assessed from configuration and kernel interfaces/routes.",
                "Visible zero swap and tmpfs do not certify memory erasure or absent provider snapshots."
            ],
            "implementation_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                      for path in (Path(__file__), ROOT / "tools/probe_execution_conditions.R",
                                                   ROOT / "tests/test_execution_conditions.py",
                                                   ROOT / "tools/build_synthetic_runtime.py", IMAGE_RECORD)},
        }
    finally:
        if created:
            # Cleanup applies only to the UUID-named container created here.
            subprocess.run(docker + ["rm", "--force", name], env=environment, check=True,
                           capture_output=True, text=True, timeout=30)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    try:
        result = run_probe()
        print(json.dumps(result, sort_keys=True, indent=2, allow_nan=False))
        return 0 if result["technical_checks_status"] == "PASS" else 2
    except Exception:
        print(FAILURE, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
