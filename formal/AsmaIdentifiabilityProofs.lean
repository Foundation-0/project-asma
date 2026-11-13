/-
  formal/AsmaIdentifiabilityProofs.lean
  Zero-dependency stock Lean 4 formal verification module for Foundation-0/project-asma.

  Research-only mathematical verification (zero third-party libraries, zero `sorry`,
  zero extra axioms). All rational identities are stated in exact cross-multiplied
  integer form over `Int` so stock Lean 4 checks every theorem in milliseconds.
-/

namespace AsmaIdentifiabilityProofs

def qNum (pN pD r cN cD : Int) : Int :=
  r * pN * cD + cN * (pD - pN)

def qDen (pN pD r _cN cD : Int) : Int :=
  (r * pN + (pD - pN)) * cD

theorem snapshot_four_worlds_indistinguishable :
    qNum 1 5 16 0 1 * 5 = 4 * qDen 1 5 16 0 1 ∧
    qNum 1 5 11 1 4 * 5 = 4 * qDen 1 5 11 1 4 ∧
    qNum 1 5 6  1 2 * 5 = 4 * qDen 1 5 6  1 2 ∧
    qNum 1 5 1  3 4 * 5 = 4 * qDen 1 5 1  3 4 := by
  decide

theorem pr78_sharp_separation_hierarchy :
    qNum 1 10 16 0 1 * 25  = 16 * qDen 1 10 16 0 1 ∧
    qNum 2 5  16 0 1 * 35  = 32 * qDen 2 5  16 0 1 ∧
    qNum 1 10 11 1 4 * 80  = 53 * qDen 1 10 11 1 4 ∧
    qNum 2 5  11 1 4 * 100 = 91 * qDen 2 5  11 1 4 ∧
    qNum 1 10 6  1 2 * 10  = 7  * qDen 1 10 6  1 2 ∧
    qNum 2 5  6  1 2 * 10  = 9  * qDen 2 5  6  1 2 ∧
    ((32 * 25 - 16 * 35) * 10 - (9 - 7) * (35 * 25)) * 700 = 4 * 13 * (35 * 25 * 10) ∧
    ((32 * 25 - 16 * 35) * 400 - (91 * 4 - 53 * 5) * (35 * 25)) * 448 = 4 * 3 * (35 * 25 * 400) ∧
    (3 : Int) * 200 < 3 * 448 ∧
    (3 : Int) * 60  < 1 * 200 ∧
    (1 : Int) * 700 < 13 * 60 := by
  decide

theorem opt_low_seed_flips_c25_and_doubles_c50 :
    qNum 1 20 16 0 1 * 35  = 16  * qDen 1 20 16 0 1 ∧
    qNum 3 8  16 0 1 * 53  = 48  * qDen 3 8  16 0 1 ∧
    qNum 1 20 11 1 4 * 64  = 43  * qDen 1 20 11 1 4 ∧
    qNum 3 8  11 1 4 * 152 = 137 * qDen 3 8  11 1 4 ∧
    qNum 1 20 6  1 2 * 50  = 31  * qDen 1 20 6  1 2 ∧
    qNum 3 8  6  1 2 * 46  = 41  * qDen 3 8  6  1 2 ∧
    ((48 * 35 - 16 * 53) * (46 * 50) - (41 * 50 - 31 * 46) * (53 * 35)) * 213325 =
      4 * 9451 * (53 * 35 * 46 * 50) ∧
    (9451 : Int) * 700 > 26 * 213325 ∧
    ((48 * 35 - 16 * 53) * (152 * 64) - (137 * 64 - 43 * 152) * (53 * 35)) * 563920 =
      4 * 10179 * (53 * 35 * 152 * 64) ∧
    (10179 : Int) * 60 > 1 * 563920 := by
  decide

theorem universal_snapshot_gap_factorization (p c : Int) :
    16 * p * ((15 - 20 * c) * p + 1) - (15 * p + 1) * ((16 - 21 * c) * p + c) =
      c * (5 * p - 1) * (1 - p) := by
  calc
    16 * p * ((15 - 20 * c) * p + 1) - (15 * p + 1) * ((16 - 21 * c) * p + c)
      = (16 * p * ((15 - 20 * c) * p) + 16 * p) -
        (15 * p * ((16 - 21 * c) * p + c) + ((16 - 21 * c) * p + c)) := by
          simp [Int.mul_add, Int.add_mul]
    _ = ((240 * (p * p) - 320 * c * (p * p)) + 16 * p) -
        (((240 * (p * p) - 315 * c * (p * p)) + 15 * c * p) + (16 * p - 21 * c * p + c)) := by
          have ha : 16 * p * ((15 - 20 * c) * p) = 240 * (p * p) - 320 * c * (p * p) := by
            calc 16 * p * ((15 - 20 * c) * p)
              _ = 16 * (15 - 20 * c) * (p * p) := by ac_rfl
              _ = (240 - 320 * c) * (p * p) := by simp [Int.mul_sub]
              _ = 240 * (p * p) - 320 * c * (p * p) := by simp [Int.sub_mul, Int.mul_assoc]
          have hb : 15 * p * ((16 - 21 * c) * p + c) = (240 * (p * p) - 315 * c * (p * p)) + 15 * c * p := by
            calc 15 * p * ((16 - 21 * c) * p + c)
              _ = 15 * p * ((16 - 21 * c) * p) + 15 * p * c := by simp [Int.mul_add]
              _ = 15 * (16 - 21 * c) * (p * p) + 15 * c * p := by
                    have hpc : 15 * p * c = 15 * c * p := by ac_rfl
                    have hpp : 15 * p * ((16 - 21 * c) * p) = 15 * (16 - 21 * c) * (p * p) := by ac_rfl
                    rw [hpp, hpc]
              _ = (240 - 315 * c) * (p * p) + 15 * c * p := by simp [Int.mul_sub]
              _ = (240 * (p * p) - 315 * c * (p * p)) + 15 * c * p := by simp [Int.sub_mul, Int.mul_assoc]
          have hc : (16 - 21 * c) * p = 16 * p - 21 * c * p := by
            simp [Int.sub_mul, Int.mul_assoc]
          rw [ha, hb, hc]
    _ = -5 * c * (p * p) + 6 * c * p - c := by omega
    _ = c * (5 * p - 1) * (1 - p) := by
          calc -5 * c * (p * p) + 6 * c * p - c
            _ = c * (-5 * (p * p) + 6 * p - 1) := by
                  simp [Int.mul_add, Int.mul_sub]
                  ac_rfl
            _ = c * ((5 * p - 1) * (1 - p)) := by
                  congr 1
                  calc -5 * (p * p) + 6 * p - 1
                    _ = (5 * p - 1) * 1 - (5 * p - 1) * p := by
                          simp [Int.sub_mul, Int.mul_assoc]
                          omega
                    _ = (5 * p - 1) * (1 - p) := by simp [Int.mul_sub]
            _ = c * (5 * p - 1) * (1 - p) := by simp [Int.mul_assoc]

theorem survival_ratio_affine_linearization (p r c : Int) :
    (1 - p) * (r * p + (1 - p)) * (1 - c) =
      ((r - 1) * p + 1) * ((1 - c) * (1 - p)) := by
  have h : r * p + (1 - p) = (r - 1) * p + 1 := by
    simp [Int.sub_mul]
    omega
  rw [h]
  ac_rfl

theorem pgl2_paralog_cross_reactivity_isomorphism (p r c : Int) :
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

theorem pilot001_stratified_5fold_pair_split :
    52 * 83 = 4316 ∧
    11 * 17 + 11 * 17 + 10 * 17 + 10 * 16 + 10 * 16 = 864 ∧
    11 * 17 + 11 * 16 + 10 * 17 + 10 * 17 + 10 * 16 = 863 ∧
    11 * 16 + 11 * 16 + 10 * 17 + 10 * 17 + 10 * 17 = 862 ∧
    4316 - 864 = 3452 ∧
    4316 - 863 = 3453 ∧
    4316 - 862 = 3454 := by
  decide

theorem within_fold_concordance_shift_invariant (sPos sNeg delta : Int) :
    (sPos + delta > sNeg + delta) ↔ (sPos > sNeg) := by
  omega

theorem cross_fold_concordance_broken_by_shift :
    ∃ (sPos sNeg deltaPos deltaNeg : Int),
      sPos > sNeg ∧ ¬ (sPos + deltaPos > sNeg + deltaNeg) := by
  exact ⟨10, 5, 0, 6, by decide, by decide⟩

end AsmaIdentifiabilityProofs
