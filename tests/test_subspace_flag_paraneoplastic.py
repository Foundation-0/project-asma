"""Unit tests for Subspace-Flag Paraneoplastic Gates, C15 Monoid Collapse, and N=1 Calibration."""

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
    verify_c15_monoid_and_flag,
    verify_paraneoplastic_cascade_gate,
    verify_prospective_n1_batch_nullspace,
)


class TestSubspaceFlagParaneoplastic(unittest.TestCase):
    def test_c15_monoid_collapse_and_three_stage_flag_recovery(self) -> None:
        res = verify_c15_monoid_and_flag()
        self.assertEqual(res["monoid_collision_worlds_verified"], 3)
        self.assertEqual(res["recovered_coexisting_world"], ["11", "1/7", "1/8"])
        self.assertEqual(res["c25_critical_paralog_bleed_fraction"], "2341/30537")
        self.assertEqual(demorgan_combine(Fraction(1, 7), Fraction(1, 8)), Fraction(1, 4))
        y0 = survival_three_pathway(Fraction(0, 1), Fraction(11, 1), Fraction(0, 1), Fraction(1, 8))
        y1 = survival_three_pathway(Fraction(0, 1), Fraction(11, 1), Fraction(1, 7), Fraction(1, 8))
        y2 = survival_three_pathway(Fraction(1, 20), Fraction(11, 1), Fraction(1, 7), Fraction(1, 8))
        self.assertEqual(
            recover_three_pathway_via_flag(y0, y1, Fraction(1, 20), y2),
            (Fraction(11, 1), Fraction(1, 7), Fraction(1, 8)),
        )

    def test_paraneoplastic_cascade_neurotoxicity_and_adjoint_gate(self) -> None:
        res = verify_paraneoplastic_cascade_gate()
        self.assertEqual(res["purkinje_injury_single_stage_1"], 0)
        self.assertEqual(res["purkinje_injury_single_stage_2"], 0)
        self.assertGreater(res["purkinje_injury_forward_ungated_at_b100"], 0)
        self.assertEqual(res["purkinje_injury_forward_adjoint_gated_at_b100"], 0)
        self.assertEqual(
            res["residual_tumor_pct_forward_adjoint_gated"],
            res["residual_tumor_pct_forward_ungated"],
        )
        self.assertLess(
            res["residual_tumor_pct_forward_adjoint_gated"],
            res["residual_tumor_pct_reversed"],
        )

    def test_prospective_n1_batch_nullspace_recovers_oracle_auroc_zero_drift(self) -> None:
        res = verify_prospective_n1_batch_nullspace(n_reps=16)
        self.assertEqual(res["total_pairs"], 4316)
        self.assertEqual(res["auroc_midrank_prospective_n1_mean"], 0.5)
        self.assertLess(float(res["max_logit_drift_under_batch_shift"]), 1e-11)
        self.assertAlmostEqual(
            float(res["auroc_nullspace_gate_prospective_n1_mean"]),
            float(res["auroc_clean_oracle_mean"]),
            places=12,
        )
        self.assertGreater(
            float(res["auroc_nullspace_gate_prospective_n1_mean"]),
            float(res["auroc_raw_pooled_shifted_mean"]) + 0.08,
        )
        self.assertGreater(
            float(res["auroc_nullspace_gate_prospective_n1_mean"]),
            float(res["auroc_midrank_batch27_mean"]) + 0.04,
        )


ifif __name__ == "__main__":
__name__ == "__main__":
    unittest.main()
