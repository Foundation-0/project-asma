#!/usr/bin/env python3
"""Checker B: recompute the atlas from raw pinned records.

Class-II parent assignment is the intersection of an assay id with the
antigen-search elution-id sets. The batch file's manifest accession is ignored.
JSON is parsed here and is not delegated to the export checker or json.loads.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


PARENTS = ("Q01850", "Q86X02")
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


class _Parser:
    """Small JSON reader with explicit string and number scanning."""

    def __init__(self, text):
        self.text = text
        self.i = 0
        self.n = len(text)

    def skip(self):
        while self.i < self.n and self.text[self.i] in " \t\r\n":
            self.i += 1

    def parse(self):
        value = self.value()
        self.skip()
        _require(self.i == self.n, "trailing JSON")
        return value

    def value(self):
        self.skip()
        _require(self.i < self.n, "truncated JSON")
        char = self.text[self.i]
        if char == "{":
            return self.object()
        if char == "[":
            return self.array()
        if char == '"':
            return self.string()
        if char == "t":
            return self.literal("true", True)
        if char == "f":
            return self.literal("false", False)
        if char == "n":
            return self.literal("null", None)
        return self.number()

    def literal(self, token, value):
        _require(self.text.startswith(token, self.i), "bad literal")
        self.i += len(token)
        return value

    def string(self):
        self.i += 1
        chars = []
        while self.i < self.n:
            char = self.text[self.i]
            if char == '"':
                self.i += 1
                return "".join(chars)
            if char == "\\":
                self.i += 1
                _require(self.i < self.n, "truncated escape")
                escaped = self.text[self.i]
                mapping = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
                if escaped in mapping:
                    chars.append(mapping[escaped])
                elif escaped == "u":
                    hex_digits = self.text[self.i + 1:self.i + 5]
                    _require(len(hex_digits) == 4, "bad unicode escape")
                    chars.append(chr(int(hex_digits, 16)))
                    self.i += 4
                else:
                    raise ValueError("bad escape")
            else:
                chars.append(char)
            self.i += 1
        raise ValueError("unterminated string")

    def number(self):
        start = self.i
        if self.text[self.i] == "-":
            self.i += 1
        _require(self.i < self.n and self.text[self.i].isdigit(), "bad number")
        if self.text[self.i] == "0":
            self.i += 1
        else:
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1
        fractional = False
        if self.i < self.n and self.text[self.i] == ".":
            fractional = True
            self.i += 1
            _require(self.i < self.n and self.text[self.i].isdigit(), "bad fraction")
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1
        if self.i < self.n and self.text[self.i] in "eE":
            fractional = True
            self.i += 1
            if self.i < self.n and self.text[self.i] in "+-":
                self.i += 1
            _require(self.i < self.n and self.text[self.i].isdigit(), "bad exponent")
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1
        token = self.text[start:self.i]
        return float(token) if fractional else int(token)

    def array(self):
        self.i += 1
        values = []
        self.skip()
        if self.i < self.n and self.text[self.i] == "]":
            self.i += 1
            return values
        while True:
            values.append(self.value())
            self.skip()
            _require(self.i < self.n, "truncated array")
            if self.text[self.i] == "]":
                self.i += 1
                return values
            _require(self.text[self.i] == ",", "expected comma")
            self.i += 1

    def object(self):
        self.i += 1
        values = {}
        self.skip()
        if self.i < self.n and self.text[self.i] == "}":
            self.i += 1
            return values
        while True:
            self.skip()
            _require(self.i < self.n and self.text[self.i] == '"', "expected key")
            key = self.string()
            self.skip()
            _require(self.i < self.n and self.text[self.i] == ":", "expected colon")
            self.i += 1
            _require(key not in values, "duplicate key")
            values[key] = self.value()
            self.skip()
            _require(self.i < self.n, "truncated object")
            if self.text[self.i] == "}":
                self.i += 1
                return values
            _require(self.text[self.i] == ",", "expected comma")
            self.i += 1


def parse_json(text):
    return _Parser(text).parse()


def _read_json(path):
    return parse_json(Path(path).read_text(encoding="utf-8"))


def _tsv(path):
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    _require(lines, "empty table")
    header = lines[0].split("\t")
    _require(len(header) == len(set(header)), "duplicate table header")
    rows = []
    for line in lines[1:]:
        cells = line.split("\t")
        _require(len(cells) == len(header), "table column drift")
        rows.append(dict(zip(header, cells)))
    return rows


def _manifest_files(result_dir):
    manifest = _read_json(result_dir / "manifest.json")
    _require(manifest.get("schema_version") == 1, "manifest schema")
    files = manifest.get("files")
    _require(isinstance(files, list) and files, "manifest files")
    return files


def _group(files, role):
    return [item for item in files if item.get("role") == role]


def _prior(prior_audit):
    audit = _read_json(prior_audit)
    found = {}
    for antigen in audit["antigens"]:
        found[antigen["uniprot"]] = {
            "elution_ids": set(antigen["returned_assay_ids"]),
            "class_ii_ids": {row["elution_id"] for row in antigen["class_ii_annotations"]},
            "antigen_sha256": antigen["antigen_response_sha256"],
            "class_ii_sha256": [query["response_sha256"] for query in antigen["queries"]],
            "parent_card_sha256": antigen["parent_cardinality_check"]["response_sha256"],
        }
    _require(set(found) >= set(PARENTS), "prior audit parents")
    return found


def _parent_ids(result_dir, item):
    payload = _read_json(result_dir / item["path"])
    _require(isinstance(payload, list) and len(payload) == 1, "expected one parent record")
    ids = payload[0]["elution_ids"]
    _require(isinstance(ids, list) and len(ids) == len(set(ids)), "parent elution ids")
    return payload[0], ids


def _membership(parents):
    owner = {}
    for accession, ids in parents.items():
        for elution_id in ids:
            _require(elution_id not in owner, "assay id belongs to both parents")
            owner[elution_id] = accession
    return owner


def _xref(entry, database):
    found = [xref.get("id") for xref in entry.get("uniProtKBCrossReferences") or [] if xref.get("database") == database]
    _require(len(found) == 1, f"expected one {database} cross-reference")
    return found[0]


def _ensembl(entry):
    for xref in entry.get("uniProtKBCrossReferences") or []:
        if xref.get("database") != "Ensembl":
            continue
        for prop in xref.get("properties") or []:
            if prop.get("key") == "GeneId" and str(prop.get("value", "")).startswith("ENSG"):
                return prop["value"]
    raise ValueError("Ensembl gene missing")


def _max_ntpm(values):
    tissue, ntpm = min(values.items(), key=lambda item: (-float(item[1]), item[0]))
    return {"tissue": tissue, "ntpm": ntpm}


def derive(result_dir, prior_audit):
    result_dir = Path(result_dir)
    files = _manifest_files(result_dir)
    prior = _prior(prior_audit)
    antigen_ids = {}
    for accession in PARENTS:
        items = [item for item in _group(files, "iedb_antigen") if item.get("accession") == accession]
        cards = [item for item in _group(files, "iedb_parent_card") if item.get("accession") == accession]
        _require(len(items) == 1 and len(cards) == 1, "parent files")
        record, ids = _parent_ids(result_dir, items[0])
        card, card_ids = _parent_ids(result_dir, cards[0])
        _require(card_ids == ids, "parent card ids differ from antigen search")
        _require(card.get("parent_source_antigen_iri") == f"UNIPROT:{accession}", "parent IRI")
        _require("elution_ids" in record, "antigen record")
        antigen_ids[accession] = ids
    owner = _membership(antigen_ids)
    rows = []
    for item in _group(files, "iedb_mhc"):
        payload = _read_json(result_dir / item["path"])
        _require(isinstance(payload, list), "mhc payload")
        for record in payload:
            elution_id = record["elution_id"]
            _require(elution_id in owner, "class-II id outside both parent lists")
            _require(record.get("mhc_class") == "II", "class filter leaked")
            titles = record.get("reference_titles")
            _require(isinstance(titles, list) and len(titles) >= 1, "reference title missing")
            rows.append({
                "parent_uniprot": owner[elution_id],
                "elution_id": elution_id,
                "reference_id": record["reference_id"],
                "pubmed_id": record["pubmed_id"],
                "reference_title": titles[0],
                "mhc_class": "II",
                "mhc_allele_name": record["mhc_allele_name"],
                "mhc_allele_evidence": record["mhc_allele_evidence"],
                "assay_names": record["assay_names"],
                "qualitative_measure": record["qualitative_measure"],
                "parent_assignment": "antigen_search_membership",
            })
    _require(len({row["elution_id"] for row in rows}) == len(rows), "duplicate class-II assay")
    rows.sort(key=lambda row: (row["parent_uniprot"], row["elution_id"]))
    by_parent = {}
    for accession in PARENTS:
        selected = [row for row in rows if row["parent_uniprot"] == accession]
        selected_ids = {row["elution_id"] for row in selected}
        added = sorted(set(antigen_ids[accession]) - prior[accession]["elution_ids"])
        removed = sorted(prior[accession]["elution_ids"] - set(antigen_ids[accession]))
        references = set()
        pubmed_ids = set()
        for row in selected:
            references.add(row["reference_id"])
            pubmed_ids.add(row["pubmed_id"])
        by_parent[accession] = {
            "rows": len(selected),
            "references": len(references),
            "pubmed_ids": sorted(pubmed_ids),
            "parent_elution_ids": len(antigen_ids[accession]),
            "parent_records": 1,
            "added_since_2026_11_05": added,
            "removed_since_2026_11_05": removed,
            "class_ii_ids_unchanged_since_2026_11_05": selected_ids == prior[accession]["class_ii_ids"],
        }
    for accession in PARENTS:
        antigen_item = next(item for item in _group(files, "iedb_antigen") if item.get("accession") == accession)
        card_item = next(item for item in _group(files, "iedb_parent_card") if item.get("accession") == accession)
        mhc_items = [item for item in _group(files, "iedb_mhc") if item.get("accession") == accession]
        by_parent[accession]["antigen_bytes_match_2026_11_05"] = (
            hashlib.sha256((result_dir / antigen_item["path"]).read_bytes()).hexdigest()
            == prior[accession]["antigen_sha256"])
        by_parent[accession]["parent_card_bytes_match_2026_11_05"] = (
            hashlib.sha256((result_dir / card_item["path"]).read_bytes()).hexdigest()
            == prior[accession]["parent_card_sha256"])
        current_mhc = sorted(
            hashlib.sha256((result_dir / item["path"]).read_bytes()).hexdigest() for item in mhc_items)
        by_parent[accession]["class_ii_bytes_match_2026_11_05"] = (
            current_mhc == sorted(prior[accession]["class_ii_sha256"]))
    delta_items = _group(files, "iedb_class_i_delta")
    _require(len(delta_items) == 1, "class-I delta file")
    delta = _read_json(result_dir / delta_items[0]["path"])
    delta_ids = sorted(row["elution_id"] for row in delta)
    _require(delta_ids == by_parent["Q01850"]["added_since_2026_11_05"], "class-I delta is not the new parent ids")
    _require(not by_parent["Q86X02"]["added_since_2026_11_05"], "CDR2L parent list changed")
    _require({row["mhc_class"] for row in delta} == {"I"}, "delta is not class I")
    uniprot = {}
    for accession in PARENTS:
        items = [item for item in _group(files, "uniprot") if item.get("accession") == accession]
        _require(len(items) == 1, "uniprot file")
        entry = _read_json(result_dir / items[0]["path"])
        uniprot[accession] = {
            "accession": entry["primaryAccession"],
            "entry_type": entry["entryType"],
            "gene": entry["genes"][0]["geneName"]["value"],
            "protein": entry["proteinDescription"]["recommendedName"]["fullName"]["value"],
            "organism": entry["organism"]["scientificName"],
            "taxon_id": entry["organism"]["taxonId"],
            "length": entry["sequence"]["length"],
            "crc64": entry["sequence"]["crc64"],
            "ensembl_gene": _ensembl(entry),
            "gene_id": _xref(entry, "GeneID"),
            "hgnc": _xref(entry, "HGNC"),
            "protein_existence": entry["proteinExistence"],
        }
    consensus = _tsv(result_dir / _group(files, "hpa_consensus")[0]["path"])
    cancer_rows = _tsv(result_dir / _group(files, "hpa_cancer_ihc")[0]["path"])
    normal_rows = _tsv(result_dir / _group(files, "hpa_normal_ihc")[0]["path"])
    hpa = {}
    for accession in PARENTS:
        items = [item for item in _group(files, "hpa_gene") if item.get("accession") == accession]
        _require(len(items) == 1, "hpa gene file")
        summary = _read_json(result_dir / items[0]["path"])
        ensembl = summary["Ensembl"]
        _require(summary["Uniprot"] == [accession], "HPA UniProt accession")
        _require(uniprot[accession]["ensembl_gene"].split(".", 1)[0] == ensembl, "Ensembl version stem")
        ntpm = {}
        for row in consensus:
            if row["Gene"] == ensembl:
                _require(row["Tissue"] not in ntpm, "duplicate tissue")
                ntpm[row["Tissue"]] = row["nTPM"]
        cancers = {}
        for row in cancer_rows:
            if row["Gene"] != ensembl:
                continue
            high, medium, low, missed = (int(row["High"]), int(row["Medium"]), int(row["Low"]), int(row["Not detected"]))
            cancers[row["Cancer"]] = {
                "high": high, "medium": medium, "low": low, "not_detected": missed,
                "patients": high + medium + low + missed,
            }
        own_normal = [row for row in normal_rows if row["Gene"] == ensembl]
        hpa[uniprot[accession]["gene"]] = {
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
            "consensus_max": _max_ntpm(ntpm),
            "cancer_ihc": {name: cancers[name] for name in GYN_CANCERS},
            "cancer_patient_total": sum(item["patients"] for item in cancers.values()),
            "cancer_types": len(cancers),
            "normal_ihc_rows": len(own_normal),
            "normal_ihc": sorted(
                [{"tissue": row["Tissue"], "cell_type": row["Cell type"], "level": row["Level"],
                  "reliability": row["Reliability"]} for row in own_normal],
                key=lambda row: (row["tissue"], row["cell_type"], row["level"]),
            ),
        }
    tcga_rows = _tsv(result_dir / _group(files, "hpa_tcga_cancers")[0]["path"])
    tissues = _tsv(result_dir / _group(files, "hpa_consensus_tissues")[0]["path"])
    legend = {row["Tissue"] for row in tissues}
    _require(set(FOCUS_TISSUES) <= legend, "tissue legend")
    return {
        "checker": "recompute_membership",
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
        "tcga_samples": {row["Cancer"]: int(row["Num samples"]) for row in tcga_rows},
    }
