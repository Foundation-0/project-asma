"""Regression checks for malformed registries and broken navigation, using no data."""

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import validate


class ScaffoldChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "registries").mkdir()
        self.sources = json.loads((validate.ROOT / "registries/sources.json").read_text())
        self.datasets = json.loads((validate.ROOT / "registries/datasets.json").read_text())

    def write_registries(self):
        for name, data in [("sources", self.sources), ("datasets", self.datasets)]:
            (self.root / "registries" / f"{name}.json").write_text(json.dumps(data))

    def test_final_tree(self):
        self.assertEqual(validate.validate(), [])

    def test_duplicate_ids_and_unknown_source(self):
        self.sources["sources"].append(copy.deepcopy(self.sources["sources"][0]))
        self.datasets["datasets"][0]["source_ids"] = ["S999"]
        self.write_registries()
        errors = validate.registry_errors(self.root)
        self.assertTrue(any("duplicate id" in error for error in errors))
        self.assertTrue(any("unknown source" in error for error in errors))

    def test_invalid_date_url_and_unearned_status(self):
        source = self.sources["sources"][0]
        source.update(checked_on="2026-02-30", url="http://example.org")
        self.datasets["datasets"][0]["download_status"] = "downloaded"
        self.write_registries()
        errors = validate.registry_errors(self.root)
        for phrase in ["invalid checked_on", "invalid HTTPS", "invalid download_status"]:
            self.assertTrue(any(phrase in error for error in errors), errors)

    def test_missing_fields_and_wrong_types(self):
        del self.sources["sources"][0]["limitations"]
        self.datasets["datasets"][0]["source_ids"] = "S01"
        self.write_registries()
        errors = validate.registry_errors(self.root)
        self.assertTrue(any("missing limitations" in error for error in errors))
        self.assertTrue(any("list of IDs" in error for error in errors))

    def test_malformed_json_is_reported(self):
        self.write_registries()
        (self.root / "registries/sources.json").write_text("{")
        self.assertTrue(any(error.startswith("sources:") for error in validate.registry_errors(self.root)))

    def test_local_files_fragments_and_fences(self):
        (self.root / "guide space.md").write_text("# First\n# First\n")
        (self.root / "README.md").write_text(
            "[ok](guide%20space.md#first-1)\n[web](https://example.org)\n"
            "```md\n[example](not-real.md)\n```\n"
        )
        self.assertEqual(validate.local_link_errors(self.root), [])
        (self.root / "README.md").write_text(
            "[missing](absent.md)\n[anchor](guide%20space.md#absent)\n[escape](../outside.md)\n"
        )
        errors = validate.local_link_errors(self.root)
        for phrase in ["missing local target", "missing heading", "escapes repository"]:
            self.assertTrue(any(phrase in error for error in errors), errors)

    def test_schema_version_and_non_object_rows(self):
        self.sources["schema_version"] = True
        self.datasets["datasets"].append(None)
        self.write_registries()
        errors = validate.registry_errors(self.root)
        self.assertTrue(any("schema_version" in error for error in errors))
        self.assertTrue(any("expected object" in error for error in errors))

    def test_malformed_kind_and_url_are_reported(self):
        self.sources["sources"][0].update(kind=[], url="https://[broken")
        self.write_registries()
        errors = validate.registry_errors(self.root)
        self.assertTrue(any("kind/verification" in error for error in errors))
        self.assertTrue(any("invalid HTTPS" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
