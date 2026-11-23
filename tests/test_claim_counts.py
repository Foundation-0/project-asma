"""CLAIMS.md row counts must match the ledger header and the site total."""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import export_claims_ledger as ledger

CLAIMS = ROOT / "CLAIMS.md"
INDEX = ROOT / "index.html"
HEADER = re.compile(
    r"PROVEN \*\*(\d+)\*\* · VERIFIED \*\*(\d+)\*\* · KNOWN \*\*(\d+)\*\* · CONJECTURE \*\*(\d+)\*\*"
)
SITE_TOTAL = re.compile(r"(\d+) labelled claims in the ledger")


def parse_header_counts(text):
    match = HEADER.search(text)
    if not match:
        raise AssertionError("CLAIMS.md header counts line not found")
    keys = ("PROVEN", "VERIFIED", "KNOWN", "CONJECTURE")
    return dict(zip(keys, map(int, match.groups())))


class ClaimCounts(unittest.TestCase):
    def test_header_site_and_rows_agree(self):
        claims_text = CLAIMS.read_text(encoding="utf-8")
        row_counts, total = ledger.parse_claim_rows_by_label(claims_text)
        header_counts = parse_header_counts(claims_text)
        self.assertEqual(header_counts, row_counts)
        site_match = SITE_TOTAL.search(INDEX.read_text(encoding="utf-8"))
        self.assertIsNotNone(site_match, "index.html labelled-claim total missing")
        self.assertEqual(int(site_match.group(1)), total)


if __name__ == "__main__":
    unittest.main()
