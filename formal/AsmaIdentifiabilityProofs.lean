/-
  formal/AsmaIdentifiabilityProofs.lean
  Zero-dependency stock Lean 4 formal verification module for Foundation-0/project-asma.
/-
  formal/AsmaIdentifiabilityProofs.lean
  Zero-dependency stock Lean 4 (`Init`) formal verification module for Foundation-0/project-asma.

  Research-only mathematical verification (zero third-party libraries, zero `sorry`,
  zero extra axioms, zero `simp` warnings). Uses only `Init` integer lemmas
  (`Int.mul_comm`, `Int.mul_assoc`, `Int.mul_add`, `Int.add_mul`, `Int.mul_sub`,
  `Int.sub_mul`, `Int.mul_one`, `Int.one_mul`), `decide` on ground arithmetic,
  and `omega` strictly on pure linear integer combinations.
-/

namespace AsmaIdentifiabilityProofs

def qNum (pN pD r cN cD : Int) : Int :=
  r * pN * cD + cN * (pD - pN)

def qDen (pN pD r _cN cD : Int) : Int :=
  (r * pN + (pD - pN)) * cD

private theorem mul_swap_outer (A D B : Int) :
    (A * D) * B = (D * B) * A :=
  calc
    (A * D) * B = B * (A * D) := Int.mul_comm (A * D) B
    _ = B * (D * A) := congrArg (fun t => B * t) (Int.mul_comm A D)
    _ = (B * D) * A := (Int.mul_assoc B D A).symm
    _ = (D * B) * A := congrArg (fun t => t * A) (Int.mul_comm B D)

private theorem mul_p_mul_p (a b p : Int) :
    (a * p) * (b * p) = (a * b) * (p * p) :=
  calc
    (a * p) * (b * p) = a * (p * (b * p)) := Int.mul_assoc a p (b * p)
    _ = a * ((b * p) * p) := congrArg (fun t => a * t) (Int.mul_comm p (b * p))
    _ = a * (b * (p * p)) := congrArg (fun t => a * t) (Int.mul_assoc b p p)
    _ = (a * b) * (p * p) := (Int.mul_assoc a b (p * p)).symm

private theorem mul_p_mul_c (a p c : Int) :
    (a * p) * c = a * (c * p) :=
  calc
    (a * p) * c = a * (p * c) := Int.mul_assoc a p c
    _ = a * (c * p) := congrArg (fun t => a * t) (Int.mul_comm p c)

private theorem sub_one_mul (r p : Int) :
    (r - 1) * p = r * p - p :=
  calc
    (r - 1) * p = r * p - 1 * p := Int.sub_mul r 1 p
    _ = r * p - p := congrArg (fun t => r * p - t) (Int.one_mul p)

private theorem lin_den (RP p : Int) :
    RP + (1 - p) = (RP - p) + 1 := by
  omega

private theorem lin_pgl2 (RP CRP CP c : Int) :
    (RP - CRP) + ((CRP - CP) + c) = (RP - CP) + c := by
  omega

private theorem lin_gap (P2 CP2 CP p c : Int) :
    ((240 * P2 - 320 * CP2) + 16 * p) -
    (((240 * P2 - 315 * CP2) + 15 * CP) + ((16 * p - 21 * CP) + c)) =
    (5 * CP - c) - (5 * CP2 - CP) := by
  omega

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
  have h240a : (16 : Int) * 15 = 240 := by decide
  have h320  : (16 : Int) * 20 = 320 := by decide
  have h240b : (15 : Int) * 16 = 240 := by decide
  have h315  : (15 : Int) * 21 = 315 := by decide
  have hL1 : 16 * p * ((15 - 20 * c) * p + 1) =
      (240 * (p * p) - 320 * (c * (p * p))) + 16 * p := by
    have ha : (16 * p) * (15 * p) = 240 * (p * p) := by
      rw [mul_p_mul_p 16 15 p, h240a]
    have hb : (16 * p) * ((20 * c) * p) = 320 * (c * (p * p)) := by
      rw [mul_p_mul_p 16 (20 * c) p, ← Int.mul_assoc 16 20 c, h320, Int.mul_assoc 320 c (p * p)]
    calc
      (16 * p) * ((15 - 20 * c) * p + 1)
        = (16 * p) * ((15 - 20 * c) * p) + (16 * p) * 1 := Int.mul_add (16 * p) ((15 - 20 * c) * p) 1
      _ = (16 * p) * ((15 - 20 * c) * p) + 16 * p := by rw [Int.mul_one (16 * p)]
      _ = (16 * p) * (15 * p - (20 * c) * p) + 16 * p := by rw [Int.sub_mul 15 (20 * c) p]
      _ = ((16 * p) * (15 * p) - (16 * p) * ((20 * c) * p)) + 16 * p := by
            rw [Int.mul_sub (16 * p) (15 * p) ((20 * c) * p)]
      _ = (240 * (p * p) - 320 * (c * (p * p))) + 16 * p := by rw [ha, hb]
  have hL2 : (15 * p + 1) * ((16 - 21 * c) * p + c) =
      ((240 * (p * p) - 315 * (c * (p * p))) + 15 * (c * p)) + ((16 * p - 21 * (c * p)) + c) := by
    have hc : (15 * p) * (16 * p) = 240 * (p * p) := by
      rw [mul_p_mul_p 15 16 p, h240b]
    have hd : (15 * p) * ((21 * c) * p) = 315 * (c * (p * p)) := by
      rw [mul_p_mul_p 15 21 c, ← Int.mul_assoc 15 21 c, h315, Int.mul_assoc 315 c (p * p)]
    have he : (16 - 21 * c) * p = 16 * p - 21 * (c * p) := by
      rw [Int.sub_mul 16 (21 * c) p, Int.mul_assoc 21 c p]
    have hf : (15 * p) * ((16 - 21 * c) * p + c) =
        (240 * (p * p) - 315 * (c * (p * p))) + 15 * (c * p) := by
      calc
        (15 * p) * ((16 - 21 * c) * p + c)
          = (15 * p) * ((16 - 21 * c) * p) + (15 * p) * c :=
              Int.mul_add (15 * p) ((16 - 21 * c) * p) c
        _ = (15 * p) * (16 * p - (21 * c) * p) + 15 * (c * p) := by
              rw [Int.sub_mul 16 (21 * c) p, mul_p_mul_c 15 p c]
        _ = ((15 * p) * (16 * p) - (15 * p) * ((21 * c) * p)) + 15 * (c * p) := by
              rw [Int.mul_sub (15 * p) (16 * p) ((21 * c) * p)]
        _ = (240 * (p * p) - 315 * (c * (p * p))) + 15 * (c * p) := by rw [hc, hd]
    calc
      (15 * p + 1) * ((16 - 21 * c) * p + c)
        = (15 * p) * ((16 - 21 * c) * p + c) + 1 * ((16 - 21 * c) * p + c) :=
            Int.add_mul (15 * p) 1 ((16 - 21 * c) * p + c)
      _ = (15 * p) * ((16 - 21 * c) * p + c) + ((16 - 21 * c) * p + c) := by
            rw [Int.one_mul ((16 - 21 * c) * p + c)]
      _ = ((240 * (p * p) - 315 * (c * (p * p))) + 15 * (c * p)) + ((16 * p - 21 * (c * p)) + c) := by
            rw [hf, he]
  have hR : c * (5 * p - 1) * (1 - p) =
      (5 * (c * p) - c) - (5 * (c * (p * p)) - c * p) := by
    have hg : c * (5 * p) = 5 * (c * p) := by
      calc
        c * (5 * p) = (c * 5) * p := (Int.mul_assoc c 5 p).symm
        _ = (5 * c) * p := congrArg (fun t => t * p) (Int.mul_comm c 5)
        _ = 5 * (c * p) := Int.mul_assoc 5 c p
    have hh : (5 * (c * p)) * p = 5 * (c * (p * p)) := by
      rw [Int.mul_assoc 5 (c * p) p, Int.mul_assoc c p p]
    calc
      (c * (5 * p - 1)) * (1 - p)
        = (c * (5 * p) - c * 1) * (1 - p) := by rw [Int.mul_sub c (5 * p) 1]
      _ = (5 * (c * p) - c) * (1 - p) := by rw [Int.mul_one c, hg]
      _ = (5 * (c * p) - c) * 1 - (5 * (c * p) - c) * p :=
            Int.mul_sub (5 * (c * p) - c) 1 p
      _ = (5 * (c * p) - c) - ((5 * (c * p)) * p - c * p) := by
            rw [Int.mul_one (5 * (c * p) - c), Int.sub_mul (5 * (c * p)) c p]
      _ = (5 * (c * p) - c) - (5 * (c * (p * p)) - c * p) := by rw [hh]
  rw [hL1, hL2, hR]
  exact lin_gap (p * p) (c * (p * p)) (c * p) p c

theorem survival_ratio_affine_linearization (p r c : Int) :
    (1 - p) * (r * p + (1 - p)) * (1 - c) =
      ((r - 1) * p + 1) * ((1 - c) * (1 - p)) := by
  have hden : r * p + (1 - p) = (r - 1) * p + 1 := by
    rw [sub_one_mul r p]
    exact lin_den (r * p) p
  calc
    ((1 - p) * (r * p + (1 - p))) * (1 - c)
      = ((1 - p) * ((r - 1) * p + 1)) * (1 - c) := by rw [hden]
    _ = (((r - 1) * p + 1) * (1 - c)) * (1 - p) :=
          mul_swap_outer (1 - p) ((r - 1) * p + 1) (1 - c)
    _ = ((r - 1) * p + 1) * ((1 - c) * (1 - p)) :=
          Int.mul_assoc ((r - 1) * p + 1) (1 - c) (1 - p)

theorem pgl2_paralog_cross_reactivity_isomorphism (p r c : Int) :
    (1 - c) * (r * p) + c * ((r - 1) * p + 1) = (r - c) * p + c := by
  have h1 : (1 - c) * (r * p) = r * p - (c * r) * p := by
    calc
      (1 - c) * (r * p) = 1 * (r * p) - c * (r * p) := Int.sub_mul 1 c (r * p)
      _ = r * p - c * (r * p) := by rw [Int.one_mul (r * p)]
      _ = r * p - (c * r) * p := by rw [← Int.mul_assoc c r p]
  have h2 : c * ((r - 1) * p + 1) = ((c * r) * p - c * p) + c := by
    calc
      c * ((r - 1) * p + 1) = c * ((r - 1) * p) + c * 1 := Int.mul_add c ((r - 1) * p) 1
      _ = c * (r * p - p) + c := by rw [sub_one_mul r p, Int.mul_one c]
      _ = (c * (r * p) - c * p) + c := by rw [Int.mul_sub c (r * p) p]
      _ = ((c * r) * p - c * p) + c := by rw [← Int.mul_assoc c r p]
  have h3 : (r - c) * p + c = (r * p - c * p) + c := by
    rw [Int.sub_mul r c p]
  rw [h1, h2, h3]
  exact lin_pgl2 (r * p) ((c * r) * p) (c * p) c

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
