#!/usr/bin/env python3
"""Re-run two CDR2/CDR2L atlas checkers against the pinned snapshot.

Offline mode fails if the checkers disagree or a pinned file hash changes.
``--live`` re-fetches the recorded URLs and refuses to write snapshot bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import urllib.request
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
RESULT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from tools import cdr2_atlas_export as export_checker
from tools import cdr2_atlas_recompute as recompute_checker

SUMS = RESULT / "SHA256SUMS"
PRIOR = ROOT / "registries/antigen-metadata-audit-2026-11-05.json"
DOC = ROOT / "docs/cdr2-cdr2l-evidence-atlas-2026-11-13.md"
PAGE = ROOT / "index.html"
BEGIN = "<!-- BEGIN CDR2 ATLAS COUNTS -->"
END = "<!-- END CDR2 ATLAS COUNTS -->"
UA = "project-asma-cdr2-atlas/2026-11-13 (public metadata; https://github.com/Foundation-0/project-asma)"
GENES = ("ENSG00000140743", "ENSG00000109089")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def comparable(result):
    copied = json.loads(json.dumps(result))
    copied.pop("checker", None)
    for row in copied["class_ii_rows"]:
        row.pop("parent_assignment", None)
    return copied


def render_counts(result):
    cdr2 = result["by_parent"]["Q01850"]
    cdr2l = result["by_parent"]["Q86X02"]
    hpa2 = result["hpa"]["CDR2"]
    hpa2l = result["hpa"]["CDR2L"]
    ovary2 = hpa2["cancer_ihc"]["ovarian cancer"]
    ovary2l = hpa2l["cancer_ihc"]["ovarian cancer"]
    lines = [
        f"CDR2 Q01850 class-II assays: {cdr2['rows']}",
        f"CDR2L Q86X02 class-II assays: {cdr2l['rows']}",
        f"CDR2 class-II references: {cdr2['references']}",
        f"CDR2L class-II references: {cdr2l['references']}",
        f"CDR2 parent elution IDs: {cdr2['parent_elution_ids']}",
        f"CDR2L parent elution IDs: {cdr2l['parent_elution_ids']}",
        f"CDR2 parent IDs added since 2026-11-05: {len(cdr2['added_since_2026_11_05'])}",
        f"CDR2L parent IDs added since 2026-11-05: {len(cdr2l['added_since_2026_11_05'])}",
        f"class-II assay IDs unchanged since 2026-11-05: {cdr2['class_ii_ids_unchanged_since_2026_11_05'] and cdr2l['class_ii_ids_unchanged_since_2026_11_05']}",
        f"CDR2L antigen, parent-card and class-II bytes match 2026-11-05: {cdr2l['antigen_bytes_match_2026_11_05'] and cdr2l['parent_card_bytes_match_2026_11_05'] and cdr2l['class_ii_bytes_match_2026_11_05']}",
        f"CDR2 antigen bytes match 2026-11-05: {cdr2['antigen_bytes_match_2026_11_05']}",
        f"CDR2 class-II response hash multiset matches 2026-11-05: {cdr2['class_ii_bytes_match_2026_11_05']}",
        f"class-I delta rows: {result['class_i_delta']['rows']}",
        f"class-I delta pubmed: {','.join(result['class_i_delta']['pubmed_ids'])}",
        f"CDR2 amino acids: {result['uniprot']['Q01850']['length']}",
        f"CDR2L amino acids: {result['uniprot']['Q86X02']['length']}",
        f"CDR2 GeneID: {result['uniprot']['Q01850']['gene_id']}",
        f"CDR2 HGNC: {result['uniprot']['Q01850']['hgnc']}",
        f"CDR2L GeneID: {result['uniprot']['Q86X02']['gene_id']}",
        f"CDR2L HGNC: {result['uniprot']['Q86X02']['hgnc']}",
        f"CDR2 cerebellum nTPM: {hpa2['consensus_ntpm']['cerebellum']}",
        f"CDR2 ovary nTPM: {hpa2['consensus_ntpm']['ovary']}",
        f"CDR2L cerebellum nTPM: {hpa2l['consensus_ntpm']['cerebellum']}",
        f"CDR2L ovary nTPM: {hpa2l['consensus_ntpm']['ovary']}",
        f"CDR2 consensus max: {hpa2['consensus_max']['tissue']} {hpa2['consensus_max']['ntpm']}",
        f"CDR2L consensus max: {hpa2l['consensus_max']['tissue']} {hpa2l['consensus_max']['ntpm']}",
        f"CDR2 ovarian cancer IHC patients: {ovary2['patients']} high {ovary2['high']} medium {ovary2['medium']} low {ovary2['low']} not_detected {ovary2['not_detected']}",
        f"CDR2L ovarian cancer IHC patients: {ovary2l['patients']} high {ovary2l['high']} medium {ovary2l['medium']} low {ovary2l['low']} not_detected {ovary2l['not_detected']}",
        f"TCGA ovary serous cystadenocarcinoma samples: {result['tcga_samples']['Ovary Serous Cystadenocarcinoma']}",
    ]
    return "\n".join(lines)


def marked_block(text):
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("Atlas count markers missing or duplicated.")
    return text.split(BEGIN, 1)[1].split(END, 1)[0].strip("\n")


def check_reports(result_dir=RESULT, prior_audit=PRIOR, doc_path=DOC, page_path=PAGE):
    export_result = export_checker.derive(result_dir, prior_audit)
    recompute_result = recompute_checker.derive(result_dir, prior_audit)
    if comparable(export_result) != comparable(recompute_result):
        raise ValueError("Export and recompute checkers disagree.")
    if export_result["checker"] == recompute_result["checker"]:
        raise ValueError("Checkers did not keep independent labels.")
    counts = render_counts(export_result)
    if marked_block(doc_path.read_text(encoding="utf-8")) != counts:
        raise ValueError("Paper count block differs from the checkers.")
    if marked_block(page_path.read_text(encoding="utf-8")) != counts:
        raise ValueError("Page count block differs from the checkers.")
    return export_result


def snapshot_files(result_dir=RESULT):
    manifest = json.loads((result_dir / "manifest.json").read_text(encoding="utf-8"))
    paths = ["manifest.json"]
    for item in manifest["files"]:
        paths.append(item["path"])
    return paths


def read_sums(result_dir=RESULT):
    sums = {}
    text = (result_dir / "SHA256SUMS").read_text(encoding="utf-8")
    for line in text.splitlines():
        digest, name = line.split("  ", 1)
        if name in sums:
            raise ValueError("Duplicate hash entry.")
        sums[name] = digest
    return sums


def check_hashes(result_dir=RESULT):
    expected = read_sums(result_dir)
    present = snapshot_files(result_dir)
    if set(expected) != set(present):
        raise ValueError("Hash list does not match the manifest file set.")
    for name, digest in expected.items():
        body = (result_dir / name).read_bytes()
        if sha256(body) != digest:
            raise ValueError(f"Snapshot hash changed: {name}")
    return expected


def extract_gene_tsv(zip_bytes, member, genes=GENES):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        raw = archive.read(member)
    lines = raw.splitlines(keepends=True)
    if not lines:
        raise ValueError("Empty HPA table.")
    kept = [lines[0]]
    for line in lines[1:]:
        gene = line.split(b"\t", 1)[0].decode("ascii")
        if gene in genes:
            kept.append(line)
    return b"".join(kept)


def unzip_member(zip_bytes, member):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        return archive.read(member)


def default_fetch(url, headers):
    request = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*", **(headers or {})})
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read(), {key.lower(): value for key, value in response.headers.items()}


def live_check(result_dir=RESULT, fetch=default_fetch):
    """Re-fetch recorded URLs. Never creates or overwrites a snapshot file."""
    manifest = json.loads((Path(result_dir) / "manifest.json").read_text(encoding="utf-8"))
    mismatches = []
    for item in manifest["files"]:
        target = Path(result_dir) / item["path"]
        if not target.is_file():
            raise ValueError(f"Refusing to create missing snapshot file: {item['path']}")
        before = target.read_bytes()
        body, headers = fetch(item["url"], item.get("request_headers") or {})
        kind = item.get("kind", "raw")
        if kind == "raw":
            got = body
        elif kind == "zip-gene-extract":
            if sha256(body) != item["source_zip_sha256"]:
                mismatches.append(item["path"] + " source zip")
                got = before
            else:
                got = extract_gene_tsv(body, item["member"])
        elif kind == "zip-member":
            if sha256(body) != item["source_zip_sha256"]:
                mismatches.append(item["path"] + " source zip")
                got = before
            else:
                got = unzip_member(body, item["member"])
        else:
            raise ValueError("Unknown snapshot kind.")
        if item.get("content_range") and headers.get("content-range") != item["content_range"]:
            mismatches.append(item["path"] + " content-range")
        if got != before:
            mismatches.append(item["path"])
        if target.read_bytes() != before:
            raise ValueError("Live check wrote snapshot bytes.")
    if mismatches:
        raise ValueError("Live bytes differ; committed snapshot was not overwritten: " + ", ".join(mismatches))
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="re-fetch and compare; do not write snapshot bytes")
    args = parser.parse_args()
    try:
        check_hashes()
        result = check_reports()
        if args.live:
            live_check()
            print("PASS: live bytes match the committed snapshot; no snapshot file was written.")
        else:
            print("PASS: two checkers agree and the pinned snapshot hashes match.")
        print(render_counts(result))
        print("Offline agreement does not establish anti-Yo receptor recognition, causation, or clinical performance.")
    except Exception as exc:
        print("FAIL: CDR2/CDR2L atlas verification.", file=sys.stderr)
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
