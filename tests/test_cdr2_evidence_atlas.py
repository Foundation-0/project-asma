"""Two CDR2/CDR2L atlas checkers and the offline replay."""
import importlib.util
import io
import json
import zipfile
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from tools import cdr2_atlas_export as export_checker
from tools import cdr2_atlas_recompute as recompute_checker

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "results/cdr2-cdr2l-evidence-atlas-2026-11-13"
PRIOR = ROOT / "registries/antigen-metadata-audit-2026-11-05.json"


def load_verify():
    spec = importlib.util.spec_from_file_location("cdr2_atlas_verify", RESULT / "verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify = load_verify()


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def uniprot(accession, gene, ensembl, gene_id, hgnc, length):
    return {
        "primaryAccession": accession,
        "entryType": "UniProtKB reviewed (Swiss-Prot)",
        "genes": [{"geneName": {"value": gene}}],
        "proteinDescription": {"recommendedName": {"fullName": {"value": gene + " protein"}}},
        "organism": {"scientificName": "Homo sapiens", "taxonId": 9606},
        "sequence": {"length": length, "crc64": "A" * 16},
        "proteinExistence": "1: Evidence at protein level",
        "uniProtKBCrossReferences": [
            {"database": "Ensembl", "properties": [{"key": "GeneId", "value": ensembl + ".1"}]},
            {"database": "GeneID", "id": gene_id},
            {"database": "HGNC", "id": hgnc},
        ],
    }


def hpa_gene(symbol, accession, ensembl):
    return {
        "Gene": symbol,
        "Ensembl": ensembl,
        "Uniprot": [accession],
        "Chromosome": "1",
        "Position": "1-2",
        "RNA tissue specificity": "Low tissue specificity",
        "RNA tissue distribution": "Detected in all",
        "RNA cancer specificity": "Low cancer specificity",
        "RNA cancer distribution": "Detected in all",
        "Reliability (IH)": "Approved",
    }


class CheckerAgreementTests(unittest.TestCase):
    def test_pinned_snapshot_counts_agree(self):
        exported = export_checker.derive(RESULT, PRIOR)
        recomputed = recompute_checker.derive(RESULT, PRIOR)
        self.assertEqual(verify.comparable(exported), verify.comparable(recomputed))
        self.assertEqual(exported["checker"], "export_fields")
        self.assertEqual(recomputed["checker"], "recompute_membership")
        self.assertNotEqual(exported["checker"], recomputed["checker"])
        self.assertEqual(exported["by_parent"]["Q01850"]["rows"], 7)
        self.assertEqual(exported["by_parent"]["Q86X02"]["rows"], 2)
        self.assertEqual(exported["by_parent"]["Q01850"]["parent_elution_ids"], 383)
        self.assertEqual(exported["by_parent"]["Q86X02"]["parent_elution_ids"], 45)
        self.assertEqual(exported["class_i_delta"]["rows"], 7)
        self.assertEqual(exported["class_i_delta"]["pubmed_ids"], ["42653321"])
        self.assertTrue(all(row["mhc_class"] == "I" for row in json.loads(
            (RESULT / "snapshot/iedb-class-i-delta.json").read_text(encoding="utf-8"))))

    def test_checkers_do_not_import_each_other(self):
        export_source = (ROOT / "tools/cdr2_atlas_export.py").read_text(encoding="utf-8")
        recompute_source = (ROOT / "tools/cdr2_atlas_recompute.py").read_text(encoding="utf-8")
        self.assertNotIn("cdr2_atlas_recompute", export_source)
        self.assertNotIn("cdr2_atlas_export", recompute_source)
        self.assertNotIn("import json", recompute_source)
        self.assertNotIn("json.loads(", recompute_source)
        self.assertIn("json.loads", export_source)

    def test_recompute_parser_escapes_and_rejects_junk(self):
        self.assertEqual(recompute_checker.parse_json(r'{"name":"A\nB\u0043"}'), {"name": "A\nBC"})
        self.assertEqual(recompute_checker.parse_json("[1, 2.5, true, null]"), [1, 2.5, True, None])
        with self.assertRaises(ValueError):
            recompute_checker.parse_json('{"a": 1} trailing')
        with self.assertRaises(ValueError):
            recompute_checker.parse_json('{"a": 1, "a": 2}')

    def test_synthetic_snapshot_agrees(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            exported = export_checker.derive(root, root / "prior.json")
            recomputed = recompute_checker.derive(root, root / "prior.json")
            self.assertEqual(verify.comparable(exported), verify.comparable(recomputed))
            self.assertEqual(exported["by_parent"]["Q01850"]["rows"], 1)
            self.assertEqual(exported["by_parent"]["Q86X02"]["rows"], 0)
            self.assertEqual(exported["by_parent"]["Q01850"]["parent_elution_ids"], 2)
            self.assertEqual(exported["class_i_delta"]["elution_ids"], [99])
            self.assertEqual(exported["hpa"]["CDR2"]["consensus_max"]["tissue"], "retina")
            self.assertEqual(exported["uniprot"]["Q01850"]["length"], 10)

    def _write_fixture(self, root):
        parents = {
            "Q01850": [10, 99],
            "Q86X02": [20],
        }
        files = []
        for accession, ids in parents.items():
            for role in ("iedb_antigen", "iedb_parent_card"):
                relative = f"snapshot/{role}-{accession}.json"
                write_json(root / relative, [{
                    "elution_ids": ids,
                    "parent_source_antigen_iri": f"UNIPROT:{accession}",
                    "parent_source_antigen_id": 1,
                }])
                files.append({"path": relative, "role": role, "accession": accession, "kind": "raw"})
        mhc_row = {
            "elution_id": 10, "reference_id": 1, "pubmed_id": "1", "reference_titles": ["Title"],
            "mhc_class": "II", "mhc_allele_name": "human", "mhc_allele_evidence": "stated",
            "assay_names": "ligand presentation", "qualitative_measure": "Positive",
        }
        for index in range(8):
            relative = f"snapshot/mhc-Q01850-{index:02d}.json"
            write_json(root / relative, [mhc_row] if index == 0 else [])
            files.append({"path": relative, "role": "iedb_mhc", "accession": "Q01850", "kind": "raw"})
        relative = "snapshot/mhc-Q86X02.json"
        write_json(root / relative, [])
        files.append({"path": relative, "role": "iedb_mhc", "accession": "Q86X02", "kind": "raw"})
        delta = "snapshot/class-i.json"
        write_json(root / delta, [{
            "elution_id": 99, "mhc_class": "I", "mhc_allele_name": "human",
            "pubmed_id": "9", "assay_names": "ligand presentation", "qualitative_measure": "Positive",
        }])
        files.append({"path": delta, "role": "iedb_class_i_delta", "kind": "raw"})
        identities = (
            ("Q01850", "CDR2", "ENSG00000000001", "1", "HGNC:1", 10),
            ("Q86X02", "CDR2L", "ENSG00000000002", "2", "HGNC:2", 20),
        )
        for accession, gene, ensembl, gene_id, hgnc, length in identities:
            relative = f"snapshot/uniprot-{accession}.json"
            write_json(root / relative, uniprot(accession, gene, ensembl, gene_id, hgnc, length))
            files.append({"path": relative, "role": "uniprot", "accession": accession, "kind": "raw"})
            relative = f"snapshot/hpa-{accession}.json"
            write_json(root / relative, hpa_gene(gene, accession, ensembl))
            files.append({"path": relative, "role": "hpa_gene", "accession": accession, "kind": "raw"})
        tissues = ("breast", "cerebellum", "cerebral cortex", "cervix", "endometrium",
                   "fallopian tube", "ovary", "retina", "spinal cord")
        consensus = ["Gene\tGene name\tTissue\tnTPM"]
        for ensembl, symbol, high in (("ENSG00000000001", "CDR2", "9.0"), ("ENSG00000000002", "CDR2L", "1.0")):
            for tissue in tissues:
                value = "9.5" if tissue == "retina" and symbol == "CDR2" else high
                consensus.append(f"{ensembl}\t{symbol}\t{tissue}\t{value}")
        (root / "snapshot").mkdir(exist_ok=True)
        (root / "snapshot/consensus.tsv").write_text("\n".join(consensus) + "\n", encoding="utf-8")
        files.append({"path": "snapshot/consensus.tsv", "role": "hpa_consensus", "kind": "raw"})
        cancers = ["Gene\tGene name\tCancer\tHigh\tMedium\tLow\tNot detected"]
        for ensembl, symbol in (("ENSG00000000001", "CDR2"), ("ENSG00000000002", "CDR2L")):
            for cancer in ("breast cancer", "cervical cancer", "endometrial cancer", "ovarian cancer"):
                cancers.append(f"{ensembl}\t{symbol}\t{cancer}\t1\t0\t0\t0")
        (root / "snapshot/cancer.tsv").write_text("\n".join(cancers) + "\n", encoding="utf-8")
        files.append({"path": "snapshot/cancer.tsv", "role": "hpa_cancer_ihc", "kind": "raw"})
        normal = ["Gene\tGene name\tTissue\tIHC tissue name\tCell type\tLevel\tReliability"]
        normal.append("ENSG00000000001\tCDR2\tovary\tovary\tfollicle cells\tMedium\tUncertain")
        (root / "snapshot/normal.tsv").write_text("\n".join(normal) + "\n", encoding="utf-8")
        files.append({"path": "snapshot/normal.tsv", "role": "hpa_normal_ihc", "kind": "raw"})
        legend = ["Tissue\tOrgan"] + [f"{tissue}\tbody" for tissue in tissues]
        (root / "snapshot/tissues.tsv").write_text("\n".join(legend) + "\n", encoding="utf-8")
        files.append({"path": "snapshot/tissues.tsv", "role": "hpa_consensus_tissues", "kind": "raw"})
        tcga = "Cancer\tAbbriviation\tCancer group\tOrgan\tNum samples\nOvary Serous Cystadenocarcinoma\tOV\tovary\tovary\t3\n"
        (root / "snapshot/tcga.tsv").write_text(tcga, encoding="utf-8")
        files.append({"path": "snapshot/tcga.tsv", "role": "hpa_tcga_cancers", "kind": "raw"})
        write_json(root / "manifest.json", {"schema_version": 1, "files": files})
        write_json(root / "prior.json", {"antigens": [
            {"uniprot": "Q01850", "returned_assay_ids": [10],
             "class_ii_annotations": [{"elution_id": 10}],
             "antigen_response_sha256": "0" * 64,
             "queries": [{"response_sha256": "1" * 64}],
             "parent_cardinality_check": {"response_sha256": "2" * 64}},
            {"uniprot": "Q86X02", "returned_assay_ids": [20],
             "class_ii_annotations": [],
             "antigen_response_sha256": "3" * 64,
             "queries": [{"response_sha256": "4" * 64}],
             "parent_cardinality_check": {"response_sha256": "5" * 64}},
        ]})


class VerifyScriptTests(unittest.TestCase):
    def test_reports_match_both_checkers(self):
        result = verify.check_reports()
        self.assertEqual(result["by_parent"]["Q01850"]["rows"], 7)
        self.assertIn("CDR2 Q01850 class-II assays: 7", verify.render_counts(result))

    def test_disagreement_fails(self):
        real = export_checker.derive

        def changed(result_dir, prior_audit):
            result = real(result_dir, prior_audit)
            result["by_parent"]["Q01850"]["rows"] = 0
            return result

        with mock.patch.object(verify.export_checker, "derive", changed):
            with self.assertRaisesRegex(ValueError, "disagree"):
                verify.check_reports()

    def test_identical_labels_fail(self):
        real = recompute_checker.derive

        def relabelled(result_dir, prior_audit):
            result = real(result_dir, prior_audit)
            result["checker"] = "export_fields"
            return result

        with mock.patch.object(verify.recompute_checker, "derive", relabelled):
            with self.assertRaisesRegex(ValueError, "independent labels"):
                verify.check_reports()

    def test_hash_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "snapshot").mkdir()
            body = b"[]"
            (root / "snapshot/a.json").write_bytes(body)
            write_json(root / "manifest.json", {"schema_version": 1, "files": [
                {"path": "snapshot/a.json", "role": "iedb_antigen", "kind": "raw"},
            ]})
            digest = verify.sha256(body)
            (root / "SHA256SUMS").write_text(f"{digest}  snapshot/a.json\n{'0' * 64}  manifest.json\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Snapshot hash changed"):
                verify.check_hashes(root)

    def test_live_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "snapshot/a.json"
            target.parent.mkdir()
            target.write_bytes(b"pinned")
            write_json(root / "manifest.json", {"schema_version": 1, "files": [{
                "path": "snapshot/a.json", "role": "iedb_antigen", "kind": "raw",
                "url": "https://example.test/a", "content_range": "0-0/*",
            }]})

            def different(_url, _headers):
                return b"changed", {"content-range": "0-0/*"}

            with mock.patch.object(Path, "write_bytes", side_effect=AssertionError("wrote bytes")):
                with mock.patch.object(Path, "write_text", side_effect=AssertionError("wrote text")):
                    with self.assertRaisesRegex(ValueError, "not overwritten"):
                        verify.live_check(root, fetch=different)
            self.assertEqual(target.read_bytes(), b"pinned")

            def same(_url, _headers):
                return b"pinned", {"content-range": "0-0/*"}

            with mock.patch.object(Path, "write_bytes", side_effect=AssertionError("wrote bytes")):
                self.assertTrue(verify.live_check(root, fetch=same))
            self.assertEqual(target.read_bytes(), b"pinned")

    def test_extract_keeps_only_the_two_genes(self):
        raw = io.BytesIO()
        with zipfile.ZipFile(raw, "w") as archive:
            archive.writestr("table.tsv", "Gene\tValue\nENSG00000140743\t1\nENSG00000999999\t9\nENSG00000109089\t2\n")
        extracted = verify.extract_gene_tsv(raw.getvalue(), "table.tsv")
        text = extracted.decode("utf-8")
        self.assertIn("ENSG00000140743", text)
        self.assertIn("ENSG00000109089", text)
        self.assertNotIn("ENSG00000999999", text)


if __name__ == "__main__":
    unittest.main()
