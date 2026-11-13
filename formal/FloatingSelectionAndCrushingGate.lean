/-
  formal/FloatingSelectionAndCrushingGate.lean
  Zero-dependency stock Lean 4 (`Init`) formal verification module.
/-
  formal/FloatingSelectionAndCrushingGate.lean
  Stock Lean 4 (v4.35.0, Init only, zero imports, pure 7-bit ASCII) formal verification.
  Complete kernel-checked proofs with zero unfinished holes or extra postulates.
-/

namespace FloatingSelectionAndCrushingGate

private theorem neg_sq_eq (u : Int) : (-u) * (-u) = u * u := by
  rw [Int.neg_mul, Int.mul_neg, Int.neg_neg]

private theorem zero_mul_int (b : Int) : (0 : Int) * b = 0 := by
  have h1 : ((1 : Int) - 1) * b = 1 * b - 1 * b := Int.sub_mul 1 1 b
  have h0 : (1 : Int) - 1 = 0 := by decide
  rw [h0] at h1
  omega

private theorem sq_nonneg (x : Int) : 0 <= x * x := by
  have htrich : 0 < x \/ x = 0 \/ 0 < -x := by omega
  cases htrich with
  | inl hp => have hpos := Int.mul_pos hp hp; omega
  | inr hr =>
    cases hr with
    | inl hz => rw [hz]; decide
    | inr hn => have hpos := Int.mul_pos hn hn; rw [neg_sq_eq x] at hpos; omega

private theorem mul_xy (a b x y : Int) : (a * x) * (b * y) = (a * b) * (x * y) :=
  calc
    (a * x) * (b * y) = a * (x * (b * y)) := Int.mul_assoc a x (b * y)
    _ = a * ((x * b) * y) := congrArg (fun t => a * t) (Int.mul_assoc x b y).symm
    _ = a * ((b * x) * y) := congrArg (fun t => a * (t * y)) (Int.mul_comm x b)
    _ = a * (b * (x * y)) := congrArg (fun t => a * t) (Int.mul_assoc b x y)
    _ = (a * b) * (x * y) := (Int.mul_assoc a b (x * y)).symm

private theorem expand_binom (a b c d x y : Int) :
    (a * x + b * y) * (c * x + d * y) =
      (a * c) * (x * x) + (a * d + b * c) * (x * y) + (b * d) * (y * y) := by
  have h1 := mul_xy a c x x
  have h2 := mul_xy a d x y
  have h3 : (b * y) * (c * x) = (b * c) * (x * y) := by rw [mul_xy b c y x, Int.mul_comm y x]
  have h4 := mul_xy b d y y
  calc
    (a * x + b * y) * (c * x + d * y)
      = (a * x) * (c * x + d * y) + (b * y) * (c * x + d * y) := Int.add_mul (a * x) (b * y) (c * x + d * y)
    _ = ((a * x) * (c * x) + (a * x) * (d * y)) + ((b * y) * (c * x) + (b * y) * (d * y)) := by
          rw [Int.mul_add (a * x) (c * x) (d * y), Int.mul_add (b * y) (c * x) (d * y)]
    _ = ((a * c) * (x * x) + (a * d) * (x * y)) + ((b * c) * (x * y) + (b * d) * (y * y)) := by rw [h1, h2, h3, h4]
    _ = (a * c) * (x * x) + ((a * d) * (x * y) + (b * c) * (x * y)) + (b * d) * (y * y) := by omega
    _ = (a * c) * (x * x) + (a * d + b * c) * (x * y) + (b * d) * (y * y) := by rw [Int.add_mul (a * d) (b * c) (x * y)]

theorem floating_r19_gap_factorization (pN pD : Int) :
    (76 * pN) * (10 * pN + pD) - (43 * pN + pD) * (18 * pN + pD) = (14 * pN - pD) * (pD - pN) := by
  have hL1 : 76 * pN = 76 * pN + 0 * pD := by omega
  have h10 : 10 * pN + pD = 10 * pN + 1 * pD := by omega
  have h43 : 43 * pN + pD = 43 * pN + 1 * pD := by omega
  have h18 : 18 * pN + pD = 18 * pN + 1 * pD := by omega
  have hR1 : 14 * pN - pD = 14 * pN + (-1) * pD := by omega
  have hR2 : pD - pN = (-1) * pN + 1 * pD := by omega
  rw [hL1, h10, h43, h18, hR1, hR2]
  rw [expand_binom 76 0 10 1 pN pD, expand_binom 43 1 18 1 pN pD, expand_binom 14 (-1) (-1) 1 pN pD]
  omega

theorem r19_continuum_quadratic_identity (pN pD : Int) :
    2 * ((18 * pN + pD) * (10 * pN + pD)) - 15 * ((14 * pN - pD) * (pD - pN)) =
      570 * (pN * pN) - 169 * (pN * pD) + 17 * (pD * pD) := by
  have h18 : 18 * pN + pD = 18 * pN + 1 * pD := by omega
  have h10 : 10 * pN + pD = 10 * pN + 1 * pD := by omega
  have hR1 : 14 * pN - pD = 14 * pN + (-1) * pD := by omega
  have hR2 : pD - pN = (-1) * pN + 1 * pD := by omega
  rw [h18, h10, hR1, hR2, expand_binom 18 1 10 1 pN pD, expand_binom 14 (-1) (-1) 1 pN pD]
  omega

theorem r19_continuum_sos_completion (pN pD : Int) :
    2280 * (570 * (pN * pN) - 169 * (pN * pD) + 17 * (pD * pD)) =
      (1140 * pN - 169 * pD) * (1140 * pN - 169 * pD) + 10199 * (pD * pD) := by
  have hB : 1140 * pN - 169 * pD = 1140 * pN + (-169) * pD := by omega
  rw [hB, expand_binom 1140 (-169) 1140 (-169) pN pD]
  omega

theorem r19_quadratic_strictly_positive (pN pD : Int) (hpD : 0 < pD) :
    0 < 570 * (pN * pN) - 169 * (pN * pD) + 17 * (pD * pD) := by
  have hSq := sq_nonneg (1140 * pN - 169 * pD)
  have hD2 := Int.mul_pos hpD hpD
  have hSos := r19_continuum_sos_completion pN pD
  omega

theorem r19_lower_branch_decomposition (pN pD : Int) :
    4 * (2 * ((18 * pN + pD) * (10 * pN + pD)) + 15 * ((14 * pN - pD) * (pD - pN))) =
      (20 * pN - pD) * (30 * pN + 57 * pD) + 14 * (pN * pD) + 5 * (pD * pD) := by
  have h18 : 18 * pN + pD = 18 * pN + 1 * pD := by omega
  have h10 : 10 * pN + pD = 10 * pN + 1 * pD := by omega
  have hR1 : 14 * pN - pD = 14 * pN + (-1) * pD := by omega
  have hR2 : pD - pN = (-1) * pN + 1 * pD := by omega
  have h20 : 20 * pN - pD = 20 * pN + (-1) * pD := by omega
  rw [h18, h10, hR1, hR2, h20, expand_binom 18 1 10 1 pN pD, expand_binom 14 (-1) (-1) 1 pN pD, expand_binom 20 (-1) 30 57 pN pD]
  omega

theorem r19_two_sided_continuum_impossibility (pN pD : Int) (hpD : 0 < pD) (hLow : pD <= 20 * pN) :
    let gap := (76 * pN) * (10 * pN + pD) - (43 * pN + pD) * (18 * pN + pD)
    let den := (18 * pN + pD) * (10 * pN + pD)
    -2 * den < 15 * gap /\ 15 * gap < 2 * den := by
  dsimp only
  rw [floating_r19_gap_factorization pN pD]
  have hUpPos : 0 < 2 * ((18 * pN + pD) * (10 * pN + pD)) - 15 * ((14 * pN - pD) * (pD - pN)) := by
    rw [r19_continuum_quadratic_identity pN pD]
    exact r19_quadratic_strictly_positive pN pD hpD
  have hpNPos : 0 < pN := by omega
  have h30Pos : 0 < 30 * pN + 57 * pD := by omega
  have hSubNonneg : 0 <= (20 * pN - pD) * (30 * pN + 57 * pD) := by
    have htrich : 0 < 20 * pN - pD \/ 20 * pN - pD = 0 := by omega
    cases htrich with
    | inl hgt => have hp := Int.mul_pos hgt h30Pos; omega
    | inr heq => rw [heq, zero_mul_int (30 * pN + 57 * pD)]; decide
  have hPDPos := Int.mul_pos hpNPos hpD
  have hD2Pos := Int.mul_pos hpD hpD
  have hLowDecomp := r19_lower_branch_decomposition pN pD
  omega

theorem remedies_low_seed_1_26_and_two_channel_19_240 :
    (20 * 1) * 5 - 4 * (19 * 1 + 5) = 4 /\
    (125 : Int) * 1 + 328 * 25 - 13 * (25 * 25) = 8 /\
    (125 : Int) * 1 + 328 * 26 - 13 * (26 * 26) = -135 /\
    (1 : Int) * (20 - 1) * 240 = 2 * 19 * ((11 * 1 + (20 - 1)) * 4) /\
    (19 : Int) * 60 > 1 * 240 := by
  decide

structure ScaffoldState where
  walls : Nat
  mobileSw : Nat
  reserveMob : Nat
  activeHold : Nat
  crossed : Bool
  crushed : Bool
  deriving DecidableEq, Repr

inductive GateAction where
  | engageHold | lockOnSwitch | deployAndLockReserve | crossGate
  deriving DecidableEq, Repr

def stepGate (sticky : Bool) (switchReq pullAura : Nat) (s : ScaffoldState) (a : GateAction) : ScaffoldState :=
  if s.crushed = true \/ s.crossed = true then s
  else match a with
  | .engageHold => if s.activeHold < 2 then { s with activeHold := s.activeHold + 1 } else s
  | .lockOnSwitch => if 0 < s.mobileSw /\ s.walls < switchReq then { s with walls := s.walls + 1, mobileSw := s.mobileSw - 1 } else s
  | .deployAndLockReserve => if 0 < s.reserveMob /\ s.walls + s.mobileSw < switchReq then { s with walls := s.walls + 1, reserveMob := s.reserveMob - 1 } else s
  | .crossGate =>
      if s.walls + s.mobileSw + s.activeHold < switchReq then s
      else if sticky = true \/ switchReq <= s.walls + (s.mobileSw - pullAura) then
        { s with mobileSw := s.mobileSw - pullAura, activeHold := 0, crossed := true, crushed := false }
      else
        { s with mobileSw := s.mobileSw - pullAura, activeHold := 0, crushed := true }

def runTrace (sticky : Bool) (switchReq pullAura : Nat) : ScaffoldState -> List GateAction -> ScaffoldState
  | s, [] => s
  | s, a :: rest => runTrace sticky switchReq pullAura (stepGate sticky switchReq pullAura s a) rest

def lowWallInit : ScaffoldState := { walls := 2, mobileSw := 5, reserveMob := 2, activeHold := 0, crossed := false, crushed := false }
def stickyMirageTrace : List GateAction := [.engageHold, .engageHold, .crossGate]
def certifiedWallLockTrace : List GateAction :=
  [.lockOnSwitch, .lockOnSwitch, .lockOnSwitch, .lockOnSwitch, .lockOnSwitch, .deployAndLockReserve, .deployAndLockReserve, .crossGate]

theorem sticky_shortcut_crushes_on_true_gate :
    let stickyOut := runTrace true 9 3 lowWallInit stickyMirageTrace
    let trueOut   := runTrace false 9 3 lowWallInit stickyMirageTrace
    let safeOut   := runTrace false 9 3 lowWallInit certifiedWallLockTrace
    stickyOut.crossed = true /\ stickyOut.crushed = false /\ stickyOut.walls = 2 /\
    trueOut.crossed = false /\ trueOut.crushed = true /\
    safeOut.crossed = true /\ safeOut.crushed = false /\ safeOut.walls = 9 := by
  decide

theorem crushing_gate_wall_quorum_necessary (switchReq pullAura : Nat) (s : ScaffoldState)
    (hNotDone : s.crushed = false /\ s.crossed = false)
    (hCrossed : (stepGate false switchReq pullAura s .crossGate).crossed = true) :
    switchReq <= s.walls + (s.mobileSw - pullAura) := by
  unfold stepGate at hCrossed
  by_cases hDone : s.crushed = true \/ s.crossed = true
  . rw [if_pos hDone] at hCrossed
    cases hDone with
    | inl hc => rw [hNotDone.1] at hc; contradiction
    | inr hx => rw [hNotDone.2] at hx; contradiction
  . rw [if_neg hDone] at hCrossed
    dsimp only at hCrossed
    by_cases hPre : s.walls + s.mobileSw + s.activeHold < switchReq
    . rw [if_pos hPre] at hCrossed; rw [hNotDone.2] at hCrossed; contradiction
    . rw [if_neg hPre] at hCrossed
      by_cases hPost : switchReq <= s.walls + (s.mobileSw - pullAura)
      . exact hPost
      . have hFalse : Not (false = true \/ switchReq <= s.walls + (s.mobileSw - pullAura)) := by
          intro hOr
          cases hOr with
          | inl hf => contradiction
          | inr hp => exact hPost hp
        rw [if_neg hFalse] at hCrossed
        dsimp only at hCrossed
        contradiction

end FloatingSelectionAndCrushingGate
  Toolchain: pinned in formal/lean-toolchain (leanprover/lean4:v4.35.0).
  Imports:   none (stock Lean 4 core `Init` only; zero external dependencies).
  Discipline: complete kernel-checked proofs with zero unfinished holes or extra postulates.
-/

namespace FloatingSelectionAndCrushingGate

private theorem neg_sq_eq (u : Int) : (-u) * (-u) = u * u := by
  rw [Int.neg_mul, Int.mul_neg, Int.neg_neg]

private theorem zero_mul_int (b : Int) : (0 : Int) * b = 0 := by
  have h1 : ((1 : Int) - 1) * b = 1 * b - 1 * b := Int.sub_mul 1 1 b
  have h0 : (1 : Int) - 1 = 0 := by decide
  rw [h0] at h1
  omega

private theorem sq_nonneg (x : Int) : 0 <= x * x := by
  have htrich : 0 < x ∨ x = 0 ∨ 0 < -x := by omega
  cases htrich with
  | inl hp =>
    have hpos : 0 < x * x := Int.mul_pos hp hp
    omega
  | inr hrest =>
    cases hrest with
    | inl hz =>
      rw [hz]
      decide
    | inr hn =>
      have hpos : 0 < (-x) * (-x) := Int.mul_pos hn hn
      rw [neg_sq_eq x] at hpos
      omega

private theorem mul_xy (a b x y : Int) :
    (a * x) * (b * y) = (a * b) * (x * y) :=
  calc
    (a * x) * (b * y) = a * (x * (b * y)) := Int.mul_assoc a x (b * y)
    _ = a * ((x * b) * y) := congrArg (fun t => a * t) (Int.mul_assoc x b y).symm
    _ = a * ((b * x) * y) := congrArg (fun t => a * (t * y)) (Int.mul_comm x b)
    _ = a * (b * (x * y)) := congrArg (fun t => a * t) (Int.mul_assoc b x y)
    _ = (a * b) * (x * y) := (Int.mul_assoc a b (x * y)).symm

private theorem expand_binom (a b c d x y : Int) :
    (a * x + b * y) * (c * x + d * y) =
      ((a * c) * (x * x) + ((a * d) * (x * y) + (b * c) * (x * y))) + (b * d) * (y * y) := by
  have h1 : (a * x) * (c * x) = (a * c) * (x * x) := mul_xy a c x x
  have h2 : (a * x) * (d * y) = (a * d) * (x * y) := mul_xy a d x y
  have h3 : (b * y) * (c * x) = (b * c) * (x * y) := by
    rw [mul_xy b c y x, Int.mul_comm y x]
  have h4 : (b * y) * (d * y) = (b * d) * (y * y) := mul_xy b d y y
  calc
    (a * x + b * y) * (c * x + d * y)
      = (a * x) * (c * x + d * y) + (b * y) * (c * x + d * y) :=
          Int.add_mul (a * x) (b * y) (c * x + d * y)
    _ = ((a * x) * (c * x) + (a * x) * (d * y)) + ((b * y) * (c * x) + (b * y) * (d * y)) := by
          rw [Int.mul_add (a * x) (c * x) (d * y), Int.mul_add (b * y) (c * x) (d * y)]
    _ = ((a * c) * (x * x) + (a * d) * (x * y)) + ((b * c) * (x * y) + (b * d) * (y * y)) := by
          rw [h1, h2, h3, h4]
    _ = ((a * c) * (x * x) + ((a * d) * (x * y) + (b * c) * (x * y))) + (b * d) * (y * y) := by
          omega

theorem floating_r19_gap_factorization (pN pD : Int) :
    (76 * pN) * (10 * pN + pD) - (43 * pN + pD) * (18 * pN + pD) =
      (14 * pN - pD) * (pD - pN) := by
  have hL1 : 76 * pN = 76 * pN + 0 * pD := by omega
  have h10 : 10 * pN + pD = 10 * pN + 1 * pD := by omega
  have h43 : 43 * pN + pD = 43 * pN + 1 * pD := by omega
  have h18 : 18 * pN + pD = 18 * pN + 1 * pD := by omega
  have hR1 : 14 * pN - pD = 14 * pN + (-1) * pD := by omega
  have hR2 : pD - pN = (-1) * pN + 1 * pD := by omega
  rw [hL1, h10, h43, h18, hR1, hR2]
  rw [expand_binom 76 0 10 1 pN pD, expand_binom 43 1 18 1 pN pD, expand_binom 14 (-1) (-1) 1 pN pD]
  have c1 : (76 : Int) * 10 = 760 := by decide
  have c2 : (76 : Int) * 1 = 76 := by decide
  have c3 : (0 : Int) * 10 = 0 := by decide
  have c4 : (0 : Int) * 1 = 0 := by decide
  have c5 : (43 : Int) * 18 = 774 := by decide
  have c6 : (43 : Int) * 1 = 43 := by decide
  have c7 : (1 : Int) * 18 = 18 := by decide
  have c8 : (1 : Int) * 1 = 1 := by decide
  have c9 : (14 : Int) * (-1) = -14 := by decide
  have c10 : (14 : Int) * 1 = 14 := by decide
  have c11 : (-1 : Int) * (-1) = 1 := by decide
  have c12 : (-1 : Int) * 1 = -1 := by decide
  rw [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]
  omega

theorem r19_continuum_quadratic_identity (pN pD : Int) :
    2 * ((18 * pN + pD) * (10 * pN + pD)) - 15 * ((14 * pN - pD) * (pD - pN)) =
      570 * (pN * pN) - 169 * (pN * pD) + 17 * (pD * pD) := by
  have h18 : 18 * pN + pD = 18 * pN + 1 * pD := by omega
  have h10 : 10 * pN + pD = 10 * pN + 1 * pD := by omega
  have hR1 : 14 * pN - pD = 14 * pN + (-1) * pD := by omega
  have hR2 : pD - pN = (-1) * pN + 1 * pD := by omega
  rw [h18, h10, hR1, hR2]
  rw [expand_binom 18 1 10 1 pN pD, expand_binom 14 (-1) (-1) 1 pN pD]
  have c1 : (18 : Int) * 10 = 180 := by decide
  have c2 : (18 : Int) * 1 = 18 := by decide
  have c3 : (1 : Int) * 10 = 10 := by decide
  have c4 : (1 : Int) * 1 = 1 := by decide
  have c5 : (14 : Int) * (-1) = -14 := by decide
  have c6 : (14 : Int) * 1 = 14 := by decide
  have c7 : (-1 : Int) * (-1) = 1 := by decide
  have c8 : (-1 : Int) * 1 = -1 := by decide
  rw [c1, c2, c3, c4, c5, c6, c7, c8]
  omega

theorem r19_continuum_sos_completion (pN pD : Int) :
    2280 * (570 * (pN * pN) - 169 * (pN * pD) + 17 * (pD * pD)) =
      (1140 * pN - 169 * pD) * (1140 * pN - 169 * pD) + 10199 * (pD * pD) := by
  have hB : 1140 * pN - 169 * pD = 1140 * pN + (-169) * pD := by omega
  rw [hB, expand_binom 1140 (-169) 1140 (-169) pN pD]
  have c1 : (1140 : Int) * 1140 = 1299600 := by decide
  have c2 : (1140 : Int) * (-169) = -192660 := by decide
  have c3 : (-169 : Int) * 1140 = -192660 := by decide
  have c4 : (-169 : Int) * (-169) = 28561 := by decide
  rw [c1, c2, c3, c4]
  omega

theorem r19_quadratic_strictly_positive (pN pD : Int) (hpD : 0 < pD) :
    0 < 570 * (pN * pN) - 169 * (pN * pD) + 17 * (pD * pD) := by
  have hSq : 0 <= (1140 * pN - 169 * pD) * (1140 * pN - 169 * pD) :=
    sq_nonneg (1140 * pN - 169 * pD)
  have hD2 : 0 < pD * pD := Int.mul_pos hpD hpD
  have hSos := r19_continuum_sos_completion pN pD
  omega

theorem r19_lower_branch_decomposition (pN pD : Int) :
    4 * (2 * ((18 * pN + pD) * (10 * pN + pD)) + 15 * ((14 * pN - pD) * (pD - pN))) =
      (20 * pN - pD) * (30 * pN + 57 * pD) + 14 * (pN * pD) + 5 * (pD * pD) := by
  have h18 : 18 * pN + pD = 18 * pN + 1 * pD := by omega
  have h10 : 10 * pN + pD = 10 * pN + 1 * pD := by omega
  have hR1 : 14 * pN - pD = 14 * pN + (-1) * pD := by omega
  have hR2 : pD - pN = (-1) * pN + 1 * pD := by omega
  have h20 : 20 * pN - pD = 20 * pN + (-1) * pD := by omega
  rw [h18, h10, hR1, hR2, h20]
  rw [expand_binom 18 1 10 1 pN pD, expand_binom 14 (-1) (-1) 1 pN pD, expand_binom 20 (-1) 30 57 pN pD]
  have c1 : (18 : Int) * 10 = 180 := by decide
  have c2 : (18 : Int) * 1 = 18 := by decide
  have c3 : (1 : Int) * 10 = 10 := by decide
  have c4 : (1 : Int) * 1 = 1 := by decide
  have c5 : (14 : Int) * (-1) = -14 := by decide
  have c6 : (14 : Int) * 1 = 14 := by decide
  have c7 : (-1 : Int) * (-1) = 1 := by decide
  have c8 : (-1 : Int) * 1 = -1 := by decide
  have c9 : (20 : Int) * 30 = 600 := by decide
  have c10 : (20 : Int) * 57 = 1140 := by decide
  have c11 : (-1 : Int) * 30 = -30 := by decide
  have c12 : (-1 : Int) * 57 = -57 := by decide
  rw [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]
  omega

theorem r19_two_sided_continuum_impossibility (pN pD : Int)
    (hpD : 0 < pD) (hLow : pD <= 20 * pN) :
    let gap := (76 * pN) * (10 * pN + pD) - (43 * pN + pD) * (18 * pN + pD)
    let den := (18 * pN + pD) * (10 * pN + pD)
    -2 * den < 15 * gap ∧ 15 * gap < 2 * den := by
  dsimp only
  rw [floating_r19_gap_factorization pN pD]
  have hUpPos : 0 < 2 * ((18 * pN + pD) * (10 * pN + pD)) - 15 * ((14 * pN - pD) * (pD - pN)) := by
    rw [r19_continuum_quadratic_identity pN pD]
    exact r19_quadratic_strictly_positive pN pD hpD
  have hpNPos : 0 < pN := by omega
  have h30Pos : 0 < 30 * pN + 57 * pD := by omega
  have hSubNonneg : 0 <= (20 * pN - pD) * (30 * pN + 57 * pD) := by
    have htrich : 0 < 20 * pN - pD ∨ 20 * pN - pD = 0 := by omega
    cases htrich with
    | inl hgt =>
      have hp := Int.mul_pos hgt h30Pos
      omega
    | inr heq =>
      rw [heq, zero_mul_int (30 * pN + 57 * pD)]
      decide
  have hPDPos : 0 < pN * pD := Int.mul_pos hpNPos hpD
  have hD2Pos : 0 < pD * pD := Int.mul_pos hpD hpD
  have hLowDecomp := r19_lower_branch_decomposition pN pD
  omega

theorem remedies_low_seed_1_26_and_two_channel_19_240 :
    (20 * 1) * 5 - 4 * (19 * 1 + 5) = 4 ∧
    (125 : Int) * 1 + 328 * 25 - 13 * (25 * 25) = 8 ∧
    (125 : Int) * 1 + 328 * 26 - 13 * (26 * 26) = -135 ∧
    (1 : Int) * (20 - 1) * 240 = 2 * 19 * ((11 * 1 + (20 - 1)) * 4) ∧
    (19 : Int) * 60 > 1 * 240 := by
  decide

structure ScaffoldState where
  walls : Nat
  mobileSw : Nat
  reserveMob : Nat
  activeHold : Nat
  crossed : Bool
  crushed : Bool
  deriving DecidableEq, Repr

inductive GateAction where
  | engageHold
  | lockOnSwitch
  | deployAndLockReserve
  | crossGate
  deriving DecidableEq, Repr

def stepGate (sticky : Bool) (switchReq pullAura : Nat) (s : ScaffoldState) (a : GateAction) : ScaffoldState :=
  if s.crushed = true ∨ s.crossed = true then s
  else match a with
  | .engageHold =>
      if s.activeHold < 2 then { s with activeHold := s.activeHold + 1 } else s
  | .lockOnSwitch =>
      if 0 < s.mobileSw ∧ s.walls < switchReq then
        { s with walls := s.walls + 1, mobileSw := s.mobileSw - 1 }
      else s
  | .deployAndLockReserve =>
      if 0 < s.reserveMob ∧ s.walls + s.mobileSw < switchReq then
        { s with walls := s.walls + 1, reserveMob := s.reserveMob - 1 }
      else s
  | .crossGate =>
      if s.walls + s.mobileSw + s.activeHold < switchReq then s
      else
        if sticky = true ∨ switchReq <= s.walls + (s.mobileSw - pullAura) then
          { s with mobileSw := s.mobileSw - pullAura, activeHold := 0, crossed := true, crushed := false }
        else
          { s with mobileSw := s.mobileSw - pullAura, activeHold := 0, crossed := false, crushed := true }

def runTrace (sticky : Bool) (switchReq pullAura : Nat) : ScaffoldState → List GateAction → ScaffoldState
  | s, [] => s
  | s, a :: rest => runTrace sticky switchReq pullAura (stepGate sticky switchReq pullAura s a) rest

def lowWallInit : ScaffoldState :=
  { walls := 2, mobileSw := 5, reserveMob := 2, activeHold := 0, crossed := false, crushed := false }

def stickyMirageTrace : List GateAction :=
  [.engageHold, .engageHold, .crossGate]

def certifiedWallLockTrace : List GateAction :=
  [.lockOnSwitch, .lockOnSwitch, .lockOnSwitch, .lockOnSwitch, .lockOnSwitch,
   .deployAndLockReserve, .deployAndLockReserve, .crossGate]

theorem sticky_shortcut_crushes_on_true_gate :
    let stickyOut := runTrace true 9 3 lowWallInit stickyMirageTrace
    let trueOut   := runTrace false 9 3 lowWallInit stickyMirageTrace
    let safeOut   := runTrace false 9 3 lowWallInit certifiedWallLockTrace
    stickyOut.crossed = true ∧ stickyOut.crushed = false ∧ stickyOut.walls = 2 ∧
    trueOut.crossed = false ∧ trueOut.crushed = true ∧
    safeOut.crossed = true ∧ safeOut.crushed = false ∧ safeOut.walls = 9 := by
  decide

theorem crushing_gate_wall_quorum_necessary (switchReq pullAura : Nat) (s : ScaffoldState)
    (hNotDone : s.crushed = false ∧ s.crossed = false)
    (hCrossed : (stepGate false switchReq pullAura s .crossGate).crossed = true) :
    switchReq <= s.walls + (s.mobileSw - pullAura) := by
  unfold stepGate at hCrossed
  by_cases hDone : s.crushed = true ∨ s.crossed = true
  · rw [if_pos hDone] at hCrossed
    cases hDone with
    | inl hc => rw [hNotDone.1] at hc; contradiction
    | inr hx => rw [hNotDone.2] at hx; contradiction
  · rw [if_neg hDone] at hCrossed
    dsimp only at hCrossed
    by_cases hPre : s.walls + s.mobileSw + s.activeHold < switchReq
    · rw [if_pos hPre] at hCrossed
      rw [hNotDone.2] at hCrossed
      contradiction
    · rw [if_neg hPre] at hCrossed
      by_cases hPost : switchReq <= s.walls + (s.mobileSw - pullAura)
      · exact hPost
      · have hFalse : ¬ (false = true ∨ switchReq <= s.walls + (s.mobileSw - pullAura)) := by
          intro hOr
          cases hOr with
          | inl hf => contradiction
          | inr hp => exact hPost hp
        rw [if_neg hFalse] at hCrossed
        dsimp only at hCrossed
        contradiction

end FloatingSelectionAndCrushingGate
