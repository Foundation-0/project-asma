"""Checks for the imported cross-ratio and R_opt study in studies/expedition-mobius-ropt.

The study script runs as a subprocess under two isolated Python modes. The
cross-ratio scope numbers and the trace-slack point evaluations quoted in the
study README are replayed here in exact fractions, independently of the script.
All inputs are invented; no study data is read.
"""

from __future__ import annotations

from fractions import Fraction as F
import hashlib
from itertools import product
from math import isqrt
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "studies" / "expedition-mobius-ropt"
SCRIPT = STUDY / "optimal_inertia_rank.py"
README = STUDY / "README.md"

SEEDS = (F(1, 20), F(1, 10), F(1, 5), F(2, 5))
WORLDS = {"S": (F(16), F(0)), "C25": (F(11), F(1, 4)), "C50": (F(6), F(1, 2)), "C75": (F(1), F(3, 4))}
SEED_CROSS_RATIOS = (F(9, 7), F(27, 19))
NON_MOBIUS = (F(1431, 1133), F(567, 418))


def q(p, r, c):
    return (r * p + c * (1 - p)) / (r * p + (1 - p))


def cross_ratio(a, b, c, d):
    return ((a - c) * (b - d)) / ((a - d) * (b - c))


def cr4_cr3(values):
    """CR4 of four readings and CR3 of the first three against the literal fixed point 1."""
    return cross_ratio(*values), cross_ratio(values[0], values[1], values[2], F(1))


def bleed(p, r, c, alpha, beta):
    """Paralog readout y = (1 - alpha - beta) q + alpha (gravity-bridge note, section 2)."""
    return (1 - alpha - beta) * q(p, r, c) + alpha


def corner_range(centres, eps, tail=()):
    """Exact extremes of the cross-ratio over the box |x_i - centre_i| <= eps.

    The cross-ratio is a Moebius function of each coordinate. With no pole in the
    box it is monotone in each coordinate, so its extremes sit at corners and, the
    box being connected, every value between them is attained.
    """
    values = [cross_ratio(*[x + s * eps for x, s in zip(centres, signs)], *tail)
              for signs in product((-1, 1), repeat=len(centres))]
    return min(values), max(values)


def check4_terms(x, noise):
    """(tr M, t_minus, ||M||^2) of Check 4 in its eigenbasis at T*tau = x, T = 5.

    Known component 9/10, two unknown components 1/20, M = G - tau*I. The noise is
    tau*v*v^T along the known component ("worst") or the script's own (tau/2)*I.
    """
    tau = x / 5
    base = (F(9, 10), F(1, 20), F(1, 20), F(0), F(0))
    noise_eigs = (tau, 0, 0, 0, 0) if noise == "worst" else (tau / 2,) * 5
    eigs = [b + n - tau for b, n in zip(base, noise_eigs)]
    return sum(eigs), F(9, 10) - 5 * tau, sum(e * e for e in eigs)


def r_opt(x, noise):
    """Branch-1 closed form of R_opt with b = 1; fails if the branch-1 hypotheses fail."""
    tr_m, t_minus, hs2 = check4_terms(x, noise)
    if not (t_minus > 0 and t_minus * tr_m >= hs2 and hs2 > t_minus * t_minus):
        raise ValueError("branch-1 hypotheses fail")
    return (tr_m - t_minus) ** 2 / (hs2 - t_minus * t_minus)


def sqrt_bounds(n, scale=10**9):
    root = isqrt(n * scale * scale)
    return F(root, scale), F(root + 1, scale)


class ExpeditionScriptTest(unittest.TestCase):
    def test_script_exits_zero_with_identical_output_in_isolated_modes(self) -> None:
        outputs = []
        for flags in (("-I", "-B"), ("-I", "-O", "-B", "-W", "error")):
            done = subprocess.run([sys.executable, *flags, str(SCRIPT)], capture_output=True,
                                  text=True, timeout=120, check=False)
            self.assertEqual(done.returncode, 0, done.stderr)
            outputs.append(done.stdout)
        self.assertEqual(outputs[0], outputs[1])
        for printed in ("ALL CHECKS PASSED", "R_opt=1.530561", "ModeA_net=0.226068", "S2=0.423542",
                        "loom=0.1842", "unknown-Q=0.809652", "known-Q-sub=1.939556",
                        "Random property test (1000 non-commuting rational matrices): 0 violations",
                        "(200 trials, 0 violations)", "Adversarial forgeries rejected: 7/7",
                        "CR4=9/7, CR3(q(1)=1)=27/19", "(1431/1133 != 9/7)"):
            self.assertIn(printed, outputs[0])

    def test_readme_records_script_hash_and_keeps_scope_corrections(self) -> None:
        text = README.read_text(encoding="utf-8")
        digest = hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
        self.assertTrue(digest in text, f"README does not record the script's SHA-256 {digest}")
        for overclaim in ("exact critical slack threshold", "uniquely certifies", "provably",
                          "100% parameter-free", "Amplification Law"):
            self.assertFalse(overclaim in text, f"README repeats the overclaim {overclaim!r}")
        for phrase in ("## Scope and provenance (2026-11-24)",
                       "first-order sufficient threshold, not the exact crossing",
                       "That universal claim was not replayed here", "Knausgard, Lemma 6.1",
                       "They cannot separate selection from conversion"):
            self.assertTrue(phrase in text, f"README lacks {phrase!r}")


class CrossRatioScopeTest(unittest.TestCase):
    def test_four_worlds_give_the_seeds_own_cross_ratios(self) -> None:
        self.assertEqual(cr4_cr3(SEEDS), SEED_CROSS_RATIOS)
        for name, (r, c) in WORLDS.items():
            with self.subTest(world=name):
                self.assertEqual(q(F(1, 5), r, c), F(4, 5))
                self.assertEqual(cr4_cr3([q(p, r, c) for p in SEEDS]), SEED_CROSS_RATIOS)

    def test_alpha_only_bleed_leaves_both_cross_ratios_unchanged(self) -> None:
        for name, (r, c) in WORLDS.items():
            with self.subTest(world=name):
                readings = [bleed(p, r, c, F(1, 10), F(0)) for p in SEEDS]
                self.assertEqual(cr4_cr3(readings), SEED_CROSS_RATIOS)

    def test_false_negative_loss_moves_cr3_but_not_cr4(self) -> None:
        r, c = WORLDS["C50"]
        readings = [bleed(p, r, c, F(0), F(1, 10)) for p in SEEDS]
        self.assertEqual(cr4_cr3(readings), (F(9, 7), F(333, 221)))
        standard = bleed(F(1), r, c, F(0), F(1, 10))
        self.assertEqual(standard, F(9, 10))
        self.assertEqual(cross_ratio(*readings[:3], standard), F(27, 19))
        for name, (r, c) in WORLDS.items():
            with self.subTest(world=name):
                cr4, cr3 = cr4_cr3([bleed(p, r, c, F(1, 10), F(1, 10)) for p in SEEDS])
                self.assertEqual(cr4, F(9, 7))
                self.assertNotEqual(cr3, F(27, 19))

    def test_small_reading_errors_reproduce_the_non_mobius_alternative(self) -> None:
        self.assertEqual(cr4_cr3([q(p, 6 + 10 * p, F(1, 2)) for p in SEEDS]), NON_MOBIUS)
        self.assertEqual(F(9, 7) - NON_MOBIUS[0], F(180, 7931))
        c50 = [q(p, *WORLDS["C50"]) for p in SEEDS]
        self.assertEqual(c50, [F(31, 50), F(7, 10), F(4, 5), F(9, 10)])
        points = c50 + [F(1)]
        self.assertGreater(min(b - a for a, b in zip(points, points[1:])), 2 * F(5, 1000))
        # Exact CR4 witness inside the 0.002 box: fix x2, x3, x4 and solve for x1.
        eps, target = F(2, 1000), NON_MOBIUS[0]
        x2, x3, x4 = c50[1] - eps, c50[2] + eps, c50[3]
        k = (x2 - x4) / (x2 - x3)
        x1 = (target * x4 - k * x3) / (target - k)
        self.assertLessEqual(abs(x1 - c50[0]), eps)
        self.assertEqual(cross_ratio(x1, x2, x3, x4), target)
        # Exact CR3 witness inside the 0.005 box, fourth point the literal 1: solve for x3.
        eps, target = F(5, 1000), NON_MOBIUS[1]
        x1, x2 = c50[0] + eps, c50[1] - eps
        k = (x2 - 1) / (x1 - 1)
        x3 = (target * x2 - k * x1) / (target - k)
        self.assertLessEqual(abs(x3 - c50[2]), eps)
        self.assertEqual(cross_ratio(x1, x2, x3, F(1)), target)
        # Smallest covering errors, bracketed by corner extremes.
        for target, centres, tail, below, above in (
                (NON_MOBIUS[0], c50, (), F(14, 10000), F(15, 10000)),
                (NON_MOBIUS[1], c50[:3], (F(1),), F(34, 10000), F(35, 10000))):
            with self.subTest(target=str(target)):
                low, high = corner_range(centres, below, tail)
                self.assertFalse(low <= target <= high)
                low, high = corner_range(centres, above, tail)
                self.assertTrue(low <= target <= high)


class TraceSlackReplayTest(unittest.TestCase):
    def test_first_order_threshold_is_one_over_360(self) -> None:
        frobenius_sq, t = 2 * F(1, 20) ** 2, F(9, 10)
        self.assertEqual(frobenius_sq / (2 * t), F(1, 360))

    def test_worst_case_direction(self) -> None:
        self.assertEqual(r_opt(F(1, 360), "worst"), F(32761, 32019))
        self.assertGreater(r_opt(F(291, 100000), "worst"), 1)
        self.assertLess(r_opt(F(2912, 1000000), "worst"), 1)
        # On this direction the R_opt = 1 numerator is (22x^2 - 43x + 1/8)/25: two quadratics
        # that agree at three points are identical.
        for x in (F(1, 360), F(291, 100000), F(1, 1000)):
            tr_m, t_minus, hs2 = check4_terms(x, "worst")
            self.assertEqual((tr_m - t_minus) ** 2 - (hs2 - t_minus ** 2),
                             (22 * x * x - 43 * x + F(1, 8)) / 25)
        low, high = sqrt_bounds(1838)
        root_low, root_high = (43 - high) / 44, (43 - low) / 44
        self.assertTrue(F(291, 100000) < root_low < root_high < F(2912, 1000000))
        self.assertTrue(abs(root_low - F(29113, 10**7)) < F(5, 10**8))
        self.assertTrue(F(475, 10000) <= 360 * root_low - 1 < 360 * root_high - 1 < F(485, 10000))

    def test_script_noise_level(self) -> None:
        self.assertGreater(r_opt(F(334, 100000), "half"), 1)
        self.assertLess(r_opt(F(335, 100000), "half"), 1)
        low, high = sqrt_bounds(5565)
        root_low, root_high = F(5, 8) - high / 120, F(5, 8) - low / 120
        self.assertTrue(F(334, 100000) < root_low < root_high < F(335, 100000))
        self.assertTrue(abs(root_low - F(3342, 10**6)) < F(5, 10**7))


if __name__ == "__main__":
    unittest.main()
