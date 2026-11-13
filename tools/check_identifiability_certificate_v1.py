#!/usr/bin/env python3
"""Regenerate the v1 identifiability and C20 certificate and check its SHA-256.

tools/generate_identifiability_certificate_v1.py is the generator from the
2026-11-13 vault drop, kept byte for byte. The certificate it writes is added by
PR #84 at results/identifiability-and-c20-2026-11-13/identifiability_and_c20_certificates.json.

This script runs a copy of the generator in a temporary directory, checks the
output hash, and compares it with #84's committed file when that file exists.

The v1 C20 section weights within-fold pairs by 863 (fold sizes 28 and 26) and
records the first fitted draw with U = 3491. The maintained verifier,
tools/verify_identifiability_and_c20.py, uses the balanced 862-pair split and
treats C20 as a fitted consistency check. Switching the v1 generator to the
862-pair split (w_in = 862/4316, negatives 16, 16, 17, 17, 17) makes it find no
draw in 4000 with U = 3491 and fold mean within 0.0025 of 0.83, so its assertion
fails and it writes no certificate. The v1 generator is kept unchanged here to
reproduce the cited hash.
"""

import hashlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "tools" / "generate_identifiability_certificate_v1.py"
NAME = "identifiability_and_c20_certificates.json"
COMMITTED = ROOT / "results" / "identifiability-and-c20-2026-11-13" / NAME
EXPECTED = "366a230dbcf8f8a253bc4d0bd14a6ae91ce54e66d019cbd0c7454abde9e73923"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tools = Path(tmp) / "tools"
        tools.mkdir()
        shutil.copy(GENERATOR, tools / GENERATOR.name)
        subprocess.run([sys.executable, str(tools / GENERATOR.name)], check=True, capture_output=True)
        regenerated = (Path(tmp) / "results" / NAME).read_bytes()
    digest = hashlib.sha256(regenerated).hexdigest()
    if digest != EXPECTED:
        print(f"FAIL: regenerated certificate hash {digest} differs from {EXPECTED}", file=sys.stderr)
        return 1
    if COMMITTED.is_file() and COMMITTED.read_bytes() != regenerated:
        print(f"FAIL: {COMMITTED.relative_to(ROOT)} differs from the regenerated certificate", file=sys.stderr)
        return 1
    where = COMMITTED.relative_to(ROOT) if COMMITTED.is_file() else "no committed copy yet (PR #84)"
    print(f"PASS: regenerated {NAME} has SHA-256 {EXPECTED}; compared with: {where}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
