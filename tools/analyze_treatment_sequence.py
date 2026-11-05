"""Exact synthetic intervention-order experiment; no network or study values.

All quantities are invented arbitrary burden units. This is not a reproduction
of Gu et al., a survival model, or a treatment selector. See the protocol.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "protocols/rosen-treatment-sequence-assumptions.md"
OUTPUT = "registries/rosen-treatment-sequence-results.json"


def rational(value):
    if isinstance(value, bool) or not isinstance(value, (int, F)) or value < 0:
        raise ValueError("expected nonnegative exact rational")
    return F(value)


def state(values):
    if not isinstance(values, (list, tuple)) or len(values) != 2:
        raise ValueError("expected two-compartment state")
    return tuple(rational(v) for v in values)


def linear(values, matrix):
    values = state(values)
    if not isinstance(matrix, (list, tuple)) or len(matrix) != 2:
        raise ValueError("expected two-by-two nonnegative matrix")
    rows = tuple(state(row) for row in matrix)
    return tuple(sum(coef * value for coef, value in zip(row, values)) for row in rows)


def proportional(values, retain):
    values, retain = state(values), rational(retain)
    if retain > 1:
        raise ValueError("retention must not exceed one")
    return tuple(retain * v for v in values)


def fixed_residual(values, target):
    values, target = state(values), rational(target)
    total = sum(values)
    return proportional(values, min(F(1), target / total)) if total else values


def summary(values):
    values = state(values)
    total = sum(values)
    return {"sensitive": str(values[0]), "resistant": str(values[1]),
            "total": str(total),
            "resistant_fraction": str(values[1] / total) if total else None}


def compare(values, a, b, retain):
    values = state(values)
    a, b, retain = rational(a), rational(b), rational(retain)
    if not 0 < a <= b <= 1 or not 0 < retain <= 1 or not all(values):
        raise ValueError("comparison requires positive compartments, 0<a<=b<=1, 0<q<=1")
    matrix = ((a, F(0)), (F(0), b))
    target = retain * sum(values)
    treated = linear(values, matrix)
    before = linear(fixed_residual(values, target), matrix)
    after = fixed_residual(treated, target)
    prop_before = linear(proportional(values, retain), matrix)
    prop_after = proportional(treated, retain)
    ratio = after[1] / before[1]
    g = sum(treated) / sum(values)
    return {"initial": summary(values), "a": str(a), "b": str(b),
            "retain": str(retain), "target": str(target), "chemo_total_multiplier": str(g),
            "fixed_surgery_first": summary(before), "fixed_chemo_first": summary(after),
            "proportional_surgery_first": summary(prop_before),
            "proportional_chemo_first": summary(prop_after),
            "fixed_after_to_before_resistant_ratio": str(ratio),
            "predicted_capped_ratio": str(min(1 / retain, 1 / g)),
            "chemo_first_target_above_available_burden": target > sum(treated),
            "fraction_equal": summary(before)["resistant_fraction"] == summary(after)["resistant_fraction"],
            "proportional_equal": prop_before == prop_after,
            "fixed_direction": "equal" if after == before else "chemo_first_higher"}


def build_result():
    cases = []
    for f, a, b, q in product((F(1,100), F(1,10), F(1,2)),
                             (F(1,100), F(1,10), F(1,2), F(1)),
                             (F(1,2), F(1)), (F(1,100), F(1,10), F(1,2), F(1))):
        if a <= b:
            cases.append(compare((100*(1-f), 100*f), a, b, q))
    example = compare((F(90), F(10)), F(1,10), F(1), F(1,10))
    reversal = fixed_residual(linear((F(90), F(10)), ((F(1,10), 0), (0, 1))), F(1))
    growth_matrix = ((F(1,2), 0), (0, F(10)))
    growth_before = linear(fixed_residual((90,10),10),growth_matrix)
    growth_after = fixed_residual(linear((90,10),growth_matrix),10)
    return {
        "schema_version": 1, "status": "executed_synthetic_exact_arithmetic_not_study_analysis",
        "protocol": PROTOCOL, "protocol_sha256": sha256((ROOT / PROTOCOL).read_bytes()).hexdigest(),
        "implementation": "tools/analyze_treatment_sequence.py",
        "implementation_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "units": "invented_arbitrary_burden_units",
        "randomness": "none", "study_data_or_third_party_code_used": False,
        "matched_exposure": "one_identical_linear_chemo_operator_zero_intervention_gap",
        "example": example,
        "lower_second_sequence_target_example": {
            "target_after_chemo": "1", "chemo_first": summary(reversal),
            "after_to_before_resistant_ratio": str(reversal[1] / F(example['fixed_surgery_first']['resistant'])),
            "hypothetical_not_clinically_established": True},
        "growth_boundary_example": {
            "a": "1/2", "b": "10", "initial": summary((90,10)), "target": "10",
            "surgery_first": summary(growth_before), "chemo_first": summary(growth_after),
            "after_to_before_resistant_ratio": str(growth_after[1] / growth_before[1]),
            "note": "outside_contraction_grid_invented_linear_growth_not_fitted"},
        "grid_summary": {
            "cases": len(cases),
            "proportional_equal": sum(c['proportional_equal'] for c in cases),
            "fixed_equal": sum(c['fixed_direction'] == 'equal' for c in cases),
            "fixed_chemo_first_higher": sum(c['fixed_direction'] == 'chemo_first_higher' for c in cases),
            "fixed_fraction_equal": sum(c['fraction_equal'] for c in cases),
            "capped_formula_matches": sum(c['predicted_capped_ratio'] == c['fixed_after_to_before_resistant_ratio'] for c in cases),
            "target_above_available_burden": sum(c['chemo_first_target_above_available_burden'] for c in cases)},
        "synthetic_cases": cases,
        "unsupported": ["clinical_sequence_preference", "survival_or_cure", "full_Gu_model_reproduction",
                        "new_biological_discovery", "real_patient_parameter_identification"]}


if __name__ == "__main__":
    print(json.dumps(build_result(), indent=2))
