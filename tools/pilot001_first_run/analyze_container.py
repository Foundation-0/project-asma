#!/usr/bin/env python3
"""Phase 2: offline parse + R reconstruction from verified raw handoff bytes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from pilot001_first_run import failure_codes as codes  # noqa: E402
from pilot001_first_run.config import REAL_REPETITIONS, default_input_manifest  # noqa: E402
from pilot001_first_run.study_fetch import (  # noqa: E402
    StudyFetchError,
    read_raw_handoff,
    verify_uncompressed_member_for_analysis,
)
from source_data_adapter import SourceAdapterError, parse_sources  # noqa: E402

HANDOFF_DIR = Path(os.environ.get("PILOT001_HANDOFF_DIR", "/handoff"))
PAYLOAD_PATH = Path("/tmp/pilot001-study/source-payload.json")


def _emit(code: str) -> None:
    sys.stdout.write(code + "\n")
    sys.stdout.flush()


def _adapter_code(category: str | None) -> str:
    mapping = {
        "authorization": codes.P001_FAIL_SOURCE_AUTHORIZATION,
        "acquisition": codes.P001_FAIL_FETCH,
        "source_bytes": codes.P001_FAIL_INPUT_INTEGRITY,
        "workbook": codes.P001_FAIL_SOURCE_ADAPTER,
        "clinical": codes.P001_FAIL_SOURCE_ADAPTER,
        "panel_membership": codes.P001_FAIL_SOURCE_ADAPTER,
        "matrix": codes.P001_FAIL_SOURCE_ADAPTER,
        "matrix_value": codes.P001_FAIL_SOURCE_ADAPTER,
        "contract": codes.P001_FAIL_SOURCE_ADAPTER,
    }
    return mapping.get(category or "", codes.P001_FAIL_SOURCE_ADAPTER)


def main() -> int:
    attestation_id = os.environ.get("PILOT001_OWNER_ATTESTATION_ID", "").strip()
    if not attestation_id:
        _emit(codes.P001_FAIL_GATE_ATTESTATION_REF)
        return 1
    try:
        pins = default_input_manifest()
        compressed, clinical, panel = read_raw_handoff(HANDOFF_DIR)
        verify_uncompressed_member_for_analysis(compressed, pins)
        payload = parse_sources(
            compressed,
            clinical,
            panel,
            owner_attestation=attestation_id,
        )
        PAYLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
        PAYLOAD_PATH.write_text(
            json.dumps(payload, allow_nan=False, separators=(",", ":")),
            encoding="utf-8",
        )
    except StudyFetchError as error:
        _emit(error.code)
        return 1
    except SourceAdapterError as error:
        _emit(_adapter_code(error.category))
        return 1
    except OSError:
        _emit(codes.P001_FAIL_INTERNAL)
        return 1
    except Exception:
        _emit(codes.P001_FAIL_INTERNAL)
        return 1

    try:
        env = os.environ.copy()
        env["PILOT001_SOURCE_PAYLOAD_PATH"] = str(PAYLOAD_PATH)
        completed = subprocess.run(
            [
                "Rscript",
                "--vanilla",
                "tools/run_pilot001_reconstruction.R",
                "--real",
                f"--repetitions={REAL_REPETITIONS}",
            ],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.stdout:
            sys.stdout.write(completed.stdout)
        if completed.returncode != 0:
            line = completed.stdout.strip().splitlines()[0] if completed.stdout.strip() else ""
            if codes.is_aggregate_failure_line(line):
                return completed.returncode
            _emit(codes.P001_FAIL_CONTAINER)
            return 1
        return 0
    except Exception:
        _emit(codes.P001_FAIL_INTERNAL)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
