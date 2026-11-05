#!/usr/bin/env python3
"""Pilot 001 first-run entrypoint (preflight, gated container run, validation)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pilot001_first_run import failure_codes as codes  # noqa: E402
from pilot001_first_run.config import RunConfig, default_input_manifest  # noqa: E402
from pilot001_first_run.gates import validate_dropbox_flag, validate_real_run_gates  # noqa: E402
from pilot001_first_run.output_validator import validate_output_dir  # noqa: E402
from pilot001_first_run.preflight import run_preflight  # noqa: E402
from pilot001_first_run.runner import (  # noqa: E402
    AGGREGATE_FILENAME,
    PREFLIGHT_FILENAME,
    emit_failure,
    emit_success_summary,
    git_sha,
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
    args = parser.parse_args(argv)
    config = build_config(args)
    config.output_dir.mkdir(parents=True, exist_ok=True)

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

    status, _detail = run_container_pipeline(config, args.image, config.output_dir)
    if status != 0:
        emit_failure(_detail if codes.is_aggregate_failure_line(_detail) else codes.P001_FAIL_CONTAINER)
        return 1

    validation_errors = validate_output_dir(config.output_dir, frozenset({AGGREGATE_FILENAME, PREFLIGHT_FILENAME}))
    if validation_errors:
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
    except Exception as exc:
        sys.stderr.write(f"{type(exc).__name__}\n")
        emit_failure(codes.P001_FAIL_INTERNAL)
        raise SystemExit(1) from None
