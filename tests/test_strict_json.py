"""Strict JSON parsing: duplicate keys and NaN/Infinity are refused in repository-authored JSON."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import audit_checkers  # noqa: E402
import check_implementation_hashes as implementation_hashes  # noqa: E402
import strict_json  # noqa: E402

# JSON this repository writes. Raw third-party responses under results/*/snapshot/ are kept
# byte-identical as evidence and are deliberately outside this scope.
REPOSITORY_AUTHORED = (
    "registries/*.json",
    "results/*/certificate.json",
    "results/*/manifest.json",
    "results/*/report.json",
    "results/*/audit.json",
    "runtime/*.json",
    "tests/fixtures/**/*.json",
)


def is_raw_snapshot(relative):
    return relative.parts[:1] == ("results",) and relative.parts[2:3] == ("snapshot",)


def tracked_paths():
    """Repository-relative paths Git tracks, or None where Git lists none (e.g. a source archive)."""
    try:
        listed = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, check=False)
    except OSError:
        return None
    paths = {path for path in listed.stdout.decode("utf-8", "replace").split("\0") if path}
    return paths if listed.returncode == 0 and paths else None


def repository_authored_json():
    # In a checkout, only tracked files: an untracked file such as the owner's attestation
    # registry is not repository-authored. Without Git, the files on disk are the tree.
    tracked = tracked_paths()
    return {
        pattern: sorted(path for path in ROOT.glob(pattern)
                        if path.is_file() and not is_raw_snapshot(path.relative_to(ROOT))
                        and (tracked is None or path.relative_to(ROOT).as_posix() in tracked))
        for pattern in REPOSITORY_AUTHORED
    }


class StrictLoads(unittest.TestCase):
    def refusal(self, text):
        with self.assertRaises(ValueError) as caught:
            strict_json.loads(text)
        return str(caught.exception)

    def test_ordinary_json_parses_as_json_loads_does(self):
        text = '{"a": [1, -2.5, 3e2, true, null, "\\u00e9"], "b": {"a": {}}, "c": 0.0}'
        self.assertEqual(strict_json.loads(text), json.loads(text))

    def test_duplicate_keys_are_refused_at_any_depth(self):
        for text, key in (('{"a": 1, "a": 2}', "a"), ('[{"b": {"c": 1, "c": 1}}]', "c"),
                          ('{"rows": [{"id": "x", "id": "y"}]}', "id")):
            with self.subTest(text=text):
                self.assertEqual(self.refusal(text), f"duplicate JSON key {key!r}")

    def test_non_finite_numbers_are_refused(self):
        for literal in ("NaN", "Infinity", "-Infinity", "1e999", "-1e999"):
            with self.subTest(literal=literal):
                self.assertEqual(self.refusal(f'{{"value": {literal}}}'), f"non-finite JSON number {literal}")

    def test_load_path_names_the_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "abstract.json"
            for text, problem in (('{"k": 1, "k": 2}', "duplicate JSON key 'k'"), ("[NaN]", "non-finite JSON number NaN"),
                                  ("{", "Expecting property name")):
                with self.subTest(text=text):
                    path.write_text(text, encoding="utf-8")
                    with self.assertRaises(ValueError) as caught:
                        strict_json.load_path(path)
                    self.assertTrue(str(caught.exception).startswith(f"{path}: {problem}"), caught.exception)


class RepositoryAuthoredJson(unittest.TestCase):
    def test_scope_excludes_raw_snapshots(self):
        self.assertTrue(is_raw_snapshot(Path("results/abstract/snapshot/nested/response.json")))
        self.assertFalse(is_raw_snapshot(Path("results/abstract/manifest.json")))
        for paths in repository_authored_json().values():
            for path in paths:
                self.assertNotIn("snapshot", path.relative_to(ROOT).parts)

    def test_scope_excludes_untracked_files_in_a_checkout(self):
        tracked = tracked_paths()
        if tracked is None:
            self.skipTest("Git lists no tracked files here")
        scanned = [path.relative_to(ROOT).as_posix() for paths in repository_authored_json().values()
                   for path in paths]
        self.assertTrue(scanned)
        self.assertLessEqual(set(scanned), tracked)
        with mock.patch.object(sys.modules[__name__], "tracked_paths", return_value=tracked - {scanned[0]}):
            self.assertNotIn(ROOT / scanned[0], [path for paths in repository_authored_json().values()
                                                for path in paths])

    def test_repository_authored_json_parses_strictly(self):
        failures = []
        for pattern, paths in repository_authored_json().items():
            with self.subTest(pattern=pattern):
                self.assertTrue(paths, f"no file matches {pattern}")
            for path in paths:
                try:
                    strict_json.load_path(path)
                except ValueError as error:
                    failures.append(str(error))
        self.assertEqual(failures, [])


class IsolatedImports(unittest.TestCase):
    """Each tool that imports strict_json finds it under `python3 -I`, as the pinned runtime runs them."""

    TOOLS = ("validate.py", "check_sha256_manifests.py", "check_implementation_hashes.py", "audit_checkers.py")

    def test_tools_import_strict_json_without_the_script_directory_on_sys_path(self):
        # -I leaves both the script's directory and the working directory off sys.path; run_path
        # executes the module body (its imports) without adding the directory or running main.
        code = "import runpy, sys; runpy.run_path(sys.argv[1], run_name='isolated_import_check')"
        with tempfile.TemporaryDirectory() as elsewhere:
            for name in self.TOOLS:
                with self.subTest(tool=name):
                    result = subprocess.run([sys.executable, "-I", "-B", "-c", code, str(ROOT / "tools" / name)],
                                            cwd=elsewhere, capture_output=True, text=True, check=False)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, "")


class CallSites(unittest.TestCase):
    """The hash and audit checkers refuse a duplicate key instead of using its last value."""

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "registries").mkdir()
        (self.root / "tools").mkdir()

    def duplicate(self, name, key="implementation_sha256"):
        path = self.root / "registries" / name
        path.write_text(f'{{"schema_version": 1, "{key}": {{}}, "{key}": {{"tools/x.py": "{"0" * 64}"}}}}',
                        encoding="utf-8")
        return path

    def test_implementation_hash_registry(self):
        self.duplicate("pilot-001-abstract.json")
        with self.assertRaises(ValueError) as caught:
            list(implementation_hashes.iter_registry_payloads(self.root))
        self.assertTrue(str(caught.exception).endswith("pilot-001-abstract.json: duplicate JSON key "
                                                       "'implementation_sha256'"))
        stderr = io.StringIO()
        with mock.patch.object(implementation_hashes, "ROOT", self.root), \
                mock.patch.object(implementation_hashes, "CAPACITY_TOOL", self.root / "tools/capacity.py"), \
                mock.patch.object(implementation_hashes, "is_inside_git_work_tree", return_value=True), \
                contextlib.redirect_stderr(stderr):
            self.assertEqual(implementation_hashes.main([]), 1)
        self.assertIn("implementation_sha256 check failed: ", stderr.getvalue())
        self.assertIn("duplicate JSON key 'implementation_sha256'", stderr.getvalue())

    def test_audit_certificate_reads(self):
        path = self.duplicate("abstract-certificate.json", key="certificate_sha256")
        reads = (("has_recorded_digest", lambda: audit_checkers.has_recorded_digest(path, "tools/abstract.py")),
                 ("run_tamper", lambda: audit_checkers.run_tamper("tools/abstract.py", path)))
        for name, read in reads:
            with self.subTest(read=name):
                with self.assertRaises(ValueError) as caught:
                    read()
                self.assertTrue(str(caught.exception).endswith("duplicate JSON key 'certificate_sha256'"))

    def test_audit_ledger_and_committed_report(self):
        broken = self.duplicate("abstract.json", key="claims")
        for target in ("LEDGER", "AUDIT_JSON"):
            with self.subTest(target=target):
                stderr = io.StringIO()
                with mock.patch.object(audit_checkers, target, broken), contextlib.redirect_stderr(stderr):
                    self.assertEqual(audit_checkers.main(["--check", "--skip-run"]), 1)
                self.assertEqual(stderr.getvalue(), f"FAIL: {broken}: duplicate JSON key 'claims'\n")


if __name__ == "__main__":
    unittest.main()
