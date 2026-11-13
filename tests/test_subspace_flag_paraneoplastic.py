"""Unit tests across all five Project Asma verification paths."""

from __future__ import annotations

import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.verify_subspace_flag_paraneoplastic import (  # noqa: E402
    demorgan_combine,
    recover_three_pathway_via_flag,
    survival_three_pathway,
    verify_c15_monoid_and_offset_saturation,
    verify_cdr2l_mhc2_core_bifurcation,
    verify_paraneoplastic_cascade_gate,
    verify_prospective_n1_and_c22_power,
    verify_soko_ilp_minimal_assays,
)


class TestSubspaceFlagParaneoplastic(unittest.TestCase):
    def test_cdr2l_mhc2_core_bifurcation_and_pf27644_localization(self) -> None:
        res = verify_cdr2l_mhc2_core_bifurcation()
        self.assertEqual(res["cdr2l_432_446_peptide"], "SQPEYKALFKEIFSR")
        self.assertEqual(res["cdr2l_445_464_peptide"], "SRIQKTKADINATKVKTHSS")
        self.assertEqual(res["ep1_exact_9_of_9_cdr2_cores"], 4)
        self.assertEqual(res["ep2_max_9mer_identity_with_cdr2"], 5)
        self.assertEqual(res["pf27644_dual_localization_prob"], "493/100573")

    def test_c15_monoid_flag_and_offset_saturation_optimum(self) -> None:
        res = verify_c15_monoid_and_offset_saturation()
        self.assertEqual(res["monoid_collision_worlds_verified"], 3)
        self.assertEqual(res["recovered_coexisting_world"], ["11", "1/7", "1/8"])
        self.assertEqual(res["c25_critical_paralog_bleed_fraction"], "2341/30537")
        self.assertEqual(res["all4_bound_2pct_seed"], "152579/4189120")
        self.assertEqual(res["all4_bound_0pct_supremum"], "3/40")
        self.assertEqual(demorgan_combine(Fraction(1, 7), Fraction(1, 8)), Fraction(1, 4))
        y0 = survival_three_pathway(Fraction(0, 1), Fraction(11, 1), Fraction(0, 1), Fraction(1, 8))
        y1 = survival_three_pathway(Fraction(0, 1), Fraction(11, 1), Fraction(1, 7), Fraction(1, 8))
        y2 = survival_three_pathway(Fraction(1, 20), Fraction(11, 1), Fraction(1, 7), Fraction(1, 8))
        self.assertEqual(
            recover_three_pathway_via_flag(y0, y1, Fraction(1, 20), y2),
            (Fraction(11, 1), Fraction(1, 7), Fraction(1, 8)),
        )

    def test_soko_ilp_minimal_three_assay_discriminator(self) -> None:
        res = verify_soko_ilp_minimal_assays()
        self.assertEqual(res["minimal_assay_cardinality"], 3)
        self.assertIn(
            ["A0_Bulk_LH", "A2_APC_Intact_p0", "A3_Orth_445_464_Tetramer"],
            res["optimal_three_assay_sets"],
        )

    def test_paraneoplastic_cascade_neurotoxicity_and_adjoint_gate(self) -> None:
        res = verify_paraneoplastic_cascade_gate()
        self.assertEqual(res["purkinje_injury_single_stage_1"], 0)
        self.assertEqual(res["purkinje_injury_single_stage_2"], 0)
        self.assertGreater(res["purkinje_injury_forward_ungated_at_b100"], 0)
        self.assertEqual(res["purkinje_injury_forward_adjoint_gated_at_b100"], 0)
        self.assertLess(
            res["residual_tumor_pct_forward_adjoint_gated"],
            res["residual_tumor_pct_reversed"],
        )

    def test_prospective_n1_and_c22_exact_power_recovery(self) -> None:
        res = verify_prospective_n1_and_c22_power(n_reps=16, c22_trials=300)
        self.assertEqual(res["total_pairs"], 4316)
        self.assertEqual(res["c22_exact_p_u_ge_76"], "302/6783")
        self.assertEqual(res["auroc_midrank_prospective_n1_mean"], 0.5)
        self.assertLess(float(res["max_logit_drift_under_batch_shift"]), 1e-11)
        self.assertAlmostEqual(
            float(res["auroc_nullspace_gate_prospective_n1_mean"]),
            float(res["auroc_clean_oracle_mean"]),
            places=12,
        )
        self.assertGreater(
            float(res["c22_power_nullspace_n1"]),
            float(res["c22_power_raw_shifted"]) + 0.20,
        )


if __name__ == "__main__":
    unittest.main()
