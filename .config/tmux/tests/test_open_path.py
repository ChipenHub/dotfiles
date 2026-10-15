"""Tests for tmux's open-path helper."""

import base64
import runpy
import shlex
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

    def test_github_style_line_range(self):
        self.assertEqual(
            split_location("src/foo.kt#L11-L20"),
            ("src/foo.kt", 11, None, 20),
        )

    def test_discards_non_numeric_content_after_line(self):
        for suffix in ("aaa", "aaa:88", "88aaa", "88aaa:99", "aaa#L921", "-3", "1.5"):
            with self.subTest(suffix=suffix):
                self.assertEqual(
                    split_location(f"src/foo.kt:99:{suffix}"),
                    ("src/foo.kt", 99, None, None),
                )

    def test_numeric_content_after_line_is_column(self):
        for suffix in ("88", "88:aaa", "88:99", "88:aaa#L921"):
            with self.subTest(suffix=suffix):
                self.assertEqual(
                    split_location(f"src/foo.kt:99:{suffix}"),
                    ("src/foo.kt", 99, 88, None),
                )

    def test_wrappers_with_trailing_punctuation(self):
        for token in (
            "[src/foo.kt:11:88],",
            "(src/foo.kt:11:88);",
            '"src/foo.kt:11:88":',
            "`src/foo.kt:11:88`,;:",
            "{src/foo.kt:11:88},",
            "<src/foo.kt:11:88>;",
            "['src/foo.kt:11:88',];",
        ):
            with self.subTest(token=token):
                self.assertEqual(split_location(token), ("src/foo.kt", 11, 88, None))
        self.assertEqual(
            split_location("[src/foo.kt#L11-L20],"),
            ("src/foo.kt", 11, None, 20),
        )

    def test_inserted_whitespace_is_still_removed(self):
        self.assertEqual(
            split_location(" [src/ foo.\nkt : 11 :\t88 ], \n"),
            ("src/foo.kt", 11, 88, None),
        )

    def test_existing_line_formats(self):
        self.assertEqual(split_location("foo.kt:12:3"), ("foo.kt", 12, 3, None))
        self.assertEqual(split_location("foo.kt(12,3)"), ("foo.kt", 12, 3, None))
        self.assertEqual(split_location("foo.kt:12"), ("foo.kt", 12, None, None))
        self.assertEqual(split_location("foo.kt:12-15"), ("foo.kt", 12, None, 15))
        self.assertEqual(split_location("foo.kt:12-15:3"), ("foo.kt", 12, 3, 15))

    def test_discards_content_after_column(self):
        path = "xxxx/xxxx/xxxx"
        for suffix in (
            "xxx", "", "error: unexpected token", "99:100", "xxx:99", "xxx#L921"
        ):
            with self.subTest(suffix=suffix):
                self.assertEqual(
                    split_location(f"{path}:11:88:{suffix}"),
                    (path, 11, 88, None),
                )

    def test_wrapped_location_with_trailing_content(self):
        self.assertEqual(
            split_location('"src/foo.kt:11:88: error: unexpected token"'),
            ("src/foo.kt", 11, 88, None),
        )

    def test_parsed_location_is_used_by_nvim_command(self):
        path = Path(__file__).resolve()
        path_text, line, column, end_line = split_location(f"{path}:11:88:xxx")
        self.assertEqual(
            OPEN_PATH["nvim_command"](Path(path_text), line, column, end_line),
            ["nvim", "+call cursor(11,88)", "--", str(path)],
        )

    def test_parsed_github_range_is_used_by_nvim_command(self):
        path = Path(__file__).resolve()
        path_text, line, column, end_line = split_location(f"{path}#L11-L20")
        self.assertEqual(
            OPEN_PATH["nvim_command"](Path(path_text), line, column, end_line),
            ["nvim", "+11", "+normal! V20G", "--", str(path)],
        )


class ReusableNvimWindowTests(unittest.TestCase):
    def test_finds_only_live_nvim_in_session(self):
        def run(command, **_kwargs):
            if command[:3] == ["tmux", "list-panes", "-s"]:
                return Mock(
                    returncode=0,
                    stdout=(
                        "%1\t@1\t/live.nvim\n"
                        "%2\t@2\t/split.nvim\n"
                        "%3\t@3\t/dead.nvim\n"
                        "%9\t@4\t\n"
                    ),
                )
            server = command[2]
            return Mock(returncode=0 if server == "/live.nvim" else 1)

        with patch.object(OPEN_PATH["subprocess"], "run", side_effect=run):
            self.assertEqual(
                find_reusable_nvim("%9"),
                ("%1", "/live.nvim"),
            )

    def test_prefers_source_nvim_even_when_its_window_is_split(self):
        def run(command, **_kwargs):
            if command[:3] == ["tmux", "list-panes", "-s"]:
                return Mock(
                    returncode=0,
                    stdout=(
                        "%1\t@1\t/fullscreen.nvim\n"
                        "%9\t@2\t/current.nvim\n"
                    ),
                )
            return Mock(returncode=0)

        with patch.object(OPEN_PATH["subprocess"], "run", side_effect=run):
            self.assertEqual(
                find_reusable_nvim("%9"),
                ("%9", "/current.nvim"),
            )

    def test_prefers_nvim_in_source_window(self):
        def run(command, **_kwargs):
            if command[:3] == ["tmux", "list-panes", "-s"]:
                return Mock(
                    returncode=0,
                    stdout=(
                        "%1\t@1\t/fullscreen.nvim\n"
                        "%8\t@2\t/window.nvim\n"
                        "%9\t@2\t\n"
                    ),
                )
            return Mock(returncode=0)

        with patch.object(OPEN_PATH["subprocess"], "run", side_effect=run):
            self.assertEqual(
                find_reusable_nvim("%9"),
                ("%8", "/window.nvim"),
            )

    def test_reuses_split_nvim_in_another_window_without_creating_a_window(self):
        def run(command, **_kwargs):
            if command[:3] == ["tmux", "list-panes", "-s"]:
                return Mock(
                    returncode=0,
                    stdout="%1\t@1\t/split.nvim\n%2\t@1\t\n%9\t@2\t\n",
                )
            return Mock(returncode=0)

        opener = Mock(return_value=True)
        with (
            patch.object(OPEN_PATH["subprocess"], "run", side_effect=run) as runner,
            patch.dict(open_target.__globals__, {"open_in_nvim": opener}),
        ):
            open_target("%9", Path("/tmp/file.txt"), 12, 3, None)

        opener.assert_called_once_with(
            "%1", "/split.nvim", Path("/tmp/file.txt"), 12, 3, None
        )
        self.assertFalse(any(
            call.args[0][:2] == ["tmux", "new-window"]
            for call in runner.call_args_list
        ))

    def test_reuses_first_nvim_when_multiple_instances_are_available(self):
        for source_window in ("@1", "@3"):
            with self.subTest(source_window=source_window):
                def run(command, **_kwargs):
                    if command[:3] == ["tmux", "list-panes", "-s"]:
                        return Mock(
                            returncode=0,
                            stdout=(
                                "%1\t@1\t/first.nvim\n"
                                "%2\t@1\t/second.nvim\n"
                                "%3\t@2\t/third.nvim\n"
                                f"%9\t{source_window}\t\n"
                            ),
                        )
                    return Mock(returncode=0)

                with patch.object(OPEN_PATH["subprocess"], "run", side_effect=run):
                    self.assertEqual(find_reusable_nvim("%9"), ("%1", "/first.nvim"))

    def test_returns_none_when_no_live_nvim_exists(self):
        def run(command, **_kwargs):
            if command[:3] == ["tmux", "list-panes", "-s"]:
                return Mock(returncode=0, stdout="%1\t@1\t/dead.nvim\n%9\t@1\t\n")
            return Mock(returncode=1)

        with patch.object(OPEN_PATH["subprocess"], "run", side_effect=run):
            self.assertIsNone(find_reusable_nvim("%9"))

    def test_enter_reuses_whole_window_nvim(self):
        finder = Mock(return_value=("%1", "/live.nvim"))
        opener = Mock(return_value=True)
        globals_ = open_target.__globals__
        with (
            patch.dict(
                globals_,
                {
                    "find_reusable_nvim": finder,
                    "open_in_nvim": opener,
                },
            ),
            patch.object(OPEN_PATH["subprocess"], "run") as run,
        ):
            open_target("%9", Path("/tmp/file.txt"), None, None, None)

        run.assert_called_once_with(
            ["tmux", "send-keys", "-t", "%1", "-X", "cancel"],
            check=False,
        )
        finder.assert_called_once_with("%9")
        opener.assert_called_once_with(
            "%1", "/live.nvim", Path("/tmp/file.txt"), None, None, None
        )

    def test_reusing_source_nvim_closes_copy_mode(self):
        finder = Mock(return_value=("%9", "/current.nvim"))
        opener = Mock(return_value=True)
        run = Mock(return_value=Mock(returncode=0))
        globals_ = open_target.__globals__
        with (
            patch.dict(
                globals_,
                {
                    "find_reusable_nvim": finder,
                    "open_in_nvim": opener,
                },
            ),
            patch.object(OPEN_PATH["subprocess"], "run", run),
        ):
            open_target("%9", Path("/tmp/file.txt"), None, None, None)

        run.assert_called_once_with(
            ["tmux", "send-keys", "-t", "%9", "-X", "cancel"],
            check=False,
        )

    def test_failed_reuse_does_not_cancel_copy_mode(self):
        run = Mock(return_value=Mock(returncode=1, stderr="failed"))
        with (
            patch.dict(
                open_target.__globals__,
                {
                    "find_reusable_nvim": Mock(return_value=("%1", "/live.nvim")),
                    "open_in_nvim": Mock(return_value=False),
                    "tmux_message": Mock(),
                },
            ),
            patch.object(OPEN_PATH["subprocess"], "run", run),
        ):
            open_target("%9", Path("/tmp/file.txt"), None, None, None)

        self.assertEqual(run.call_count, 1)
        self.assertEqual(run.call_args.args[0][:2], ["tmux", "new-window"])

    def test_reuse_switches_to_a_listed_buffer_or_edits_a_new_one(self):
        run = Mock(return_value=Mock(returncode=0))
        path = Path(__file__).resolve()
        with (
            patch.object(OPEN_PATH["subprocess"], "run", run),
            patch.dict(open_in_nvim.__globals__, {"set_pane_name": Mock()}),
        ):
            self.assertTrue(open_in_nvim("%1", "/live.nvim", path, 12, 3, None))

        remote_expressions = [
            call.args[0][-1]
            for call in run.call_args_list
            if call.args[0][:3] == ["nvim", "--server", "/live.nvim"]
        ]
        self.assertIn("buflisted(bufnr(", remote_expressions[0])
        self.assertIn("? 'hide buffer '", remote_expressions[0])
        self.assertIn(": 'hide edit '", remote_expressions[0])
        self.assertEqual(remote_expressions[1], "cursor(12, 3)")

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


class PaneTargetTests(unittest.TestCase):
    def test_picker_passes_selected_pane_and_encoded_path_to_launcher(self):
        path = Path("/tmp/中文 ' %% #{pane_id}.txt")
        run = Mock(return_value=Mock(returncode=0))
        finder = Mock()
        with (
            patch.object(OPEN_PATH["subprocess"], "check_output", return_value="/socket\tclient\n"),
            patch.object(OPEN_PATH["subprocess"], "run", run),
            patch.dict(open_target.__globals__, {"find_reusable_nvim": finder}),
        ):
            open_target("%9", path, 12, 3, 15, in_pane=True)

        finder.assert_not_called()
        command = run.call_args.args[0]
        self.assertEqual(command[:-1], ["tmux", "display-panes", "-b", "-d", "0"])
        callback = shlex.split(command[-1])
        self.assertEqual(callback[:2], ["run-shell", "-b"])
        launcher = shlex.split(callback[2])
        self.assertEqual(Path(launcher[0]).name, "copy-mode-enter")
        self.assertEqual(launcher[1:4], ["%%", "/socket", "client"])
        self.assertEqual(base64.b64decode(launcher[4]).decode(), str(path))
        self.assertEqual(launcher[5:], ["12", "3", "15"])

    def test_path_popup_closes_before_pane_picker_and_cancel_does_not_open(self):
        chooser = OPEN_PATH["choose_target"]
        for choose in (False, True):
            with self.subTest(choose=choose):
                opener = Mock()

                def popup(command, **_kwargs):
                    opener.assert_not_called()
                    index = command.index("--choose-pane")
                    if choose:
                        Path(command[index + 1]).write_text("/tmp/chosen.txt")
                    return Mock(returncode=0)

                with (
                    patch.object(OPEN_PATH["subprocess"], "run", side_effect=popup),
                    patch.dict(chooser.__globals__, {"open_target": opener}),
                ):
                    chooser("%9", Path("/tmp"), [Path("/tmp/chosen.txt")], 12, 3, 15, in_pane=True)

                if choose:
                    opener.assert_called_once_with("%9", Path("/tmp/chosen.txt"), 12, 3, 15, in_pane=True)
                else:
                    opener.assert_not_called()


if __name__ == "__main__":
    unittest.main()
