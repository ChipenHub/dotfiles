"""Tests for tmux's search-selection helper."""

import runpy
from pathlib import Path
import unittest
from unittest.mock import patch


SEARCH_SELECTION = runpy.run_path(
    Path(__file__).resolve().parents[1] / "search-selection"
)
normalize_query = SEARCH_SELECTION["normalize_query"]
search_root = SEARCH_SELECTION["search_root"]
show_results = SEARCH_SELECTION["show_results"]


class NormalizeQueryTests(unittest.TestCase):
    def test_removes_line_breaks_and_trims_outer_whitespace(self):
        self.assertEqual(normalize_query("  foo\nbar\r\nbaz  "), "foobarbaz")

    def test_preserves_spaces_within_selected_text(self):
        self.assertEqual(normalize_query("foo bar"), "foo bar")


class SearchRootTests(unittest.TestCase):
    @patch("subprocess.run")
    def test_uses_git_root_when_available(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = "/repo/root\n"

        self.assertEqual(search_root(Path("/repo/root/subdir")), Path("/repo/root"))

    @patch("subprocess.run")
    def test_falls_back_to_pane_directory_outside_git(self, run):
        run.return_value.returncode = 128
        run.return_value.stdout = ""
        cwd = Path("/tmp/project")

        self.assertEqual(search_root(cwd), cwd)


class ShowResultsTests(unittest.TestCase):
    @patch("subprocess.run")
    def test_uses_fixed_string_search_and_argument_separator(self, run):
        run.return_value.returncode = 0

        self.assertEqual(show_results("-literal.*text"), 0)

        run.assert_called_once_with(
            [
                "rg",
                "-n",
                "-F",
                "--color=always",
                "--",
                "-literal.*text",
                ".",
            ],
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
