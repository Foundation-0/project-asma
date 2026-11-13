#!/usr/bin/env python3
"""Checker A: read pinned IEDB, UniProt and HPA export fields directly.

Parent assignment for a class-II row follows the manifest accession of the
batch file. It does not recompute membership from the antigen-search ID list.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path


PARENTS = ("Q01850", "Q86X02")
MHC_FIELDS = (
    "elution_id", "reference_id", "pubmed_id", "reference_titles", "mhc_class",
    "mhc_allele_name", "mhc_allele_evidence", "assay_names", "qualitative_measure",
)
FOCUS_TISSUES = (
    "breast", "cerebellum", "cerebral cortex", "cervix", "endometrium",
    "fallopian tube", "ovary", "retina", "spinal cord",
)
GYN_CANCERS = (
    "breast cancer", "cervical cancer", "endometrial cancer", "ovarian cancer",
)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _load(result_dir, relative):
    return json.loads((result_dir / relative).read_text(encoding="utf-8"))


def _manifest(result_dir):
    manifest = _load(result_dir, "manifest.json")
    _require(manifest.get("schema_version") == 1, "manifest schema")
    files = manifest.get("files")
    _require(isinstance(files, list) and files, "manifest files")
    return files


def _files(result_dir, role, accession=None):
    found = []
    for item in _manifest(result_dir):
        if item.get("role") != role:
            continue
        if accession is not None and item.get("accession") != accession:
            continue
        found.append(item)
    _require(found, f"missing {role} {accession or ''}".strip())
    return found


def _one(result_dir, role, accession=None):
    found = _files(result_dir, role, accession)
    _require(len(found) == 1, f"expected one {role} {accession or ''}".strip())
    return found[0]


def _prior_parents(prior_audit):
    audit = json.loads(Path(prior_audit).read_text(encoding="utf-8"))
    by_parent = {}
    for antigen in audit["antigens"]:
        accession = antigen["uniprot"]
        by_parent[accession] = {
            "elution_ids": set(antigen["returned_assay_ids"]),
            "class_ii_ids": {row["elution_id"] for row in antigen["class_ii_annotations"]},
            "antigen_sha256": antigen["antigen_response_sha256"],
            "class_ii_sha256": [query["response_sha256"] for query in antigen["queries"]],
            "parent_card_sha256": antigen["parent_cardinality_check"]["response_sha256"],
        }
    _require(set(by_parent) >= set(PARENTS), "prior audit parents")
    return by_parent


def _class_ii_rows(result_dir):
    rows = []
    for accession in PARENTS:
        batches = _files(result_dir, "iedb_mhc", accession)
        _require(len(batches) == (8 if accession == "Q01850" else 1), "unexpected batch count")
        for item in batches:
            payload = _load(result_dir, item["path"])
            _require(isinstance(payload, list), "mhc export is not a list")
            for record in payload:
                _require(set(MHC_FIELDS) <= set(record), "mhc export field missing")
                _require(record["mhc_class"] == "II", "class filter leaked")
                titles = record["reference_titles"]
                _require(isinstance(titles, list) and titles and all(isinstance(t, str) for t in titles),
                         "reference title missing")
                rows.append({
                    "parent_uniprot": accession,
                    "elution_id": record["elution_id"],
                    "reference_id": record["reference_id"],
                    "pubmed_id": record["pubmed_id"],
                    "reference_title": titles[0],
                    "mhc_class": record["mhc_class"],
                    "mhc_allele_name": record["mhc_allele_name"],
                    "mhc_allele_evidence": record["mhc_allele_evidence"],
                    "assay_names": record["assay_names"],
                    "qualitative_measure": record["qualitative_measure"],
                    "parent_assignment": "manifest_batch_accession",
                })
    _require(len({row["elution_id"] for row in rows}) == len(rows), "duplicate class-II assay")
    return sorted(rows, key=lambda row: (row["parent_uniprot"], row["elution_id"]))


def _id_list(result_dir, role, accession):
    payload = _load(result_dir, _one(result_dir, role, accession)["path"])
    _require(isinstance(payload, list) and len(payload) == 1, "expected one parent record")
    record = payload[0]
    ids = record["elution_ids"]
    _require(isinstance(ids, list) and len(ids) == len(set(ids)), "parent elution ids")
    return record, ids


def _xref_id(entry, database):
    found = [xref.get("id") for xref in entry.get("uniProtKBCrossReferences") or [] if xref.get("database") == database]
    _require(len(found) == 1, f"expected one {database} cross-reference")
    return found[0]


def _ensembl_gene(entry):
    for xref in entry.get("uniProtKBCrossReferences") or []:
        if xref.get("database") != "Ensembl":
            continue
        for prop in xref.get("properties") or []:
            if prop.get("key") == "GeneId":
                return prop["value"]
    raise ValueError("Ensembl gene missing")


def _uniprot(result_dir, accession):
    entry = _load(result_dir, _one(result_dir, "uniprot", accession)["path"])
    gene = entry["genes"][0]["geneName"]["value"]
    return {
        "accession": entry["primaryAccession"],
        "entry_type": entry["entryType"],
        "gene": gene,
        "protein": entry["proteinDescription"]["recommendedName"]["fullName"]["value"],
        "organism": entry["organism"]["scientificName"],
        "taxon_id": entry["organism"]["taxonId"],
        "length": entry["sequence"]["length"],
        "crc64": entry["sequence"]["crc64"],
        "ensembl_gene": _ensembl_gene(entry),
        "gene_id": _xref_id(entry, "GeneID"),
        "hgnc": _xref_id(entry, "HGNC"),
        "protein_existence": entry["proteinExistence"],
    }


def _tsv(result_dir, item):
    text = (result_dir / item["path"]).read_text(encoding="utf-8")
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def _ntpm_max(values):
    # Tie break is the tissue name so both checkers share one rule.
    tissue, ntpm = min(values.items(), key=lambda item: (-float(item[1]), item[0]))
    return {"tissue": tissue, "ntpm": ntpm}


def _hpa_gene(result_dir, accession, uniprot_entry):
    summary = _load(result_dir, _one(result_dir, "hpa_gene", accession)["path"])
    consensus = _tsv(result_dir, _one(result_dir, "hpa_consensus", None))
    cancer = _tsv(result_dir, _one(result_dir, "hpa_cancer_ihc", None))
    normal = _tsv(result_dir, _one(result_dir, "hpa_normal_ihc", None))
    ensembl = summary["Ensembl"]
    _require(summary["Uniprot"] == [accession], "HPA UniProt accession")
    _require(uniprot_entry["ensembl_gene"].split(".", 1)[0] == ensembl, "Ensembl version stem")
    gene_rows = [row for row in consensus if row["Gene"] == ensembl]
    ntpm = {row["Tissue"]: row["nTPM"] for row in gene_rows}
    _require(len(ntpm) == len(gene_rows) and ntpm, "consensus tissue rows")
    cancers = {}
    for row in cancer:
        if row["Gene"] != ensembl:
            continue
        bins = {key: int(row[key]) for key in ("High", "Medium", "Low", "Not detected")}
        cancers[row["Cancer"]] = {
            "high": bins["High"], "medium": bins["Medium"], "low": bins["Low"],
            "not_detected": bins["Not detected"], "patients": sum(bins.values()),
        }
    normal_rows = [row for row in normal if row["Gene"] == ensembl]
    return {
        "gene": summary["Gene"],
        "ensembl": ensembl,
        "uniprot": accession,
        "chromosome": summary["Chromosome"],
        "position": summary["Position"],
        "rna_tissue_specificity": summary["RNA tissue specificity"],
        "rna_tissue_distribution": summary["RNA tissue distribution"],
        "rna_cancer_specificity": summary["RNA cancer specificity"],
        "rna_cancer_distribution": summary["RNA cancer distribution"],
        "ihc_reliability": summary["Reliability (IH)"],
        "consensus_tissues": len(ntpm),
        "consensus_ntpm": {tissue: ntpm[tissue] for tissue in FOCUS_TISSUES},
        "consensus_max": _ntpm_max(ntpm),
        "cancer_ihc": {name: cancers[name] for name in GYN_CANCERS},
        "cancer_patient_total": sum(item["patients"] for item in cancers.values()),
        "cancer_types": len(cancers),
        "normal_ihc_rows": len(normal_rows),
        "normal_ihc": sorted(
            [{"tissue": row["Tissue"], "cell_type": row["Cell type"], "level": row["Level"],
              "reliability": row["Reliability"]} for row in normal_rows],
            key=lambda row: (row["tissue"], row["cell_type"], row["level"]),
        ),
    }


def derive(result_dir, prior_audit):
    result_dir = Path(result_dir)
    prior = _prior_parents(prior_audit)
    rows = _class_ii_rows(result_dir)
    by_parent = {}
    for accession in PARENTS:
        record, ids = _id_list(result_dir, "iedb_antigen", accession)
        card, card_ids = _id_list(result_dir, "iedb_parent_card", accession)
        _require(card_ids == ids, "parent card ids differ from antigen search")
        _require(card["parent_source_antigen_iri"] == f"UNIPROT:{accession}", "parent IRI")
        selected = [row for row in rows if row["parent_uniprot"] == accession]
        selected_ids = {row["elution_id"] for row in selected}
        _require(selected_ids <= set(ids), "class-II id outside parent list")
        added = sorted(set(ids) - prior[accession]["elution_ids"])
        removed = sorted(prior[accession]["elution_ids"] - set(ids))
        by_parent[accession] = {
            "rows": len(selected),
            "references": len({row["reference_id"] for row in selected}),
            "pubmed_ids": sorted({row["pubmed_id"] for row in selected}),
            "parent_elution_ids": len(ids),
            "parent_records": 1,
            "added_since_2026_11_05": added,
            "removed_since_2026_11_05": removed,
            "class_ii_ids_unchanged_since_2026_11_05": selected_ids == prior[accession]["class_ii_ids"],
        }
    for accession in PARENTS:
        antigen_item = _one(result_dir, "iedb_antigen", accession)
        card_item = _one(result_dir, "iedb_parent_card", accession)
        mhc_items = _files(result_dir, "iedb_mhc", accession)
        by_parent[accession]["antigen_bytes_match_2026_11_05"] = (
            hashlib.sha256((result_dir / antigen_item["path"]).read_bytes()).hexdigest()
            == prior[accession]["antigen_sha256"])
        by_parent[accession]["parent_card_bytes_match_2026_11_05"] = (
            hashlib.sha256((result_dir / card_item["path"]).read_bytes()).hexdigest()
            == prior[accession]["parent_card_sha256"])
        current_mhc = sorted(hashlib.sha256((result_dir / item["path"]).read_bytes()).hexdigest() for item in mhc_items)
        # Empty class-II batches are the two-byte payload [] and share one digest.
        by_parent[accession]["class_ii_bytes_match_2026_11_05"] = (
            current_mhc == sorted(prior[accession]["class_ii_sha256"]))
    delta_item = _one(result_dir, "iedb_class_i_delta")
    delta = _load(result_dir, delta_item["path"])
    delta_ids = sorted(row["elution_id"] for row in delta)
    _require(delta_ids == by_parent["Q01850"]["added_since_2026_11_05"], "class-I delta is not the new parent ids")
    _require(by_parent["Q86X02"]["added_since_2026_11_05"] == [], "CDR2L parent list changed")
    _require(all(row["mhc_class"] == "I" for row in delta), "delta is not class I")
    uniprot = {accession: _uniprot(result_dir, accession) for accession in PARENTS}
    hpa = {uniprot[accession]["gene"]: _hpa_gene(result_dir, accession, uniprot[accession]) for accession in PARENTS}
    tcga = _tsv(result_dir, _one(result_dir, "hpa_tcga_cancers"))
    tissues = _tsv(result_dir, _one(result_dir, "hpa_consensus_tissues"))
    _require({row["Tissue"] for row in tissues} >= set(FOCUS_TISSUES), "tissue legend")
    return {
        "checker": "export_fields",
        "class_ii_rows": rows,
        "by_parent": by_parent,
        "qualitative_measures": sorted({row["qualitative_measure"] for row in rows}),
        "assay_names": sorted({row["assay_names"] for row in rows}),
        "class_i_delta": {
            "rows": len(delta),
            "elution_ids": delta_ids,
            "mhc_classes": sorted({row["mhc_class"] for row in delta}),
            "pubmed_ids": sorted({row["pubmed_id"] for row in delta}),
            "allele_names": sorted({row["mhc_allele_name"] for row in delta}),
        },
        "uniprot": uniprot,
        "hpa": hpa,
        "hpa_tissue_legend": len(tissues),
        "tcga_samples": {row["Cancer"]: int(row["Num samples"]) for row in tcga},
    }
