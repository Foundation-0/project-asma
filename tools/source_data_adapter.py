#!/usr/bin/env python3
"""Parse pinned source bytes into an in-memory reconstruction payload.

parse_sources performs no file/network I/O. load_pinned_sources is an explicit
network acquisition function, without a CLI. It refuses to run without an entry
in the owner's attestation file; callers must still establish actual
data-use/execution conditions before calling it or supplying study bytes.
Only the provenance field of a returned payload is safe to print.
"""

import collections
import copy
import datetime
import hashlib
import io
import json
import math
from pathlib import Path
import posixpath
import re
import urllib.parse
import urllib.request
import zipfile
import zlib
from xml.etree import ElementTree as ET

import audit_author_archive as archive
import audit_author_features as features
import audit_published_cohorts as cohorts

FAILURE = "ERROR: source adapter failed; no row-level details emitted."
# Fixed aggregate codes naming the stage that failed; never row data or values.
CATEGORIES = ("contract", "source_bytes", "workbook", "clinical", "panel_membership",
              "matrix", "matrix_value", "acquisition", "authorization")
# Created and edited only by the owner; this repository does not contain it.
ATTESTATIONS = Path(__file__).resolve().parents[1] / "registries/pilot-001-owner-attestations.json"
ATTESTATION_FIELDS = {"id", "date", "execution_context", "instruction"}
MAX_ATTESTATION_BYTES = 64 * 1024
CLINICAL_COLUMNS = [cohorts.LABEL_COLUMN] + cohorts.CRITICAL
NS = cohorts.NS
RELATIONSHIP_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
MAX_XML_BYTES = 128 * 1024 * 1024
MAX_WORKBOOK_MEMBERS = 2048
MAX_XML_ROWS = 100000
MAX_LINE_BYTES = 65536
NUMBER = re.compile(r"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?\Z")
DEFAULT_CONTRACT = {
    "member": dict(archive.MEMBER_CONTRACT,
                   compressed_sha256="38268f2c80a50562c7d102446136c71ab5e6e20a283813598610f148095a79c6",
                   sha256="b7eea435bb7fa65f31a6e8f50d977ff046f0f9bd851126e43cf9a5f52e62be62"),
    "workbooks": copy.deepcopy(cohorts.SOURCES),
    "matrix": {"rows": 8800, "columns": 178, "header_sha256": features.HEADER_SHA256},
    "panel": {"count": 64, "sha256": features.PANEL_SHA256},
    "cohort": {"measurements": 168, "samples": 158, "patients": 158,
               "selected": 135, "negative": 83, "positive": 52,
               "triplicate_groups": 5, "singletons": 153,
               "retained_missing_location": 1, "clinical_na": 63, "clinical_rows": 231},
}


class SourceAdapterError(ValueError):
    """Fixed-message failure; never include input values in exceptions.

    category is None or one code from CATEGORIES; any other value becomes None,
    so stray text never surfaces. The public functions always set a code from
    CATEGORIES. The message stays FAILURE.
    """

    def __init__(self, category=None):
        super().__init__(FAILURE)
        self.category = category if type(category) is str and category in CATEGORIES else None


def require(condition, category=None):
    if not condition:
        raise SourceAdapterError(category)


def _identity(value, literal_na=False):
    return (isinstance(value, str) and bool(value) and value == value.strip()
            and not any(c in value for c in "\x00\r\n\t") and (literal_na or value != "NA"))


def _check_contract(contract):
    require(isinstance(contract, dict) and set(contract) == set(DEFAULT_CONTRACT))
    for group, fields in (("matrix", ("rows", "columns")), ("panel", ("count",))):
        for field in fields:
            value = contract[group][field]
            require(type(value) is int and 0 < value <= DEFAULT_CONTRACT[group][field])
    require(contract["matrix"]["columns"] > len(features.ANNOTATIONS))
    for field, maximum in DEFAULT_CONTRACT["cohort"].items():
        value = contract["cohort"][field]
        require(type(value) is int and 0 <= value <= maximum)
    require(set(contract["cohort"]) == set(DEFAULT_CONTRACT["cohort"]))
    for field in ("compressed_bytes", "uncompressed_bytes"):
        value = contract["member"][field]
        require(type(value) is int and 0 < value <= DEFAULT_CONTRACT["member"][field])
    for key in cohorts.SOURCES:
        value = contract["workbooks"][key]["bytes"]
        require(type(value) is int and 0 < value <= cohorts.SOURCES[key]["bytes"])


def _verify_bytes(body, source):
    require(type(body) is bytes and len(body) == source["bytes"], "source_bytes")
    require(hashlib.sha256(body).hexdigest() == source["sha256"], "source_bytes")
    if "md5" in source:
        require(hashlib.md5(body).hexdigest() == source["md5"], "source_bytes")


def _inflate(packed, contract):
    require(type(packed) is bytes and len(packed) == contract["compressed_bytes"], "source_bytes")
    require(hashlib.sha256(packed).hexdigest() == contract["compressed_sha256"], "source_bytes")
    inflater = zlib.decompressobj(-15)
    body = inflater.decompress(packed, contract["uncompressed_bytes"] + 1)
    require(inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail, "source_bytes")
    require(len(body) == contract["uncompressed_bytes"], "source_bytes")
    require(zlib.crc32(body) == contract["crc32"], "source_bytes")
    require(hashlib.sha256(body).hexdigest() == contract["sha256"], "source_bytes")
    return body


class MemoryWorkbook:
    """Read selected cells from an already verified XLSX byte buffer."""

    def __init__(self, body):
        self.archive = zipfile.ZipFile(io.BytesIO(body))
        members = self.archive.infolist()
        names = [member.filename for member in members]
        require(0 < len(names) <= MAX_WORKBOOK_MEMBERS and len(names) == len(set(names)))
        require(all(not member.flag_bits & 1 for member in members))
        require(all(not name.startswith("/") and ".." not in name.split("/")
                    and "\\" not in name for name in names))
        self.strings = []
        if "xl/sharedStrings.xml" in names:
            self.strings = ["".join(node.text or "" for node in item.findall(".//s:t", NS))
                            for item in self.xml("xl/sharedStrings.xml")]
        relationships = {}
        for relation in self.xml("xl/_rels/workbook.xml.rels"):
            key, target = relation.get("Id"), relation.get("Target")
            require(_identity(key) and key not in relationships and _identity(target))
            require(relation.get("TargetMode", "Internal") == "Internal")
            require("\\" not in target and ".." not in target.split("/"))
            path = target.lstrip("/") if target.startswith("/") else "xl/" + target
            require(posixpath.normpath(path) == path and path.startswith("xl/") and path in names)
            relationships[key] = path
        self.sheets = {}
        for sheet in self.xml("xl/workbook.xml").findall("s:sheets/s:sheet", NS):
            name, key = sheet.get("name"), sheet.get(RELATIONSHIP_ID)
            require(_identity(name) and name not in self.sheets and key in relationships)
            self.sheets[name] = relationships[key]

    def xml(self, name):
        member = self.archive.getinfo(name)
        require(0 < member.file_size <= MAX_XML_BYTES)
        with self.archive.open(member) as source:
            data = source.read(MAX_XML_BYTES + 1)
        require(len(data) == member.file_size and len(data) <= MAX_XML_BYTES)
        require(b"\x00" not in data and b"<!DOCTYPE" not in data.upper()
                and b"<!ENTITY" not in data.upper())
        return ET.fromstring(data)

    def value(self, cell):
        require(cell.find("s:f", NS) is None)
        kind = cell.get("t")
        require(kind in (None, "n", "s", "inlineStr", "str"))
        values = cell.findall("s:v", NS)
        require(len(values) <= 1)
        raw = values[0].text if values else ""
        if kind == "s":
            require(isinstance(raw, str) and re.fullmatch(r"[0-9]+", raw) is not None)
            index = int(raw)
            require(0 <= index < len(self.strings))
            return self.strings[index]
        if kind == "inlineStr":
            return "".join(node.text or "" for node in cell.findall(".//s:t", NS))
        return raw or ""

    def rows(self, sheet, columns=None):
        require(sheet in self.sheets)
        rows = self.xml(self.sheets[sheet]).findall("s:sheetData/s:row", NS)
        require(0 < len(rows) <= MAX_XML_ROWS)
        output = []
        for number, row in enumerate(rows, 1):
            require(row.get("r") == str(number))
            cells = {}
            for cell in row.findall("s:c", NS):
                address = cell.get("r", "")
                match = re.fullmatch(r"([A-Z]+)([1-9][0-9]*)", address)
                require(match is not None and match[2] == str(number))
                column = match[1]
                require(column not in cells)
                # Crucially, never call value() on prediction cells after header.
                cells[column] = (self.value(cell) if number == 1 or columns is None
                                 or column in columns else None)
            output.append({key: value for key, value in cells.items() if value is not None})
        return output


def _clinical(book, contract):
    header = book.rows("FFPE_Discovery_clinical", columns=set())[0]
    require(len(set(header.values())) == len(header))
    columns = {value: key for key, value in header.items()}
    require(set(CLINICAL_COLUMNS) <= set(columns))
    rows = book.rows("FFPE_Discovery_clinical", columns={columns[key] for key in CLINICAL_COLUMNS})[1:]
    require(len(rows) == contract["clinical_rows"])
    records = [{key: row[columns[key]] for key in CLINICAL_COLUMNS} for row in rows]
    require(all(_identity(value, literal_na=True) for row in records for value in row.values()))
    require(len({row[cohorts.LABEL_COLUMN] for row in records}) == len(records))
    biological, missing = cohorts.classify_clinical(records)
    require(len(biological) == contract["measurements"] and len(missing) == contract["clinical_na"])
    groups = collections.defaultdict(list)
    for row in biological:
        groups[row["Sample ID"]].append(row)
    sizes = collections.Counter(map(len, groups.values()))
    # The {1, 3} clause is implied by the measurement total and the two counts;
    # it states the rule directly.
    require(set(sizes) <= {1, 3} and sizes[1] == contract["singletons"]
            and sizes[3] == contract["triplicate_groups"])
    unique = cohorts.collapse_replicates(biological)
    require(len(unique) == contract["samples"]
            and len(cohorts.patient_keys(unique)) == contract["patients"] == len(unique))
    eligible = cohorts.eligible_samples(unique)
    require(len(eligible) == contract["selected"]
            and sum(row["Tumor response"] == "sensitive" for row in eligible) == contract["negative"]
            and sum(row["Tumor response"] == "refractory" for row in eligible) == contract["positive"]
            and sum(row["Tumor Location Group"] == "NA" for row in eligible) == contract["retained_missing_location"])
    return records, biological, eligible


def _panel_membership(book, contract, records, eligible):
    panel_rows = book.rows("64_protein_predictors", {"A"})
    require(panel_rows[0].get("A") == "Proteins")
    panel = [row["A"] for row in panel_rows[1:]]
    require(len(panel) == contract["panel"]["count"] and len(set(panel)) == len(panel)
            and all(_identity(symbol) for symbol in panel))
    require(hashlib.sha256(("\n".join(panel) + "\n").encode()).hexdigest() == contract["panel"]["sha256"])
    score_rows = book.rows("FFPE_pred_scores", {"A"})
    require(score_rows[0].get("A") == "Samples" and score_rows[0].get("B") == "Pred.scores")
    keys = [row["A"] for row in score_rows[1:]]
    require(len(keys) == contract["cohort"]["selected"])
    joined = cohorts.join_score_membership(keys, records)
    require(cohorts.sample_keys(joined) == cohorts.sample_keys(eligible))
    require(cohorts.patient_keys(joined) == cohorts.patient_keys(eligible))
    return panel, keys


def _field(raw):
    if raw.startswith(b'"'):
        require(len(raw) >= 2 and raw.endswith(b'"'))
        require(b'"' not in raw[1:-1].replace(b'""', b''))
        raw = raw[1:-1].replace(b'""', b'"')
    else:
        require(b'"' not in raw)
    return raw.decode("utf-8")


def _number(raw):
    text = _field(raw)
    require(NUMBER.fullmatch(text) is not None, "matrix_value")
    value = float(text)
    require(math.isfinite(value), "matrix_value")
    return value


def _matrix(body, panel, biological, eligible, contract):
    require(body.endswith(b"\n") and b"\x00" not in body)
    lines = io.BytesIO(body)
    header = lines.readline(MAX_LINE_BYTES + 1)
    require(header.endswith(b"\n") and len(header) <= MAX_LINE_BYTES)
    require(hashlib.sha256(header).hexdigest() == contract["header_sha256"])
    names = [_field(field) for field in header.rstrip(b"\r\n").split(b"\t")]
    require(len(names) == contract["columns"] and len(set(names)) == len(names))
    require(names[:len(features.ANNOTATIONS)] == list(features.ANNOTATIONS))
    require(all(_identity(name, literal_na=True) for name in names))
    labels = {row[cohorts.LABEL_COLUMN]: row for row in biological}
    require(set(labels) <= set(names[len(features.ANNOTATIONS):]))
    columns = [name for name in names[len(features.ANNOTATIONS):] if name in labels]
    positions = [names.index(column) for column in columns]
    selected_samples = cohorts.sample_keys(eligible)
    selected = [labels[column]["Sample ID"] in selected_samples for column in columns]
    found, symbols = {}, set()
    count = 0
    while True:
        line = lines.readline(MAX_LINE_BYTES + 1)
        if not line:
            break
        require(line.endswith(b"\n") and len(line) <= MAX_LINE_BYTES)
        row = line[:-1]
        if row.endswith(b"\r"):
            row = row[:-1]
        require(b"\r" not in row and b"\n" not in row)
        fields = row.split(b"\t")
        require(len(fields) == contract["columns"])
        annotation = [_field(field) for field in fields[:len(features.ANNOTATIONS)]]
        symbol = annotation[1]
        require(_identity(symbol) and symbol not in symbols)
        symbols.add(symbol)
        count += 1
        require(count <= contract["rows"])
        if symbol in panel:
            # Excluded measurements stay missing; their fields are never decoded.
            found[symbol] = [_number(fields[position]) if include else None
                             for position, include in zip(positions, selected)]
    require(count == contract["rows"] and set(found) == set(panel))
    return {"row_names": list(panel), "column_names": columns,
            "values": [found[symbol] for symbol in panel]}


def _key_label_digest(eligible):
    """Return one SHA-256 over the selected patient keys and their 0/1 labels.

    Keys are sorted by their UTF-8 bytes. Each key gives one line: the key, a
    tab, "1" for refractory or "0" for sensitive, and a newline, all UTF-8.
    Checked keys hold no tab or newline. No per-patient hash is formed.
    """
    rows = sorted((row["Patient ID"].encode("utf-8"), row["Tumor response"] == "refractory")
                  for row in eligible)
    return hashlib.sha256(b"".join(key + (b"\t1\n" if positive else b"\t0\n")
                                   for key, positive in rows)).hexdigest()


def parse_sources(compressed_member, clinical_workbook, panel_workbook, contract=None):
    """Return private in-memory values only after complete pinned-byte checks.

    contract is an explicit fixture seam, not a production bypass option. No CLI
    exposes it. The default requires the exact independently audited source bytes.
    Provenance reports source_pins_verified only for the default contract. Any
    other contract sets fixture_contract, and its echoed fingerprints are then
    the caller's pins, not the study's. SourceAdapterError always has a fixed
    message, a category from CATEGORIES, and no cause or context.
    """
    stage = "contract"
    try:
        contract = copy.deepcopy(DEFAULT_CONTRACT if contract is None else contract)
        _check_contract(contract)
        pinned = contract == DEFAULT_CONTRACT
        stage = "source_bytes"
        _verify_bytes(clinical_workbook, contract["workbooks"]["clinical"])
        _verify_bytes(panel_workbook, contract["workbooks"]["panel_and_scores"])
        body = _inflate(compressed_member, contract["member"])
        stage = "workbook"
        clinical_book = MemoryWorkbook(clinical_workbook)
        panel_book = MemoryWorkbook(panel_workbook)
        stage = "clinical"
        records, biological, eligible = _clinical(clinical_book, contract["cohort"])
        key_label_digest = _key_label_digest(eligible)
        stage = "panel_membership"
        panel, keys = _panel_membership(panel_book, contract, records, eligible)
        stage = "matrix"
        measurements = _matrix(body, panel, biological, eligible, contract["matrix"])
        return {
            "schema_version": 1, "measurements": measurements,
            "clinical": {"columns": list(CLINICAL_COLUMNS),
                         "rows": [[row[key] for key in CLINICAL_COLUMNS] for row in records]},
            "panel": panel, "published_keys": keys,
            "provenance": {
                "source_pins_verified": pinned, "fixture_contract": not pinned,
                "member_sha256": contract["member"]["sha256"],
                "compressed_sha256": contract["member"]["compressed_sha256"],
                "member_crc32": f"{contract['member']['crc32']:08x}",
                "header_sha256": contract["matrix"]["header_sha256"],
                "clinical_sha256": contract["workbooks"]["clinical"]["sha256"],
                "panel_workbook_sha256": contract["workbooks"]["panel_and_scores"]["sha256"],
                "canonical_panel_sha256": contract["panel"]["sha256"],
                "matrix_rows": contract["matrix"]["rows"],
                "matrix_columns": contract["matrix"]["columns"],
                "biological_measurements": len(biological),
                "selected_samples": len(eligible),
                "selected_patient_labels_sha256": key_label_digest,
                "published_score_values_read": False,
            },
        }
    except SourceAdapterError as error:
        stage = error.category or stage
    except Exception:
        pass
    # Raised after the handler ends, so the original exception is not kept as context.
    raise SourceAdapterError(stage) from None


def _no_duplicate_keys(pairs):
    require(len({key for key, _ in pairs}) == len(pairs))
    return dict(pairs)


def _check_attestation(identifier):
    """Require identifier as an entry id in the owner's attestation file.

    The file holds {"schema_version": 1, "attestations": [...]}; each entry has
    exactly id, date (YYYY-MM-DD), execution_context and instruction. An absent,
    oversized or malformed file, or an unknown identifier, fails as
    "authorization". Nothing here touches the network.
    """
    try:
        # An exact str, so a subclass cannot redefine equality and match any entry.
        require(type(identifier) is str and _identity(identifier))
        with open(ATTESTATIONS, "rb") as source:
            data = source.read(MAX_ATTESTATION_BYTES + 1)
        require(len(data) <= MAX_ATTESTATION_BYTES)
        record = json.loads(data.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
        require(type(record) is dict and set(record) == {"schema_version", "attestations"}
                and type(record["schema_version"]) is int and record["schema_version"] == 1
                and type(record["attestations"]) is list and record["attestations"])
        ids = []
        for entry in record["attestations"]:
            require(type(entry) is dict and set(entry) == ATTESTATION_FIELDS and _identity(entry["id"])
                    and all(type(entry[field]) is str and entry[field].strip()
                            for field in ("execution_context", "instruction")))
            require(type(entry["date"]) is str
                    and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", entry["date"]) is not None)
            datetime.date.fromisoformat(entry["date"])
            ids.append(entry["id"])
        require(len(ids) == len(set(ids)) and identifier in ids)
        return
    except Exception:
        pass
    raise SourceAdapterError("authorization") from None


def load_pinned_sources(*, owner_attestation):
    """Explicitly acquire and parse the fixed sources in a suitable execution context.

    owner_attestation must be the id of an entry in ATTESTATIONS, a file that only
    the owner creates or edits; automated sessions must never create or edit it.
    Without a valid file and a matching entry, the call fails as "authorization"
    before any network access. This guards against accidental calls; it is not a
    security boundary, since code that can edit files could forge an entry, which
    the agent guidance forbids. It is not an approval mechanism either. The caller
    must first establish data-use applicability and technical controls for
    acquisition, Python parsing, transfer and model execution. No paths,
    alternate URLs or fixture contracts are accepted. This module does not
    expose a command-line acquisition option.
    """
    try:
        _check_attestation(owner_attestation)
        start = archive.ARCHIVE_BYTES - archive.TAIL_BYTES
        name, directory = archive.inspect_directory(archive.fetch_range(start, archive.ARCHIVE_BYTES - 1))
        offset = archive.member_data_offset(archive.fetch_range, name)
        parts, consumed = [], 0
        for chunk in features.member_chunks(offset):
            require(type(chunk) is bytes and 0 < len(chunk) <= features.CHUNK_BYTES)
            consumed += len(chunk)
            require(consumed <= DEFAULT_CONTRACT["member"]["compressed_bytes"])
            parts.append(chunk)
        require(consumed == DEFAULT_CONTRACT["member"]["compressed_bytes"])
        packed = b"".join(parts)
        del parts
        repeated_name, repeated_directory = archive.inspect_directory(
            archive.fetch_range(start, archive.ARCHIVE_BYTES - 1))
        require(name == repeated_name and directory == repeated_directory)
        books = {}
        for key in ("clinical", "panel_and_scores"):
            source = cohorts.SOURCES[key]
            url = cohorts.BASE + source["filename"]
            request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
            with urllib.request.urlopen(request, timeout=60) as response:
                actual, expected = urllib.parse.urlsplit(response.geturl()), urllib.parse.urlsplit(url)
                require(response.status == 200 and actual.scheme == "https"
                        and actual.netloc == expected.netloc and actual.path == expected.path)
                require(response.headers.get("Content-Encoding", "identity") == "identity")
                body = response.read(source["bytes"] + 1)
            _verify_bytes(body, source)
            books[key] = body
        result = parse_sources(packed, books["clinical"], books["panel_and_scores"])
        result["provenance"].update(archive_directory_sha256=directory["sha256"],
                                    archive_directory_entries=directory["entries"],
                                    archive_directory_rechecked=True,
                                    whole_archive_checksum_verified=False)
        return result
    except SourceAdapterError as error:
        category = error.category or "acquisition"
    except Exception:
        category = "acquisition"
    raise SourceAdapterError(category) from None
