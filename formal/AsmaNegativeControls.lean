/-
  formal/AsmaNegativeControls.lean
  Stock Lean 4 module for Foundation-0/project-asma. It imports nothing.
-/

namespace AsmaNegativeControls

def qNum (pN pD r cN cD : Int) : Int :=
  r * pN * cD + cN * (pD - pN)

def qDen (pN pD r _cN cD : Int) : Int :=
  (r * pN + (pD - pN)) * cD

theorem chebyshev_19_560_sharp_collision_control :
    qNum 1 20 16 0 1 * 35 = 16 * qDen 1 20 16 0 1 ∧
    qNum 1 20 11 1 4 * 40 = 21 * qDen 1 20 11 1 4 ∧
    qNum 3 8 16 0 1 * 53 = 48 * qDen 3 8 16 0 1 ∧
    qNum 3 8 11 1 4 * 152 = 137 * qDen 3 8 11 1 4 ∧
    ((55 : Int) * 35 - 16 * 112) * 560 = 19 * (112 * 35) ∧
    ((21 : Int) * 112 - 55 * 40) * 560 = 19 * (40 * 112) ∧
    ((48 : Int) * 16112 - 14557 * 53) * 16112 = 35 * (53 * 16112) ∧
    ((14557 : Int) * 152 - 137 * 16112) * 16112 = 35 * (16112 * 152) ∧
    (35 : Int) * 560 < 19 * 16112 := by
  decide

theorem slope_10179_563920_sharp_collision_control :
    (((48 : Int) * 35 - 16 * 53) * 563920 - 2 * 10179 * (53 * 35)) * 56392 =
      23257 * (53 * 35 * 563920) ∧
    (((137 : Int) * 40 - 21 * 152) * 563920 + 2 * 10179 * (152 * 40)) * 56392 =
      23257 * (152 * 40 * 563920) := by
  decide

theorem patient_only_p0_control_mutation_rejected :
    qNum 0 1 11 1 4 * 4 = 1 * qDen 0 1 11 1 4 ∧
    qNum 1 20 11 1 4 * 40 = 21 * qDen 1 20 11 1 4 ∧
    qNum 1 5 11 1 4 * 5 = 4 * qDen 1 5 11 1 4 ∧
    qNum 3 8 11 1 4 * 152 = 137 * qDen 3 8 11 1 4 ∧
    qNum 0 1 11 0 1 * 1 = 0 * qDen 0 1 11 0 1 ∧
    (1 : Int) > 0 := by
  decide

theorem rank_one_probe_det_zero (s1 s2 a b : Int) :
    (s1 * a) * (s2 * b) - (s1 * b) * (s2 * a) = 0 := by
  have h : (s1 * a) * (s2 * b) = (s1 * b) * (s2 * a) :=
    calc
      (s1 * a) * (s2 * b) = s1 * (a * (s2 * b)) := Int.mul_assoc s1 a (s2 * b)
      _ = s1 * ((s2 * b) * a) := congrArg (fun t => s1 * t) (Int.mul_comm a (s2 * b))
      _ = s1 * (s2 * (b * a)) := congrArg (fun t => s1 * t) (Int.mul_assoc s2 b a)
      _ = s1 * (s2 * (a * b)) := congrArg (fun t => s1 * (s2 * t)) (Int.mul_comm b a)
      _ = s1 * ((a * b) * s2) := congrArg (fun t => s1 * t) (Int.mul_comm s2 (a * b))
      _ = s1 * (a * (b * s2)) := congrArg (fun t => s1 * t) (Int.mul_assoc a b s2)
      _ = s1 * ((b * s2) * a) := congrArg (fun t => s1 * t) (Int.mul_comm a (b * s2))
      _ = s1 * (b * (s2 * a)) := congrArg (fun t => s1 * t) (Int.mul_assoc b s2 a)
      _ = (s1 * b) * (s2 * a) := (Int.mul_assoc s1 b (s2 * a)).symm
  rw [h, Int.sub_self]

theorem multiplicative_gain_s_vs_c25_obstruction (s1 s2 a b : Int) :
    ¬ ((848 : Int) = s1 * a ∧ (1680 : Int) = s1 * b ∧ (3192 : Int) = s2 * a ∧ (5480 : Int) = s2 * b) := by
  intro ⟨hu1, hu2, hv1, hv2⟩
  have hdet : (848 : Int) * 5480 - 1680 * 3192 ≠ 0 := by decide
  apply hdet
  rw [hu1, hu2, hv1, hv2]
  exact rank_one_probe_det_zero s1 s2 a b

end AsmaNegativeControls
