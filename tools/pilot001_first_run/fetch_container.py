#!/usr/bin/env python3
"""Phase 1: allowlisted download + manifest verify; raw bytes to handoff volume only."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from pilot001_first_run import failure_codes as codes  # noqa: E402
from pilot001_first_run.config import default_input_manifest  # noqa: E402
from pilot001_first_run.study_fetch import StudyFetchError, fetch_for_handoff, write_raw_handoff  # noqa: E402

HANDOFF_DIR = Path(os.environ.get("PILOT001_HANDOFF_DIR", "/handoff"))


def _emit(code: str) -> None:
    sys.stdout.write(code + "\n")
    sys.stdout.flush()


def main() -> int:
    try:
        pins = default_input_manifest()
        compressed, clinical, panel = fetch_for_handoff(pins)
        write_raw_handoff(HANDOFF_DIR, compressed, clinical, panel)
    except StudyFetchError as error:
        _emit(error.code)
        return 1
    except OSError:
        _emit(codes.P001_FAIL_INTERNAL)
        return 1
    except Exception:
        _emit(codes.P001_FAIL_INTERNAL)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
