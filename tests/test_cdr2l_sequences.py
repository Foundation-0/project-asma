"""Artificial sequence and catalog response checks; no study data."""
import copy
import json
import unittest
from unittest.mock import patch

from tools import audit_cdr2l_sequences as audit


def assays():
    return [{"elution_id": i, "pubmed_id": pmid, "mhc_class": "II",
             "parent_source_antigen_iri": "UNIPROT:Q86X02", "qualitative_measure": "Positive",
             "linear_sequence": "A" * (end - start + 1),
             "curated_source_antigen": {"accession": "Q86X02.2", "starting_position": start,
                                        "ending_position": end}}
            for i, (pmid, start, end) in audit.ASSAYS.items()]


class SequenceAuditTests(unittest.TestCase):
    def test_coordinates_and_overlapping_matches(self):
        self.assertEqual(audit.positions("AAAA", "AA"), [1, 2, 3])
        self.assertEqual(audit.positions("ACDE", "DE"), [3])
        self.assertEqual(audit.positions("ACDE", "ACDEF"), [])
        self.assertEqual(audit.positions("ACDE", "CF"), [])

    def test_il_is_explicit_and_symmetric(self):
        self.assertEqual(audit.positions("AILL", "ALL"), [])
        self.assertEqual(audit.positions("AILL", "ALL", True), [1])

    def test_il_does_not_collapse_other_residues(self):
        self.assertEqual(audit.positions("AIK", "ALL", True), [])

    def test_invalid_or_empty_residues_fail(self):
        for sequence, peptide in [("", "A"), ("A", ""), ("AX", "A"), ("AIL", "a"), ("A*", "A")]:
            with self.subTest(sequence=sequence, peptide=peptide), self.assertRaises(ValueError):
                audit.positions(sequence, peptide)

    def test_assay_identity_and_coordinate_drift(self):
        self.assertEqual(len(audit.validate_assays(assays()[::-1])), 2)
        for key, value in [("pubmed_id", "other"), ("mhc_class", "I"),
                           ("parent_source_antigen_iri", "UNIPROT:Q01850"),
                           ("qualitative_measure", "Negative"), ("linear_sequence", "A")]:
            rows = assays()
            rows[0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                audit.validate_assays(rows)
        rows = assays()
        rows[0]["curated_source_antigen"]["starting_position"] += 1
        with self.assertRaises(ValueError):
            audit.validate_assays(rows)

    def test_duplicate_and_extra_assays_fail(self):
        for rows in [[assays()[0]] * 2, assays() + [assays()[0]]]:
            with self.assertRaises(ValueError):
                audit.validate_assays(rows)

    def test_remote_parameters_checked_and_http_location_upgraded(self):
        responses = [(202, {"location": "http://peptidesearch.uniprot.org/asyncrest/jobs/PM123"}, b""),
                     (200, {}, b"Q86X02"),
                     (200, {}, b"QueryPetides:AIL\nTaxonIds:9606\nlEqi:Y\nswissProtOnly:N")]
        with patch.object(audit, "request", side_effect=responses) as request:
            result = audit.peptide_search("AIL", True)
        self.assertEqual(result["accessions"], ["Q86X02"])
        self.assertTrue(request.call_args_list[1].args[0].startswith("https://"))
        responses[-1] = (200, {}, b"QueryPetides:AIL\nTaxonIds:9606\nlEqi:N\nswissProtOnly:N")
        with patch.object(audit, "request", side_effect=responses), self.assertRaises(ValueError):
            audit.peptide_search("AIL", True)

    def test_untrusted_job_location_rejected(self):
        for location in ["https://example.com/PM123", "http://peptidesearch.uniprot.org.evil/asyncrest/jobs/PM123"]:
            with patch.object(audit, "request", return_value=(202, {"location": location}, b"")), self.assertRaises(ValueError):
                audit.peptide_search("AIL", False)

    def test_retained_certificate_integrity(self):
        report = json.loads(audit.RESULT.read_text())
        self.assertTrue(audit.check_report(report))
        altered = copy.deepcopy(report)
        altered["leads"][0]["peptide_length"] += 1
        with self.assertRaisesRegex(ValueError, "digest"):
            audit.check_report(altered)
        altered["certificate_sha256"] = audit.sha(audit.canonical({k: v for k, v in altered.items() if k != "certificate_sha256"}))
        with self.assertRaisesRegex(ValueError, "coordinates"):
            audit.check_report(altered)

    def test_rehashed_inconsistent_certificate_refused(self):
        mutations = [
            lambda r: r["leads"][0].update(pubmed_id="wrong"),
            lambda r: r["proteins"]["Q86X02"].update(taxon_id=10090),
            lambda r: r["proteins"]["Q86X02"].update(length=-1),
            lambda r: r["leads"][0]["local_matches"]["Q86X02"].update(il_positions=[]),
            lambda r: r["leads"][0]["local_matches"]["A0ACI8RKQ2"].update(exact_positions=[900]),
            lambda r: r["leads"][0]["local_matches"].pop("Q01850"),
            lambda r: r.update(database_search_status="completed"),
            lambda r: r.update(candidate_universe=["Q86X02"]),
        ]
        for mutate in mutations:
            report = json.loads(audit.RESULT.read_text())
            mutate(report)
            report["certificate_sha256"] = audit.sha(audit.canonical({k: v for k, v in report.items() if k != "certificate_sha256"}))
            with self.subTest(mutation=mutate), self.assertRaises((ValueError, KeyError)):
                audit.check_report(report)


if __name__ == "__main__":
    unittest.main()
