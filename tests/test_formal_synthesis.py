"""Unit and adversarial negative-control tests for formal synthesis (P01-P03 & Scan 23848)."""

from __future__ import annotations

import copy
from fractions import Fraction
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_formal_synthesis as afs  # noqa: E402


class TestFormalSynthesisAndScan23848(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = afs.build_report()

    def test_01_p01_canonical_suffix_non_existence_and_disjoint_scan23848_partition(self) -> None:
        p01 = self.report["p01_scan23848_deconvolution"]
        self.assertEqual(p01["peak_count"], 173)
        self.assertEqual(p01["p01_canonical_suffix_count"], 0)
        self.assertEqual(len(p01["cdr2l_cleaved_bonds"]), 10)
        self.assertEqual(p01["cdr2l_uncleaved_bonds"], [1, 4, 13, 14])
        part = p01["disjoint_partition"]
        self.assertEqual(sum(v["peaks"] for v in part.values()), 173)
        self.assertGreater(
            part["chimeric_615_026_ladder"]["ion_current_pct"],
            part["cdr2l_primary_by"]["ion_current_pct"],
        )

    def test_02_p02_permutation_unbiasedness_and_c20_witness(self) -> None:
        p02 = self.report["p02_c20_fold_vs_pooled_auc"]
        self.assertEqual(p02["pooled_auc_exact"], "3491/4316")
        self.assertEqual(p02["permutation_expected_fold_mean_exact"], "3491/4316")
        self.assertEqual(p02["witness_tied_pairs"], 0)
        self.assertEqual(p02["witness_pooled_concordant_pairs"], 3491)
        self.assertEqual(p02["witness_fold_mean_rounded_2dp"], "0.83")

    def test_03_p03_dual_checker_identities_and_reversal_boundary(self) -> None:
        p03 = self.report["p03_treatment_sequence_identities"]
        self.assertTrue(p03["dual_checker_distinct_alpha_skeleton"])
        self.assertEqual(p03["parameter_tuples_dual_verified"], 3375)
        self.assertEqual(p03["reference_90_10_resistant_fraction"], "10/19")

    def test_04_ast_auditor_rejects_float_division_and_alpha_renamed_tautology(self) -> None:
        with self.assertRaises(ValueError):
            afs.alpha_skeleton_sha256("def eval_regimes(x, y):\n    return x / y\n")
        skel_a = afs.alpha_skeleton_sha256("def f(a, b):\n    return a + b\n")
        skel_b = afs.alpha_skeleton_sha256("def g(u, v):\n    return u + v\n")
        self.assertEqual(skel_a, skel_b)

    def test_05_independent_bundle_verifier_passes_and_rejects_tampered_witness(self) -> None:
        verify_script = ROOT / "results/formal-synthesis-2026-11-13/verify.py"
        completed = subprocess.run(
            [sys.executable, str(verify_script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

        # Negative control: tie injection into C20 witness must be caught by independent verifier
        spec = importlib.util.spec_from_file_location("formal_synthesis_verify", verify_script)
        self.assertIsNotNone(spec)
        assert spec is not None and spec.loader is not None
        bundle_verify = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bundle_verify)

        tampered = copy.deepcopy(self.report)
        tampered["p02_c20_fold_vs_pooled_auc"]["witness_folds"][0]["positives_num_1e6"][0] = (
            tampered["p02_c20_fold_vs_pooled_auc"]["witness_folds"][0]["negatives_num_1e6"][0]
        )
        with self.assertRaises(AssertionError):
            bundle_verify.check_p02_witness_independent(tampered)

        # Boundary check on P03 exact inequality: at equality tau_2 == g * min(T0, tau_1), after_R == before_R (not <)
        s0, r0 = Fraction(90), Fraction(10)
        a, b = Fraction(1, 10), Fraction(1)
        tau1 = Fraction(10)
        g = (a * s0 + b * r0) / (s0 + r0)  # 19/100
        tau2_eq = g * min(s0 + r0, tau1)   # 19/10
        spec_ns: dict[str, object] = {}
        exec(afs.SPEC_SEQUENCE_CHECKER, spec_ns)
        before, after, _, _ = spec_ns["eval_regimes"](
            (90, 1), (10, 1), (1, 10), (1, 1), (10, 1), (tau2_eq.numerator, tau2_eq.denominator)
        )
        self.assertEqual(Fraction(*after[1]), Fraction(*before[1]))


if __name__ == "__main__":
    unittest.main()
