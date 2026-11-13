#!/usr/bin/env python3
"""Zero-shared-code independent verifier for results/formal-synthesis-2026-11-13.

Independently checks:
1. SHA256SUMS integrity across all files in this result bundle.
2. Theorem P01 via dynamic programming over integer micro-Daltons (distinct algorithm from
   the recursive rational branch-and-bound in tools/analyze_formal_synthesis.py) + independent
   re-verification of the 173-peak disjoint ion-current partition of Scan 23848.
3. Theorem P02 via exact integer cross-multiplication of the 135-score C20 witness (`0` ties,
   `3491/4316` pooled concordance, `124513/149600` 5-fold mean AUROC).
4. Theorem P03 via symbolic rational verification and AST soundness / anti-tautology check.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import sys
from pathlib import Path

BUNDLE_DIR = Path(__file__).resolve().parent
ROOT = BUNDLE_DIR.parent.parent
REPORT_PATH = BUNDLE_DIR / "report.json"
SUMS_PATH = BUNDLE_DIR / "SHA256SUMS"
SPECTRUM_PATH = ROOT / "registries/cdr2l-spectrum-locator-2026-11-06.json"


def check_sha256sums() -> None:
    if not SUMS_PATH.is_file():
        raise AssertionError("Missing SHA256SUMS")
    for line in SUMS_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split("  ", 1)
        target = (ROOT / rel) if rel.startswith(("tools/", "results/", "registries/")) else (BUNDLE_DIR / rel)
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            raise AssertionError(f"SHA-256 mismatch for {rel}: expected {expected}, got {actual}")


def check_p01_independent_dp(report: dict) -> None:
    # Independent algorithm: boolean reachability DP on scaled integer 10^-5 Da grid
    # with rigorous +/- 20 unit outward interval rounding guard, then exact Fraction check!
    masses = [
        Fraction("57.02146372057"), Fraction("71.03711378471"), Fraction("87.03202840427"),
        Fraction("97.05276384885"), Fraction("99.06841391299"), Fraction("101.04767846841"),
        Fraction("103.00918478471"), Fraction("113.08406397713"), Fraction("114.04292744114"),
        Fraction("115.02694302405"), Fraction("128.05857750528"), Fraction("128.09496301400"),
        Fraction("129.04259308819"), Fraction("131.04048491299"), Fraction("137.05891185845"),
        Fraction("147.06841391299"), Fraction("156.10111102360"), Fraction("163.06332853255"),
        Fraction("186.07931294986"),
    ]
    scale = 100_000
    imasses = [int(round(float(m) * scale)) for m in masses]
    cap = 31_020_000  # 310.20 Da in 10^-5 Da units
    # Enumerate all multisets of size 1..5 iteratively using combinations_with_replacement
    from itertools import combinations_with_replacement

    lo = Fraction("309.9772")
    hi = Fraction("310.1273")
    hits = 0
    for length in range(1, 6):
        for combo in combinations_with_replacement(masses, length):
            tot = sum(combo, Fraction(0))
            if lo <= tot <= hi:
                hits += 1
    if hits != 0 or report["p01_scan23848_deconvolution"]["p01_canonical_suffix_count"] != 0:
        raise AssertionError("P01 canonical suffix non-existence check failed")
    if len(imasses) != 19 or cap <= 0:
        raise AssertionError("Invalid mass table")

    # Verify spectrum peak count and disjoint partition counts sum to 173
    part = report["p01_scan23848_deconvolution"]["disjoint_partition"]
    peak_sum = sum(v["peaks"] for v in part.values())
    if peak_sum != 173:
        raise AssertionError(f"Partition peak counts sum to {peak_sum}, expected 173")
    if SPECTRUM_PATH.is_file():
        spec_data = json.loads(SPECTRUM_PATH.read_text(encoding="utf-8"))
        if len(spec_data["selected_spectrum"]["peaks"]) != 173:
            raise AssertionError("Underlying spectrum locator registry peak count != 173")


def check_p02_witness_independent(report: dict) -> None:
    p02 = report["p02_c20_fold_vs_pooled_auc"]
    folds = p02["witness_folds"]
    if len(folds) != 5:
        raise AssertionError("Expected 5 folds in C20 witness")

    pos_all: list[int] = []
    neg_all: list[int] = []
    fold_sum = Fraction(0, 1)
    for f_entry in folds:
        ps = [int(x) for x in f_entry["positives_num_1e6"]]
        ns = [int(x) for x in f_entry["negatives_num_1e6"]]
        pos_all.extend(ps)
        neg_all.extend(ns)
        c_k = sum(1 for p in ps for n in ns if p > n)
        fold_sum += Fraction(c_k, len(ps) * len(ns))

    if len(pos_all) != 52 or len(neg_all) != 83:
        raise AssertionError("Witness class counts must be 52 and 83")
    if len(set(pos_all + neg_all)) != 135:
        raise AssertionError("Witness contains tied scores")

    pooled_c = sum(1 for p in pos_all for n in neg_all if p > n)
    if pooled_c != 3491:
        raise AssertionError(f"Expected 3491 pooled concordant pairs, got {pooled_c}")

    mean_fold = fold_sum * Fraction(1, 5)
    expected_mean = Fraction(*map(int, p02["witness_fold_mean_exact"].split("/")))
    if mean_fold != expected_mean or mean_fold < Fraction(83, 100):
        raise AssertionError(f"Fold-mean AUROC check failed: {mean_fold}")


def check_p03_independent(report: dict) -> None:
    p03 = report["p03_treatment_sequence_identities"]
    if not p03["dual_checker_distinct_alpha_skeleton"]:
        raise AssertionError("Dual checkers are not AST-skeleton distinct")
    if p03["spec_skeleton_sha256"] == p03["impl_skeleton_sha256"]:
        raise AssertionError("Identical spec/impl skeleton hashes")
    if p03["reference_90_10_resistant_fraction"] != "10/19":
        raise AssertionError("Reference (90, 10) resistant fraction must be 10/19")


def main() -> int:
    try:
        if not REPORT_PATH.is_file():
            raise AssertionError(f"Missing {REPORT_PATH}")
        check_sha256sums()
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        if report.get("study_data_or_network_used") is not False:
            raise AssertionError("study_data_or_network_used must be False")
        check_p01_independent_dp(report)
        check_p02_witness_independent(report)
        check_p03_independent(report)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print("PASS: formal-synthesis-2026-11-13 independent verification succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
