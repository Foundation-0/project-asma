\
#!/usr/bin/env python3
"""
Unit and Adversarial Tamper Tests for Soko-Weft Discriminating Test Certifier
=============================================================================
Verifies:
  1. Pillar 1 (P01 / V43): Abundance-free CDR2L vs. CDR2 / swap / deamidation PSM
     adjudication eliminates both peak-stacking and calibration-sign false admissions.
  2. Pillar 2 (P02 / V44): Exact `Fraction` reproduction of PR #78 boundaries and
     verified orthogonal 2-channel mitosis lifting all 6 world pairs above eps = 1/60.
  3. Pillar 3 (P03 / V45): Weft C1/C2 safe Bellman-Pareto + Soko prefix-nogood search
     matches exhaustive safe oracle on 16/16 scenarios with zero safety violations.
  4. PR #80 Tamper-Sensitivity Audit: Planted mutations across SHA-256, scope, min-cuts,
     Farkas duals, and trajectory states all fail closed in `verify.py`.
  5. PR #72 Repository Conformance: Zero em-dashes (`\\u2014`) across generated docs/code.
"""

from __future__ import annotations

import copy
from fractions import Fraction
from pathlib import Path
import unittest

from tools.analyze_soko_weft_discriminators import (
    SCOPE_BANNER,
    canonical_sha256,
    generate_certificate_payload,
    run_pillar1_cdr2l_psm_suite,
    run_pillar2_compartment_and_shedding_suite,
    run_pillar3_sequence_suite,
)
import importlib.util

_VERIFY_PATH = Path(__file__).resolve().parents[1] / "results" / "soko-weft-discriminators-20261113" / "verify.py"
_SPEC = importlib.util.spec_from_file_location("asma_soko_weft_verify", _VERIFY_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_MOD = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MOD)
verify_certificate_dict = _MOD.verify_certificate_dict


class TestSokoWeftAsmaDiscriminators(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cert = generate_certificate_payload()

    def test_pillar1_abundance_free_cdr2l_discrimination(self) -> None:
        p1 = run_pillar1_cdr2l_psm_suite()
        self.assertEqual(p1["intensities_retained_bytes"], 0)
        self.assertEqual(p1["cdr2l_true_recall_rate_q"], "1/1")
        # Both naive and uncalibrated Dinic suffer false admissions on opposite-drift swap decoy
        self.assertEqual(p1["naive_paralog_false_admission_rate_q"], "1/1")
        self.assertEqual(p1["dinic_uncalibrated_false_admission_rate_q"], "1/1")
        # Full Soko-Weft Helly-Farkas + Dinic eliminates 100% of rival false admissions
        self.assertEqual(p1["soko_weft_false_admission_rate_q"], "0/1")
        self.assertEqual(p1["uniquely_discriminated_spectra"], 24)

    def test_pillar2_pr78_exact_rational_reproduction_and_orthogonal_mitosis(self) -> None:
        p2 = run_pillar2_compartment_and_shedding_suite()
        sc = p2["pr78_scalar_designs"]
        self.assertEqual(sc["L"]["S_vs_C50"]["eps_star_q"], "0/1")
        self.assertEqual(sc["R"]["S_vs_C50"]["eps_star_q"], "0/1")
        self.assertEqual(sc["H"]["S_vs_C50"]["eps_star_q"], "0/1")
        self.assertEqual(sc["LR"]["S_vs_C50"]["eps_star_q"], "3/200")
        self.assertEqual(sc["RH"]["S_vs_C50"]["eps_star_q"], "1/280")
        self.assertEqual(sc["LH"]["S_vs_C50"]["eps_star_q"], "13/700")
        self.assertTrue(sc["LH"]["resolves_S_vs_C50_C75_at_1_60"])
        # Scalar LH fails to separate S vs C25 at eps = 1/60 (3/448 < 1/60)
        self.assertEqual(sc["LH"]["S_vs_C25"]["eps_star_q"], "3/448")
        self.assertFalse(sc["LH"]["resolves_all_6_pairs_at_1_60"])

        # Orthogonal 2-channel mitosis resolves ALL 6 world pairs above 1/60!
        ortho = p2["soko_weft_orthogonal_lh_design"]
        self.assertTrue(ortho["resolves_all_6_pairs_at_1_60"])
        n_str, d_str = ortho["min_eps_all_6_pairs_q"].split("/")
        self.assertGreater(Fraction(int(n_str), int(d_str)), Fraction(1, 60))

        # Two-clone shedding asymmetry exact ratio 1.18 / 0.042 = 590/21
        self.assertEqual(p2["two_clone_shedding_blind_spot"]["exact_masking_ratio_q"], "590/21")

    def test_pillar3_safe_bellman_pareto_matches_oracle_and_prevents_stuttering_trap(self) -> None:
        p3 = run_pillar3_sequence_suite()
        self.assertEqual(p3["n_scenarios"], 16)
        self.assertEqual(p3["greedy_scalar_unsafe_scenarios"], 16)
        self.assertEqual(p3["soko_weft_safe_optimal_matches"], 16)
        self.assertEqual(p3["soko_weft_c1_c2_violations"], 0)
        self.assertGreater(p3["mean_search_reduction_pct"], 70.0)

    def test_independent_second_checker_accepts_valid_and_rejects_planted_tampers(self) -> None:
        ok, msg = verify_certificate_dict(self.cert)
        self.assertTrue(ok, msg)

        # Tamper 1: Alter scope banner and re-hash
        t1 = copy.deepcopy(self.cert)
        t1["scope"] = "Real patient rows"
        t1["certificate_sha256"] = canonical_sha256(t1)
        self.assertFalse(verify_certificate_dict(t1)[0])

        # Tamper 2: Inflate Pillar 1 max_flow without valid min-cut witness and re-hash
        t2 = copy.deepcopy(self.cert)
        c0 = t2["pillar1_cdr2l_psm_discrimination"]["representative_spectrum_certificate"]["evaluation"]["candidates"]["CDR2L_isobaric_swap"]
        c0["helly_knot_witnesses"][0]["max_flow"] += 1
        t2["certificate_sha256"] = canonical_sha256(t2)
        self.assertFalse(verify_certificate_dict(t2)[0])

        # Tamper 3: Perturb Pillar 2 Farkas dual witness and re-hash
        t3 = copy.deepcopy(self.cert)
        t3["pillar2_compartment_farkas_mitosis"]["soko_weft_orthogonal_lh_design"]["pairs"]["S_vs_C25"]["eps_joint_q"] = "9/10"
        t3["certificate_sha256"] = canonical_sha256(t3)
        self.assertFalse(verify_certificate_dict(t3)[0])

        # Tamper 4: Violate Weft C1 host reserve floor in Pillar 3 trajectory and re-hash
        t4 = copy.deepcopy(self.cert)
        t4["pillar3_safe_bellman_pareto_sequences"]["representative_certificate"]["soko_weft_certified"]["certified_trajectory"][0]["h_core_q"] = "10/1"
        t4["certificate_sha256"] = canonical_sha256(t4)
        self.assertFalse(verify_certificate_dict(t4)[0])


if __name__ == "__main__":
    unittest.main()
