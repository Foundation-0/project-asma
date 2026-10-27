"""Static checks for the two site pages: no third-party requests, working same-page links, withheld values."""

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "404.html")
STYLES = ("assets/f0.css", "page.css")
# Public reports carry only reviewed aggregates (docs/reproducibility-and-data.md). Until external review is
# recorded, the site withholds the preliminary AUROC and the pair counts behind it, the rebuilt cohort counts,
# the linkage and feature counts, and the panel-coverage results.
WITHHELD = (r"0\.8088", r"(?<![\d.])0\.81(?!\d)", r"(?<![\d.])0\.191(?!\d)", r"0\.0211", r"3,491",
            r"(?<![\d.,])168(?![\d,])", r"8,?800", r"(?<![\d.,])61 frozen", r"(?<![\d.,])20 FFPE",
            r"64 ?/ ?64", r"(?<![\d.,])0 of 64")
# A URL with a scheme or a leading // reaches another host; data: URIs make no request.
REMOTE = re.compile(r"^(?!data:)(?:[a-z][a-z0-9+.-]*:|//)", re.I)
CSS_REMOTE = re.compile(r"(?:@import|url\()\s*(?:url\()?\s*['\"]?(?!data:)(?:[a-z][a-z0-9+.-]*:|//)", re.I)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.refs, self.loads = set(), [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag in {"a", "use"} and attrs.get("href"):
            self.refs.append(attrs["href"])
        if tag == "link" and attrs.get("rel") not in {"canonical", "alternate"}:
            self.loads.append(attrs.get("href", ""))
        if attrs.get("src"):
            self.loads.append(attrs["src"])


def page(name):
    return Page((ROOT / name).read_text(encoding="utf-8"))


class SiteChecks(unittest.TestCase):
    def test_no_third_party_requests(self):
        for name in PAGES:
            self.assertIn("assets/f0.css", page(name).loads, name)
            for url in page(name).loads:
                self.assertNotRegex(url.strip(), REMOTE, f"{name} loads {url}")
        for name in PAGES + STYLES:
            found = CSS_REMOTE.search((ROOT / name).read_text(encoding="utf-8"))
            self.assertIsNone(found, f"{name} loads {found and found.group()}")

    def test_same_page_links_have_targets(self):
        home = page("index.html").ids
        for name in PAGES:
            parsed = page(name)
            self.assertIn("#main", parsed.refs, f"{name} has no skip link")
            for ref in parsed.refs:
                if ref.startswith("#"):
                    self.assertIn(ref[1:], parsed.ids, f"{name} links to {ref}")
                elif ref.startswith("./#"):
                    self.assertIn(ref[3:], home, f"{name} links to {ref}")

    def test_withheld_values_absent(self):
        for name in PAGES:
            text = (ROOT / name).read_text(encoding="utf-8")
            for pattern in WITHHELD:
                found = re.search(pattern, text)
                self.assertIsNone(found, f"{name} shows {found and found.group()}")


if __name__ == "__main__":
    unittest.main()
