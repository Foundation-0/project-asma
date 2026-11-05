#!/usr/bin/env python3
"""Standalone read-only preflight CLI for Pilot 001 first run."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pilot001_first_run.preflight import run_preflight  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=["linux-ci", "macos"], required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    report = run_preflight(args.host, Path(args.output_dir))
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
