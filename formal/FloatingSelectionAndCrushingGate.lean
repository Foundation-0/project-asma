/-
  formal/FloatingSelectionAndCrushingGate.lean
  Zero-dependency stock Lean 4 (`Init`) formal verification module.

  Toolchain: pinned in formal/lean-toolchain (leanprover/lean4:v4.35.0).
  Imports:   none (stock Lean 4 core `Init` only; zero external dependencies, pure 7-bit ASCII).
  Discipline: complete kernel-checked proofs with zero unfinished holes or extra postulates.

  Theorems proved:
  1. `floating_r19_gap_factorization`:
     Cross-multiplied difference between floating pure selection `q(p; 19, 0)` and
     conversion `C25` `q(p; 11, 1/4)` factors identically as `(14*pN - pD)*(pD - pN)`.
  2. `r19_continuum_quadratic_identity` & `r19_continuum_sos_completion`:
     Cross-multiplied `1/60` ceiling margin `2*(18*pN + pD)*(10*pN + pD) - 15*(14*pN - pD)*(pD - pN)`
     equals `570*pN^2 - 169*pN*pD + 17*pD^2`, whose `2280x` multiple completes the square as
     `(1140*pN - 169*pD)^2 + 10199*pD^2` (discriminant `Delta = -10199 < 0`).
  3. `r19_quadratic_strictly_positive` & `r19_two_sided_continuum_impossibility`:
     For EVERY rational `p = pN / pD` in `[1/20, 1]` (`0 < pD`, `pD <= 20*pN`),
     `|q(p; 19, 0) - q(p; 11, 1/4)| / 2 < 1/60` holds strictly on both branches.
  4. `remedy_single_channel_below_quadratic_root`, `unit_fraction_1_26_sharp_witness`,
     & `remedy_two_channel_19_240_universal`:
     Proves universally over ALL rationals `p = pN / pD` in `(0, 1)` satisfying
     `125*pN^2 + 328*pN*pD - 13*pD^2 < 0` (`p < ~0.039051`, with `p = 1/26` certified as the
     largest unit-fraction witness since `p = 1/25` gives `+200 > 0`) and ALL rationals
     `r_S = rN / rD >= 0` that single-channel anchor `p_0 = 1/5` restores `> 1/30` full gap,
     and proves universally over ALL `r_S = rN / rD >= 0` that Channel-2 newly-converted
     fraction `u` at `p = 1/20` achieves `19/120` full gap (`19/240 > 1/60`).
  5. `sticky_shortcut_crushes_on_true_gate` & `crushing_gate_wall_quorum_necessary`:
     Formalizes the standalone synthetic quorum-pull crushing-gate automaton (`switchReq = 9, pullAura = 3`),
     proving that the 3-step sticky shortcut from `w = 2` crushes on turn-end re-evaluation
     and that `crossGate` cannot succeed unless `switchReq <= walls + (mobileSw - pullAura)`.
-/

namespace FloatingSelectionAndCrushingGate

private theorem neg_sq_eq (u : Int) : (-u) * (-u) = u * u := by
  rw [Int.neg_mul, Int.mul_neg, Int.neg_neg]

private theorem zero_mul_int (b : Int) : (0 : Int) * b = 0 := by
  have h1 : ((1 : Int) - 1) * b = 1 * b - 1 * b := Int.sub_mul 1 1 b
  have h0 : (1 : Int) - 1 = 0 := by decide
  rw [h0] at h1
  omega

private theorem nonneg_mul_pos {a b : Int} (ha : 0 <= a) (hb : 0 < b) : 0 <= a * b := by
  have htrich : 0 < a \/ a = 0 := by omega
  cases htrich with
  | inl hp =>
    have hm : 0 < a * b := Int.mul_pos hp hb
    omega
  | inr hz =>
    rw [hz, zero_mul_int b]
    decide

private theorem sq_nonneg (x : Int) : 0 <= x * x := by
  have htrich : 0 < x \/ x = 0 \/ 0 < -x := by omega
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

private theorem mul3_swap12 (x y z : Int) : x * (y * z) = y * (x * z) :=
  calc
    x * (y * z) = (x * y) * z := (Int.mul_assoc x y z).symm
    _ = (y * x) * z := congrArg (fun t => t * z) (Int.mul_comm x y)
    _ = y * (x * z) := Int.mul_assoc y x z

private theorem swap_outer (x y z : Int) : x * (y * z) = z * (y * x) :=
  calc
    x * (y * z) = x * (z * y) := congrArg (fun t => x * t) (Int.mul_comm y z)
    _ = z * (x * y) := mul3_swap12 x z y
    _ = z * (y * x) := congrArg (fun t => z * t) (Int.mul_comm x y)

private theorem int_mul_sub (a b c : Int) : a * (b - c) = a * b - a * c :=
  calc
    a * (b - c) = (b - c) * a := Int.mul_comm a (b - c)
    _ = b * a - c * a := Int.sub_mul b c a
    _ = a * b - a * c := by rw [Int.mul_comm b a, Int.mul_comm c a]

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
    -2 * den < 15 * gap /\ 15 * gap < 2 * den := by
  dsimp only
  rw [floating_r19_gap_factorization pN pD]
  have hUpPos : 0 < 2 * ((18 * pN + pD) * (10 * pN + pD)) - 15 * ((14 * pN - pD) * (pD - pN)) := by
    rw [r19_continuum_quadratic_identity pN pD]
    exact r19_quadratic_strictly_positive pN pD hpD
  have hpNPos : 0 < pN := by omega
  have h30Pos : 0 < 30 * pN + 57 * pD := by omega
  have hSubNonneg : 0 <= (20 * pN - pD) * (30 * pN + 57 * pD) :=
    nonneg_mul_pos (by omega) h30Pos
  have hPDPos : 0 < pN * pD := Int.mul_pos hpNPos hpD
  have hD2Pos : 0 < pD * pD := Int.mul_pos hpD hpD
  have hLowDecomp := r19_lower_branch_decomposition pN pD
  omega

def qSelNum (pN _pD rN _rD : Int) : Int := rN * pN
def qSelDen (pN pD rN rD : Int) : Int := rN * pN + rD * (pD - pN)
def qC25Num (pN pD : Int) : Int := 43 * pN + pD
def qC25Den (pN pD : Int) : Int := 4 * (10 * pN + pD)

private theorem expand_scaled_diff (K X Y Z : Int) :
    K * (30 * (X - Y) - Z) = (30 * (K * X) - 30 * (K * Y)) - K * Z :=
  calc
    K * (30 * (X - Y) - Z)
      = K * (30 * (X - Y)) - K * Z := int_mul_sub K (30 * (X - Y)) Z
    _ = 30 * (K * (X - Y)) - K * Z := by rw [mul3_swap12 K 30 (X - Y)]
    _ = 30 * (K * X - K * Y) - K * Z := by rw [int_mul_sub K X Y]
    _ = (30 * (K * X) - 30 * (K * Y)) - K * Z := by rw [int_mul_sub 30 (K * X) (K * Y)]

private theorem telescoping_margin_identity (A B M N D P : Int) :
    M * (30 * (A * D - N * B) - B * D) =
      D * (30 * (A * M - P * B) - B * M) + (30 * B) * (P * D - N * M) := by
  have hL := expand_scaled_diff M (A * D) (N * B) (B * D)
  have hR1 := expand_scaled_diff D (A * M) (P * B) (B * M)
  have hR2 : (30 * B) * (P * D - N * M) = 30 * (B * (P * D)) - 30 * (B * (N * M)) :=
    calc
      (30 * B) * (P * D - N * M)
        = (30 * B) * (P * D) - (30 * B) * (N * M) := int_mul_sub (30 * B) (P * D) (N * M)
      _ = 30 * (B * (P * D)) - 30 * (B * (N * M)) := by
            rw [Int.mul_assoc 30 B (P * D), Int.mul_assoc 30 B (N * M)]
  have h1 : D * (A * M) = M * (A * D) := swap_outer D A M
  have h2 : D * (B * M) = M * (B * D) := swap_outer D B M
  have h3 : D * (P * B) = B * (P * D) := swap_outer D P B
  have h4 : B * (N * M) = M * (N * B) := swap_outer B N M
  rw [hL, hR1, hR2, h1, h2, h3, h4]
  omega

private theorem remedy_a_boundary_r20 (pN pD : Int) :
    30 * (qC25Num pN pD * (19 * pN + pD) - (20 * pN) * qC25Den pN pD)
      - qC25Den pN pD * (19 * pN + pD) =
    -2 * (125 * (pN * pN) + 328 * (pN * pD) - 13 * (pD * pD)) := by
  unfold qC25Num qC25Den
  have h43 : 43 * pN + pD = 43 * pN + 1 * pD := by omega
  have h19 : 19 * pN + pD = 19 * pN + 1 * pD := by omega
  have h20 : 20 * pN = 20 * pN + 0 * pD := by omega
  have h40 : 4 * (10 * pN + pD) = 40 * pN + 4 * pD := by omega
  rw [h43, h19, h20, h40]
  rw [expand_binom 43 1 19 1 pN pD, expand_binom 20 0 40 4 pN pD, expand_binom 40 4 19 1 pN pD]
  have c1 : (43 : Int) * 19 = 817 := by decide
  have c2 : (43 : Int) * 1 = 43 := by decide
  have c3 : (1 : Int) * 19 = 19 := by decide
  have c4 : (1 : Int) * 1 = 1 := by decide
  have c5 : (20 : Int) * 40 = 800 := by decide
  have c6 : (20 : Int) * 4 = 80 := by decide
  have c7 : (0 : Int) * 40 = 0 := by decide
  have c8 : (0 : Int) * 4 = 0 := by decide
  have c9 : (40 : Int) * 19 = 760 := by decide
  have c10 : (40 : Int) * 1 = 40 := by decide
  have c11 : (4 : Int) * 19 = 76 := by decide
  have c12 : (4 : Int) * 1 = 4 := by decide
  rw [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]
  omega

private theorem remedy_a_monotonicity_r20 (pN pD rN rD : Int) :
    (20 * pN) * qSelDen pN pD rN rD - qSelNum pN pD rN rD * (19 * pN + pD) =
      (20 * rD - rN) * (pN * (pD - pN)) := by
  unfold qSelNum qSelDen
  have hL : (20 * pN) * (rN * pN + rD * (pD - pN)) =
      rN * (20 * (pN * pN)) + (20 * rD) * (pN * (pD - pN)) :=
    calc
      (20 * pN) * (rN * pN + rD * (pD - pN))
        = (20 * pN) * (rN * pN) + (20 * pN) * (rD * (pD - pN)) :=
            Int.mul_add (20 * pN) (rN * pN) (rD * (pD - pN))
      _ = (20 * rN) * (pN * pN) + (20 * rD) * (pN * (pD - pN)) := by
            rw [mul_xy 20 rN pN pN, mul_xy 20 rD pN (pD - pN)]
      _ = (rN * 20) * (pN * pN) + (20 * rD) * (pN * (pD - pN)) := by
            rw [Int.mul_comm 20 rN]
      _ = rN * (20 * (pN * pN)) + (20 * rD) * (pN * (pD - pN)) := by
            rw [Int.mul_assoc rN 20 (pN * pN)]
  have hSplit : 19 * pN + pD = 20 * pN + (pD - pN) := by omega
  have hM : (rN * pN) * (19 * pN + pD) =
      rN * (20 * (pN * pN)) + rN * (pN * (pD - pN)) :=
    calc
      (rN * pN) * (19 * pN + pD)
        = (rN * pN) * (20 * pN + (pD - pN)) := by rw [hSplit]
      _ = (rN * pN) * (20 * pN) + (rN * pN) * (pD - pN) :=
            Int.mul_add (rN * pN) (20 * pN) (pD - pN)
      _ = (rN * 20) * (pN * pN) + rN * (pN * (pD - pN)) := by
            rw [mul_xy rN 20 pN pN, Int.mul_assoc rN pN (pD - pN)]
      _ = rN * (20 * (pN * pN)) + rN * (pN * (pD - pN)) := by
            rw [Int.mul_assoc rN 20 (pN * pN)]
  have hR : (20 * rD - rN) * (pN * (pD - pN)) =
      (20 * rD) * (pN * (pD - pN)) - rN * (pN * (pD - pN)) :=
    Int.sub_mul (20 * rD) rN (pN * (pD - pN))
  rw [hL, hM, hR]
  omega

theorem remedy_single_channel_below_quadratic_root (pN pD rN rD : Int)
    (hpN : 0 < pN) (hpD : pN < pD) (hrN : 0 <= rN) (hrD : 0 < rD)
    (hQuad : 125 * (pN * pN) + 328 * (pN * pD) - 13 * (pD * pD) < 0) :
    (0 < qSelDen 1 5 rN rD /\
      5 * qSelDen 1 5 rN rD < 30 * (qSelNum 1 5 rN rD * 5 - 4 * qSelDen 1 5 rN rD)) \/
    (0 < qC25Den pN pD * qSelDen pN pD rN rD /\
      qC25Den pN pD * qSelDen pN pD rN rD <
        30 * (qC25Num pN pD * qSelDen pN pD rN rD - qSelNum pN pD rN rD * qC25Den pN pD)) := by
  have hSplit : 20 * rD < rN \/ rN <= 20 * rD := by omega
  cases hSplit with
  | inl hHigh =>
    left
    unfold qSelNum qSelDen
    have hc51 : (5 : Int) - 1 = 4 := by decide
    rw [hc51]
    omega
  | inr hLe =>
    right
    have hDenC25 : 0 < qC25Den pN pD := by unfold qC25Den; omega
    have hDen20 : 0 < 19 * pN + pD := by omega
    have hDenSel : 0 < qSelDen pN pD rN rD := by
      unfold qSelDen
      have h1 : 0 <= rN * pN := nonneg_mul_pos hrN hpN
      have h2 : 0 < rD * (pD - pN) := Int.mul_pos hrD (by omega)
      omega
    refine And.intro (Int.mul_pos hDenC25 hDenSel) ?_
    have hY : 0 < 30 * (qC25Num pN pD * (19 * pN + pD) - (20 * pN) * qC25Den pN pD)
        - qC25Den pN pD * (19 * pN + pD) := by
      have hB := remedy_a_boundary_r20 pN pD
      omega
    have hZ : 0 <= (20 * pN) * qSelDen pN pD rN rD - qSelNum pN pD rN rD * (19 * pN + pD) := by
      have hM := remedy_a_monotonicity_r20 pN pD rN rD
      have hPosFactor : 0 < pN * (pD - pN) := Int.mul_pos hpN (by omega)
      have hNonneg : 0 <= (20 * rD - rN) * (pN * (pD - pN)) :=
        nonneg_mul_pos (by omega) hPosFactor
      omega
    have hDY : 0 < qSelDen pN pD rN rD *
        (30 * (qC25Num pN pD * (19 * pN + pD) - (20 * pN) * qC25Den pN pD)
          - qC25Den pN pD * (19 * pN + pD)) :=
      Int.mul_pos hDenSel hY
    have h30B : 0 < 30 * qC25Den pN pD := by omega
    have hBZ : 0 <= ((20 * pN) * qSelDen pN pD rN rD - qSelNum pN pD rN rD * (19 * pN + pD)) *
        (30 * qC25Den pN pD) :=
      nonneg_mul_pos hZ h30B
    rw [Int.mul_comm _ (30 * qC25Den pN pD)] at hBZ
    have hTel := telescoping_margin_identity
      (qC25Num pN pD) (qC25Den pN pD) (19 * pN + pD)
      (qSelNum pN pD rN rD) (qSelDen pN pD rN rD) (20 * pN)
    have hMXPos : 0 < (19 * pN + pD) *
        (30 * (qC25Num pN pD * qSelDen pN pD rN rD - qSelNum pN pD rN rD * qC25Den pN pD)
          - qC25Den pN pD * qSelDen pN pD rN rD) := by
      omega
    have hDich :
        0 < 30 * (qC25Num pN pD * qSelDen pN pD rN rD - qSelNum pN pD rN rD * qC25Den pN pD)
          - qC25Den pN pD * qSelDen pN pD rN rD \/
        0 <= -(30 * (qC25Num pN pD * qSelDen pN pD rN rD - qSelNum pN pD rN rD * qC25Den pN pD)
          - qC25Den pN pD * qSelDen pN pD rN rD) := by
      omega
    cases hDich with
    | inl hGoalPos => omega
    | inr hNeg =>
      have hBad := nonneg_mul_pos hNeg hDen20
      rw [Int.neg_mul, Int.mul_comm _ (19 * pN + pD)] at hBad
      omega

theorem unit_fraction_1_26_sharp_witness :
    (125 : Int) * 1 + 328 * 25 - 13 * (25 * 25) = 200 /\
    (125 : Int) * 1 + 328 * 26 - 13 * (26 * 26) = -135 := by
  decide

def uNum (pN pD _rN rD cN _cD : Int) : Int := cN * rD * (pD - pN)
def uDen (pN pD rN rD cD : Int) : Int := (rN * pN + rD * (pD - pN)) * cD

theorem remedy_two_channel_19_240_universal (rN rD : Int) (hrN : 0 <= rN) (hrD : 0 < rD) :
    uNum 1 20 rN rD 0 1 = 0 /\
    0 < uDen 1 20 rN rD 1 /\
    0 < uDen 1 20 11 1 4 /\
    120 * (uNum 1 20 11 1 1 4 * uDen 1 20 rN rD 1 - uNum 1 20 rN rD 0 1 * uDen 1 20 11 1 4) =
      19 * (uDen 1 20 11 1 4 * uDen 1 20 rN rD 1) /\
    (19 : Int) * 60 > 1 * 240 := by
  unfold uNum uDen
  have hZero1 : (0 : Int) * rD * (20 - 1) = 0 := by
    rw [zero_mul_int rD, zero_mul_int (20 - 1)]
  have hDenPos : 0 < (rN * 1 + rD * (20 - 1)) * 1 := by
    have hc19 : (20 : Int) - 1 = 19 := by decide
    rw [hc19]
    omega
  refine And.intro hZero1 (And.intro hDenPos (And.intro (by decide) (And.intro ?_ (by decide))))
  rw [hZero1, zero_mul_int ((11 * 1 + 1 * (20 - 1)) * 4)]
  have hcA : (1 : Int) * 1 * (20 - 1) = 19 := by decide
  have hcB : ((11 : Int) * 1 + 1 * (20 - 1)) * 4 = 120 := by decide
  rw [hcA, hcB]
  omega

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
  if s.crushed = true \/ s.crossed = true then s
  else match a with
  | .engageHold =>
      if s.activeHold < 2 then { s with activeHold := s.activeHold + 1 } else s
  | .lockOnSwitch =>
      if 0 < s.mobileSw /\ s.walls < switchReq then
        { s with walls := s.walls + 1, mobileSw := s.mobileSw - 1 }
      else s
  | .deployAndLockReserve =>
      if 0 < s.reserveMob /\ s.walls + s.mobileSw < switchReq then
        { s with walls := s.walls + 1, reserveMob := s.reserveMob - 1 }
      else s
  | .crossGate =>
      if s.walls + s.mobileSw + s.activeHold < switchReq then s
      else
        let msAfter := s.mobileSw - pullAura
        if sticky = true \/ switchReq <= s.walls + msAfter then
          { s with mobileSw := msAfter, activeHold := 0, crossed := true, crushed := false }
        else
          { s with mobileSw := msAfter, activeHold := 0, crossed := false, crushed := true }

def runTrace (sticky : Bool) (switchReq pullAura : Nat) : ScaffoldState -> List GateAction -> ScaffoldState
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
    stickyOut.crossed = true /\ stickyOut.crushed = false /\ stickyOut.walls = 2 /\
    trueOut.crossed = false /\ trueOut.crushed = true /\
    safeOut.crossed = true /\ safeOut.crushed = false /\ safeOut.walls = 9 := by
  decide

theorem crushing_gate_wall_quorum_necessary (switchReq pullAura : Nat) (s : ScaffoldState)
    (hNotDone : s.crushed = false /\ s.crossed = false)
    (hCrossed : (stepGate false switchReq pullAura s .crossGate).crossed = true) :
    switchReq <= s.walls + (s.mobileSw - pullAura) := by
  unfold stepGate at hCrossed
  cases Classical.em (s.crushed = true \/ s.crossed = true) with
  | inl hDone =>
    rw [if_pos hDone] at hCrossed
    cases hDone with
    | inl hc => rw [hNotDone.1] at hc; contradiction
    | inr hx => rw [hNotDone.2] at hx; contradiction
  | inr hDone =>
    rw [if_neg hDone] at hCrossed
    dsimp only at hCrossed
    cases Classical.em (s.walls + s.mobileSw + s.activeHold < switchReq) with
    | inl hPre =>
      rw [if_pos hPre] at hCrossed
      rw [hNotDone.2] at hCrossed
      contradiction
    | inr hPre =>
      rw [if_neg hPre] at hCrossed
      dsimp only at hCrossed
      cases Classical.em (switchReq <= s.walls + (s.mobileSw - pullAura)) with
      | inl hPost => exact hPost
      | inr hPost =>
        have hFalse : Not (false = true \/ switchReq <= s.walls + (s.mobileSw - pullAura)) := by
          intro hOr
          cases hOr with
          | inl hf => contradiction
          | inr hp => exact hPost hp
        rw [if_neg hFalse] at hCrossed
        contradiction

#print axioms floating_r19_gap_factorization
#print axioms r19_continuum_quadratic_identity
#print axioms r19_continuum_sos_completion
#print axioms r19_quadratic_strictly_positive
#print axioms r19_lower_branch_decomposition
#print axioms r19_two_sided_continuum_impossibility
#print axioms remedy_single_channel_below_quadratic_root
#print axioms unit_fraction_1_26_sharp_witness
#print axioms remedy_two_channel_19_240_universal
#print axioms sticky_shortcut_crushes_on_true_gate
#print axioms crushing_gate_wall_quorum_necessary

end FloatingSelectionAndCrushingGate
