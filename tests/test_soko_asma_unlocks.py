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
        self.assertEqual(sticky["final_walls"], 2)
        self.assertFalse(sticky["survives_true_crushing_gate"])
        self.assertEqual(sticky["crushed_at_step_on_true_gate"], 3)
        self.assertEqual(true_gate["optimal_steps"], 8)
        self.assertEqual(true_gate["final_walls"], 9)
        self.assertTrue(true_gate["survives_true_crushing_gate"])
        self.assertEqual(somatic["optimal_steps"], 2)

    def test_clonal_schedule_sticky_mirage_vs_wall_transmutation(self) -> None:
        sticky_mono = v.solve_clonal_schedule(sticky_gate=True, allow_wall_transmutation=False)
        true_mono = v.solve_clonal_schedule(sticky_gate=False, allow_wall_transmutation=False)
        true_wall = v.solve_clonal_schedule(sticky_gate=False, allow_wall_transmutation=True)
        self.assertEqual(sticky_mono["optimal_steps"], 4)
        self.assertIsNone(true_mono["optimal_steps"])
        self.assertEqual(true_wall["optimal_steps"], 5)

    def test_ms2_causal_rung_conservation_rejects_dipeptide_swap_chimera(self) -> None:
        res = v.evaluate_ms2_static_vs_causal()
        self.assertEqual(res["intensity_bytes_retained"], 0)
        self.assertEqual(res["true_target_candidate"]["static_p01_flow"], 11)
        self.assertEqual(res["dipeptide_swap_chimera_decoy"]["static_p01_flow"], 11)
        self.assertEqual(res["true_target_candidate"]["causal_p01_plus_flow"], 11)
        self.assertEqual(res["dipeptide_swap_chimera_decoy"]["causal_p01_plus_flow"], 8)
        self.assertEqual(res["dipeptide_swap_chimera_decoy"]["cnf_blocked_orphan_losses"], 1)

    def test_floating_rs_continuum_impossibility_and_cures(self) -> None:
        res = v.verify_floating_rs_continuum_impossibility()
        self.assertEqual(res["pinned_s16_lh_bounds"]["legacy_1_10_2_5_C25"], "3/448")
        self.assertEqual(res["pinned_s16_lh_bounds"]["optimal_1_20_3_8_C25"], "10179/563920")
        imp = res["floating_rs_impossibility_on_1_20_to_1"]
        self.assertTrue(imp["algebraic_factorization_verified"])
        self.assertEqual(imp["positivity_quadratic_discriminant"], -10199)
        self.assertTrue(imp["continuum_sup_strictly_below_1_over_60"])
        cure_a = res["cure_a_single_channel_threshold_with_p0_1_5"]
        self.assertEqual(cure_a["at_p_1_25_quadratic_val"], "8/25")
        self.assertLess(cure_a["at_p_1_25_eps_star"], 1.0 / 60.0)
        self.assertEqual(cure_a["at_p_1_26_quadratic_val"], "-135/676")
        self.assertGreater(cure_a["at_p_1_26_eps_star"], 1.0 / 60.0)
        self.assertEqual(res["cure_b_two_channel_farkas_at_p_1_20"]["rs_invariant_eps_star_fraction"], "19/240")


if __name__ == "__main__":
    unittest.main()
