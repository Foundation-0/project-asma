"""Artificial HTML fixtures test source scope and non-retention of identifiers."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

from tools import audit_cdr2l_atlas as atlas


def page(rows, headers=None, prediction=True):
    head = "".join(f"<th>{x}</th>" for x in (headers or atlas.HEADERS))
    body = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in row) + "</tr>" for row in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>" + (atlas.NO_PREDICTION if prediction else "")


def row(tissue="Test tissue", quality="0.01"):
    return ["PRIVATE_DONOR_SENTINEL", tissue] + ["GENOTYPE_SENTINEL"] * 6 + [quality]


class AtlasAuditTests(unittest.TestCase):
    def test_aggregates_without_identifiers(self):
        result = atlas.summarize_portal(page([row(), row("Other tissue", "0.02"), row()]))
        self.assertEqual(result["source_association_rows"], 3)
        self.assertEqual(result["tissue_counts"], {"Other tissue": 1, "Test tissue": 2})
        self.assertEqual(result["displayed_q_value_range"], ["0.01", "0.02"])
        self.assertNotIn("SENTINEL", json.dumps(result))
        self.assertTrue(result["explicit_no_binding_prediction"])
        self.assertEqual(result["peptide_specific_allotype"], "unresolved")

    def test_missing_sentence_does_not_imply_positive_prediction(self):
        result = atlas.summarize_portal(page([row()], prediction=False))
        self.assertFalse(result["explicit_no_binding_prediction"])
        self.assertEqual(result["peptide_specific_allotype"], "unresolved")

    def test_nonrendered_prediction_text_is_not_evidence(self):
        for tag in ("script", "style", "template"):
            html = page([row()], prediction=False) + f"<{tag}>{atlas.NO_PREDICTION}</{tag}>"
            self.assertFalse(atlas.summarize_portal(html)["explicit_no_binding_prediction"])

    def test_identity_requires_actual_heading_and_anchors(self):
        sequence = "ACDEFGHIKLMNPQRSTVWY"
        anchors = '<a href="http://www.iedb.org/epitope/1281771">IEDB</a><a href="/protein/Q86X02">source</a>'
        heading = '<h3><tt>' + ''.join(f'<span>{c}</span>' for c in sequence) + '</tt></h3>'
        atlas.validate_page_identity(heading + anchors, sequence)
        for html in [sequence + anchors, heading, '<script>' + heading + anchors + '</script>',
                     '<template>' + heading + anchors + '</template>', heading + anchors + '<h3>AAAAAAAA</h3>']:
            with self.assertRaises(ValueError):
                atlas.validate_page_identity(html, sequence)

    def test_q_is_not_binding_score_or_spectrum_error_probability(self):
        result = atlas.summarize_portal(page([row(quality="0")] ))
        self.assertEqual(result["quality_label"], "q-value")
        self.assertEqual(result["quality_granularity"], "unresolved")
        self.assertEqual(result["original_spectrum_validation"], "not_performed")

    def test_malformed_values_and_columns_rejected(self):
        for value in ["NaN", "Infinity", "-0.1", "1.1", "unknown"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                atlas.summarize_portal(page([row(quality=value)]))
        for html in [page([]), page([row()[:-1]]), page([row()], headers=["x"] * 9),
                     page([row()]) + page([row()]), page([row()]).replace("</table>", "")]:
            with self.assertRaises(ValueError):
                atlas.summarize_portal(html)

    def test_nested_markup_and_other_tables(self):
        html = "<table><tr><th>Unrelated</th></tr></table>" + page([row("Test <b>tissue</b>")])
        self.assertEqual(atlas.summarize_portal(html)["tissue_counts"], {"Test tissue": 1})

    def test_certificate_and_rehashed_overclaims(self):
        report = json.loads(atlas.RESULT.read_text())
        self.assertTrue(atlas.check_report(report))
        mutations = [lambda r: r.update(script_sha256="0" * 64),
                     lambda r: r.update(donor="PRIVATE"),
                     lambda r: r.update(source="https://example.com"),
                     lambda r: r.update(peptide_sha256="0" * 64),
                     lambda r: r.update(limits=["arbitrary source content"]),
                     lambda r: r["summary"].update(peptide_specific_allotype="DRB1*01:01"),
                     lambda r: r["summary"].update(quality_granularity="spectrum_PEP"),
                     lambda r: r["summary"].update(original_spectrum_validation="passed"),
                     lambda r: r["summary"].update(source_association_rows=7),
                     lambda r: r["summary"].update(displayed_q_value_range=["NaN", "NaN"])]
        for mutate in mutations:
            changed = copy.deepcopy(report)
            mutate(changed)
            changed["certificate_sha256"] = atlas.sha(atlas.canonical({k: v for k, v in changed.items() if k != "certificate_sha256"}))
            with self.assertRaises(ValueError):
                atlas.check_report(changed)

    def test_live_refuses_to_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "certificate.json"
            output.write_bytes(b"historical receipt\n")
            with mock.patch.object(atlas, "live_audit", return_value={"summary": {}}) as live_audit, \
                    mock.patch.object(sys, "argv", ["audit", "--live", "--output", str(output)]):
                with self.assertRaises(ValueError):
                    atlas.main()
            self.assertEqual(output.read_bytes(), b"historical receipt\n")
            live_audit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
