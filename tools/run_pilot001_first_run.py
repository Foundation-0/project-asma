#!/usr/bin/env python3
"""Pilot 001 first-run entrypoint (preflight, gated container run, validation)."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pilot001_first_run import failure_codes as codes  # noqa: E402
from pilot001_first_run.config import RunConfig, default_input_manifest  # noqa: E402
from pilot001_first_run.cross_arch_equivalence import (  # noqa: E402
    PASS_FILENAME as EQUIVALENCE_PASS_FILENAME,
    load_pass_record,
    try_download_pass_record_from_ci,
)
from pilot001_first_run.gates import (  # noqa: E402
    validate_cross_arch_equivalence_for_real_run,
    validate_dropbox_flag,
    validate_real_run_gates,
)
from pilot001_first_run.output_validator import validate_output_dir  # noqa: E402
from pilot001_first_run.preflight import run_preflight  # noqa: E402
from pilot001_first_run.runner import (  # noqa: E402
    AGGREGATE_FILENAME,
    PREFLIGHT_FILENAME,
    STAGING_AGGREGATE,
    emit_failure,
    emit_success_summary,
    git_sha,
    inspect_image,
    postflight,
    run_container_pipeline,
)


def build_config(args: argparse.Namespace) -> RunConfig:
    return RunConfig(
        host=args.host,
        output_dir=Path(args.output_dir),
        dry_run=not args.real,
        gate0_signed=args.gate0_signed,
        gate0_attestation_ref=args.gate0_attestation_ref,
        dropbox_cleared=args.dropbox_cleared,
        input_manifest=default_input_manifest(),
        git_sha=git_sha(),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=["linux-ci", "macos"], required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--image", default="asma-synthetic:4.4.3")
    parser.add_argument("--real", action="store_true", help="Real study-data mode (disabled in CI)")
    parser.add_argument("--gate0-signed", action="store_true", default=False)
    parser.add_argument("--gate0-attestation-ref", default=None)
    parser.add_argument("--dropbox-cleared", action="store_true", default=False)
    parser.add_argument(
        "--reference-image",
        default="asma-synthetic:4.4.3",
        help="Recorded amd64 synthetic image tag for cross-arch equivalence on Apple Silicon",
    )
    parser.add_argument(
        "--equivalence-record",
        default=None,
        help=(
            f"Offline override: path to {EQUIVALENCE_PASS_FILENAME} "
            "(default: download CI artifact for HEAD, else output dir file)"
        ),
    )
    args = parser.parse_args(argv)
    config = build_config(args)
    config.output_dir.mkdir(parents=True, exist_ok=True)
    head_sha = git_sha()

    preflight = run_preflight(config.host, config.output_dir)
    (config.output_dir / PREFLIGHT_FILENAME).write_text(
        json.dumps(preflight.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not preflight.passed:
        emit_failure(codes.P001_FAIL_PREFLIGHT)
        return 1

    dropbox_gate = validate_dropbox_flag(config, preflight_passed=preflight.passed)
    if dropbox_gate:
        emit_failure(dropbox_gate)
        return 1

    real_gate = validate_real_run_gates(config, preflight_passed=preflight.passed)
    if real_gate:
        emit_failure(real_gate)
        return 1

    if config.host == "macos" and not config.dry_run and platform.machine() in {"arm64", "aarch64"}:
        try:
            amd64_inspect = inspect_image(args.reference_image)
            arm64_inspect = inspect_image(args.image)
            amd64_id = amd64_inspect["Id"]
            arm64_id = arm64_inspect["Id"]
            arm64_arch = arm64_inspect.get("Architecture", "")
        except (subprocess.CalledProcessError, OSError, KeyError, IndexError, json.JSONDecodeError):
            emit_failure(codes.P001_FAIL_GATE_CROSS_ARCH_EQUIVALENCE)
            return 1

        pass_record = None
        if args.equivalence_record is not None:
            pass_record = load_pass_record(Path(args.equivalence_record), require_git_sha=head_sha)
        else:
            with tempfile.TemporaryDirectory(prefix="pilot001-equiv-") as tmp:
                pass_record = try_download_pass_record_from_ci(git_sha=head_sha, dest_dir=Path(tmp))
            if pass_record is None:
                pass_record = load_pass_record(
                    config.output_dir / EQUIVALENCE_PASS_FILENAME,
                    require_git_sha=head_sha,
                )

        cross_arch_gate = validate_cross_arch_equivalence_for_real_run(
            machine_arch=platform.machine(),
            real_mode=True,
            head_git_sha=head_sha,
            amd64_image_id=amd64_id,
            arm64_image_id=arm64_id,
            arm64_image_architecture=arm64_arch,
            pass_record=pass_record,
        )
        if cross_arch_gate:
            emit_failure(cross_arch_gate)
            return 1

    status, _detail = run_container_pipeline(config, args.image, config.output_dir)
    if status != 0:
        emit_failure(_detail if codes.is_aggregate_failure_line(_detail) else codes.P001_FAIL_CONTAINER)
        return 1

    validation_errors = validate_output_dir(config.output_dir, frozenset({AGGREGATE_FILENAME, PREFLIGHT_FILENAME}))
    if validation_errors:
        aggregate_path = config.output_dir / AGGREGATE_FILENAME
        staging_path = config.output_dir / STAGING_AGGREGATE
        for path in (aggregate_path, staging_path):
            if path.is_file():
                path.unlink()
        emit_failure(codes.P001_FAIL_OUTPUT_VALIDATION)
        return 1

    postflight_error = postflight()
    if postflight_error:
        emit_failure(postflight_error)
        return 1

    emit_success_summary(config.output_dir)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        emit_failure(codes.P001_FAIL_INTERNAL)
        raise SystemExit(1) from None
