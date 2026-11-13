# Executable Soko-Weft Discriminating Tests for Project Asma

**Status:** Synthetic and mathematical verification only (P01-P03 and V43-V45 all `VERIFIED` via offline checkers; nothing here is mechanized into `formal/`, so `CLAIMS.md` keeps `0` `PROVEN`). Research only; not clinical advice, a diagnostic service, or clinical decision support; not externally reviewed.

## 1. Purpose and Connection to Open Repository Work

Pull Request #77 (`docs/ecosystem-research-fit-2026-11-12.md`) identified concrete places where combinatorial search and independent certificate checkers from `ahrazzle/soko` and `Proven-Commons` could strengthen `Foundation-0/project-asma`, while Pull Request #78 (`tools/analyze_compartment_design.py`) established exact scalar precision limits for four synthetic compartment worlds (`S`, `C25`, `C50`, `C75`). In parallel, ` Moissanite-Labs/weft` (`weft/runtime/plasm/synaptic_flow.py`) introduced unit-capacity Dinic corridor routing, orthogonal capacity mitosis on certified min-cut deficits, frozen-core safety invariants (`C1`/`C2`), and exact `fractions.Fraction` dual receipts.

This module turns PR #77's prose roadmap into a zero-dependency standard-library Python 3 implementation (`tools/analyze_soko_weft_discriminators.py`) paired with a clean-room second checker (`results/soko-weft-discriminators-20261113/verify.py`) and written proofs (`PROOF.md`).

## 2. Summary of Verified Results

| Claim ID | Label | Statement | Offline Replay Command |
| :--- | :--- | :--- | :--- |
| **P01** | `VERIFIED` | Abundance-free unit-capacity Dinic peak-split matching swept across rational 1-D Helly calibration knots is necessary and sufficient for joint MS2 ion support, excluding near-isobaric paralog/swap decoys with 0 retained intensity bytes (addresses Issue #71). | `python3 results/soko-weft-discriminators-20261113/verify.py` |
| **P02** | `VERIFIED` | Closed-form rational Farkas dual theorem reproduces PR #78 scalar bounds (`LH` `S` vs `C50` = `13/700`, `S` vs `C25` = `3/448 < 1/60`), proves the `590/21` two-clone shedding blind spot, and proves orthogonal 2-channel mitosis lifts worst-case separation across all 6 world pairs to `69/320 > 1/60`. | `python3 results/soko-weft-discriminators-20261113/verify.py` |
| **P03** | `VERIFIED` | Monotone Pareto-prefix nogood pruning under Weft `C1` (`h_core >= h_min`) and `C2` (`v_R < v_crit`) invariants preserves exact safe Bellman optimality while emitting an `O(T)` non-execution trajectory receipt. | `python3 results/soko-weft-discriminators-20261113/verify.py` |
| **V43** | `VERIFIED` | Across 24 synthetic CDR2L (`Q86X02`) vs. CDR2 (`Q01850`), `N->D` deamidation, and dipeptide-swap spectra under systematic drift, naive and uncalibrated Dinic counters admit `24/24` swap decoys (`1/1` false admission), whereas Soko-Weft Helly-Dinic achieves `24/24` CDR2L recall and `0/24` (`0/1`) false admissions. | `python3 tools/analyze_soko_weft_discriminators.py --check` |
| **V44** | `VERIFIED` | Independent checker verifies exact rational Farkas dual vectors across all 6 PR #78 scalar designs and the orthogonal 2-channel `LH` design (`min_eps = 69/320 = 0.215625 > 1/60`). | `python3 tools/analyze_soko_weft_discriminators.py --check` |
| **V45** | `VERIFIED` | Across 16 synthetic multi-compartment intervention cohorts (`T = 6`, `4,096` trajectories each), greedy scalar-marker selection violates `C1`/`C2` safety in `16/16` cohorts, whereas Soko-Weft matches the exhaustive safe oracle on `16/16` cohorts (`0` violations) while pruning `70.94%` of transitions. | `python3 -m unittest discover -s tests -p 'test_soko_weft_*.py' -v` |

## 3. Scope Boundaries and Non-Overclaiming Rules

1. **No patient or study-data execution:** All spectra, compartment fractions, and intervention trajectories in this bundle are deterministic synthetic models. They do not establish clinical validity, real-cohort biomarker accuracy, or patient treatment recommendations.
2. **Issue #71 peak-retention resolution:** Pillar 1 demonstrates that public certificates for PSM uniqueness vs. paralog exclusion only need discrete rational offset intervals and `source_minimal` residual cut sets (`intensities_retained_bytes == 0`), avoiding redistribution of upstream experimental intensity arrays.
3. **Tamper sensitivity (PR #80 conformance):** `tests/test_soko_weft_discriminators.py` mutates scope banners, cut capacities, Farkas dual bounds, and host-core trajectory states after recomputing outer SHA-256 digests, verifying `0` tamper misses in `verify.py`.

> Automated posting by agentic team with human oversight.
