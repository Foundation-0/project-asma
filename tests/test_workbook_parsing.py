"""Offline tests for the XLSX parsing layer, using a synthetic workbook.

The fixture carries abstract tokens only. It exercises sheet resolution,
shared-string, inline-string and numeric cell values, the column filter,
checksum pinning and the document-type-declaration guard without any network access
or published supplement.
"""

import hashlib
import io
from pathlib import Path
import sys
import unittest
from unittest import mock
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_published_cohorts as audit


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
SHARED_STRINGS = (
    f'<sst xmlns="{MAIN_NS}" count="3" uniqueCount="3">'
    "<si><t>Samples</t></si><si><t>Pred.scores</t></si>"
    "<si><t>label-alpha</t></si></sst>"
)
SHEET = (
    f'<worksheet xmlns="{MAIN_NS}"><sheetData>'
    '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>'
    '<row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2"><v>0.25</v></c></row>'
    '<row r="3"><c r="A3" t="inlineStr"><is><t>label-beta</t></is></c>'
    '<c r="B3"><v>7</v></c></row>'
    "</sheetData></worksheet>"
)


def workbook_bytes(shared_strings=SHARED_STRINGS, target="worksheets/sheet1.xml"):
    relationships = (
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
        f'relationships"><Relationship Id="rId1" Target="{target}"/></Relationships>'
    )
    book = (
        f'<workbook xmlns="{MAIN_NS}" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/'
        'relationships"><sheets>'
        '<sheet name="Data" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("xl/sharedStrings.xml", shared_strings)
        archive.writestr("xl/_rels/workbook.xml.rels", relationships)
        archive.writestr("xl/workbook.xml", book)
        archive.writestr("xl/worksheets/sheet1.xml", SHEET)
    return buffer.getvalue()


def source_for(body, **changes):
    source = {
        "filename": "fixture.xlsx",
        "bytes": len(body),
        "md5": hashlib.md5(body).hexdigest(),
        "sha256": hashlib.sha256(body).hexdigest(),
    }
    source.update(changes)
    return source


def load(body, **changes):
    with mock.patch.object(urllib.request, "urlopen",
                           return_value=io.BytesIO(body)):
        return audit.Workbook(source_for(body, **changes))


class WorkbookParsingChecks(unittest.TestCase):
    def test_sheets_and_cell_values(self):
        book = load(workbook_bytes())
        self.assertEqual(book.sheets, {"Data": "xl/worksheets/sheet1.xml"})
        self.assertEqual(book.rows("Data"), [
            {"A": "Samples", "B": "Pred.scores"},
            {"A": "label-alpha", "B": "0.25"},
            {"A": "label-beta", "B": "7"},
        ])

    def test_absolute_relationship_target_is_normalized(self):
        book = load(workbook_bytes(target="/xl/worksheets/sheet1.xml"))
        self.assertEqual(book.sheets, {"Data": "xl/worksheets/sheet1.xml"})
        self.assertEqual(book.rows("Data")[1]["A"], "label-alpha")

    def test_column_filter_keeps_full_header_only(self):
        book = load(workbook_bytes())
        rows = book.rows("Data", columns={"A"})
        self.assertEqual(rows[0], {"A": "Samples", "B": "Pred.scores"})
        self.assertEqual(rows[1:], [{"A": "label-alpha"}, {"A": "label-beta"}])

    def test_checksum_or_size_mismatch_fails(self):
        body = workbook_bytes()
        with self.assertRaises(audit.AuditError):
            load(body, sha256="0" * 64)
        with self.assertRaises(audit.AuditError):
            load(body, bytes=len(body) + 1)

    def test_document_type_declaration_is_rejected_before_parsing(self):
        # Entity-free declarations can still inject default attributes.
        for declaration in ('<!DOCTYPE sst [<!ENTITY probe "expanded">]>',
                            "<!DOCTYPE sst>",
                            '<!DOCTYPE sst [<!ATTLIST si x CDATA "y">]>'):
            with self.subTest(declaration=declaration), \
                    self.assertRaisesRegex(audit.AuditError, "document type"):
                load(workbook_bytes(shared_strings=declaration + SHARED_STRINGS))

    def test_utf16_part_cannot_hide_a_declaration(self):
        malicious = ('<!DOCTYPE sst [<!ENTITY probe "expanded">]>'
                     + SHARED_STRINGS.replace("label-alpha", "&probe;"))
        for encoding in ("utf-16", "utf-16-le"):
            with self.subTest(encoding=encoding), \
                    self.assertRaisesRegex(audit.AuditError, "document type"):
                load(workbook_bytes(shared_strings=malicious.encode(encoding)))

    def test_conformant_utf16_part_is_read(self):
        # Open Packaging Conventions allow UTF-8 or UTF-16 XML parts.
        declared = '<?xml version="1.0" encoding="UTF-16" standalone="yes"?>'
        book = load(workbook_bytes(
            shared_strings=(declared + SHARED_STRINGS).encode("utf-16")))
        self.assertEqual(book.rows("Data")[1], {"A": "label-alpha", "B": "0.25"})

    def test_unreadable_part_fails_with_audit_error(self):
        for part in ("<sst><si>",
                     '<?xml version="1.0" encoding="no-such-codec"?>' + SHARED_STRINGS,
                     '<?xml version="1.0" encoding="utf-7"?>' + SHARED_STRINGS,
                     SHARED_STRINGS.encode("utf-32")):
            with self.subTest(part=part[:40]), \
                    self.assertRaisesRegex(audit.AuditError, "Unreadable"):
                load(workbook_bytes(shared_strings=part))


if __name__ == "__main__":
    unittest.main()
