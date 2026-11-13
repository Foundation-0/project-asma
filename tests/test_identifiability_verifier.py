"""Run the identifiability verifier and the v1 certificate regeneration check."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IdentifiabilityVerifierTest(unittest.TestCase):
    def run_script(self, relative):
        return subprocess.run(
            [sys.executable, str(ROOT / relative)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_exact_rationals_and_c20_fitted_check(self):
        done = self.run_script("tools/verify_identifiability_and_c20.py")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("fitted consistency check", done.stdout)
        self.assertIn("OK: exact rational checks passed", done.stdout)

    def test_v1_certificate_regenerates(self):
        done = self.run_script("tools/check_identifiability_certificate_v1.py")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("366a230dbcf8f8a253bc4d0bd14a6ae91ce54e66d019cbd0c7454abde9e73923", done.stdout)

    def test_lean_toolchain_pinned(self):
        pin = (ROOT / "formal" / "lean-toolchain").read_text(encoding="utf-8").strip()
        self.assertEqual(pin, "leanprover/lean4:v4.35.0")
        source = (ROOT / "formal" / "AsmaIdentifiabilityProofs.lean").read_text(encoding="utf-8")
        for word in ("sorry", "admit", "native_decide"):
            self.assertNotIn(word, source.replace("no sorry", ""))


if __name__ == "__main__":
    unittest.main()
