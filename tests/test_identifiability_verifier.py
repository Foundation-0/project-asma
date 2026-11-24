"""Run the identifiability verifier and the v1 certificate regeneration check."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The three isolated interpreter modes of aletheia contract R4 and the
# cave-expedition verify workflow: plain, optimized (-O drops assert
# statements) and warnings as errors.
PARITY_MODES = (("-I", "-B"), ("-I", "-O", "-B"), ("-I", "-B", "-W", "error"))


class IdentifiabilityVerifierTest(unittest.TestCase):
    def run_script(self, relative, *flags):
        return subprocess.run(
            [sys.executable, *flags, str(ROOT / relative)],
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

    def test_verifier_gives_same_result_in_all_three_modes(self):
        runs = [self.run_script("tools/verify_identifiability_and_c20.py", *flags) for flags in PARITY_MODES]
        for flags, done in zip(PARITY_MODES, runs):
            self.assertEqual(done.returncode, 0, (flags, done.stderr))
            self.assertEqual(done.stdout, runs[0].stdout, flags)
        self.assertIn("OK: exact rational checks passed", runs[0].stdout)

    def test_tampered_expected_value_fails_in_all_three_modes(self):
        # Must-fail control: with bare asserts, -O printed OK on this tampered copy.
        source = (ROOT / "tools" / "verify_identifiability_and_c20.py").read_text(encoding="utf-8")
        expected = 'eps[("S", "C25")] == Fraction(10179, 563920)'
        self.assertEqual(source.count(expected), 1)
        with tempfile.TemporaryDirectory() as tmp:
            tampered = Path(tmp) / "verify_tampered.py"
            tampered.write_text(source.replace(expected, 'eps[("S", "C25")] == Fraction(1, 2)'), encoding="utf-8")
            for flags in PARITY_MODES:
                done = subprocess.run(
                    [sys.executable, *flags, str(tampered)], capture_output=True, text=True, check=False
                )
                self.assertEqual(done.returncode, 1, flags)
                self.assertNotIn("OK:", done.stdout, flags)
                self.assertIn("AssertionError", done.stderr, flags)

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
