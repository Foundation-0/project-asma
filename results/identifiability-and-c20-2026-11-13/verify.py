#!/usr/bin/env python3
"""Regenerate the archived v1 certificate and compare its SHA-256.

generator_v1.py is the original generator from the 2026-11-13 vault drop, kept
byte for byte. It writes ../results/identifiability_and_c20_certificates.json
relative to its own parent directory, so this script runs a copy inside a
temporary directory and compares the output with the committed file.
"""

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = "366a230dbcf8f8a253bc4d0bd14a6ae91ce54e66d019cbd0c7454abde9e73923"
NAME = "identifiability_and_c20_certificates.json"


def main() -> int:
    committed = (HERE / NAME).read_bytes()
    if hashlib.sha256(committed).hexdigest() != EXPECTED:
        print("FAIL: committed certificate hash differs", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        tools = Path(tmp) / "tools"
        tools.mkdir()
        shutil.copy(HERE / "generator_v1.py", tools / "generator_v1.py")
        subprocess.run([sys.executable, str(tools / "generator_v1.py")], check=True, capture_output=True)
        regenerated = (Path(tmp) / "results" / NAME).read_bytes()
    if regenerated != committed:
        print("FAIL: regenerated certificate differs from the committed file", file=sys.stderr)
        return 1
    print(f"PASS: regenerated {NAME} matches SHA-256 {EXPECTED}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
