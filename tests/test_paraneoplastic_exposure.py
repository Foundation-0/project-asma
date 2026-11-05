"""Hand-derived values, independent recomputation and artifact replay."""
from fractions import Fraction as F
import importlib.util
from itertools import permutations
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("exposure", ROOT / "tools/analyze_paraneoplastic_exposure.py")
exposure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exposure)
RESULT = exposure.build_result()


def schedule(position, q, a, cycles=6):
    ops = [("chemo", a)] * cycles
    ops.insert(position, ("surgery", q))
    return ops


class ParaneoplasticExposureTests(unittest.TestCase):
    def test_worked_example_by_hand(self):
        # Surgery first: 10 held, then 10*(1/2)^k for k=1..6 -> 10*(127/64).
        early = exposure.run_schedule(100, schedule(0, F(1, 10), F(1, 2)))
        late = exposure.run_schedule(100, schedule(3, F(1, 10), F(1, 2)))
        self.assertEqual(early["final"], late["final"])
        self.assertEqual(early["final"], F(5, 32))
        self.assertEqual(early["burden_auc"], F(635, 32))
        self.assertEqual(late["burden_auc"], F(50) + 25 + F(25, 2) + F(5, 4) + F(5, 8) + F(5, 16) + F(5, 32))
        self.assertEqual(late["burden_auc"] - early["burden_auc"], 70)
        self.assertEqual(early["killed_in_body"], F(315, 32))
        self.assertEqual(late["killed_in_body"], F(2835, 32))
        worked = RESULT["A_worked_order_comparison"]
        self.assertEqual(worked["effective_surgery"]["burden_driven"]["cumulative_hazard_difference_late_minus_early"], "7/5")
        self.assertEqual(worked["effective_surgery"]["death_driven"]["cumulative_hazard_difference_late_minus_early"], "63/40")
        self.assertEqual(worked["less_effective_surgery"]["burden_driven"]["cumulative_hazard_difference_late_minus_early"], "-7/8")
        self.assertEqual(worked["less_effective_surgery"]["death_driven"]["cumulative_hazard_difference_late_minus_early"], "7/16")
        for case in worked.values():
            self.assertTrue(case["tumor_endpoint_equal"])
            for hypothesis in ("burden_driven", "death_driven"):
                self.assertTrue(case[hypothesis]["identity_holds"])

    def test_adjacent_position_and_mass_balance_formulas(self):
        for q in (F(0), F(1, 3), F(1)):
            for a in (F(1, 7), F(2, 3), F(1)):
                runs = [exposure.run_schedule(F(9), schedule(p, q, a, 4)) for p in range(5)]
                for p in range(4):
                    self.assertEqual(runs[p + 1]["burden_auc"] - runs[p]["burden_auc"], 9 * a ** p * (a - q))
                    self.assertEqual(runs[p + 1]["killed_in_body"] - runs[p]["killed_in_body"],
                                     9 * a ** p * (1 - a) * (1 - q))
                for run in runs:
                    self.assertEqual(run["killed_in_body"], 9 - run["final"] - run["removed_surgically"])
        grid = RESULT["A_surgery_position_grid"]
        self.assertEqual(grid["cases"], 30)
        for key in ("endpoint_invariant", "mass_balance_holds", "adjacent_step_formula_holds"):
            self.assertEqual(grid[key], 30)
        # Disagreement occurs exactly when surgery removes something (q < 1) but retains
        # more than one cycle (q > a). With q = 1 release is position-independent.
        expected = sum(F(r["chemo_keep"]) < F(r["surgery_keep"]) < 1 for r in grid["rows"])
        self.assertEqual(grid["hypotheses_disagree_on_best_position"], expected)
        self.assertEqual(expected, 6)

    def test_most_effective_first_by_independent_enumeration(self):
        keeps = (F(3, 4), F(1, 10), F(1, 2), F(1, 4))
        intervals = (F(2), F(1, 2), F(5), F(1))
        def auc(order):
            level, total = F(100), F(0)
            for keep, dt in zip(order, intervals):
                level *= keep
                total += level * dt
            return total
        self.assertEqual(min(auc(o) for o in permutations(keeps)), auc(sorted(keeps)))
        self.assertTrue(all(row["ascending_is_minimum"] for row in RESULT["A_exchange_checks"]))
        mixture = RESULT["A_mixed_presentation_criterion"]
        self.assertEqual(mixture["cases"], 150)
        self.assertEqual(mixture["best_position_is_first_or_last"], 150)
        self.assertEqual(mixture["criterion_predicts_first"], 150)

    def test_discrete_exposure_identity(self):
        drive = [F(3), F(0), F(7, 2), F(1, 9)]
        sums = exposure.effector_sums(drive, F(2, 5), F(3, 7), F(1, 3))
        self.assertEqual(sums["total_sum"], sums["identity_total"])
        # Independent loop with an explicit long tail and its exact geometric remainder.
        e, total = F(1, 3), F(0)
        for u in drive + [0] * 40:
            total += e
            e = F(2, 5) * e + F(3, 7) * u
        self.assertEqual(total + e / (1 - F(2, 5)), sums["identity_total"])

    def test_state_and_rate(self):
        b = RESULT["B_state_versus_rate"]
        self.assertEqual(b["deficit_at_visits_ended"], b["deficit_at_visits_ongoing"])
        self.assertEqual(b["marker_at_second_visit_ended"], "3/80")
        self.assertEqual(b["marker_at_second_visit_ongoing"], "9/64")
        self.assertEqual(b["marker_ratio_ongoing_to_ended"], "15/4")
        low, high = RESULT["B_intensity_needs_state_and_rate"]
        self.assertEqual(low["loss_rate"], high["loss_rate"])
        self.assertEqual(F(high["per_capita_hazard"]) / F(low["per_capita_hazard"]), 18)

    def test_aggregate_marker_counterexample(self):
        c = RESULT["C_aggregate_marker_counterexample"]
        self.assertLess(F(c["marker_after"]), F(c["marker_before"]))
        self.assertGreater(F(c["drive_after"]), F(c["drive_before"]))
        self.assertTrue(RESULT["C_opposed_sign_iff_not_nonnegative_multiple_on_grid"])

    def test_regimes_and_committed_bound(self):
        d = RESULT["D_regimes_after_antigen_removal"]
        driven, autonomous = d["antigen_driven"], d["autonomous_cns"]
        self.assertTrue(driven["committed_bound_exact"])
        self.assertEqual(driven["committed_hazard_bound"], "7/50")
        self.assertGreater(F(autonomous["late_to_early_loss_ratio"]), 50 * F(driven["late_to_early_loss_ratio"]))

    def test_no_rise_theorem_and_release_signature(self):
        s = RESULT["D_steady_state_signature"]
        self.assertEqual(s["cases"], 72)
        self.assertEqual(s["burden_driven_never_rises"], 72)
        self.assertEqual(s["death_driven_rises_after_surgery"], 0)
        self.assertEqual(s["death_driven_rises_after_first_chemo_from_steady_state"], s["chemo_first_cases"])
        self.assertEqual((s["chemo_first_cases"], s["surgery_first_cases"]), (54, 18))
        self.assertEqual(s["death_driven_rises_after_first_chemo_following_surgery"], 15)
        # From steady state the first cycle rises iff (1-a)(1-d) > 0.
        for a in (F(0), F(1, 3), F(1)):
            for d in (F(0), F(1, 2), F(1)):
                h = exposure.presentation_hazards(F(10), [("chemo", a)], d, True, F(1, 2), F(1), F(1, 100))
                self.assertEqual(h[1] > h[0], (1 - a) * (1 - d) > 0)

    def test_invalid_inputs_rejected(self):
        for bad in (True, -1, 0.5, "1"):
            with self.assertRaises(ValueError):
                exposure.run_schedule(bad, [("chemo", F(1, 2))])
        with self.assertRaises(ValueError):
            exposure.run_schedule(1, [("chemo", 2)])
        with self.assertRaises(ValueError):
            exposure.run_schedule(1, [("radiation", F(1, 2))])
        with self.assertRaises(ValueError):
            exposure.run_schedule(1, [])
        with self.assertRaises(ValueError):
            exposure.effector_sums([1], 1, 1)
        with self.assertRaises(ValueError):
            exposure.regime_trajectory([F(500)], 1, F(1, 2), F(1), F(1), F(0), F(0), F(0))

    def test_committed_artifact_matches(self):
        self.assertEqual(RESULT, json.loads((ROOT / exposure.OUTPUT).read_text()))


if __name__ == "__main__":
    unittest.main()
