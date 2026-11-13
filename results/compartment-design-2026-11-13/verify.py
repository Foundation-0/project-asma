"""Independently check the frozen synthetic measurement-design certificate.

Uses count bookkeeping and continuous interval feasibility, without importing
or reading the producer's source. Source bytes are read only to check its hash.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = "protocols/compartment-measurement-design.md"
PROTOCOL_SHA256 = "23a9e656b903c005559554f0d0bd1f02600016fc8d0557af1694c05f5bb29220"
IMPLEMENTATION = "tools/analyze_compartment_design.py"
CERTIFICATE = "results/compartment-design-2026-11-13/certificate.json"
WORLDS = (("S", F(16), F(0)), ("C25", F(11), F(1, 4)),
          ("C50", F(6), F(1, 2)), ("C75", F(1), F(3, 4)))
ACTIONS = (("L", F(1, 10)), ("R", F(1, 5)), ("H", F(2, 5)))
DESIGNS = (("L",), ("R",), ("H",), ("L", "R"),
           ("L", "H"), ("R", "H"))
NOISE_SWEEP = tuple(map(F, ("0", "1/280", "9/1600", "3/448", "3/200",
                           "1/60", "13/700", "1/40")))
BIAS = F(1, 20)
EPSILON = F(1, 60)
NOISE_MAX = F(1, 40)
UNSUPPORTED = ["biological_mechanism_identification", "arbitrarily_small_conversion_detection",
               "clinical_measurement_feasibility", "clinical_efficacy_or_treatment_selection",
               "novelty_to_literature", "independent_scientific_peer_review"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def keys(value, expected, label):
    require(type(value) is dict and set(value) == set(expected),
            f"{label}: missing, extra, or malformed fields")


def rational(value):
    require(type(value) is str, "rational must be a canonical string")
    try:
        result = F(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("invalid rational") from exc
    require(str(result) == value, "noncanonical rational")
    return result


def scalar(value, expected, label):
    require(rational(value) == expected, f"{label}: incorrect rational")


def boolean(value, expected, label):
    require(type(value) is bool and value == expected, f"{label}: incorrect boolean")


def selected_converted_fraction(p, r, c):
    """Count selected high/low weights, then transfer converted low weight."""
    low_before, high_before = 1 - p, p
    low_selected, high_selected = low_before, r * high_before
    moved = c * low_selected
    high_after, low_after = high_selected + moved, low_selected - moved
    return high_after / (high_after + low_after)


def predictions():
    return {name: {action: selected_converted_fraction(p, r, c)
                   for action, p in ACTIONS} for name, r, c in WORLDS}


def overlap_interval(differences, epsilon, bias=BIAS):
    """Feasible difference of two shared offsets; closed bounds keep touches."""
    require(epsilon >= 0 and bias >= 0 and bool(differences), "invalid uncertainty set")
    lower, upper = -2 * bias, 2 * bias
    for difference in differences:
        lower = max(lower, difference - 2 * epsilon)
        upper = min(upper, difference + 2 * epsilon)
    return lower, upper


def shared_overlap(differences, epsilon, bias=BIAS):
    lower, upper = overlap_interval(differences, epsilon, bias)
    return lower <= upper


def independent_overlap(differences, epsilon, bias=BIAS):
    return all(shared_overlap((difference,), epsilon, bias) for difference in differences)


def critical_radius(differences, independent=False):
    """Solve the lower<=upper inequalities of the interval intersection."""
    lower_slope_constraints = [F(0)]
    for left in differences:
        lower_slope_constraints.append((left - 2 * BIAS) / 2)
        lower_slope_constraints.append((-left - 2 * BIAS) / 2)
        if not independent:
            for right in differences:
                lower_slope_constraints.append((left - right) / 4)
    return max(lower_slope_constraints)


def check_shared_witness(witness, pair, actions, noise, predicted):
    keys(witness, ("readouts", "biases", "errors"), "threshold witness")
    keys(witness["readouts"], actions, "witness readouts")
    keys(witness["biases"], pair, "witness biases")
    keys(witness["errors"], pair, "witness errors")
    for world in pair:
        bias = rational(witness["biases"][world])
        require(abs(bias) <= BIAS, "witness bias outside bound")
        keys(witness["errors"][world], actions, "world errors")
        for action in actions:
            observed = rational(witness["readouts"][action])
            error = rational(witness["errors"][world][action])
            require(abs(error) <= noise, "witness error outside radius")
            require(observed == predicted[world][action] + bias + error,
                    "witness does not reproduce the same reading")


def check_controls(controls, predicted):
    keys(controls, ("independent_offsets_collision", "heterogeneous_selection_collision"),
         "controls")
    collision = controls["independent_offsets_collision"]
    keys(collision, ("world_ids", "readouts", "biases", "errors"), "independent collision")
    pair = ("S", "C50")
    require(collision["world_ids"] == list(pair), "wrong independent collision worlds")
    actions = tuple(action for action, _ in ACTIONS)
    keys(collision["readouts"], actions, "independent readouts")
    for field in ("biases", "errors"):
        keys(collision[field], pair, f"independent {field}")
        for world in pair:
            keys(collision[field][world], actions, f"independent {world} {field}")
    for world in pair:
        for action in actions:
            bias = rational(collision["biases"][world][action])
            error = rational(collision["errors"][world][action])
            observed = rational(collision["readouts"][action])
            require(abs(bias) <= BIAS and error == 0, "invalid zero-error independent collision")
            require(0 <= observed <= 1 and observed == predicted[world][action] + bias,
                    "false independent-offset collision")
    heterogeneous = controls["heterogeneous_selection_collision"]
    keys(heterogeneous, ("reference_world_id", "conversion", "selection_by_action", "readouts"),
         "heterogeneous collision")
    require(heterogeneous["reference_world_id"] == "C50", "wrong heterogeneous reference")
    scalar(heterogeneous["conversion"], F(0), "heterogeneous conversion")
    keys(heterogeneous["selection_by_action"], actions, "heterogeneous selection")
    keys(heterogeneous["readouts"], actions, "heterogeneous readouts")
    expected_selection = {"L": F(21), "R": F(16), "H": F(27, 2)}
    for action, p in ACTIONS:
        r = rational(heterogeneous["selection_by_action"][action])
        require(r == expected_selection[action], "changed heterogeneous control")
        observed = rational(heterogeneous["readouts"][action])
        require(observed == selected_converted_fraction(p, r, F(0)) == predicted["C50"][action],
                "false heterogeneous-selection collision")


def expected_contract():
    return {"worlds": [{"id": name, "r": str(r), "c": str(c)} for name, r, c in WORLDS],
            "actions": [{"id": name, "input_high_fraction": str(p)} for name, p in ACTIONS],
            "bias_bound": str(BIAS), "epsilon": str(EPSILON), "noise_max": str(NOISE_MAX),
            "action_budget": 2, "noise_sweep": list(map(str, NOISE_SWEEP)),
            "target_groups": {"zero_conversion": ["S"], "material_conversion": ["C50", "C75"],
                              "intermediate": ["C25"]}}


def verify_artifact(artifact, root=ROOT):
    keys(artifact, ("schema_version", "contract_id", "status", "protocol", "protocol_sha256",
                    "implementation", "implementation_sha256", "contract", "predictions",
                    "designs", "optimal_designs", "optimal_design_cost", "controls",
                    "unsupported_claims"), "certificate")
    require(type(artifact["schema_version"]) is int and artifact["schema_version"] == 1,
            "unsupported schema revision")
    require(artifact["contract_id"] == "asma-compartment-design-v1" and artifact["status"] == "complete",
            "wrong model revision or incomplete computation")
    require(artifact["protocol"] == PROTOCOL and artifact["protocol_sha256"] == PROTOCOL_SHA256,
            "frozen protocol revision mismatch")
    require(sha256((root / PROTOCOL).read_bytes()).hexdigest() == PROTOCOL_SHA256,
            "protocol file changed after freeze")
    require(artifact["implementation"] == IMPLEMENTATION, "unexpected producer path")
    require(artifact["implementation_sha256"] == sha256((root / IMPLEMENTATION).read_bytes()).hexdigest(),
            "producer hash mismatch")
    require(type(artifact["contract"]) is dict and artifact["contract"] == expected_contract(),
            "changed, unknown, or incomplete input universe")
    require(type(artifact["contract"]["action_budget"]) is int, "action budget must be integer")
    require(artifact["unsupported_claims"] == UNSUPPORTED, "scope limitations missing or changed")

    predicted = predictions()
    require(type(artifact["predictions"]) is list and len(artifact["predictions"]) == len(WORLDS),
            "incomplete prediction universe")
    for row, (world, _, _) in zip(artifact["predictions"], WORLDS):
        keys(row, ("world_id", "readouts"), "prediction")
        require(row["world_id"] == world, "duplicate, missing, or reordered world")
        keys(row["readouts"], dict(ACTIONS), "prediction readouts")
        for action, expected in predicted[world].items():
            scalar(row["readouts"][action], expected, "prediction")
            require(expected - BIAS - NOISE_MAX >= 0 and expected + BIAS + NOISE_MAX <= 1,
                    "declared readout model would require clipping")
        require(predicted[world]["R"] == F(4, 5), "baseline not recovered")

    require(type(artifact["designs"]) is list and len(artifact["designs"]) == len(DESIGNS),
            "incomplete design enumeration")
    pairs = tuple(combinations((name for name, _, _ in WORLDS), 2))
    valid_designs = []
    for row, actions in zip(artifact["designs"], DESIGNS):
        keys(row, ("actions", "pairs", "target_critical_noise", "all_world_critical_noise",
                   "target_separates_at_epsilon", "all_world_separates_at_epsilon",
                   "independent_offsets_target_separates_at_epsilon", "noise_sweep"), "design")
        require(row["actions"] == list(actions), "duplicate, missing, or reordered design")
        require(type(row["pairs"]) is list and len(row["pairs"]) == len(pairs), "incomplete pair table")
        criticals, target_criticals, differences_by_pair = [], [], {}
        independent_target_results = []
        for pair_row, pair in zip(row["pairs"], pairs):
            keys(pair_row, ("world_ids", "is_target_pair", "critical_noise", "overlap_at_epsilon",
                            "threshold_witness", "independent_offset_critical_noise",
                            "independent_offset_overlap_at_epsilon", "critical_noise_within_domain"), "pair")
            require(pair_row["world_ids"] == list(pair), "duplicate, missing, or reordered pair")
            target = pair[0] == "S" and pair[1] in ("C50", "C75")
            boolean(pair_row["is_target_pair"], target, "target pair")
            differences = tuple(predicted[pair[0]][action] - predicted[pair[1]][action] for action in actions)
            differences_by_pair[pair] = differences
            radius = critical_radius(differences)
            independent_radius = critical_radius(differences, independent=True)
            scalar(pair_row["critical_noise"], radius, "shared critical radius")
            scalar(pair_row["independent_offset_critical_noise"], independent_radius,
                   "independent critical radius")
            boolean(pair_row["critical_noise_within_domain"], radius <= NOISE_MAX, "radius scope")
            boolean(pair_row["overlap_at_epsilon"], shared_overlap(differences, EPSILON), "shared overlap")
            boolean(pair_row["independent_offset_overlap_at_epsilon"], independent_overlap(differences, EPSILON),
                    "independent overlap")
            require(shared_overlap(differences, radius), "algebraic boundary failed interval feasibility")
            if radius:
                require(not shared_overlap(differences, radius / 2), "claimed boundary is not minimal")
            check_shared_witness(pair_row["threshold_witness"], pair, actions, radius, predicted)
            criticals.append(radius)
            if target:
                target_criticals.append(radius)
                independent_target_results.append(not independent_overlap(differences, EPSILON))
        target_radius, all_radius = min(target_criticals), min(criticals)
        target_separates = all(not shared_overlap(differences_by_pair[pair], EPSILON)
                               for pair in (("S", "C50"), ("S", "C75")))
        all_separate = all(not shared_overlap(differences, EPSILON) for differences in differences_by_pair.values())
        scalar(row["target_critical_noise"], target_radius, "target boundary")
        scalar(row["all_world_critical_noise"], all_radius, "all-world boundary")
        boolean(row["target_separates_at_epsilon"], target_separates, "target outcome")
        boolean(row["all_world_separates_at_epsilon"], all_separate, "all-world outcome")
        boolean(row["independent_offsets_target_separates_at_epsilon"], all(independent_target_results),
                "independent target outcome")
        require(type(row["noise_sweep"]) is list and len(row["noise_sweep"]) == len(NOISE_SWEEP),
                "incomplete noise presentation table")
        for noise_row, noise in zip(row["noise_sweep"], NOISE_SWEEP):
            keys(noise_row, ("epsilon", "target_separates", "all_world_separates"), "noise row")
            scalar(noise_row["epsilon"], noise, "noise point")
            target_result = all(not shared_overlap(differences_by_pair[pair], noise)
                                for pair in (("S", "C50"), ("S", "C75")))
            all_result = all(not shared_overlap(differences, noise) for differences in differences_by_pair.values())
            boolean(noise_row["target_separates"], target_result, "noise target outcome")
            boolean(noise_row["all_world_separates"], all_result, "noise all-world outcome")
        if target_separates:
            valid_designs.append(list(actions))
    require(bool(valid_designs), "frozen design has no successful candidate")
    min_cost = min(map(len, valid_designs))
    expected_optimal = [design for design in valid_designs if len(design) == min_cost]
    require(artifact["optimal_designs"] == expected_optimal, "incorrect minimum-cost design selection")
    require(type(artifact["optimal_design_cost"]) is int and artifact["optimal_design_cost"] == min_cost,
            "incorrect selected design cost")
    check_controls(artifact["controls"], predicted)
    return {"status": "verified_synthetic_certificate_only", "designs_checked": len(DESIGNS),
            "world_pairs_checked": len(DESIGNS) * len(pairs), "minimum_observation_cost": min_cost,
            "selected_designs": expected_optimal, "biological_validation": False}


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_certificate(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=reject_duplicate_keys)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=ROOT / CERTIFICATE)
    args = parser.parse_args()
    try:
        result = verify_artifact(load_certificate(args.certificate))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(1, f"INVALID certificate; no exclusion established: {exc}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
