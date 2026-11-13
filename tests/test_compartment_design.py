"""Independent continuous-set checks and adversarial certificate mutations."""
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "results/compartment-design-2026-11-13/verify.py"
spec = importlib.util.spec_from_file_location("compartment_design_verifier", CHECKER)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class CompartmentDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = checker.load_certificate(ROOT / checker.CERTIFICATE)

    def rejected(self, mutation):
        forged = deepcopy(self.artifact)
        mutation(forged)
        with self.assertRaises(ValueError):
            checker.verify_artifact(forged)

    def test_complete_committed_certificate(self):
        result = checker.verify_artifact(self.artifact)
        self.assertEqual(result["world_pairs_checked"], 36)
        self.assertEqual(result["selected_designs"], [["L", "H"]])
        self.assertEqual(result["minimum_observation_cost"], 2)
        self.assertFalse(result["biological_validation"])

    def test_independent_mass_bookkeeping_recovers_known_fractions(self):
        predicted = checker.predictions()
        self.assertEqual(predicted["S"], {"L": F(16, 25), "R": F(4, 5), "H": F(32, 35)})
        self.assertEqual(predicted["C25"], {"L": F(53, 80), "R": F(4, 5), "H": F(91, 100)})
        self.assertEqual(predicted["C50"], {"L": F(7, 10), "R": F(4, 5), "H": F(9, 10)})
        self.assertEqual(predicted["C75"], {"L": F(31, 40), "R": F(4, 5), "H": F(17, 20)})

    def test_repeat_is_an_offset_calibration_control(self):
        expected = {("L", "R"): F(3, 200), ("L", "H"): F(13, 700), ("R", "H"): F(1, 280)}
        predicted = checker.predictions()
        for design, target in expected.items():
            differences = tuple(predicted["S"][a] - predicted["C50"][a] for a in design)
            self.assertEqual(checker.critical_radius(differences), target)
        self.assertEqual(expected[("L", "H")] / expected[("L", "R")], F(26, 21))

    def test_intermediate_world_is_retained(self):
        predicted = checker.predictions()
        differences = tuple(predicted["S"][a] - predicted["C25"][a] for a in ("L", "H"))
        self.assertTrue(checker.shared_overlap(differences, F(1, 60)))
        self.assertEqual(checker.critical_radius(differences), F(3, 448))
        pair = next(row for row in self.artifact["designs"][4]["pairs"]
                    if row["world_ids"] == ["S", "C25"])
        self.assertFalse(pair["is_target_pair"])
        self.assertFalse(self.artifact["designs"][4]["all_world_separates_at_epsilon"])

    def test_all_world_precision_boundaries(self):
        expected = [F(0), F(0), F(0), F(9, 1600), F(3, 448), F(3, 2800)]
        self.assertEqual([F(row["all_world_critical_noise"]) for row in self.artifact["designs"]], expected)

    def test_continuous_boundary_touch_is_overlap(self):
        predicted = checker.predictions()
        differences = tuple(predicted["S"][a] - predicted["C50"][a] for a in ("L", "H"))
        boundary = F(13, 700)
        self.assertFalse(checker.shared_overlap(differences, boundary - F(1, 1000000)))
        self.assertTrue(checker.shared_overlap(differences, boundary))
        self.assertTrue(checker.shared_overlap(differences, boundary + F(1, 1000000)))
        lower, upper = checker.overlap_interval(differences, boundary)
        self.assertEqual(lower, upper)
        self.assertEqual(lower, -F(4, 175))

    def test_feasible_offset_need_not_be_a_sampled_endpoint(self):
        # At zero residual error, the feasible offset difference is exactly 1/30,
        # neither zero nor an endpoint of [-1/10, 1/10].
        differences = (F(1, 30), F(1, 30))
        self.assertEqual(checker.overlap_interval(differences, F(0)), (F(1, 30), F(1, 30)))
        self.assertTrue(checker.shared_overlap(differences, F(0)))

    def test_independent_offsets_destroy_target_guarantee(self):
        predicted = checker.predictions()
        differences = tuple(predicted["S"][a] - predicted["C50"][a] for a, _ in checker.ACTIONS)
        self.assertTrue(checker.independent_overlap(differences, F(0)))
        self.assertFalse(checker.shared_overlap(differences, F(0)))
        self.assertTrue(all(not row["independent_offsets_target_separates_at_epsilon"]
                            for row in self.artifact["designs"]))
        checker.check_controls(self.artifact["controls"], predicted)

    def test_changed_mechanism_matches_every_action_without_conversion(self):
        predicted = checker.predictions()
        for (action, p), r in zip(checker.ACTIONS, (F(21), F(16), F(27, 2))):
            self.assertEqual(checker.selected_converted_fraction(p, r, F(0)), predicted["C50"][action])

    def test_main_domain_requires_no_clipping(self):
        for world in checker.predictions().values():
            for prediction in world.values():
                self.assertGreaterEqual(prediction - F(1, 20) - F(1, 40), 0)
                self.assertLessEqual(prediction + F(1, 20) + F(1, 40), 1)
        outside = [pair for row in self.artifact["designs"] for pair in row["pairs"]
                   if not pair["critical_noise_within_domain"]]
        self.assertTrue(outside)
        self.assertTrue(all(F(pair["critical_noise"]) > F(1, 40) for pair in outside))

    def test_prediction_and_threshold_corruptions_rejected(self):
        self.rejected(lambda data: data["predictions"][0]["readouts"].__setitem__("L", "1/2"))
        self.rejected(lambda data: data["designs"][4]["pairs"][1].__setitem__("critical_noise", "1/50"))
        self.rejected(lambda data: data["designs"][4].__setitem__("target_critical_noise", "1/50"))
        self.rejected(lambda data: data["designs"][4]["pairs"][1].__setitem__("independent_offset_critical_noise", "1/100"))

    def test_flags_and_chosen_design_corruptions_rejected(self):
        self.rejected(lambda data: data["designs"][4].__setitem__("target_separates_at_epsilon", False))
        self.rejected(lambda data: data["designs"][4].__setitem__("all_world_separates_at_epsilon", True))
        self.rejected(lambda data: data["designs"][4]["pairs"][0].__setitem__("is_target_pair", True))
        self.rejected(lambda data: data.__setitem__("optimal_designs", [["L", "R"]]))
        self.rejected(lambda data: data.__setitem__("optimal_design_cost", 1))
        self.rejected(lambda data: data["designs"][4]["noise_sweep"][6].__setitem__("target_separates", True))

    def test_witness_corruptions_rejected(self):
        self.rejected(lambda data: data["designs"][4]["pairs"][1]["threshold_witness"]["readouts"].__setitem__("L", "0"))
        self.rejected(lambda data: data["designs"][4]["pairs"][1]["threshold_witness"]["biases"].__setitem__("S", "1"))
        self.rejected(lambda data: data["controls"]["independent_offsets_collision"]["errors"]["S"].__setitem__("L", "1/100"))
        self.rejected(lambda data: data["controls"]["heterogeneous_selection_collision"]["selection_by_action"].__setitem__("L", "20"))

    def test_incomplete_and_duplicate_universes_rejected(self):
        self.rejected(lambda data: data["designs"].pop())
        self.rejected(lambda data: data["designs"].append(deepcopy(data["designs"][0])))
        self.rejected(lambda data: data["designs"].__setitem__(1, deepcopy(data["designs"][0])))
        self.rejected(lambda data: data["designs"][4]["pairs"].pop())
        self.rejected(lambda data: data["designs"][4]["pairs"].__setitem__(1, deepcopy(data["designs"][4]["pairs"][0])))
        self.rejected(lambda data: data["predictions"].pop())
        self.rejected(lambda data: data["designs"][4]["noise_sweep"].pop())
        self.rejected(lambda data: data.__setitem__("status", "timeout"))

    def test_unknown_or_revised_inputs_cannot_exclude_worlds(self):
        self.rejected(lambda data: data["contract"]["worlds"][0].__setitem__("c", None))
        self.rejected(lambda data: data["contract"].__setitem__("bias_bound", None))
        self.rejected(lambda data: data["contract"]["worlds"].pop())
        self.rejected(lambda data: data["contract"]["target_groups"].__setitem__("intermediate", []))
        self.rejected(lambda data: data["contract"].__setitem__("noise_max", "1/2"))
        self.rejected(lambda data: data.__setitem__("contract_id", "asma-compartment-design-v2"))
        self.rejected(lambda data: data.__setitem__("schema_version", 2))
        self.rejected(lambda data: data["unsupported_claims"].pop())

    def test_strict_types_and_canonical_fractions(self):
        self.rejected(lambda data: data["designs"][4].__setitem__("target_separates_at_epsilon", 1))
        self.rejected(lambda data: data.__setitem__("schema_version", True))
        self.rejected(lambda data: data["predictions"][0]["readouts"].__setitem__("R", "0.8"))
        self.rejected(lambda data: data["predictions"][0]["readouts"].__setitem__("R", "8/10"))
        self.rejected(lambda data: data["predictions"][0]["readouts"].__setitem__("R", 0.8))
        self.rejected(lambda data: data["predictions"][0]["readouts"].__setitem__("R", "1/0"))
        self.rejected(lambda data: data["designs"][4].__setitem__("unreviewed_model", "replacement"))

    def test_hash_and_protocol_revision_corruptions_rejected(self):
        self.rejected(lambda data: data.__setitem__("protocol_sha256", "0" * 64))
        self.rejected(lambda data: data.__setitem__("implementation_sha256", "0" * 64))
        self.rejected(lambda data: data.__setitem__("implementation", "tools/analyze_treatment_sequence.py"))
        # Copy opaque bytes only: this test does not inspect or import producer
        # source. Refreshing a valid implementation hash must preserve semantic
        # checking, while the independently frozen protocol cannot be redefined.
        with tempfile.TemporaryDirectory() as directory:
            isolated_root = Path(directory)
            for relative in (checker.PROTOCOL, checker.IMPLEMENTATION):
                target = isolated_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / relative).read_bytes())
            implementation = isolated_root / checker.IMPLEMENTATION
            implementation.write_bytes(implementation.read_bytes() + b"\n# Harmless hash-refresh test.\n")
            refreshed = deepcopy(self.artifact)
            refreshed["implementation_sha256"] = sha256(implementation.read_bytes()).hexdigest()
            self.assertEqual(checker.verify_artifact(refreshed, root=isolated_root)["selected_designs"],
                             [["L", "H"]])
            forged = deepcopy(refreshed)
            forged["predictions"][0]["readouts"]["L"] = "1/2"
            with self.assertRaises(ValueError):
                checker.verify_artifact(forged, root=isolated_root)
            protocol = isolated_root / checker.PROTOCOL
            protocol.write_bytes(protocol.read_bytes() + b"\nChanged contract revision.\n")
            refreshed["protocol_sha256"] = sha256(protocol.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):
                checker.verify_artifact(refreshed, root=isolated_root)

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"status":"complete","status":"complete"}',
                       object_pairs_hook=checker.reject_duplicate_keys)

    def test_cli_fails_closed_on_truncated_forged_complete_artifact(self):
        forged = deepcopy(self.artifact)
        forged["designs"] = forged["designs"][:1]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "forged.json"
            path.write_text(json.dumps(forged))
            result = subprocess.run([sys.executable, str(CHECKER), "--certificate", str(path)],
                                    capture_output=True, text=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("no exclusion established", result.stderr)


if __name__ == "__main__":
    unittest.main()
