"""Evidence-scope regression tests; artificial assertions below are not results."""

from copy import deepcopy
import hashlib
import json
import unittest

from tools.evidence_graph import EvidenceMap, ROOT, load


class EvidenceGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = load()

    def test_public_request_benchmark_and_scoped_negative(self):
        report = self.evidence.report()
        self.assertEqual(report["observations"], 24)
        self.assertEqual(len(report["queries"]), 22)
        self.assertTrue(report["fixtures_match_expectations"])
        negative = next(q for q in report["queries"] if q["id"] == "Q19")
        self.assertEqual(negative["status"], "counterevidence")
        self.assertEqual(negative["counterevidence"], ["E19"])
        broad = next(q for q in report["queries"] if q["id"] == "Q20")
        self.assertEqual(broad["status"], "unresolved")

    def test_marginal_annotation_join_is_not_an_observation(self):
        query = next(q for q in self.evidence.data["queries"] if q["id"] == "Q05")
        result = self.evidence.assess(query["requires"], query["evidence_ids"])
        self.assertEqual(result["status"], "unresolved")
        # Each requested value exists somewhere, but never in one observation.
        rows = [r for r in self.evidence.observations if r["id"] in query["evidence_ids"]]
        self.assertTrue(any(r["subject"] == "UNIPROT:Q86X02" for r in rows))
        self.assertTrue(any(r["context"]["model"] == "CIITA_transduced_glioblastoma" for r in rows))
        self.assertTrue(any("S113" in r["source_ids"] for r in rows))
        self.assertFalse(result["supporting"])

    def test_unknown_allele_cannot_become_a_specific_hla_context(self):
        request = {"relation": "hla_ligand_annotation", "subject": "UNIPROT:Q86X02",
                   "object": "HLA-II", "context": {"species": "human", "allele": "example_HLA_allele"}}
        result = self.evidence.assess(request, ["E02", "E03"])
        self.assertEqual(result["status"], "unresolved")
        self.assertIn("context.allele", result["mismatches"]["E02"])
        request["context"]["allele"] = "unknown"
        with self.assertRaisesRegex(ValueError, "unknown context"):
            self.evidence.assess(request)

    def test_sparse_existence_query_returns_full_scope_not_generalized_scope(self):
        query = next(q for q in self.evidence.data["queries"] if q["id"] == "Q03")
        result = self.evidence.assess(query["requires"], query["evidence_ids"])
        match = result["matched_evidence"][0]
        self.assertIsNone(match["context"]["surface_display"])
        self.assertEqual(match["source_ids"], ["S110", "S111"])
        self.assertIn("11610866", match["locator"])

    def test_permutation_does_not_change_support(self):
        sources = json.loads((ROOT / "registries/sources.json").read_text())["sources"]
        reordered = deepcopy(self.evidence.data)
        reordered["observations"].reverse()
        other = EvidenceMap(reordered, sources)
        for query in self.evidence.data["queries"]:
            a = self.evidence.assess(query["requires"], query["evidence_ids"])
            b = other.assess(query["requires"], query["evidence_ids"])
            for key in ("status", "supporting", "counterevidence"):
                self.assertEqual(a[key], b[key])

    def test_two_axes_and_unresolved_direct_ligand_links_are_preserved(self):
        report = self.evidence.report()
        hypotheses = {h["id"]: h for h in report["hypotheses"]}
        self.assertEqual(hypotheses["direct_ligand"]["axis"], "recognition")
        self.assertEqual(hypotheses["indirect_injury"]["axis"], "injury")
        self.assertEqual([r["status"] for r in hypotheses["direct_ligand"]["requirements"]],
                         ["supported_within_scope", "unresolved", "unresolved"])
        self.assertFalse(any("probability" in h for h in report["hypotheses"]))

    @staticmethod
    def synthetic_map(relation, subject, obj, context, polarity="supports"):
        """An explicitly artificial in-memory source, never a literature record."""
        observation = {"id": "fixture", "observation_key": "artificial:fixture",
                       "relation": relation, "subject": subject, "object": obj,
                       "context": context, "source_ids": ["ARTIFICIAL"],
                       "locator": "unit-test fixture; no scientific source",
                       "summary": "Invented software test assertion, not a study observation.",
                       "kind": "reported_observation", "polarity": polarity}
        sources = [{"id": "ARTIFICIAL", "url": "https://example.invalid/test-only"}]
        return EvidenceMap({"schema_version": 1, "observations": [observation]}, sources), sources

    def test_whole_protein_rescue_does_not_identify_recognized_ligand(self):
        graph, _ = self.synthetic_map("whole_protein_rescue", "CDR2L", "activation",
                                      {"system": "invented_source_presenter_receptor"})
        request = {"relation": "ligand_identity", "subject": "CDR2L", "object": "recognized_peptide",
                   "context": {"system": "invented_source_presenter_receptor"}}
        self.assertEqual(graph.assess(request)["status"], "unresolved")

    def test_organ_connection_does_not_establish_barrier_passage(self):
        graph, _ = self.synthetic_map("organ_connection", "blood", "brain", {"system": "invented"})
        request = {"relation": "barrier_passage", "subject": "blood", "object": "brain",
                   "context": {"system": "invented"}}
        self.assertEqual(graph.assess(request)["status"], "unresolved")

    def test_compartment_snapshot_does_not_establish_a_trajectory(self):
        graph, _ = self.synthetic_map("shared_clone_state_difference", "blood", "CSF",
                                      {"system": "invented", "design": "snapshot"})
        request = {"relation": "local_state_conversion", "subject": "blood", "object": "CSF",
                   "context": {"system": "invented", "design": "time_resolved"}}
        self.assertEqual(graph.assess(request)["status"], "unresolved")

    def test_conflicting_assertions_are_retained_without_majority_vote(self):
        graph, sources = self.synthetic_map("effect", "A", "B", {"system": "invented"})
        data = deepcopy(graph.data)
        contrary = deepcopy(data["observations"][0])
        contrary.update(id="contrary", observation_key="artificial:contrary", polarity="contradicts")
        data["observations"].append(contrary)
        graph = EvidenceMap(data, sources)
        request = {"relation": "effect", "subject": "A", "object": "B", "context": {"system": "invented"}}
        result = graph.assess(request)
        self.assertEqual(result["status"], "conflicting")
        self.assertEqual(result["supporting"], ["fixture"])
        self.assertEqual(result["counterevidence"], ["contrary"])
        self.assertEqual(len(result["matched_evidence"]), 2)

    def test_duplicate_observation_identity_is_not_replication(self):
        graph, sources = self.synthetic_map("effect", "A", "B", {"system": "invented"})
        data = deepcopy(graph.data)
        duplicate = deepcopy(data["observations"][0])
        duplicate["id"] = "renamed"
        data["observations"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "duplicate observation_key"):
            EvidenceMap(data, sources)

    def test_missing_source_and_invalid_selector_fail(self):
        graph, sources = self.synthetic_map("effect", "A", "B", {"system": "invented"})
        data = deepcopy(graph.data)
        data["observations"][0]["source_ids"] = ["MISSING"]
        with self.assertRaisesRegex(ValueError, "source reference"):
            EvidenceMap(data, sources)
        request = {"relation": "effect", "subject": "A", "object": "B", "context": {"system": "invented"}}
        with self.assertRaisesRegex(ValueError, "unknown observation"):
            graph.assess(request, ["MISSING"])

    def test_vendored_graph_and_license_are_exact_pinned_copies(self):
        vendor = ROOT / "tools/vendor/virtual_human"
        provenance = json.loads((vendor / "provenance.json").read_text())
        self.assertEqual(provenance["commit"], "3d75e8e25d6f3fec08e1ccecd424532bccaa1b82")
        for name, detail in provenance["copied_files"].items():
            self.assertEqual(hashlib.sha256((vendor / name).read_bytes()).hexdigest(), detail["sha256"])
        self.assertIn("Copyright (c) 2026 Rohan Arun", (vendor / "LICENSE").read_text())


if __name__ == "__main__":
    unittest.main()
