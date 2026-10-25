"""In-memory source-format fixtures; no study data, network or file writes."""

import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
import warnings
import zipfile
import zlib
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import source_data_adapter as adapter

MAIN = adapter.NS["s"]
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
DOC_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def workbook(sheets, shared=False):
    """Build minimal genuine XLSX container bytes; special dict cells are XML."""
    package = io.BytesIO()
    root = ET.Element("workbook", xmlns=MAIN)
    sheet_nodes = ET.SubElement(root, "sheets")
    rels = ET.Element("Relationships", xmlns=REL)
    strings = []
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        for number, (name, rows) in enumerate(sheets.items(), 1):
            ET.SubElement(sheet_nodes, "sheet", name=name, sheetId=str(number),
                          attrib={"{" + DOC_REL + "}id": f"rId{number}"})
            ET.SubElement(rels, "Relationship", Id=f"rId{number}",
                          Target=f"worksheets/sheet{number}.xml")
            worksheet = ET.Element("worksheet", xmlns=MAIN)
            data = ET.SubElement(worksheet, "sheetData")
            for row_number, values in enumerate(rows, 1):
                row = ET.SubElement(data, "row", r=str(row_number))
                for column, value in values.items():
                    cell = ET.SubElement(row, "c", r=column + str(row_number))
                    if isinstance(value, dict):
                        cell.set("t", value.get("type", "n"))
                        if "formula" in value:
                            ET.SubElement(cell, "f").text = value["formula"]
                        ET.SubElement(cell, "v").text = value.get("value", "")
                    elif shared:
                        cell.set("t", "s")
                        ET.SubElement(cell, "v").text = str(len(strings))
                        strings.append(value)
                    else:
                        cell.set("t", "inlineStr")
                        ET.SubElement(ET.SubElement(cell, "is"), "t").text = value
            archive.writestr(f"xl/worksheets/sheet{number}.xml", ET.tostring(worksheet))
        archive.writestr("xl/workbook.xml", ET.tostring(root))
        archive.writestr("xl/_rels/workbook.xml.rels", ET.tostring(rels))
        if shared:
            table = ET.Element("sst", xmlns=MAIN)
            for value in strings:
                ET.SubElement(ET.SubElement(table, "si"), "t").text = value
            archive.writestr("xl/sharedStrings.xml", ET.tostring(table))
    return package.getvalue()


def pin_workbook(body):
    return {"bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
            "md5": hashlib.md5(body).hexdigest()}


def pin_matrix(body, contract):
    compressor = zlib.compressobj(wbits=-15)
    packed = compressor.compress(body) + compressor.flush()
    result = copy.deepcopy(contract)
    result["member"].update(compressed_bytes=len(packed), uncompressed_bytes=len(body),
                             compressed_sha256=hashlib.sha256(packed).hexdigest(),
                             sha256=hashlib.sha256(body).hexdigest(), crc32=zlib.crc32(body))
    result["matrix"]["header_sha256"] = hashlib.sha256(body.splitlines(keepends=True)[0]).hexdigest()
    return packed, result


def make_fixture(mutator=None, shared=False):
    """Return packed matrix, two workbooks, complete small fixture contract."""
    clinical_columns = dict(zip("ABCDEFG", adapter.CLINICAL_COLUMNS))
    clinical = [clinical_columns]
    names = ["abstract-a-1", "abstract-a-2", "abstract-a-3", "abstract-b", "abstract-excluded"]
    for index, label in enumerate(names):
        sample = "a" if index < 3 else ("b" if index == 3 else "excluded")
        values = [label, "abstract-patient-" + sample, "abstract-sample-" + sample,
                  "yes" if index == 4 else "no", "sensitive" if index < 3 else "refractory",
                  "NA" if index == 3 else "OV", "abstract-type"]
        clinical.append(dict(zip("ABCDEFG", values)))
    clinical.append(dict(zip("ABCDEFG", ["abstract-control"] + ["NA"] * 6)))
    clinical_sheets = {"FFPE_Discovery_clinical": clinical}
    panel_sheets = {
        "64_protein_predictors": [{"A": "Proteins"}, {"A": "abstract-feature-A"}, {"A": "abstract-feature-B"}],
        "FFPE_pred_scores": [{"A": "Samples", "B": "Pred.scores"},
                             {"A": "abstract-a-2", "B": {"formula": "PRIVATE_SENTINEL", "value": "not-a-number"}},
                             {"A": "abstract-b", "B": {"type": "s", "value": "unreadable-index"}}],
    }
    header = list(adapter.features.ANNOTATIONS) + names + ["abstract-control"]
    rows = [["abstract-accession-B", "abstract-feature-B", "name", "location", "index-b", "1", "1", "protein", "1",
             "12", "0", "-6", "-3", "Inf", "unused-control"],
            ["abstract-accession-A", "abstract-feature-A", "name", "location", "index-a", "1", "1", "protein", "1",
             "2", "6", "10", "9", "NA", "unused-control"],
            ["abstract-accession-X", "abstract-unused", "name", "location", "index-x", "1", "1", "protein", "1"]
            + ["unread-unused-values"] * 6]
    if mutator:
        mutator(clinical_sheets, panel_sheets, header, rows)
    clinical_bytes, panel_bytes = workbook(clinical_sheets, shared), workbook(panel_sheets, shared)
    body = ("\t".join(header) + "\n" + "".join("\t".join(row) + "\n" for row in rows)).encode()
    contract = copy.deepcopy(adapter.DEFAULT_CONTRACT)
    contract["workbooks"] = {"clinical": pin_workbook(clinical_bytes), "panel_and_scores": pin_workbook(panel_bytes)}
    contract["matrix"].update(rows=3, columns=15)
    contract["panel"] = {"count": 2, "sha256": hashlib.sha256(b"abstract-feature-A\nabstract-feature-B\n").hexdigest()}
    contract["cohort"] = {"measurements": 5, "samples": 3, "patients": 3, "selected": 2,
                          "negative": 1, "positive": 1, "triplicate_groups": 1, "singletons": 2,
                          "retained_missing_location": 1, "clinical_na": 1, "clinical_rows": 6}
    packed, contract = pin_matrix(body, contract)
    return packed, clinical_bytes, panel_bytes, contract


def parse(fixture):
    return adapter.parse_sources(*fixture[:3], contract=fixture[3])


def rewrite_zip(body, change):
    with zipfile.ZipFile(io.BytesIO(body)) as source:
        members = {name: source.read(name) for name in source.namelist()}
    change(members)
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
        for name, value in members.items():
            target.writestr(name, value)
    return output.getvalue()


@contextlib.contextmanager
def mocked_acquisition(chunks=(b"abc", b"de"), bad_response=None, drift=False):
    """All acquisition dependencies mocked; no live URL can be called."""
    bodies = {"clinical": b"abstract-clinical", "panel_and_scores": b"abstract-panel"}
    sources = {key: dict(pin_workbook(body), filename=adapter.cohorts.SOURCES[key]["filename"])
               for key, body in bodies.items()}
    requests, reads = [], []
    class Response(io.BytesIO):
        def __init__(self, key, url):
            super().__init__(bodies[key] + (b"x" if bad_response == "overflow" else b""))
            self.status = 206 if bad_response == "status" else 200
            self.headers = {"Content-Encoding": "gzip" if bad_response == "encoding" else "identity"}
            self.url = "https://example.invalid/redirect" if bad_response == "redirect" else url
        def geturl(self):
            return self.url
        def read(self, size=-1):
            reads.append(size)
            return super().read(size)
    def open_request(request, timeout):
        requests.append(request)
        key = next(key for key, source in sources.items() if request.full_url.endswith(source["filename"]))
        return Response(key, request.full_url)
    contract = copy.deepcopy(adapter.DEFAULT_CONTRACT)
    contract["member"]["compressed_bytes"] = 5
    directory = {"sha256": adapter.archive.CENTRAL_SHA256, "entries": 42}
    second = dict(directory, entries=41) if drift else directory
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.object(adapter, "DEFAULT_CONTRACT", contract))
        stack.enter_context(mock.patch.object(adapter.cohorts, "SOURCES", sources))
        fetch = stack.enter_context(mock.patch.object(adapter.archive, "fetch_range", return_value=b"abstract-tail"))
        inspect = stack.enter_context(mock.patch.object(adapter.archive, "inspect_directory", side_effect=[(b"abstract-member", directory), (b"abstract-member", second)]))
        offset = stack.enter_context(mock.patch.object(adapter.archive, "member_data_offset", return_value=123))
        member = stack.enter_context(mock.patch.object(adapter.features, "member_chunks", return_value=iter(chunks)))
        stack.enter_context(mock.patch.object(adapter.urllib.request, "urlopen", side_effect=open_request))
        parser = stack.enter_context(mock.patch.object(adapter, "parse_sources", return_value={"provenance": {}}))
        yield {"requests": requests, "reads": reads, "sources": sources, "fetch": fetch,
               "inspect": inspect, "offset": offset, "member": member, "parser": parser,
               "bodies": bodies}


class SourceAdapterChecks(unittest.TestCase):
    def rejects(self, fixture):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            with self.assertRaises(adapter.SourceAdapterError) as caught:
                parse(fixture)
        self.assertEqual(str(caught.exception), adapter.FAILURE)
        self.assertTrue(caught.exception.__suppress_context__)
        self.assertEqual(out.getvalue() + err.getvalue(), "")

    def test_exact_input_payload_keeps_all_replicates_in_panel_order(self):
        result = parse(make_fixture())
        self.assertEqual(result["measurements"]["row_names"], ["abstract-feature-A", "abstract-feature-B"])
        self.assertEqual(result["measurements"]["values"], [[2, 6, 10, 9, None], [12, 0, -6, -3, None]])
        self.assertEqual(len(result["measurements"]["column_names"]), 5)
        self.assertEqual(result["published_keys"], ["abstract-a-2", "abstract-b"])
        self.assertEqual(result["clinical"]["columns"], adapter.CLINICAL_COLUMNS)
        self.assertFalse(result["provenance"]["published_score_values_read"])
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(result, allow_nan=False))
        self.assertNotIn("abstract-", json.dumps(result["provenance"]))

    def test_shared_strings_and_inline_strings_produce_identical_private_payload(self):
        inline, shared = parse(make_fixture()), parse(make_fixture(shared=True))
        inline.pop("provenance"); shared.pop("provenance")
        self.assertEqual(inline, shared)

    def test_integrity_checks_precede_any_workbook_or_numeric_parsing(self):
        fixture = make_fixture()
        for position in range(3):
            changed = list(fixture)
            changed[position] = changed[position][:-1] + bytes([changed[position][-1] ^ 1])
            with mock.patch.object(adapter, "MemoryWorkbook") as book, mock.patch.object(adapter, "_number") as number:
                self.rejects(changed)
            book.assert_not_called(); number.assert_not_called()

    def test_missing_or_extra_source_bytes_are_rejected(self):
        for position in range(3):
            for suffix in (None, b"x"):
                changed = list(make_fixture())
                changed[position] = changed[position][:-1] if suffix is None else changed[position] + suffix
                self.rejects(changed)

    def test_crc_header_and_uncompressed_hash_are_independently_checked(self):
        for section, key, value in (("member", "crc32", 0), ("member", "sha256", "0" * 64),
                                    ("matrix", "header_sha256", "0" * 64),
                                    ("member", "uncompressed_bytes", 1)):
            changed = list(make_fixture())
            changed[3][section][key] = value
            self.rejects(changed)

    def test_truncated_concatenated_and_trailing_deflate_streams_rejected_even_when_hash_repinned(self):
        for operation in (lambda value: value[:-1], lambda value: value + b"x", lambda value: value + value):
            changed = list(make_fixture()); changed[0] = operation(changed[0])
            changed[3]["member"].update(compressed_bytes=len(changed[0]), compressed_sha256=hashlib.sha256(changed[0]).hexdigest())
            self.rejects(changed)

    def test_selected_values_must_be_finite_strict_decimal_numbers(self):
        for value in ("NA", "NaN", "Inf", "1e999", "1_000", " 1", "1 ", "=2+2", "PRIVATE_SENTINEL"):
            self.rejects(make_fixture(lambda c, p, h, r: r[0].__setitem__(9, value)))

    def test_numeric_scores_are_never_decoded_even_if_malformed_or_formula(self):
        original = adapter.MemoryWorkbook.value
        def checked(book, cell):
            if cell.get("r") in ("B2", "B3") and (cell.find("s:f", adapter.NS) is not None or cell.get("t") == "s"):
                self.fail("Prediction cell decoding attempted")
            return original(book, cell)
        with mock.patch.object(adapter.MemoryWorkbook, "value", checked):
            result = parse(make_fixture())
        self.assertFalse(result["provenance"]["published_score_values_read"])

    def test_formula_cells_in_used_clinical_panel_or_membership_fields_rejected(self):
        mutations = [lambda c, p, h, r: c["FFPE_Discovery_clinical"][1].__setitem__("A", {"formula": "PRIVATE_SENTINEL", "value": "abstract-a-1"}),
                     lambda c, p, h, r: p["64_protein_predictors"][1].__setitem__("A", {"formula": "PRIVATE_SENTINEL", "value": "abstract-feature-A"}),
                     lambda c, p, h, r: p["FFPE_pred_scores"][1].__setitem__("A", {"formula": "PRIVATE_SENTINEL", "value": "abstract-a-2"})]
        for mutation in mutations:
            self.rejects(make_fixture(mutation))

    def test_exact_identity_and_membership_changes_fail_without_normalizing(self):
        mutations = [lambda c, p, h, r: h.__setitem__(9, " abstract-a-1"),
                     lambda c, p, h, r: h.__setitem__(9, "abstract-a-2"),
                     lambda c, p, h, r: p["FFPE_pred_scores"][1].__setitem__("A", "abstract-excluded"),
                     lambda c, p, h, r: p["FFPE_pred_scores"][1].__setitem__("A", "abstract-b"),
                     lambda c, p, h, r: p["64_protein_predictors"][1].__setitem__("A", "abstract-feature-a"),
                     lambda c, p, h, r: c["FFPE_Discovery_clinical"][2].__setitem__("B", "abstract-other-patient"),
                     lambda c, p, h, r: c["FFPE_Discovery_clinical"][2].__setitem__("E", "refractory"),
                     lambda c, p, h, r: c["FFPE_Discovery_clinical"][2].__setitem__("A", "abstract-a-1")]
        for mutation in mutations:
            self.rejects(make_fixture(mutation))

    def test_matrix_schema_feature_multiplicity_and_row_width_fail_closed(self):
        mutations = [lambda c, p, h, r: h.__setitem__(1, "renamed-feature-key"),
                     lambda c, p, h, r: r[0].__setitem__(1, "abstract-feature-A"),
                     lambda c, p, h, r: r[0].__setitem__(1, "missing-feature"),
                     lambda c, p, h, r: r[0].pop(),
                     lambda c, p, h, r: r.pop(),
                     lambda c, p, h, r: r[0].__setitem__(1, '"abstract-feature-B"tail'),
                     lambda c, p, h, r: r[0].__setitem__(1, "abstract-feature-B\rhidden")]
        for mutation in mutations:
            self.rejects(make_fixture(mutation))

    def test_balanced_tsv_quoting_preserves_exact_feature_and_numeric_values(self):
        result = parse(make_fixture(lambda c, p, h, r: (r[0].__setitem__(1, '"abstract-feature-B"'),
                                                         r[0].__setitem__(9, '"12"'))))
        self.assertEqual(result["measurements"]["values"][1][0], 12)

    def test_unused_feature_values_are_not_decoded_or_converted(self):
        fixture = list(make_fixture())
        body = zlib.decompress(fixture[0], -15).replace(b"unread-unused-values", b"\xff\xfe")
        fixture[0], fixture[3] = pin_matrix(body, fixture[3])
        self.assertEqual(parse(fixture)["measurements"]["values"][0][:4], [2, 6, 10, 9])

    def test_xlsx_entities_external_paths_and_duplicate_addresses_rejected(self):
        operations = [lambda files: files.__setitem__("xl/workbook.xml", b'<!DOCTYPE workbook [<!ENTITY leak "PRIVATE_SENTINEL">]>' + files["xl/workbook.xml"]),
                      lambda files: files.__setitem__("xl/workbook.xml", ('<!DOCTYPE workbook [<!ENTITY leak "PRIVATE_SENTINEL">]>' + files["xl/workbook.xml"].decode()).encode("utf-16")),
                      lambda files: files.__setitem__("xl/_rels/workbook.xml.rels", files["xl/_rels/workbook.xml.rels"].replace(b'worksheets/sheet1.xml', b'../sheet1.xml')),
                      lambda files: files.__setitem__("xl/worksheets/sheet1.xml", files["xl/worksheets/sheet1.xml"].replace(b'r="B2"', b'r="A2"'))]
        for operation in operations:
            fixture = list(make_fixture()); fixture[1] = rewrite_zip(fixture[1], operation)
            fixture[3]["workbooks"]["clinical"] = pin_workbook(fixture[1])
            self.rejects(fixture)

    def test_zip_duplicate_member_and_xml_size_bounds_rejected(self):
        fixture = list(make_fixture())
        output = io.BytesIO(fixture[1])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(output, "a") as archive:
                archive.writestr("xl/workbook.xml", "PRIVATE_SENTINEL")
        fixture[1] = output.getvalue(); fixture[3]["workbooks"]["clinical"] = pin_workbook(fixture[1])
        self.rejects(fixture)
        with mock.patch.object(adapter, "MAX_XML_BYTES", 1):
            self.rejects(make_fixture())

    def test_explicit_acquisition_uses_only_pinned_ranges_urls_and_bounded_reads(self):
        with mocked_acquisition() as state:
            result = adapter.load_pinned_sources()
        start = adapter.archive.ARCHIVE_BYTES - adapter.archive.TAIL_BYTES
        self.assertEqual(state["fetch"].call_args_list,
                         [mock.call(start, adapter.archive.ARCHIVE_BYTES - 1)] * 2)
        state["offset"].assert_called_once_with(state["fetch"], b"abstract-member")
        state["member"].assert_called_once_with(123)
        self.assertEqual([request.full_url for request in state["requests"]],
                         [adapter.cohorts.BASE + source["filename"] for source in state["sources"].values()])
        self.assertEqual(state["reads"], [source["bytes"] + 1 for source in state["sources"].values()])
        state["parser"].assert_called_once_with(b"abcde", state["bodies"]["clinical"],
                                               state["bodies"]["panel_and_scores"])
        self.assertTrue(result["provenance"]["archive_directory_rechecked"])
        self.assertFalse(result["provenance"]["whole_archive_checksum_verified"])

    def test_acquisition_rejects_chunk_bounds_truncation_and_directory_drift(self):
        for chunks, drift in (((), False), ((b"abc",), False), ((b"abcdef",), False),
                              ((b"x" * (adapter.features.CHUNK_BYTES + 1),), False),
                              ((b"abc", b"de"), True)):
            with mocked_acquisition(chunks=chunks, drift=drift) as state:
                with self.assertRaises(adapter.SourceAdapterError) as error:
                    adapter.load_pinned_sources()
            self.assertEqual(str(error.exception), adapter.FAILURE)
            state["parser"].assert_not_called()
            self.assertEqual(state["requests"], [])

    def test_acquisition_rejects_malformed_redirect_encoding_status_or_overflow(self):
        for failure in ("redirect", "encoding", "status", "overflow"):
            with mocked_acquisition(bad_response=failure) as state:
                with self.assertRaises(adapter.SourceAdapterError) as error:
                    adapter.load_pinned_sources()
            self.assertEqual(str(error.exception), adapter.FAILURE)
            state["parser"].assert_not_called()
        with mocked_acquisition() as state, mock.patch.object(adapter.archive, "fetch_range", side_effect=ValueError("PRIVATE_SENTINEL")):
            with self.assertRaises(adapter.SourceAdapterError) as error:
                adapter.load_pinned_sources()
            self.assertEqual(str(error.exception), adapter.FAILURE)
            state["parser"].assert_not_called()

    def test_default_contract_rejects_fixture_pins_and_bounds_cannot_be_raised(self):
        fixture = make_fixture()
        with self.assertRaises(adapter.SourceAdapterError):
            adapter.parse_sources(*fixture[:3])
        for group, field in (("member", "uncompressed_bytes"), ("matrix", "rows"), ("cohort", "selected")):
            changed = list(make_fixture()); changed[3][group][field] = adapter.DEFAULT_CONTRACT[group][field] + 1
            self.rejects(changed)


if __name__ == "__main__":
    unittest.main()
