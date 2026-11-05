"""Read-only host preflight for Pilot 001 first-run orchestration."""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class PreflightReport:
    host: str
    passed: bool
    checks: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"host": self.host, "passed": self.passed, "checks": self.checks}


CommandRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def _default_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def _ulimit_core(runner: CommandRunner) -> tuple[bool, str]:
    result = runner(["bash", "-lc", "ulimit -c"])
    value = (result.stdout or "").strip()
    ok = result.returncode == 0 and value == "0"
    return ok, value or f"exit={result.returncode}"


def _path_excluded(path: Path, runner: CommandRunner) -> bool | None:
    if not path.exists():
        return True
    result = runner(["tmutil", "isexcluded", str(path)])
    if result.returncode != 0:
        return None
    text = (result.stdout or "").strip().lower()
    if "[excluded]" in text:
        return True
    if "[included]" in text:
        return False
    return None


def _forbidden_output_path(path: Path, runner: CommandRunner) -> str | None:
    resolved = path.expanduser().resolve()
    text = str(resolved)
    lowered = text.lower()
    if "icloud drive" in lowered or "/library/mobile documents/com~apple~clouddocs" in lowered:
        return "icloud"
    parts = resolved.parts
    if "Dropbox" in parts:
        return "dropbox_sync"
    excluded = _path_excluded(resolved, runner)
    if excluded is False:
        return "time_machine"
    return None


def run_linux_preflight(output_dir: Path, runner: CommandRunner | None = None) -> PreflightReport:
    runner = runner or _default_runner
    checks: dict[str, str] = {}
    ok_core, detail = _ulimit_core(runner)
    checks["ulimit_core"] = "PASS" if ok_core else f"FAIL:{detail}"
    forbidden = _forbidden_output_path(output_dir, runner)
    if forbidden:
        checks["output_path"] = f"FAIL:{forbidden}"
    else:
        checks["output_path"] = "PASS"
    passed = all(value.startswith("PASS") for value in checks.values())
    return PreflightReport("linux-ci", passed, checks)


def run_macos_preflight(
    output_dir: Path,
    runner: CommandRunner | None = None,
    *,
    docker_desktop_swap: int | None = None,
) -> PreflightReport:
    runner = runner or _default_runner
    checks: dict[str, str] = {}
    ok_core, detail = _ulimit_core(runner)
    checks["ulimit_core"] = "PASS" if ok_core else f"FAIL:{detail}"

    for name, command in (
        ("kern_coredump", ["sysctl", "-n", "kern.coredump"]),
        ("vm_swapusage", ["sysctl", "-n", "vm.swapusage"]),
        ("fdesetup_status", ["fdesetup", "status"]),
    ):
        result = runner(command)
        checks[name] = "PASS" if result.returncode == 0 else f"FAIL:exit={result.returncode}"

    if docker_desktop_swap is None:
        settings = Path.home() / "Library/Group Containers/group.com.docker/settings.json"
        swap_value = None
        if settings.is_file():
            try:
                payload = json.loads(settings.read_text(encoding="utf-8"))
                swap_value = payload.get("swapMiB")
            except (OSError, ValueError):
                swap_value = None
        docker_desktop_swap = swap_value
    if docker_desktop_swap != 0:
        checks["docker_desktop_swap"] = f"FAIL:{docker_desktop_swap!r}"
    else:
        checks["docker_desktop_swap"] = "PASS"

    forbidden = _forbidden_output_path(output_dir, runner)
    if forbidden:
        checks["output_path"] = f"FAIL:{forbidden}"
    else:
        checks["output_path"] = "PASS"

    passed = all(value.startswith("PASS") for value in checks.values())
    return PreflightReport("macos", passed, checks)


def run_preflight(host: str, output_dir: Path, runner: CommandRunner | None = None, **kwargs) -> PreflightReport:
    if host == "macos":
        return run_macos_preflight(output_dir, runner, **kwargs)
    return run_linux_preflight(output_dir, runner)


ICLOUD_PATTERN = re.compile(r"icloud|clouddocs", re.I)
