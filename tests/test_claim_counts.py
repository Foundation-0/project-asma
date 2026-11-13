"""CLAIMS.md row counts must match the ledger header and the site total."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "CLAIMS.md"
INDEX = ROOT / "index.html"

ROW = re.compile(r"^\|\s*([VKCP]\d+)\s*\|")
HEADER = re.compile(
    r"PROVEN \*\*(\d+)\*\* · VERIFIED \*\*(\d+)\*\* · KNOWN \*\*(\d+)\*\* · CONJECTURE \*\*(\d+)\*\*"
)
SITE_TOTAL = re.compile(r"(\d+) labelled claims in the ledger")
PREFIX_LABEL = {
    "V": "VERIFIED",
    "K": "KNOWN",
    "C": "CONJECTURE",
    "P": "PROVEN",
}


def parse_claim_rows(text):
    by_label = {label: set() for label in PREFIX_LABEL.values()}
    for line in text.splitlines():
        match = ROW.match(line)
        if not match:
            continue
        claim_id = match.group(1)
        parts = [part.strip() for part in line.split("|")]
        label = parts[2] if len(parts) > 2 and parts[2] in PREFIX_LABEL else PREFIX_LABEL[claim_id[0]]
        by_label[label].add(claim_id)
    return {label: len(ids) for label, ids in by_label.items()}, sum(len(ids) for ids in by_label.values())


def parse_header_counts(text):
    match = HEADER.search(text)
    if not match:
        raise AssertionError("CLAIMS.md header counts line not found")
    keys = ("PROVEN", "VERIFIED", "KNOWN", "CONJECTURE")
    return dict(zip(keys, map(int, match.groups())))


class ClaimCounts(unittest.TestCase):
    def test_header_site_and_rows_agree(self):
        claims_text = CLAIMS.read_text(encoding="utf-8")
        row_counts, total = parse_claim_rows(claims_text)
        header_counts = parse_header_counts(claims_text)
        self.assertEqual(header_counts, row_counts)
        site_match = SITE_TOTAL.search(INDEX.read_text(encoding="utf-8"))
        self.assertIsNotNone(site_match, "index.html labelled-claim total missing")
        self.assertEqual(int(site_match.group(1)), total)


if __name__ == "__main__":
    unittest.main()
