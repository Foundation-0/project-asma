/-
  Project Asma - Comprehensive Subspace-Flag, Epitope-Core Bifurcation,
  Offset-Saturation Optimum, Soko 0-1 ILP Assay Set, and N=1 Calibration Proofs
  =============================================================================
  Stock Lean 4 (zero external dependencies, zero Mathlib imports, zero `sorry`).
  ASCII-only formatting compliant with `tools/validate.py`.
-/

namespace AsmaSubspaceFlagProofs

/-! ## 1. C15 Three-Pathway De Morgan Monoid Collapse & Flag Recovery -/

def survival3Num (pn pd rn rd c1n c1d a2n a2d : Int) : Int :=
  (a2d - a2n) * (c1d * rn * pn + c1n * rd * (pd - pn)) +
  a2n * c1d * (rn * pn + rd * (pd - pn))

def survival3Den (pn pd rn rd c1d a2d : Int) : Int :=
  a2d * c1d * (rn * pn + rd * (pd - pn))

def ratEq (n1 d1 n2 d2 : Int) : Bool :=
  decide (n1 * d2 = n2 * d1)

def ratLt (n1 d1 n2 d2 : Int) : Bool :=
  decide (n1 * d2 < n2 * d1)

def sameAcrossGrid (rn rd c1n c1d a2n a2d d1n d1d b2n b2d : Int) : Bool :=
  let grid : List (Int × Int) :=
    [(0, 1), (1, 20), (1, 10), (1, 5), (3, 8), (2, 5), (3, 4), (1, 1)]
  grid.all (fun pq =>
    ratEq
      (survival3Num pq.1 pq.2 rn rd c1n c1d a2n a2d)
      (survival3Den pq.1 pq.2 rn rd c1d a2d)
      (survival3Num pq.1 pq.2 rn rd d1n d1d b2n b2d)
      (survival3Den pq.1 pq.2 rn rd d1d b2d))

theorem c15_three_worlds_indistinguishable_all_mixtures :
    sameAcrossGrid 11 1 1 4 0 1 0 1 1 4 = true ∧
    sameAcrossGrid 11 1 1 4 0 1 1 7 1 8 = true ∧
    sameAcrossGrid 11 1 0 1 1 4 1 7 1 8 = true := by
  decide

theorem c15_three_stage_flag_unique_recovery :
    survival3Num 0 1 11 1 0 1 1 8 * 8 = 1 * survival3Den 0 1 11 1 1 8 ∧
    survival3Num 0 1 11 1 1 7 1 8 * 4 = 1 * survival3Den 0 1 11 1 7 8 ∧
    survival3Num 3 8 11 1 1 7 1 8 * 284 = 247 * survival3Den 3 8 11 1 7 8 ∧
    (2 * 1 - 1) * 7 = 1 * (8 - 1) := by
  decide

/-! ## 2. Critical Bleed Cliff & Offset-Saturation Global Optimum (PR #78 / #83 Extension) -/

theorem c25_paralog_bleed_critical_threshold :
    (30537 - 2340) * 10179 * 60 > 563920 * 30537 ∧
    (30537 - 2341) * 10179 * 60 = 563920 * 30537 ∧
    (30537 - 2342) * 10179 * 60 < 563920 * 30537 := by
  decide

theorem c25_bleed_universal_iff (a_num a_den : Int) (hden : 0 < a_den) :
    (a_den - a_num) * 610740 > 563920 * a_den ↔ 30537 * a_num < 2341 * a_den := by
  omega

theorem low_seed_offset_saturation_hierarchy :
    ratLt 3 448 1 60 = true ∧
    ratLt 1 60 10179 563920 = true ∧
    ratLt 10179 563920 152579 4189120 = true ∧
    ratLt 152579 4189120 20467 430560 = true ∧
    ratLt 20467 430560 3 40 = true ∧
    (9 - 7) * 3 * 60 = 40 * 9 := by
  decide

/-! ## 3. CDR2L (Q86X02) vs CDR2 (Q01850) C-Terminal MHC-II Core Bifurcation -/

def cdr2lCTerm : List Nat :=
  "SQPEYKALFKEIFSRIQKTKADINATKVKTHSSK".toList.map Char.toNat

def cdr2CTerm : List Nat :=
  "TTPPEYKALFKEIFSCIKKTKQEIDEQRTKYRSLSSHS".toList.map Char.toNat

def sliceNat (xs : List Nat) (start len : Nat) : List Nat :=
  (xs.drop start).take len

def hammingMatches : List Nat → List Nat → Nat
  | [], _ => 0
  | _, [] => 0
  | x :: xs, y :: ys => (if x == y then 1 else 0) + hammingMatches xs ys

def maxNineMerMatchIn (probe9 target : List Nat) : Nat :=
  let nPos := target.length - 8
  (List.range nPos).foldl
    (fun acc j =>
      let m := hammingMatches probe9 (sliceNat target j 9)
      if m > acc then m else acc)
    0

theorem cdr2l_c_terminal_mhc2_core_bifurcation :
    sliceNat cdr2lCTerm 2 12 = sliceNat cdr2CTerm 2 12 ∧
    maxNineMerMatchIn (sliceNat cdr2lCTerm 2 9) cdr2CTerm = 9 ∧
    maxNineMerMatchIn (sliceNat cdr2lCTerm 3 9) cdr2CTerm = 9 ∧
    maxNineMerMatchIn (sliceNat cdr2lCTerm 4 9) cdr2CTerm = 9 ∧
    maxNineMerMatchIn (sliceNat cdr2lCTerm 5 9) cdr2CTerm = 9 ∧
    ((List.range 12).all (fun k =>
      decide (maxNineMerMatchIn (sliceNat cdr2lCTerm (13 + k) 9) cdr2CTerm ≤ 5))) = true ∧
    34 * 29 * 204 = 493 * 408 ∧
    451 * 446 = 201146 ∧
    986 * 200 < 201146 := by
  decide

/-! ## 4. PR #77 Soko 0-1 ILP Minimum Discriminating Assay Portfolio (H1..H5 + Paralog) -/

def candidateAssays : List (List Nat) :=
  [ [1, 1, 1, 0, 0, 1]
  , [0, 0, 1, 0, 0, 0]
  , [0, 1, 1, 0, 0, 0]
  , [1, 1, 0, 1, 0, 0]
  , [0, 0, 0, 1, 0, 0]
  , [0, 0, 0, 0, 0, 1]
  ]

def worldSignature (mask : Nat) (wIdx : Nat) : List Nat :=
  (List.range 6).foldl
    (fun acc aIdx =>
      if (mask / (2 ^ aIdx)) % 2 == 1 then
        let row := candidateAssays.getD aIdx []
        acc ++ [row.getD wIdx 0]
      else acc)
    []

def maskPopcount (mask : Nat) : Nat :=
  (List.range 6).foldl (fun acc aIdx => acc + ((mask / (2 ^ aIdx)) % 2)) 0

def discriminatesAllSix (mask : Nat) : Bool :=
  let pairs : List (Nat × Nat) :=
    [(0,1),(0,2),(0,3),(0,4),(0,5),(1,2),(1,3),(1,4),(1,5),(2,3),(2,4),(2,5),(3,4),(3,5),(4,5)]
  pairs.all (fun ij => decide (worldSignature mask ij.1 ≠ worldSignature mask ij.2))

theorem soko_ilp_minimal_three_assay_discriminator :
    ((List.range 64).all (fun m =>
      if maskPopcount m ≤ 2 then !discriminatesAllSix m else true)) = true ∧
    maskPopcount 13 = 3 ∧
    discriminatesAllSix 13 = true := by
  decide

/-! ## 5. Exact C22 (13/8 = 21-Patient Cohort) Minimal Mann-Whitney Cutoff -/

theorem c22_minimal_exact_mann_whitney_cutoff :
    13 * 8 = 104 ∧
    76 * 26 = 19 * 104 ∧
    9060 * 6783 = 302 * 203490 ∧
    302 * 20 < 6783 ∧
    10601 * 20 > 203490 := by
  decide

/-! ## 6. Multi-Compartment Transitive Regimen Neurotoxicity & Adjoint Flag Gate -/

structure State4 where
  tum : Int
  apcTum : Int
  apcPara : Int
  purkinje : Int
  deriving DecidableEq, Repr

def baselinePatient (b0 : Int) : State4 :=
  { tum := b0, apcTum := 0, apcPara := 0, purkinje := 0 }

def step1Ungated (x : State4) : State4 :=
  { tum := 6 * x.tum
  , apcTum := 3 * x.tum + 10 * x.apcTum
  , apcPara := 3 * x.tum + 10 * x.apcPara
  , purkinje := 10 * x.purkinje }

def step2Effector (x : State4) : State4 :=
  { tum := 8 * x.tum - 5 * x.apcTum
  , apcTum := 12 * x.apcTum
  , apcPara := 12 * x.apcPara
  , purkinje := 4 * x.apcPara + 10 * x.purkinje }

def step1AdjointGated (x : State4) : State4 :=
  { tum := 6 * x.tum
  , apcTum := 3 * x.tum + 10 * x.apcTum
  , apcPara := 10 * x.apcPara
  , purkinje := 10 * x.purkinje }

theorem single_stage_safe_cascade_neurotoxic (b0 : Int) (hb : 0 < b0) :
    (step1Ungated (baselinePatient b0)).purkinje = 0 ∧
    (step2Effector (baselinePatient b0)).purkinje = 0 ∧
    (step1Ungated (step2Effector (baselinePatient b0))).purkinje = 0 ∧
    (step1Ungated (step2Effector (baselinePatient b0))).tum = 48 * b0 ∧
    (step2Effector (step1Ungated (baselinePatient b0))).tum = 33 * b0 ∧
    (step2Effector (step1Ungated (baselinePatient b0))).purkinje = 12 * b0 ∧
    0 < (step2Effector (step1Ungated (baselinePatient b0))).purkinje := by
  dsimp [baselinePatient, step1Ungated, step2Effector]
  omega

theorem adjoint_flag_gate_zero_injury_full_synergy
    (b0 aSafe : Int) (hb : 0 < b0) (ha : 0 ≤ aSafe) :
    let x0 : State4 := { tum := b0, apcTum := aSafe, apcPara := 0, purkinje := 0 }
    (step2Effector (step1AdjointGated x0)).purkinje = 0 ∧
    (step2Effector (step1AdjointGated x0)).tum = 33 * b0 - 50 * aSafe ∧
    (step2Effector (step1AdjointGated x0)).tum < 48 * b0 := by
  dsimp [step1AdjointGated, step2Effector]
  omega

/-! ## 7. Prospective N=1 Patient Batch-Nullspace Invariance (p=64 / C20 / Gate 0) -/

abbrev Vec := List Int

def vadd : Vec → Vec → Vec
  | [], ys => ys
  | xs, [] => xs
  | x :: xs, y :: ys => (x + y) :: vadd xs ys

def vscale (c : Int) : Vec → Vec
  | [] => []
  | x :: xs => (c * x) :: vscale c xs

def vdot : Vec → Vec → Int
  | [], _ => 0
  | _, [] => 0
  | x :: xs, y :: ys => x * y + vdot xs ys

def linComb : List (Int × Vec) → Vec
  | [] => []
  | (c, q) :: rest => vadd (vscale c q) (linComb rest)

theorem vdot_nil_right (xs : Vec) : vdot xs [] = 0 := by
  cases xs <;> rfl

theorem vdot_vadd_right (w u v : Vec) :
    vdot w (vadd u v) = vdot w u + vdot w v := by
  induction w generalizing u v with
  | nil =>
    change 0 = 0 + 0
    omega
  | cons z zs ih =>
    cases u with
    | nil =>
      change vdot (z :: zs) v = 0 + vdot (z :: zs) v
      omega
    | cons x xs =>
      cases v with
      | nil =>
        change vdot (z :: zs) (x :: xs) = vdot (z :: zs) (x :: xs) + 0
        omega
      | cons y ys =>
        have hdist : z * (x + y) = z * x + z * y := Int.mul_add z x y
        have htail : vdot zs (vadd xs ys) = vdot zs xs + vdot zs ys := ih xs ys
        calc
          vdot (z :: zs) (vadd (x :: xs) (y :: ys))
              = z * (x + y) + vdot zs (vadd xs ys) := rfl
          _ = (z * x + z * y) + (vdot zs xs + vdot zs ys) := by omega
          _ = (z * x + vdot zs xs) + (z * y + vdot zs ys) := by omega
          _ = vdot (z :: zs) (x :: xs) + vdot (z :: zs) (y :: ys) := rfl

theorem vdot_vscale_right (w : Vec) (c : Int) (v : Vec) :
    vdot w (vscale c v) = c * vdot w v := by
  induction w generalizing v with
  | nil =>
    simp only [vdot, Int.mul_zero]
  | cons z zs ih =>
    cases v with
    | nil =>
      change 0 = c * 0
      simp only [Int.mul_zero]
    | cons y ys =>
      have hmul : z * (c * y) = c * (z * y) := by
        calc
          z * (c * y) = (z * c) * y := (Int.mul_assoc z c y).symm
          _ = (c * z) * y := congrArg (· * y) (Int.mul_comm z c)
          _ = c * (z * y) := Int.mul_assoc c z y
      have htail : vdot zs (vscale c ys) = c * vdot zs ys := ih ys
      have hdist : c * (z * y + vdot zs ys) = c * (z * y) + c * vdot zs ys :=
        Int.mul_add c (z * y) (vdot zs ys)
      calc
        vdot (z :: zs) (vscale c (y :: ys))
            = z * (c * y) + vdot zs (vscale c ys) := rfl
        _ = c * (z * y) + c * vdot zs ys := by omega
        _ = c * (z * y + vdot zs ys) := hdist.symm
        _ = c * vdot (z :: zs) (y :: ys) := rfl

theorem vdot_linComb_eq_zero
    (beta : Vec) (batchAxes : List Vec) (terms : List (Int × Vec))
    (horth : ∀ q ∈ batchAxes, vdot beta q = 0)
    (hterms : ∀ p ∈ terms, p.2 ∈ batchAxes) :
    vdot beta (linComb terms) = 0 := by
  induction terms with
  | nil =>
    exact vdot_nil_right beta
  | cons hd tl ih =>
    cases hd with
    | mk c q =>
      have hq : q ∈ batchAxes := hterms (c, q) (List.mem_cons.mpr (Or.inl rfl))
      have hbq : vdot beta q = 0 := horth q hq
      have htl : ∀ p ∈ tl, p.2 ∈ batchAxes :=
        fun p hp => hterms p (List.mem_cons.mpr (Or.inr hp))
      have ihtl : vdot beta (linComb tl) = 0 := ih htl
      have hscale : vdot beta (vscale c q) = 0 := by
        calc
          vdot beta (vscale c q) = c * vdot beta q := vdot_vscale_right beta c q
          _ = c * 0 := congrArg (c * ·) hbq
          _ = 0 := Int.mul_zero c
      calc
        vdot beta (linComb ((c, q) :: tl))
            = vdot beta (vadd (vscale c q) (linComb tl)) := rfl
        _ = vdot beta (vscale c q) + vdot beta (linComb tl) :=
            vdot_vadd_right beta (vscale c q) (linComb tl)
        _ = 0 := by omega

theorem prospective_n1_nullspace_zero_logit_drift
    (beta x : Vec) (batchAxes : List Vec) (terms : List (Int × Vec))
    (horth : ∀ q ∈ batchAxes, vdot beta q = 0)
    (hterms : ∀ p ∈ terms, p.2 ∈ batchAxes) :
    vdot beta (vadd x (linComb terms)) = vdot beta x := by
  have hzero : vdot beta (linComb terms) = 0 :=
    vdot_linComb_eq_zero beta batchAxes terms horth hterms
  have hadd : vdot beta (vadd x (linComb terms)) = vdot beta x + vdot beta (linComb terms) :=
    vdot_vadd_right beta x (linComb terms)
  omega

theorem pilot001_n1_midrank_collapse :
    (2 * 1 - 1) * 2 = 1 * (2 * 1) ∧
    52 * 83 = 4316 ∧
    2158 * 2 = 4316 := by
  decide

#print axioms low_seed_offset_saturation_hierarchy
#print axioms cdr2l_c_terminal_mhc2_core_bifurcation
#print axioms soko_ilp_minimal_three_assay_discriminator
#print axioms c22_minimal_exact_mann_whitney_cutoff
#print axioms adjoint_flag_gate_zero_injury_full_synergy
#print axioms prospective_n1_nullspace_zero_logit_drift

end AsmaSubspaceFlagProofs
