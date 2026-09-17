"""Tests for tmux's open-path helper."""

import runpy
from pathlib import Path
import unittest
from unittest.mock import Mock, patch


OPEN_PATH = runpy.run_path(Path(__file__).resolve().parents[1] / "open-path")
split_location = OPEN_PATH["split_location"]
find_reusable_nvim = OPEN_PATH["find_reusable_nvim"]
open_in_nvim = OPEN_PATH["open_in_nvim"]
open_target = OPEN_PATH["open_target"]


class SplitLocationTests(unittest.TestCase):
    def test_github_style_line_fragment(self):
        path = (
            "modules/biz/libedit/src/main/java/com/vega/image/edit/panel/"
            "AiChatEditInputPanel.kt"
        )
        self.assertEqual(
            split_location(f"{path}#L921"),
            (path, 921, None, None),
        )

    def test_existing_line_formats(self):
        self.assertEqual(split_location("foo.kt:12:3"), ("foo.kt", 12, 3, None))
        self.assertEqual(split_location("foo.kt(12,3)"), ("foo.kt", 12, 3, None))


class ReusableNvimWindowTests(unittest.TestCase):
    def test_finds_only_live_whole_window_nvim_in_session(self):
        def run(command, **_kwargs):
            if command[:3] == ["tmux", "list-panes", "-s"]:
                return Mock(
                    returncode=0,
                    stdout=(
                        "%1\t1\t/live.nvim\n"
                        "%2\t2\t/split.nvim\n"
                        "%3\t1\t/dead.nvim\n"
                    ),
                )
            server = command[2]
            return Mock(returncode=0 if server == "/live.nvim" else 1)

        with patch.object(OPEN_PATH["subprocess"], "run", side_effect=run):
            self.assertEqual(
                find_reusable_nvim("%9"),
                ("%1", "/live.nvim"),
            )

    def test_enter_reuses_whole_window_nvim(self):
        finder = Mock(return_value=("%1", "/live.nvim"))
        opener = Mock(return_value=True)
        globals_ = open_target.__globals__
        with patch.dict(
            globals_,
            {
                "find_reusable_nvim": finder,
                "open_in_nvim": opener,
            },
        ):
            open_target("%9", Path("/tmp/file.txt"), None, None, None)

        finder.assert_called_once_with("%9")
        opener.assert_called_once_with(
            "%1", "/live.nvim", Path("/tmp/file.txt"), None, None, None
        )

    def test_reuse_switches_to_the_nvim_window(self):
        run = Mock(return_value=Mock(returncode=0))
        with (
            patch.object(OPEN_PATH["subprocess"], "run", run),
            patch.dict(open_in_nvim.__globals__, {"set_pane_name": Mock()}),
        ):
            self.assertTrue(
                open_in_nvim(
                    "%1", "/live.nvim", Path("/tmp/file.txt"), None, None, None
                )
            )

        commands = [call.args[0] for call in run.call_args_list]
        self.assertIn(["tmux", "select-window", "-t", "%1"], commands)
        self.assertIn(["tmux", "select-pane", "-t", "%1"], commands)


if __name__ == "__main__":
    unittest.main()
