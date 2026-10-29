"""Regression checks for malformed registries and broken navigation, using no data."""

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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

    def metadata_audited_fixture(self):
        for identifier in ("S12", "S13"):
            if not any(row["id"] == identifier for row in self.sources["sources"]):
                source = copy.deepcopy(self.sources["sources"][0])
                source.update(id=identifier, title="Abstract evidence fixture " + identifier,
                              url="https://example.org/" + identifier,
                              reviewed_via="https://example.org/" + identifier)
                self.sources["sources"].append(source)
        for row in self.datasets["datasets"]:
            if row["id"] in {"PDC000358", "PDC000360", "PDC000362"}:
                row.update(
                    access_status="open_processed_file_metadata_verified",
                    terms_status="pdc_public_data_terms_reviewed",
                    download_status="headers_inspected_in_memory",
                    provenance_status="study_version_and_linkage_metadata_verified",
                    overlap_status="catalog_overlap_measured_analysis_membership_unresolved",
                    release="1", sha256=None,
                )
                row["source_ids"] = list(dict.fromkeys(row["source_ids"] + ["S12", "S13"]))

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

    def test_complete_metadata_audit_transition_is_allowed(self):
        self.metadata_audited_fixture()
        self.write_registries()
        self.assertEqual(validate.registry_errors(self.root), [])

    def test_partial_or_unearned_metadata_audit_is_rejected(self):
        self.metadata_audited_fixture()
        complete = copy.deepcopy(self.datasets)
        changes = (
            ({"terms_status": "not_reviewed"}, "invalid terms_status"),
            ({"id": "PDC999999"}, "not eligible"),
            ({"assay": "phosphoproteome"}, "not eligible"),
            ({"pilot_role": "context_only"}, "not eligible"),
            ({"source_ids": ["S01", "S13"]}, "requires source references S12 and S13"),
            ({"source_ids": ["S01", "S12"]}, "requires source references S12 and S13"),
            ({"sha256": "a" * 64}, "invalid sha256"),
            ({"release": 1}, "invalid release"),
        )
        for change, expected in changes:
            with self.subTest(change=change):
                self.datasets = copy.deepcopy(complete)
                row = next(row for row in self.datasets["datasets"] if row["id"] == "PDC000360")
                row.update(change)
                self.write_registries()
                errors = validate.registry_errors(self.root)
                self.assertTrue(any(expected in error for error in errors), errors)

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

    def isolated_git(self):
        """Ignore a surrounding Git command's repository settings, e.g. inside a commit hook."""
        patcher = mock.patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                    "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR"):
            os.environ.pop(key, None)

    @unittest.skipUnless(shutil.which("git"), "git is not installed")
    def test_owner_attestation_file_must_not_be_tracked_or_staged(self):
        self.isolated_git()
        def git(*arguments):
            return subprocess.run(["git", "-C", str(self.root), *arguments], check=True, capture_output=True,
                                  text=True).stdout
        def flagged(root):
            errors = validate.attestation_errors(root)
            return bool(errors) and all("tracked or staged" in error for error in errors)
        commit = ("-c", "user.name=abstract", "-c", "user.email=abstract@example.invalid",
                  "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify", "-m", "abstract")
        name = validate.OWNER_ATTESTATIONS
        # Without a repository there is nothing to commit, so nothing to check.
        self.assertEqual(validate.attestation_errors(self.root), [])
        git("init", "-q")
        (self.root / name).write_text("{}")
        (self.root / "registries/sources.json").write_text("{}")
        git("add", "registries/sources.json")
        # Present but untracked is how the owner keeps it.
        self.assertEqual(validate.attestation_errors(self.root), [])
        # Committed and unchanged: nothing is staged, but Git still tracks it. -f gets past a global
        # excludes file that lists it.
        git("add", "-f", "--", name)
        git(*commit)
        self.assertTrue(flagged(self.root))
        # Pathspec settings that a surrounding Git command exports, e.g. to its hooks, change nothing.
        for variable in ("GIT_LITERAL_PATHSPECS", "GIT_GLOB_PATHSPECS", "GIT_NOGLOB_PATHSPECS",
                         "GIT_ICASE_PATHSPECS"):
            with mock.patch.dict(os.environ, {variable: "1"}):
                self.assertTrue(flagged(self.root), variable)
        self.assertTrue(any("tracked or staged" in error for error in validate.validate(self.root)))
        git("rm", "-q", "--cached", "--", name)
        git(*commit)
        self.assertEqual(validate.attestation_errors(self.root), [])
        # Any letter case is caught. The entries go straight into the index: on a case-insensitive
        # filesystem, where Git sets core.ignorecase, `git add` would fold Registries/ into the
        # registries/ directory Git already tracks. Both settings are tried, as either checkout has it.
        # Appended last to GIT_CONFIG_PARAMETERS, each beats any setting from the environment and also
        # reaches the validator's own Git call.
        blob = git("hash-object", "-w", "--", name).strip()
        spellings = (name, name.replace("pilot", "Pilot"), name.replace("registries", "Registries"))
        outer = os.environ.get("GIT_CONFIG_PARAMETERS", "")
        for ignorecase in ("false", "true"):
            parameters = f"{outer} 'core.ignorecase={ignorecase}'".strip()
            with mock.patch.dict(os.environ, GIT_CONFIG_PARAMETERS=parameters):
                for spelling in spellings:
                    git("update-index", "--add", "--cacheinfo", "100644", blob, spelling)
                    self.assertIn(spelling, git("ls-files", "-z").split("\0"), (ignorecase, spelling))
                    self.assertTrue(flagged(self.root), (ignorecase, spelling))
                    git("update-index", "--force-remove", "--", spelling)
        self.assertEqual(validate.attestation_errors(self.root), [])
        # A checkout whose .git is a file, as in a worktree, is checked too.
        separate = self.root / "separate"
        (separate / "registries").mkdir(parents=True)
        subprocess.run(["git", "-C", str(separate), "init", "-q", "--separate-git-dir",
                        str(self.root / "separate.git")], check=True, capture_output=True)
        self.assertTrue((separate / ".git").is_file())
        (separate / name).write_text("{}")
        subprocess.run(["git", "-C", str(separate), "add", "-f", "--", name], check=True, capture_output=True)
        self.assertTrue(flagged(separate))
        # If Git cannot answer, the check fails closed and says why when it can.
        with mock.patch.object(validate.subprocess, "run", side_effect=OSError("abstract reason")):
            self.assertIn("(git: abstract reason)", validate.attestation_errors(self.root)[0])
        for stderr, shown in ((b"fatal: abstract reason\nmore\n", "(git: fatal: abstract reason)"), (b"", "")):
            failed = subprocess.CompletedProcess([], 128, b"", stderr)
            with mock.patch.object(validate.subprocess, "run", return_value=failed):
                errors = validate.attestation_errors(self.root)
            message = f"{name}: cannot check whether Git tracks it"
            self.assertEqual(errors, [message + (f" {shown}" if shown else "")])

    @unittest.skipUnless(shutil.which("git") and (validate.ROOT / ".git").exists(), "no Git checkout")
    def test_repository_ignores_the_owner_attestation_file(self):
        ignored = subprocess.run(["git", "-C", str(validate.ROOT), "check-ignore", "-v", "--no-index",
                                  "--", validate.OWNER_ATTESTATIONS], capture_output=True, text=True)
        self.assertEqual(ignored.returncode, 0, ignored.stderr)
        # The rule must come from the committed .gitignore, not a local exclude file.
        self.assertTrue(ignored.stdout.startswith(".gitignore:"), ignored.stdout)

if __name__ == "__main__":
    unittest.main()
