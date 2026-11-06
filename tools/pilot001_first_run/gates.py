"""Input and clearance gates for real-data mode."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from pilot001_first_run import failure_codes as codes
from pilot001_first_run.config import RunConfig, parse_attestation_ref
from pilot001_first_run.cross_arch_equivalence import (
    NATIVE_ARM64_ARCH,
    git_sha_matches_head,
    pass_record_matches_images,
    verify_pass_record_payload,
)

TORONTO = ZoneInfo("America/Toronto")


def toronto_today() -> datetime.date:
    return datetime.now(TORONTO).date()


def validate_real_run_gates(
    config: RunConfig,
    *,
    preflight_passed: bool,
) -> str | None:
    """Return an aggregate failure code or None when real mode may proceed."""
    if config.dry_run:
        return None
    if not config.gate0_signed or not config.dropbox_cleared:
        return codes.P001_FAIL_GATE_REAL_FLAGS
    parsed = parse_attestation_ref(config.gate0_attestation_ref)
    if not parsed:
        return codes.P001_FAIL_GATE_ATTESTATION_REF
    _att_id, att_date = parsed
    try:
        att = datetime.strptime(att_date, "%Y-%m-%d").date()
    except ValueError:
        return codes.P001_FAIL_GATE_ATTESTATION_REF
    if att != toronto_today():
        return codes.P001_FAIL_GATE_ATTESTATION_DATE
    if config.dropbox_cleared:
        if config.host != "macos":
            return codes.P001_FAIL_GATE_DROPBOX_HOST
        if not preflight_passed:
            return codes.P001_FAIL_GATE_DROPBOX_PREFLIGHT
    return None


def validate_dropbox_flag(config: RunConfig, *, preflight_passed: bool) -> str | None:
    """Enforce grk-helix clearance: dropbox flag only on macOS after preflight."""
    if not config.dropbox_cleared:
        return None
    if config.host != "macos":
        return codes.P001_FAIL_GATE_DROPBOX_HOST
    if not preflight_passed:
        return codes.P001_FAIL_GATE_DROPBOX_PREFLIGHT
    return None


def validate_cross_arch_equivalence_for_real_run(
    *,
    machine_arch: str,
    real_mode: bool,
    head_git_sha: str,
    amd64_image_id: str,
    arm64_image_id: str,
    arm64_image_architecture: str,
    pass_record: dict | None,
) -> str | None:
    """Refuse macOS arm64 --real unless a CI-auditable pass record matches HEAD and images."""
    if machine_arch not in NATIVE_ARM64_ARCH or not real_mode:
        return None
    if pass_record is None or not verify_pass_record_payload(pass_record):
        return codes.P001_FAIL_GATE_CROSS_ARCH_EQUIVALENCE
    if not git_sha_matches_head(pass_record.get("git_sha"), head_git_sha):
        return codes.P001_FAIL_GATE_CROSS_ARCH_EQUIVALENCE
    if str(arm64_image_architecture).lower() not in NATIVE_ARM64_ARCH:
        return codes.P001_FAIL_GATE_CROSS_ARCH_EQUIVALENCE
    if not pass_record_matches_images(
        pass_record,
        amd64_image_id=amd64_image_id,
        arm64_image_id=arm64_image_id,
    ):
        return codes.P001_FAIL_GATE_CROSS_ARCH_EQUIVALENCE
    return None
