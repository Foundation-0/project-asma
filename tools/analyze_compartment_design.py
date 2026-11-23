"""Original exact synthetic measurement-design calculation; no study inputs.

Run from any directory. The certificate is printed to stdout; this program
does not read study files, use a network, or import the independent checker.
"""

from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "protocols/compartment-measurement-design.md"
IMPLEMENTATION = "tools/analyze_compartment_design.py"
WORLDS = (("S", F(16), F(0)), ("C25", F(11), F(1, 4)),
          ("C50", F(6), F(1, 2)), ("C75", F(1), F(3, 4)))
ACTIONS = (("L", F(1, 10)), ("R", F(1, 5)), ("H", F(2, 5)))
BIAS = F(1, 20)
EPSILON = F(1, 60)
NOISE_MAX = F(1, 40)
NOISE_SWEEP = (F(0), F(1, 280), F(9, 1600), F(3, 448), F(3, 200),
               EPSILON, F(13, 700), NOISE_MAX)
UNSUPPORTED = ["biological_mechanism_identification",
               "arbitrarily_small_conversion_detection",
               "clinical_measurement_feasibility",
               "clinical_efficacy_or_treatment_selection",
               "novelty_to_literature", "independent_scientific_peer_review"]


def predicted_fraction(p, selection, conversion):
    """Select high/low expected weights, then convert selected low cells."""
    return (selection * p + conversion * (1 - p)) / (selection * p + 1 - p)


def critical_radius(differences):
    """Minimum residual error permitting collision after a common offset.

    The difference of two allowable biases lies in [-2 BIAS, 2 BIAS].
    Centering the prediction differences needs half their range; restricting
    that center to the bias interval can require an additional residual.
    Two competing residual errors together provide twice the error radius.
    """
    low, high = min(differences), max(differences)
    return max(F(0), (high - low) / 4,
               (high - 2 * BIAS) / 2, (-2 * BIAS - low) / 2)


def collision_at_boundary(left, right, design, predictions, radius):
    """Construct, rather than merely assert, one same-observation witness."""
    differences = [predictions[right][a] - predictions[left][a] for a in design]
    offset_difference = min(2 * BIAS, max(-2 * BIAS,
                             (min(differences) + max(differences)) / 2))
    biases = {left: offset_difference / 2, right: -offset_difference / 2}
    readings = {a: (predictions[left][a] + predictions[right][a]) / 2 for a in design}
    errors = {world: {a: readings[a] - predictions[world][a] - biases[world]
                      for a in design} for world in (left, right)}
    if any(abs(error) > radius for values in errors.values() for error in values.values()):
        raise RuntimeError("Constructed boundary witness exceeds its error radius")
    return {"readouts": {a: str(value) for a, value in readings.items()},
            "biases": {world: str(value) for world, value in biases.items()},
            "errors": {world: {a: str(value) for a, value in values.items()}
                       for world, values in errors.items()}}


def build_result():
    predictions = {world: {a: predicted_fraction(p, r, c) for a, p in ACTIONS}
                   for world, r, c in WORLDS}
    for world, r, c in WORLDS:
        if predicted_fraction(F(1, 5), r, c) != F(4, 5):
            raise RuntimeError("World violates the baseline constraint")
        for value in predictions[world].values():
            if not 0 <= value - BIAS - NOISE_MAX <= value + BIAS + NOISE_MAX <= 1:
                raise RuntimeError("Declared readout domain would require clipping")

    designs = []
    action_ids = [a for a, _ in ACTIONS]
    world_ids = [world for world, _, _ in WORLDS]
    for size in (1, 2):
        for design in combinations(action_ids, size):
            pairs = []
            for left, right in combinations(world_ids, 2):
                differences = [predictions[right][a] - predictions[left][a] for a in design]
                radius = critical_radius(differences)
                independent_radius = max(F(0), (max(map(abs, differences)) - 2 * BIAS) / 2)
                pairs.append({
                    "world_ids": [left, right],
                    "is_target_pair": left == "S" and right in ("C50", "C75"),
                    "critical_noise": str(radius),
                    "critical_noise_within_domain": radius <= NOISE_MAX,
                    "overlap_at_epsilon": EPSILON >= radius,
                    "independent_offset_critical_noise": str(independent_radius),
                    "independent_offset_overlap_at_epsilon": EPSILON >= independent_radius,
                    "threshold_witness": collision_at_boundary(left, right, design,
                                                                 predictions, radius),
                })
            target_radius = min(F(pair["critical_noise"]) for pair in pairs if pair["is_target_pair"])
            all_radius = min(F(pair["critical_noise"]) for pair in pairs)
            independent_target_radius = min(F(pair["independent_offset_critical_noise"])
                                            for pair in pairs if pair["is_target_pair"])
            designs.append({
                "actions": list(design), "pairs": pairs,
                "target_critical_noise": str(target_radius),
                "all_world_critical_noise": str(all_radius),
                "target_separates_at_epsilon": EPSILON < target_radius,
                "all_world_separates_at_epsilon": EPSILON < all_radius,
                "independent_offsets_target_separates_at_epsilon": EPSILON < independent_target_radius,
                "noise_sweep": [{"epsilon": str(error), "target_separates": error < target_radius,
                                 "all_world_separates": error < all_radius}
                                for error in NOISE_SWEEP],
            })

    successful = [design["actions"] for design in designs if design["target_separates_at_epsilon"]]
    minimum_cost = min(map(len, successful), default=None)
    optimal_designs = [design for design in successful if len(design) == minimum_cost]

    # Changed-model controls deliberately do not enter the main model universe.
    independent_readings = {a: (predictions["S"][a] + predictions["C50"][a]) / 2
                            for a in action_ids}
    independent_biases = {world: {a: independent_readings[a] - predictions[world][a]
                                 for a in action_ids} for world in ("S", "C50")}
    if any(abs(value) > BIAS for row in independent_biases.values() for value in row.values()):
        raise RuntimeError("Independent-offset control exceeds the offset bound")
    changing_selection = {a: predictions["C50"][a] * (1 - p) /
                          (p * (1 - predictions["C50"][a])) for a, p in ACTIONS}
    if any(predicted_fraction(p, changing_selection[a], F(0)) != predictions["C50"][a]
           for a, p in ACTIONS):
        raise RuntimeError("Heterogeneous-selection control fails to match")

    return {
        "schema_version": 1, "contract_id": "asma-compartment-design-v1", "status": "complete",
        "protocol": PROTOCOL, "protocol_sha256": sha256((ROOT / PROTOCOL).read_bytes()).hexdigest(),
        "implementation": IMPLEMENTATION,
        "implementation_sha256": sha256((ROOT / IMPLEMENTATION).read_bytes()).hexdigest(),
        "contract": {
            "worlds": [{"id": world, "r": str(r), "c": str(c)} for world, r, c in WORLDS],
            "actions": [{"id": a, "input_high_fraction": str(p)} for a, p in ACTIONS],
            "bias_bound": str(BIAS), "epsilon": str(EPSILON), "noise_max": str(NOISE_MAX),
            "noise_sweep": list(map(str, NOISE_SWEEP)), "action_budget": 2,
            "target_groups": {"zero_conversion": ["S"], "material_conversion": ["C50", "C75"],
                              "intermediate": ["C25"]},
        },
        "predictions": [{"world_id": world, "readouts": {a: str(value) for a, value in row.items()}}
                        for world, row in predictions.items()],
        "designs": designs, "optimal_designs": optimal_designs, "optimal_design_cost": minimum_cost,
        "controls": {
            "independent_offsets_collision": {
                "world_ids": ["S", "C50"],
                "readouts": {a: str(value) for a, value in independent_readings.items()},
                "biases": {world: {a: str(value) for a, value in row.items()}
                           for world, row in independent_biases.items()},
                "errors": {world: {a: "0" for a in action_ids} for world in ("S", "C50")},
            },
            "heterogeneous_selection_collision": {
                "reference_world_id": "C50", "conversion": "0",
                "selection_by_action": {a: str(value) for a, value in changing_selection.items()},
                "readouts": {a: str(value) for a, value in predictions["C50"].items()},
            },
        },
        "unsupported_claims": UNSUPPORTED,
    }


if __name__ == "__main__":
    print(json.dumps(build_result(), indent=2, allow_nan=False))
