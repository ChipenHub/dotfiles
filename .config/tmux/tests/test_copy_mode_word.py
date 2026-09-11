"""Run with: python3 -m unittest discover -s .config/tmux/tests -v"""

from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import copy_mode_word as word


class WordTests(unittest.TestCase):
    def select(self, text, position, action):
        cells, _ = word.cells_from_capture(text + "\n", text + "\n")
        start, end = word.word_target(cells, position, action)
        return "".join(cell.text for cell in cells[start:end + 1])

    def test_inner_word(self):
        for text, position, expected in [
            ("123_456", 1, "123"), ("123_456", 5, "456"),
            ("foo__bar", 3, "__"), ("foo  bar", 3, "  "),
            ("你好：123", 3, "123"), ("你好：123", 0, "你"),
            ("你好：123", 1, "好"), ("你好：123", 2, "："),
            ("foo,bar", 3, ","), ("foo\nbar", 4, "bar"),
        ]:
            with self.subTest(text=text, position=position):
                self.assertEqual(self.select(text, position, "iw"), expected)

    def test_around_word(self):
        for text, position, expected in [
            ("foo  bar", 1, "foo  "), ("foo  bar", 3, "  bar"),
            ("foo  bar", 6, "  bar"), ("foo,bar", 1, "foo"),
            ("foo,bar", 3, ","), ("foo__bar", 3, "__"),
            ("  foo", 3, "foo"), ("foo\n  bar", 7, "bar"),
            ("foo \nbar", 3, " \nbar"), ("foo  ", 1, "foo  "),
            ("你好：123，456", 4, "123"),
        ]:
            with self.subTest(text=text, position=position):
                self.assertEqual(self.select(text, position, "aw"), expected)

    def test_path_boundaries(self):
        for punctuation in "：，。！？；、（）【】《》「」『』“”‘’…—﹐﹕﹙﹚":
            text = f"你好{punctuation}/tmp/a_b.py:12{punctuation}其他"
            with self.subTest(punctuation=punctuation):
                self.assertEqual(self.select(text, 5, "ip"), "/tmp/a_b.py:12")
        self.assertEqual(self.select("中文/tmp/foo", 4, "ip"), "/tmp/foo")
        self.assertEqual(self.select("a\tb", 2, "ip"), "b")
        self.assertEqual(self.select("a\u3000b", 2, "ip"), "b")

    def test_motion_destinations(self):
        text = "你好：123_456，abc"
        cells, _ = word.cells_from_capture(text + "\n", text + "\n")
        for action, positions in [
            ("w", [0, 1, 2, 3, 6, 7, 10, 11]),
            ("e", [0, 1, 2, 5, 6, 9, 10, 13]),
            ("b", [13, 11, 10, 7, 6, 3, 2, 1, 0]),
        ]:
            for current, expected in zip(positions, positions[1:]):
                with self.subTest(action=action, current=current):
                    self.assertEqual(word.word_target(cells, current, action), (expected, expected))

    def test_local_capture_matches_full_history(self):
        text = "old\n" * 100 + "你好：123_456\n\n  \nabc  def\n" + "new\n" * 100
        full, _ = word.cells_from_capture(text, text)
        for row in range(100, 104):
            local, _ = word.cells_from_capture(text, text, row)
            for cursor, cell in enumerate(local):
                if cell.y != row:
                    continue
                full_cursor = full.index(cell)
                for action in ["iw", "aw", "ip", "b", "e", "w"]:
                    with self.subTest(row=row, x=cell.x, action=action):
                        left, right = word.word_target(local, cursor, action)
                        full_left, full_right = word.word_target(full, full_cursor, action)
                        self.assertEqual(local[left:right + 1], full[full_left:full_right + 1])

    def test_tab_coordinates_keep_native_cursor_step_counts(self):
        text = "你\tfoo\tbar\n"
        cells, _ = word.cells_from_capture(text, text)
        self.assertEqual(
            [(cell.text, cell.x, cell.column) for cell in cells],
            [("你", 0, 0), ("\t", 2, 1), ("f", 8, 2), ("o", 9, 3),
             ("o", 10, 4), ("\t", 11, 5), ("b", 16, 6), ("a", 17, 7),
             ("r", 18, 8), ("\n", 19, 9)],
        )

    def test_wrap_and_combining_coordinates(self):
        cells, starts = word.cells_from_capture("你éfo\no：bar\n", "你éfoo：bar\n")
        self.assertEqual(starts, [0, 0])
        self.assertEqual([(c.text, c.x, c.y) for c in cells[:3]], [("你", 0, 0), ("é", 2, 0), ("f", 3, 0)])
        start, end = word.word_target(cells, 3, "iw")
        self.assertEqual("".join(c.text for c in cells[start:end + 1]), "éfoo")


class PairTests(unittest.TestCase):
    def select(self, text, position, action):
        cells, _ = word.cells_from_capture(text + "\n", text + "\n")
        target = word.pair_target(cells, position, action)
        if target is None:
            return None
        start, end = target
        return "".join(cell.text for cell in cells[start:end + 1])

    def test_quote_objects(self):
        for name in ["double-quote", "single-quote", "backtick"]:
            quote = word.PAIRS[name][0]
            text = f"xx {quote}你好：foo bar{quote} yy"
            for position in [0, 3, 7, 14]:
                with self.subTest(name=name, position=position):
                    self.assertEqual(self.select(text, position, "i-" + name), "你好：foo bar")
                    self.assertEqual(self.select(text, position, "a-" + name), f"{quote}你好：foo bar{quote} ")

    def test_quote_escapes_and_whitespace(self):
        for text, position, action, expected in [
            ('"foo \\" bar"', 3, "i-double-quote", 'foo \\" bar'),
            ('"foo\\\\" bar', 3, "i-double-quote", "foo\\\\"),
            ('  "foo"', 4, "a-double-quote", '  "foo"'),
            ('"foo" "bar"', 5, "i-double-quote", " "),
            ('"foo" "bar"', 4, "i-double-quote", "foo"),
            ('"foo" "bar"', 6, "i-double-quote", "bar"),
        ]:
            with self.subTest(text=text, position=position):
                self.assertEqual(self.select(text, position, action), expected)

    def test_nested_blocks(self):
        for name in ["paren", "bracket", "brace", "angle"]:
            opening, closing = word.PAIRS[name]
            text = f"xx {opening}foo {opening}bar baz{closing} end{closing} yy"
            for position in [8, 10, 15]:
                with self.subTest(name=name, position=position):
                    self.assertEqual(self.select(text, position, "i-" + name), "bar baz")
                    self.assertEqual(self.select(text, position, "a-" + name), f"{opening}bar baz{closing}")
            self.assertEqual(self.select(text, 0, "i-" + name), f"foo {opening}bar baz{closing} end")

    def test_multiline_blocks(self):
        self.assertEqual(self.select("(\n  foo\n  )", 5, "i-paren"), "  foo\n")
        self.assertEqual(self.select("(\n  foo\n  )", 5, "a-paren"), "(\n  foo\n  )")
        self.assertEqual(self.select("(foo\n\n\nbar)", 2, "i-paren"), "foo\n\n\nbar")

    def test_empty_and_unmatched_pairs(self):
        for name, (opening, closing) in word.PAIRS.items():
            with self.subTest(name=name):
                self.assertEqual(self.select(opening + closing, 0, "i-" + name), "")
                self.assertEqual(self.select(opening + closing, 0, "a-" + name), opening + closing)
                self.assertIsNone(self.select(opening + "abc", 2, "i-" + name))
        self.assertIsNone(self.select('"foo\nbar"', 2, "i-double-quote"))
        self.assertIsNone(self.select('(foo) bar', 7, "i-paren"))


@unittest.skipUnless(shutil.which("tmux"), "tmux is required")
class TmuxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.socket = "dotfiles-word-test-" + uuid.uuid4().hex
        cls.config = Path(__file__).resolve().parents[3] / ".tmux.conf"
        cls.tmux("-f", str(cls.config), "new-session", "-d", "-s", "words", "-x", "40", "-y", "10", "sleep 3600")
        cls.socket_path = cls.tmux("display-message", "-p", "#{socket_path}").strip()
        cls.environment = patch.dict(os.environ, {"TMUX": cls.socket_path + ",0,0"})
        cls.environment.start()
        cls.home = tempfile.TemporaryDirectory(prefix="dotfiles-tmux-home-")
        config_dir = Path(cls.home.name) / ".config"
        config_dir.mkdir()
        (config_dir / "tmux").symlink_to(Path(__file__).resolve().parents[1])
        cls.tmux("set-environment", "-g", "HOME", cls.home.name)
        cls.tmux("set-environment", "-t", "words", "HOME", cls.home.name)

    @classmethod
    def tearDownClass(cls):
        cls.environment.stop()
        # This is only the unique server created by this test class.
        cls.tmux("kill-server")
        cls.home.cleanup()

    @classmethod
    def tmux(cls, *args):
        return subprocess.check_output(["tmux", "-L", cls.socket, *args], text=True)

    def setUp(self):
        self.pane = None

    def tearDown(self):
        if self.pane is not None:
            self.tmux("kill-pane", "-t", self.pane)

    def load(self, text, column=0, row=0):
        program = [sys.executable, "-c", f"import os,time; os.write(1, {text.encode()!r}); time.sleep(3600)"]
        self.pane = self.tmux("new-window", "-d", "-P", "-F", "#{pane_id}", *program).strip()
        for _ in range(100):
            if self.tmux("capture-pane", "-p", "-t", self.pane).strip():
                break
            time.sleep(0.01)
        else:
            self.fail("pane did not produce output")
        self.tmux("copy-mode", "-t", self.pane)
        self.send("history-top")
        self.send("start-of-line")
        if row:
            self.send("cursor-down", count=row)
        if column:
            self.send("cursor-right", count=column)

    def send(self, command, count=1):
        self.tmux("send-keys", "-t", self.pane, "-X", "-N", str(count), command)

    def cursor(self):
        return self.tmux("display-message", "-p", "-t", self.pane, "#{copy_cursor_x},#{copy_cursor_y},#{scroll_position}").strip()

    def selection(self, action):
        word.run(self.pane, action)
        self.send("copy-selection-no-clear")
        return self.tmux("show-buffer")

    @contextmanager
    def attached_client(self):
        self.tmux("select-window", "-t", self.pane)
        client = subprocess.Popen(
            ["tmux", "-L", self.socket, "-C", "attach-session", "-t", "words"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            for _ in range(100):
                name = self.tmux("list-clients", "-F", "#{client_name}").strip()
                if name:
                    break
                time.sleep(0.01)
            self.assertTrue(name, "control client did not attach")
            yield name
        finally:
            client.communicate(timeout=5)

    def assert_key_selection(self, client, keys, expected):
        self.tmux("send-keys", "-c", client, "-K", *keys)
        for _ in range(100):
            actual = self.tmux(
                "display-message", "-p", "-t", self.pane,
                "#{copy_cursor_x},#{copy_cursor_y},#{selection_start_x},#{selection_start_y},"
                "#{selection_end_x},#{selection_end_y},#{rectangle_toggle},#{selection_active}",
            ).strip()
            if actual == expected:
                break
            time.sleep(0.01)
        self.assertEqual(actual, expected, keys)

    def test_chinese_motion_cells(self):
        self.load("你好：123_456，abc")
        for expected in [2, 4, 6, 9, 10, 13, 15]:
            word.run(self.pane, "w")
            self.assertEqual(int(self.cursor().split(",")[0]), expected)
        word.run(self.pane, "b")
        self.assertEqual(int(self.cursor().split(",")[0]), 13)

    def test_wide_character_selection(self):
        self.load("你好：123", column=1)
        self.assertEqual(self.selection("iw"), "好")

    def test_inner_word_selection(self):
        self.load("你好：123_456", column=4)
        self.assertEqual(self.selection("iw"), "123")

    def test_inner_whitespace_selection(self):
        self.load("foo  bar", column=3)
        self.assertEqual(self.selection("iw"), "  ")

    def test_around_punctuation_selection(self):
        self.load("foo,bar", column=1)
        self.assertEqual(self.selection("aw"), "foo")

    def test_around_trailing_whitespace(self):
        self.load("foo  bar", column=1)
        self.assertEqual(self.selection("aw"), "foo  ")

    def test_around_leading_whitespace(self):
        self.load("foo  bar", column=6)
        self.assertEqual(self.selection("aw"), "  bar")

    def test_path_selection(self):
        self.load("路径：/tmp/a_b.py:12，后文", column=7)
        self.assertEqual(self.selection("ip"), "/tmp/a_b.py:12")

    def test_backward_motion_on_tab_prefixed_path(self):
        text = "\t.config/tmux/copy_mode_word.py"
        self.load(text, column=len(text) - 1)
        for index in [text.rindex("py"), text.rindex("."), text.index("word"),
                      text.index("_word"), text.index("mode"), text.index("_mode")]:
            word.run(self.pane, "b")
            self.assertEqual(self.cursor(), f"{index + 7},0,0")

    def test_objects_on_tab_prefixed_path(self):
        text = "\t.config/tmux/copy_mode_word.py"
        self.load(text, column=text.index("word") + 1)
        self.assertEqual(self.selection("iw"), "word")
        self.assertEqual(self.selection("ip"), text[1:])

    def test_tab_prefixed_objects_after_resize_refresh(self):
        text = "\t.config/tmux/copy_mode_word.py"
        self.load(text, column=text.index("word") + 1)
        self.tmux("resize-window", "-t", self.pane, "-x", "60")
        for _ in range(150):
            pending = self.tmux("display-message", "-p", "-t", self.pane, "#{E:@copy_refresh_pending}").strip()
            if pending == "0":
                break
            time.sleep(0.01)
        self.assertEqual(pending, "0")
        self.assertEqual(self.selection("iw"), "word")
        self.assertEqual(self.selection("ip"), text[1:])

    def test_real_keys_on_tab_prefixed_path(self):
        text = "\t.config/tmux/copy_mode_word.py"
        self.load(text, column=len(text) - 1)
        with self.attached_client() as client:
            self.tmux("send-keys", "-c", client, "-K", "B")
            for _ in range(100):
                if self.cursor() == "8,0,0":
                    break
                time.sleep(0.01)
            self.assertEqual(self.cursor(), "8,0,0")
            for keys, expected in [(["v", "i", "p", "y"], text[1:]),
                                   (["v", "i", "w", "y"], "py")]:
                self.tmux("set-buffer", "pending")
                self.tmux("send-keys", "-c", client, "-K", *keys)
                for _ in range(100):
                    if self.tmux("show-buffer") == expected:
                        break
                    time.sleep(0.01)
                self.assertEqual(self.tmux("show-buffer"), expected, keys)

    def test_wrapped_selection(self):
        self.load("你：" + "x" * 50 + "，end", column=12, row=1)
        self.assertEqual(self.selection("iw"), "x" * 50)

    def test_history_selection(self):
        self.load("你好：123_456\r\n" + "other\r\n" * 20, column=4)
        self.assertEqual(self.selection("iw"), "123")

    def test_visual_motion_keeps_anchor(self):
        self.load("你好：123", column=3)
        self.send("begin-selection")
        word.run(self.pane, "e")
        self.send("copy-selection-no-clear")
        self.assertEqual(self.tmux("show-buffer"), "123")

    def test_pair_selection_preserves_rectangle_and_right_endpoint(self):
        self.load('"foo bar"\r\nabcdefghij\r\nx\r\n0123456789', column=4)
        self.send("rectangle-on")
        self.assertEqual(self.selection("i-double-quote"), "foo bar")
        self.assertEqual(self.cursor(), "7,0,0")
        self.send("cursor-down")
        self.assertEqual(self.cursor(), "7,1,0")
        self.send("copy-selection-no-clear")
        self.assertEqual(self.tmux("show-buffer"), "foo bar\nbcdefgh")
        self.send("cursor-down", count=2)
        self.assertEqual(self.cursor(), "7,3,0")
        self.send("cursor-up", count=3)
        self.assertEqual(self.cursor(), "7,0,0")
        self.assertEqual(self.tmux("display-message", "-p", "-t", self.pane, "#{rectangle_toggle}").strip(), "1")

    def test_wrapped_quote_selection(self):
        self.load('xx"' + "a" * 50 + '"yy', column=6, row=1)
        self.assertEqual(self.selection("i-double-quote"), "a" * 50)
        self.assertEqual(self.cursor(), "12,1,0")

    def test_multiline_pair_selection(self):
        self.load("  (foo\r\n\r\n\r\nbar) tail", column=4)
        self.assertEqual(self.selection("i-paren"), "foo\n\n\nbar")
        self.assertEqual(self.cursor(), "2,3,0")

    def test_empty_inner_object_clears_selection(self):
        self.load('""', column=1)
        self.send("begin-selection")
        self.send("rectangle-on")
        word.run(self.pane, "i-double-quote")
        self.assertEqual(self.tmux("display-message", "-p", "-t", self.pane, "#{selection_active} #{rectangle_toggle}").strip(), "0 1")

    def test_unmatched_pair_preserves_selection(self):
        self.load("foo bar", column=1)
        self.assertEqual(self.selection("iw"), "foo")
        before = self.cursor()
        self.assertEqual(self.selection("i-double-quote"), "foo")
        self.assertEqual(self.cursor(), before)

    def test_real_pair_keys(self):
        text = 'xx[({<"foo \'bar `baz` qux\' end">})]yy'
        self.load(text, column=text.index("baz") + 1)
        aliases = {
            "double-quote": ['"'], "single-quote": ["'"], "backtick": ["`"],
            "paren": ["(", ")", "b"], "bracket": ["[", "]"],
            "brace": ["{", "}", "B"], "angle": ["<", ">"],
        }
        with self.attached_client() as client:
            for pair, keys in aliases.items():
                opening, closing = word.PAIRS[pair]
                for key in keys:
                    for action in ["i", "a"]:
                        with self.subTest(pair=pair, key=key, action=action):
                            self.send("clear-selection")
                            self.send("start-of-line")
                            self.send("cursor-right", count=text.index("baz") + 1)
                            left, right = text.index(opening), text.rindex(closing)
                            if action == "i":
                                left, right = left + 1, right - 1
                            elif opening == closing and text[right + 1] == " ":
                                right += 1
                            self.assert_key_selection(client, ["v", action, key], f"{right},0,{left},0,{right},0,0,1")
                            self.send("copy-selection-no-clear")
                            self.assertEqual(self.tmux("show-buffer"), text[left:right + 1])

    def test_keys_quote_then_rectangle_vertical(self):
        self.load('abcdefghijklm\r\nxx"foo bar"yy\r\n0123456789ABC\r\nx\r\nABCDEFGHIJKLM', column=5, row=1)
        with self.attached_client() as client:
            self.assert_key_selection(client, ["v", "i", '"'], "9,1,3,1,9,1,0,1")
            self.assert_key_selection(client, ["C-v", "j"], "9,2,3,1,9,2,1,1")
            self.send("copy-selection-no-clear")
            self.assertEqual(self.tmux("show-buffer"), "foo bar\n3456789")
            self.assert_key_selection(client, ["j", "j"], "9,4,3,1,9,4,1,1")
            self.assert_key_selection(client, ["k", "k", "k", "k"], "9,0,3,1,9,0,1,1")
            self.send("copy-selection-no-clear")
            self.assertEqual(self.tmux("show-buffer"), "defghij\nfoo bar")

    def test_keys_rectangle_then_pair(self):
        self.load('abcdefghijklm\r\nxx("foo bar")yy\r\n0123456789ABC', column=6, row=1)
        with self.attached_client() as client:
            self.assert_key_selection(client, ["C-v", "i", "("], "11,1,3,1,11,1,1,1")
            self.assert_key_selection(client, ["j"], "11,2,3,1,11,2,1,1")
            self.send("copy-selection-no-clear")
            self.assertEqual(self.tmux("show-buffer"), '"foo bar"\n3456789AB')
            self.assert_key_selection(client, ["k", "a", ")"], "12,1,2,1,12,1,1,1")
            self.assert_key_selection(client, ["k"], "12,0,2,1,12,0,1,1")

    def test_quote_rectangle_includes_full_width_of_chinese(self):
        self.load('abcde\r\n"你好"\r\n01234', column=2, row=1)
        with self.attached_client() as client:
            self.assert_key_selection(client, ["v", "i", '"'], "3,1,1,1,3,1,0,1")
            self.assert_key_selection(client, ["C-v", "j"], "4,2,1,1,4,2,1,1")
            self.send("copy-selection-no-clear")
            self.assertEqual(self.tmux("show-buffer"), "你好\n1234")
            self.assert_key_selection(client, ["k", "i", '"'], "4,1,1,1,4,1,1,1")

    def test_single_chinese_character_rectangle(self):
        self.load('"好"\r\n01234', column=1)
        with self.attached_client() as client:
            self.assert_key_selection(client, ["v", "i", '"'], "1,0,1,0,1,0,0,1")
            self.assert_key_selection(client, ["C-v", "j"], "2,1,1,0,2,1,1,1")
            self.send("copy-selection-no-clear")
            self.assertEqual(self.tmux("show-buffer"), "好\n12")

    def test_wrapped_pair_rectangle_uses_right_endpoint(self):
        self.load("p" * 35 + '"' + "z" * 10 + '"', column=38)
        with self.attached_client() as client:
            self.assert_key_selection(client, ["v", "i", '"'], "5,1,36,0,5,1,0,1")
            self.assert_key_selection(client, ["C-v"], "36,0,36,0,5,1,1,1")
            self.assert_key_selection(client, ["j"], "36,1,36,1,5,1,1,1")

    def test_real_key_tables(self):
        self.load("你好：123_456", column=4)
        with self.attached_client() as name:
            self.tmux("send-keys", "-c", name, "-K", "v", "i", "w", "y")
            for _ in range(100):
                if self.tmux("list-buffers", "-F", "#{buffer_sample}").splitlines()[0:1] == ["123"]:
                    break
                time.sleep(0.01)
            self.assertEqual(self.tmux("show-buffer"), "123")
            self.assertEqual(self.tmux("display-message", "-p", "-c", name, "#{client_key_table}").strip(), "root")
            for keys, expected in [(["v", "a", "w", "y"], "123"), (["v", "i", "p", "y"], "123_456")]:
                self.tmux("set-buffer", "pending")
                self.tmux("send-keys", "-c", name, "-K", *keys)
                for _ in range(100):
                    if self.tmux("show-buffer") == expected:
                        break
                    time.sleep(0.01)
                self.assertEqual(self.tmux("show-buffer"), expected, keys)
            for keys, expected in [(["0", "3", "w"], 6), (["2", "l", "w"], 9), (["w"], 10)]:
                for key in keys:
                    self.tmux("send-keys", "-c", name, "-K", key)
                    time.sleep(0.03)  # Let command-prompt install its input handler.
                for _ in range(100):
                    if int(self.cursor().split(",")[0]) == expected:
                        break
                    time.sleep(0.01)
                self.assertEqual(int(self.cursor().split(",")[0]), expected, keys)

    def test_path_extension_and_no_global_mutation(self):
        self.load("你好：/a_b：/c_d", column=4)
        separators = self.tmux("show-options", "-gv", "word-separators")
        self.assertEqual(self.selection("extend-path"), "/a_b")
        self.assertEqual(self.selection("extend-path"), "/a_b：")
        self.assertEqual(self.tmux("show-options", "-gv", "word-separators"), separators)


if __name__ == "__main__":
    unittest.main()
