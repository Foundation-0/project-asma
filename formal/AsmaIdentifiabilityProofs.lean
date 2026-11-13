/-
  formal/AsmaIdentifiabilityProofs.lean
  Stock Lean 4 module for Foundation-0/project-asma. It imports nothing.

  Toolchain: pinned in formal/lean-toolchain (leanprover/lean4:v4.35.0).
  Build:     cd formal && lake build
  Check:     cd formal && lake env lean AsmaIdentifiabilityProofs.lean

  Rational identities are stated in cross-multiplied integer form over `Int`.
  The module contains no sorry and declares no axioms. The `#print axioms`
  report for every theorem is at the end of this file and in
  formal/axioms-lean-4.35.0.txt.

  gem-nexus's presentation in PR #83 is unreproduced except for the statements
  this file proves.

  Compartment model (docs/compartment-identifiability.md):
    q(p; r, c) = (r*p + c*(1-p)) / (r*p + (1-p)).
  With p = pN/pD and c = cN/cD, qNum/qDen below is that fraction scaled by pD*cD.
-/

namespace AsmaIdentifiabilityProofs

def qNum (pN pD r cN cD : Int) : Int :=
  r * pN * cD + cN * (pD - pN)

def qDen (pN pD r _cN cD : Int) : Int :=
  (r * pN + (pD - pN)) * cD

/-- At p = 1/5 the worlds S (16,0), C25 (11,1/4), C50 (6,1/2), C75 (1,3/4)
all give q = 4/5. -/
theorem snapshot_four_worlds_indistinguishable :
    qNum 1 5 16 0 1 * 5 = 4 * qDen 1 5 16 0 1 ∧
    qNum 1 5 11 1 4 * 5 = 4 * qDen 1 5 11 1 4 ∧
    qNum 1 5 6  1 2 * 5 = 4 * qDen 1 5 6  1 2 ∧
    qNum 1 5 1  3 4 * 5 = 4 * qDen 1 5 1  3 4 := by
  decide

/-- Paired design (L, H) = (1/10, 2/5): contrast ceilings eps*_C25 = 3/448 and
eps*_C50 = 13/700, with 3/448 < 1/60 < 13/700. -/
theorem pr78_sharp_separation_hierarchy :
    qNum 1 10 16 0 1 * 25  = 16 * qDen 1 10 16 0 1 ∧
    qNum 2 5  16 0 1 * 35  = 32 * qDen 2 5  16 0 1 ∧
    qNum 1 10 11 1 4 * 80  = 53 * qDen 1 10 11 1 4 ∧
    qNum 2 5  11 1 4 * 100 = 91 * qDen 2 5  11 1 4 ∧
    qNum 1 10 6  1 2 * 10  = 7  * qDen 1 10 6  1 2 ∧
    qNum 2 5  6  1 2 * 10  = 9  * qDen 2 5  6  1 2 ∧
    ((32 * 25 - 16 * 35) * 10 - (9 - 7) * (35 * 25)) * 700 = 4 * 13 * (35 * 25 * 10) ∧
    ((32 * 25 - 16 * 35) * 400 - (91 * 4 - 53 * 5) * (35 * 25)) * 448 = 4 * 3 * (35 * 25 * 400) ∧
    (3 : Int) * 60  < 1 * 448 ∧
    (1 : Int) * 700 < 13 * 60 := by
  decide

/-- Paired design (L, H) = (1/20, 3/8).
q-values at L: S 16/35, C25 21/40, C50 31/50, C75 61/80.
q-values at H: S 48/53, C25 137/152, C50 41/46, C75 27/32.
Contrast ceilings against S: eps*_C25 = 10179/563920, eps*_C50 = 9451/213325,
eps*_C75 = 21801/237440. Each exceeds 1/60, and eps*_C50 exceeds 26/700 = 2 * 13/700.
This states the ceilings for these two seeds. It makes no claim that the seeds are optimal. -/
theorem low_seed_1_20_3_8_ceilings_vs_snapshot :
    qNum 1 20 16 0 1 * 35  = 16  * qDen 1 20 16 0 1 ∧
    qNum 3 8  16 0 1 * 53  = 48  * qDen 3 8  16 0 1 ∧
    qNum 1 20 11 1 4 * 40  = 21  * qDen 1 20 11 1 4 ∧
    qNum 3 8  11 1 4 * 152 = 137 * qDen 3 8  11 1 4 ∧
    qNum 1 20 6  1 2 * 50  = 31  * qDen 1 20 6  1 2 ∧
    qNum 3 8  6  1 2 * 46  = 41  * qDen 3 8  6  1 2 ∧
    qNum 1 20 1  3 4 * 80  = 61  * qDen 1 20 1  3 4 ∧
    qNum 3 8  1  3 4 * 32  = 27  * qDen 3 8  1  3 4 ∧
    ((48 * 35 - 16 * 53) * (46 * 50) - (41 * 50 - 31 * 46) * (53 * 35)) * 213325 =
      4 * 9451 * (53 * 35 * 46 * 50) ∧
    (9451 : Int) * 700 > 26 * 213325 ∧
    ((48 * 35 - 16 * 53) * (152 * 40) - (137 * 40 - 21 * 152) * (53 * 35)) * 563920 =
      4 * 10179 * (53 * 35 * 152 * 40) ∧
    (10179 : Int) * 60 > 1 * 563920 ∧
    ((48 * 35 - 16 * 53) * (32 * 80) - (27 * 80 - 61 * 32) * (53 * 35)) * 237440 =
      4 * 21801 * (53 * 35 * 32 * 80) ∧
    (21801 : Int) * 60 > 1 * 237440 := by
  decide

/-- Pairwise ceilings among the conversion worlds at (1/20, 3/8):
C25 vs C50 = 4589/174800, C25 vs C75 = 897/12160, C50 vs C75 = 3497/73600.
Each exceeds 1/60. -/
theorem low_seed_1_20_3_8_pairwise_conversion_ceilings :
    ((137 * 40 - 21 * 152) * (46 * 50) - (41 * 50 - 31 * 46) * (152 * 40)) * 174800 =
      4 * 4589 * (152 * 40 * 46 * 50) ∧
    (4589 : Int) * 60 > 1 * 174800 ∧
    ((137 * 40 - 21 * 152) * (32 * 80) - (27 * 80 - 61 * 32) * (152 * 40)) * 12160 =
      4 * 897 * (152 * 40 * 32 * 80) ∧
    (897 : Int) * 60 > 1 * 12160 ∧
    ((41 * 50 - 31 * 46) * (32 * 80) - (27 * 80 - 61 * 32) * (46 * 50)) * 73600 =
      4 * 3497 * (46 * 50 * 32 * 80) ∧
    (3497 : Int) * 60 > 1 * 73600 := by
  decide

/-- Numerator of q_S(p) - q_c(p) along the snapshot locus r = 16 - 20*c. -/
theorem universal_snapshot_gap_factorization (p c : Int) :
    16 * p * ((15 - 20 * c) * p + 1) - (15 * p + 1) * ((16 - 21 * c) * p + c) =
      c * (5 * p - 1) * (1 - p) := by
  grind

/-- Survival-ratio pencil. With N = r*p + c*(1-p) and D = r*p + (1-p), q = N/D and
1 - q = (D - N)/D = (1-c)*(1-p)/D, so Phi(p) = (1-p)/(1-q) = ((r-1)*p + 1)/(1-c)
whenever p ≠ 1 and c ≠ 1. The third conjunct is that last equality cross-multiplied. -/
theorem survival_ratio_pencil (p r c : Int) :
    (r * p + (1 - p)) - (r * p + c * (1 - p)) = (1 - c) * (1 - p) ∧
    r * p + (1 - p) = (r - 1) * p + 1 ∧
    (1 - p) * (r * p + (1 - p)) * (1 - c) =
      ((r - 1) * p + 1) * ((r * p + (1 - p)) - (r * p + c * (1 - p))) := by
  refine ⟨?_, ?_, ?_⟩ <;> grind

/-- Pencil values for the four worlds, computed from qNum/qDen. With p = pN/pD,
Phi(p) = (1-p)/(1-q) = (pD - pN) * qDen / (pD * (qDen - qNum)).
Phi(0) is 1, 4/3, 2, 4 for S, C25, C50, C75, and Phi(1/5) = 4 for all four. -/
theorem survival_ratio_pencil_four_worlds :
    1 * ((1 - 0) * qDen 0 1 16 0 1) = 1 * (1 * (qDen 0 1 16 0 1 - qNum 0 1 16 0 1)) ∧
    3 * ((1 - 0) * qDen 0 1 11 1 4) = 4 * (1 * (qDen 0 1 11 1 4 - qNum 0 1 11 1 4)) ∧
    1 * ((1 - 0) * qDen 0 1 6  1 2) = 2 * (1 * (qDen 0 1 6  1 2 - qNum 0 1 6  1 2)) ∧
    1 * ((1 - 0) * qDen 0 1 1  3 4) = 4 * (1 * (qDen 0 1 1  3 4 - qNum 0 1 1  3 4)) ∧
    (5 - 1) * qDen 1 5 16 0 1 = 4 * (5 * (qDen 1 5 16 0 1 - qNum 1 5 16 0 1)) ∧
    (5 - 1) * qDen 1 5 11 1 4 = 4 * (5 * (qDen 1 5 11 1 4 - qNum 1 5 11 1 4)) ∧
    (5 - 1) * qDen 1 5 6  1 2 = 4 * (5 * (qDen 1 5 6  1 2 - qNum 1 5 6  1 2)) ∧
    (5 - 1) * qDen 1 5 1  3 4 = 4 * (5 * (qDen 1 5 1  3 4 - qNum 1 5 1  3 4)) := by
  decide

/-- (1 - c) * q(p; r, 0) + c = q(p; r, c), cross-multiplied over the shared
denominator (r - 1)*p + 1. -/
theorem blend_numerator_equality (p r c : Int) :
    (1 - c) * (r * p) + c * ((r - 1) * p + 1) = (r - c) * p + c := by
  calc
    (1 - c) * (r * p) + c * ((r - 1) * p + 1)
      = (r * p - c * (r * p)) + (c * ((r - 1) * p) + c) := by
          simp [Int.sub_mul, Int.mul_add]
    _ = (r * p - c * r * p) + ((c * r * p - c * p) + c) := by
          have h1 : c * (r * p) = c * r * p := by ac_rfl
          have h2 : c * ((r - 1) * p) = c * r * p - c * p := by
            calc c * ((r - 1) * p)
              _ = c * (r * p - p) := by simp [Int.sub_mul]
              _ = c * (r * p) - c * p := by simp [Int.mul_sub]
              _ = c * r * p - c * p := by rw [h1]
          rw [h1, h2]
    _ = r * p - c * p + c := by omega
    _ = (r - c) * p + c := by simp [Int.sub_mul]

/-- Pilot 001: 52 positives and 83 negatives give 4316 pairs. Positives per fold
are [11, 11, 10, 10, 10]. The balanced split pairs them with negatives
[16, 16, 17, 17, 17], so every fold has 27 samples and the within-fold pair count
is 862 (3454 cross-fold). The alignments [17, 16, 17, 17, 16] (fold sizes
28, 27, 27, 27, 26) and [17, 17, 17, 16, 16] (fold sizes 28, 28, 27, 26, 26) give
863 and 864. -/
theorem pilot001_stratified_5fold_pair_split :
    52 * 83 = 4316 ∧
    11 + 11 + 10 + 10 + 10 = 52 ∧
    16 + 16 + 17 + 17 + 17 = 83 ∧
    11 + 16 = 27 ∧ 10 + 17 = 27 ∧
    11 * 16 + 11 * 16 + 10 * 17 + 10 * 17 + 10 * 17 = 862 ∧
    4316 - 862 = 3454 ∧
    11 * 17 + 11 * 16 + 10 * 17 + 10 * 17 + 10 * 16 = 863 ∧
    11 * 17 + 11 * 17 + 10 * 17 + 10 * 16 + 10 * 16 = 864 := by
  decide

/-- Integer order: adding the same integer to both sides preserves `>`. -/
theorem int_gt_cancel_common_addend (sPos sNeg delta : Int) :
    (sPos + delta > sNeg + delta) ↔ (sPos > sNeg) := by
  omega

/-- Integer order: adding different integers can reverse `>`. Witness 10 > 5
while 10 + 0 is not greater than 5 + 6. -/
theorem int_gt_unequal_addends_witness :
    ∃ (sPos sNeg deltaPos deltaNeg : Int),
      sPos > sNeg ∧ ¬ (sPos + deltaPos > sNeg + deltaNeg) := by
  exact ⟨10, 5, 0, 6, by decide, by decide⟩

end AsmaIdentifiabilityProofs

#print axioms AsmaIdentifiabilityProofs.snapshot_four_worlds_indistinguishable
#print axioms AsmaIdentifiabilityProofs.pr78_sharp_separation_hierarchy
#print axioms AsmaIdentifiabilityProofs.low_seed_1_20_3_8_ceilings_vs_snapshot
#print axioms AsmaIdentifiabilityProofs.low_seed_1_20_3_8_pairwise_conversion_ceilings
#print axioms AsmaIdentifiabilityProofs.universal_snapshot_gap_factorization
#print axioms AsmaIdentifiabilityProofs.survival_ratio_pencil
#print axioms AsmaIdentifiabilityProofs.survival_ratio_pencil_four_worlds
#print axioms AsmaIdentifiabilityProofs.blend_numerator_equality
#print axioms AsmaIdentifiabilityProofs.pilot001_stratified_5fold_pair_split
#print axioms AsmaIdentifiabilityProofs.int_gt_cancel_common_addend
#print axioms AsmaIdentifiabilityProofs.int_gt_unequal_addends_witness
