"""Must-fail controls for the tracked-study-source guard, using synthetic placeholders only.

Each control force-adds a one-line placeholder whose *path* matches a guarded
pattern to a throwaway Git repository and requires the guard to exit 1. No study
file, row or identifier is created; the placeholder text says what it is.
"""

import contextlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "check_tracked_study_sources.py"
sys.path.insert(0, str(ROOT / "tools"))
import check_tracked_study_sources as guard  # noqa: E402

PLACEHOLDER_TEXT = "synthetic placeholder for a guard test; not study data\n"
# At least one placeholder per pattern, plus the spellings the guard once let through.
PLACEHOLDERS = (
    "NIHMS1918576-supplement-MMC1.xlsx",
    "nested/NIHMS1918576-supplement-MMC4.xlsx",
    "placeholder.RData",
    "nested/discovery_matrix.txt",
    # Top level: git prints no leading slash, so "/pilot-001-scratch/" never matched it.
    "pilot-001-scratch/placeholder.txt",
    "nested/pilot-001-scratch/placeholder.txt",
    "PDC000357.tsv",
    "nested/PDC000362.tsv",
    # Non-ASCII names: without -z, git quotes them ("...\303\251..."), so anchors missed.
    "pilot-001-scratch/été.txt",
    "données/PDC000358.tsv",
)
REDIRECTING_GIT_VARIABLES = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                             "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR", "GIT_NAMESPACE")
EMPTY_LISTING = "ERROR: git lists no tracked files in this tree, so the tree was not checked"


class PlaceholderCoverage(unittest.TestCase):
    def test_every_pattern_has_a_placeholder(self):
        for pattern in guard.PATTERNS:
            with self.subTest(pattern=pattern.pattern):
                self.assertTrue(any(pattern.search(path) for path in PLACEHOLDERS))


@unittest.skipUnless(shutil.which("git"), "git is not installed")
class TrackedPlaceholdersFail(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        env = {key: value for key, value in os.environ.items()
               if key not in REDIRECTING_GIT_VARIABLES and not key.startswith("GIT_CONFIG")}
        # Never let git walk up from the temporary directory into a surrounding repository.
        env["GIT_CEILING_DIRECTORIES"] = str(self.base.parent)
        # Ignore the user's and the system's git configuration, and pin git's default
        # core.quotePath=true: with core.quotePath=false a guard that dropped -z would
        # still see the non-ASCII placeholders verbatim and the -z control would not bite.
        env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_COUNT="1",
                   GIT_CONFIG_KEY_0="core.quotePath", GIT_CONFIG_VALUE_0="true")
        env["PYTHONIOENCODING"] = "utf-8"
        self.env = env

    def tree_with_guard(self, name):
        root = self.base / name
        (root / "tools").mkdir(parents=True)
        shutil.copy2(TOOL, root / "tools" / TOOL.name)
        return root

    def git(self, root, *arguments):
        subprocess.run(["git", "-C", str(root), *arguments], check=True, capture_output=True, env=self.env)

    def run_guard(self, root):
        return subprocess.run([sys.executable, str(root / "tools" / TOOL.name)], cwd=root, env=self.env,
                              capture_output=True, encoding="utf-8", errors="replace", check=False)

    def test_each_force_added_placeholder_exits_1(self):
        root = self.tree_with_guard("repository")
        self.git(root, "init", "-q")
        # The guard itself is the one ordinary tracked file of the clean tree.
        self.git(root, "add", "--", f"tools/{TOOL.name}")
        clean = self.run_guard(root)
        self.assertEqual((clean.returncode, clean.stdout.strip()), (0, "PASS: no tracked study source paths"),
                         clean.stderr)
        for relative in PLACEHOLDERS:
            with self.subTest(path=relative):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(PLACEHOLDER_TEXT, encoding="utf-8")
                self.git(root, "add", "-f", "--", relative)
                caught = self.run_guard(root)
                self.assertEqual(caught.returncode, 1, caught.stdout + caught.stderr)
                self.assertEqual(caught.stdout.splitlines(),
                                 ["FAIL: tracked study source or scratch paths detected:", relative])
                self.git(root, "rm", "-q", "--cached", "-f", "--", relative)
                self.assertEqual(self.run_guard(root).returncode, 0)

    def test_empty_listing_exits_2(self):
        """Git runs but lists nothing here, so nothing was checked and nothing may pass."""
        fresh = self.tree_with_guard("fresh-repository")
        self.git(fresh, "init", "-q")
        outer = self.base / "outer-repository"
        outer.mkdir()
        self.git(outer, "init", "-q")
        (outer / "tracked.txt").write_text(PLACEHOLDER_TEXT, encoding="utf-8")
        self.git(outer, "add", "--", "tracked.txt")
        nested = outer / "untracked-tree"
        (nested / "tools").mkdir(parents=True)
        shutil.copy2(TOOL, nested / "tools" / TOOL.name)
        for name, root in (("fresh repository", fresh), ("tree inside a repository that does not track it", nested)):
            with self.subTest(case=name):
                result = self.run_guard(root)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual((result.stdout, result.stderr.strip()), ("", EMPTY_LISTING))

    def test_directory_outside_git_exits_nonzero(self):
        root = self.tree_with_guard("not-a-repository")
        result = self.run_guard(root)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("PASS", result.stdout)
        self.assertIn("ERROR: cannot list tracked files with git, so the tree was not checked (git: ",
                      result.stderr)


class GitFailureFailsClosed(unittest.TestCase):
    def outcome(self, **run):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(guard.subprocess, "run", **run), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = guard.main()
        return code, out.getvalue(), err.getvalue()

    def test_missing_git_executable(self):
        code, out, err = self.outcome(side_effect=OSError("abstract reason"))
        self.assertEqual((code, out), (2, ""))
        self.assertIn("(git: abstract reason)", err)

    def test_git_error_exit(self):
        for stderr, shown in ((b"fatal: abstract reason\nmore\n", "(git: fatal: abstract reason)"),
                              (b"", "(git: git exited 128)")):
            with self.subTest(stderr=stderr):
                failed = subprocess.CompletedProcess([], 128, b"PDC000357.tsv\0", stderr)
                code, out, err = self.outcome(return_value=failed)
                self.assertEqual((code, out), (2, ""))
                self.assertIn(shown, err)

    def test_empty_listing(self):
        for stdout in (b"", b"\0"):
            with self.subTest(stdout=stdout):
                listed = subprocess.CompletedProcess([], 0, stdout, b"")
                self.assertEqual(self.outcome(return_value=listed), (2, "", EMPTY_LISTING + "\n"))


class RepositoryTree(unittest.TestCase):
    def test_clean_repository_tree_passes_or_fails_closed(self):
        """The real tree passes in a checkout; a source archive without Git cannot be checked."""
        try:
            listed = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True, check=False)
            listable = listed.returncode == 0 and listed.stdout.strip(b"\0") != b""
        except OSError:
            listable = False
        result = subprocess.run([sys.executable, str(TOOL)], cwd=ROOT, capture_output=True, text=True,
                                check=False)
        if listable:
            self.assertEqual((result.returncode, result.stdout.strip()),
                             (0, "PASS: no tracked study source paths"), result.stdout + result.stderr)
        else:
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
