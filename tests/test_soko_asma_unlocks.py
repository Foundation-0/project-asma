#!/usr/bin/env python3
"""Unit tests for synthetic offline Soko-to-Asma phase-transition and floating-r_S verifiers."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import verify_soko_asma_unlocks as v  # noqa: E402


class TestSokoAsmaUnlocks(unittest.TestCase):
    def test_crushing_gate_phase_transition_and_bellman_audit(self) -> None:
        sticky = v.solve_and_audit_scaffold_gate(2, 5, 2, sticky_relaxation=True)
        true_gate = v.solve_and_audit_scaffold_gate(2, 5, 2, sticky_relaxation=False)
        somatic = v.solve_and_audit_scaffold_gate(8, 1, 0, sticky_relaxation=False)
        self.assertEqual(sticky["bellman_violations"], 0)
        self.assertEqual(true_gate["bellman_violations"], 0)
        self.assertEqual(somatic["bellman_violations"], 0)
        self.assertEqual(sticky["optimal_steps"], 3)
        self.assertFalse(sticky["survives_true_crushing_gate"])
        self.assertEqual(true_gate["optimal_steps"], 8)
        self.assertEqual(true_gate["final_walls"], 9)
        self.assertTrue(true_gate["survives_true_crushing_gate"])

    def test_clonal_schedule_sticky_mirage_vs_wall_transmutation(self) -> None:
        self.assertEqual(v.solve_clonal_schedule(sticky_gate=True, allow_wall_transmutation=False)["optimal_steps"], 4)
        self.assertIsNone(v.solve_clonal_schedule(sticky_gate=False, allow_wall_transmutation=False)["optimal_steps"])
        self.assertEqual(v.solve_clonal_schedule(sticky_gate=False, allow_wall_transmutation=True)["optimal_steps"], 5)

    def test_ms2_unlabelled_observable_tiebreak_and_full_chimera_negative_control(self) -> None:
        res = v.evaluate_ms2_static_vs_causal()
        self.assertEqual(res["oracle_flags_used"], 0)
        single = res["single_sided_interferent_spectrum"]
        self.assertEqual(single["true_target_candidate"]["static_p01_flow"], 10)
        self.assertEqual(single["dipeptide_swap_decoy"]["static_p01_flow"], 10)
        self.assertEqual(single["true_target_candidate"]["causal_p01_plus_flow"], 10)
        self.assertEqual(single["dipeptide_swap_decoy"]["causal_p01_plus_flow"], 9)
        self.assertTrue(single["separated_by_observable_rung_and_cnf"])
        neg = res["full_complementary_chimera_negative_control"]
        self.assertEqual(neg["true_target_candidate"]["causal_p01_plus_flow"], 11)
        self.assertEqual(neg["dipeptide_swap_decoy"]["causal_p01_plus_flow"], 11)
        self.assertTrue(neg["ambiguous_tie_as_expected"])

    def test_floating_rs_continuum_impossibility_and_cures(self) -> None:
        res = v.verify_floating_rs_continuum_impossibility()
        self.assertEqual(res["pinned_s16_lh_bounds"]["optimal_1_20_3_8_C25"], "10179/563920")
        self.assertEqual(res["floating_rs_impossibility_on_1_20_to_1"]["positivity_quadratic_discriminant"], -10199)
        self.assertLess(res["cure_a_single_channel_threshold_with_p0_1_5"]["at_p_1_25_eps_star"], 1.0 / 60.0)
        self.assertGreater(res["cure_a_single_channel_threshold_with_p0_1_5"]["at_p_1_26_eps_star"], 1.0 / 60.0)
        self.assertEqual(res["cure_b_two_channel_farkas_at_p_1_20"]["rs_invariant_eps_star_fraction"], "19/240")


if __name__ == "__main__":
    unittest.main()
