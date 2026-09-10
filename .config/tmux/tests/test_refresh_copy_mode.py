"""Unit and isolated-server tests for delayed copy-mode refresh."""

import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import refresh_copy_mode as refresh


class PageTopTests(unittest.TestCase):
    def test_appended_output_does_not_move_page(self):
        old = [str(i) for i in range(20)]
        self.assertEqual(refresh.page_top(old, old + ["new"], 5, 6), 5)

    def test_trimmed_history(self):
        old = [str(i) for i in range(20)]
        self.assertEqual(refresh.page_top(old, old[3:] + ["new"], 5, 5), 2)

    def test_context_disambiguates_repeated_lines(self):
        old = ["a", "same", "b", "c", "same", "d"]
        self.assertEqual(refresh.page_top(old, old[3:], 4, 2), 1)

    def test_replaced_screen_uses_fallback(self):
        self.assertEqual(refresh.page_top(["old"], ["new"], 0, 0), 0)


@unittest.skipUnless(shutil.which("tmux"), "tmux is required")
class RefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.socket = "dotfiles-refresh-test-" + uuid.uuid4().hex
        cls.root = Path(__file__).resolve().parents[3]
        cls.home = tempfile.TemporaryDirectory(prefix="dotfiles-refresh-home-")
        config = Path(cls.home.name) / ".config"
        config.mkdir()
        (config / "tmux").symlink_to(cls.root / ".config/tmux")
        cls.tmux("-f", "/dev/null", "new-session", "-d", "-s", "refresh", "-x", "80", "-y", "16", "sleep 3600")
        cls.tmux("set-environment", "-g", "HOME", cls.home.name)
        cls.tmux("set-environment", "-t", "refresh", "HOME", cls.home.name)
        cls.tmux("source-file", str(cls.root / ".tmux.conf"))
        cls.socket_path = cls.tmux("display-message", "-p", "#{socket_path}").strip()

    @classmethod
    def tearDownClass(cls):
        cls.tmux("kill-server")  # Only this class's unique test server.
        cls.home.cleanup()

    @classmethod
    def tmux(cls, *args):
        return subprocess.check_output(["tmux", "-L", cls.socket, *args], text=True)

    def setUp(self):
        program = (
            "import os,signal,time; "
            "signal.signal(signal.SIGUSR1, lambda *_: os.write(1, b'fresh-output\\r\\n')); "
            "signal.signal(signal.SIGUSR2, lambda *_: os.write(1, b'\\x1b[3J')); "
            "os.write(1, ''.join(f'row-{i:03d} 中文 contents\\r\\n' for i in range(60)).encode()); "
            "time.sleep(3600)"
        )
        self.pane = self.tmux("new-window", "-d", "-P", "-F", "#{pane_id}", sys.executable, "-c", program).strip()
        self.window = self.state("#{window_id}")
        self.wait_for(lambda: "row-059" in self.capture())
        self.tmux("split-window", "-d", "-h", "-t", self.pane, "sleep 3600")
        self.tmux("copy-mode", "-t", self.pane)
        self.tmux("send-keys", "-t", self.pane, "-X", "goto-line", "20")
        self.tmux("send-keys", "-t", self.pane, "-X", "top-line")
        self.tmux("send-keys", "-t", self.pane, "-X", "-N", "3", "cursor-down")
        self.tmux("send-keys", "-t", self.pane, "-X", "-N", "10", "cursor-right")
        self.wait_for(lambda: self.state("#{@copy_refresh_size}") == self.state("#{pane_width}x#{pane_height}"))
        time.sleep(0.35)  # Let the setup layout job expire before each test.

    def tearDown(self):
        self.tmux("kill-window", "-t", self.window)

    def state(self, fmt):
        return self.tmux("display-message", "-p", "-t", self.pane, fmt).strip()

    def capture(self, copy=False):
        return self.tmux("capture-pane", "-p", *(["-M"] if copy else []), "-S", "-", "-E", "-", "-t", self.pane)

    def wait_for(self, predicate):
        for _ in range(150):
            if predicate():
                return
            time.sleep(0.01)
        self.fail("timed out waiting for tmux refresh")

    def fresh_output(self):
        os.kill(int(self.state("#{pane_pid}")), signal.SIGUSR1)
        self.wait_for(lambda: "fresh-output" in self.capture())

    def resize(self):
        self.tmux("resize-pane", "-t", self.pane, "-R", "1")

    def wait_refreshed(self):
        self.wait_for(lambda: self.state("#{@copy_refresh_pending}") == "0")

    def page(self):
        scroll, height = map(int, self.state("#{scroll_position} #{pane_height}").split())
        lines = self.capture(copy=True).splitlines()
        return lines[len(lines) - height - scroll:][:height]

    def test_refresh_keeps_page_and_cursor_without_exiting_mode(self):
        self.tmux("set-hook", "-p", "-t", self.pane, "pane-mode-changed[92]", "set-option -p @unexpected_mode_change yes")
        self.resize()
        page = self.page()
        cursor = self.state("#{copy_cursor_x},#{copy_cursor_y}")
        self.fresh_output()
        self.assertNotIn("fresh-output", self.capture(copy=True))
        self.wait_refreshed()
        self.assertIn("fresh-output", self.capture(copy=True))
        self.assertEqual(self.page(), page)
        self.assertEqual(self.state("#{copy_cursor_x},#{copy_cursor_y}"), cursor)
        self.assertEqual(self.state("#{pane_mode}"), "copy-mode")
        self.assertEqual(self.state("#{@unexpected_mode_change}"), "")

    def test_wrapped_lines_keep_post_resize_page_and_cursor(self):
        self.tmux("resize-pane", "-t", self.pane, "-x", "17")
        page = self.page()
        cursor = self.state("#{copy_cursor_x},#{copy_cursor_y}")
        self.fresh_output()
        self.wait_refreshed()
        self.assertEqual(self.page(), page)
        self.assertEqual(self.state("#{copy_cursor_x},#{copy_cursor_y}"), cursor)

    def test_history_cleared_while_scrolled_does_not_crash_server(self):
        self.resize()
        self.assertGreater(int(self.state("#{scroll_position}")), 0)
        os.kill(int(self.state("#{pane_pid}")), signal.SIGUSR2)
        self.wait_for(lambda: self.state("#{history_size}") == "0")
        self.assertEqual(self.state("#{pane_mode}"), "copy-mode")
        self.wait_refreshed()
        self.assertEqual(self.state("#{pane_mode} #{scroll_position}"), "copy-mode 0")
        self.assertEqual(self.capture(copy=True), self.capture())

    def test_history_shrink_after_capture_does_not_crash_server(self):
        # Invoke the worker directly so the race is deterministic, not timed.
        self.tmux("set-hook", "-gu", "window-layout-changed[91]")
        try:
            self.tmux("set-option", "-p", "-t", self.pane, "@copy_refresh_pending", "1")
            check_output = subprocess.check_output
            cleared = False

            def clear_before_refresh(command, **kwargs):
                nonlocal cleared
                if "if-shell" in command and not cleared:
                    cleared = True
                    os.kill(int(self.state("#{pane_pid}")), signal.SIGUSR2)
                    self.wait_for(lambda: self.state("#{history_size}") == "0")
                return check_output(command, **kwargs)

            with patch.object(refresh.subprocess, "check_output", side_effect=clear_before_refresh):
                refresh.run(self.socket_path, self.window, self.state("#{@copy_resize_generation}"))
            self.assertTrue(cleared)
            self.assertEqual(self.state("#{pane_mode} #{scroll_position} #{@copy_refresh_pending}"), "copy-mode 0 0")
        finally:
            self.tmux("source-file", str(self.root / ".tmux.conf"))

    def test_terminal_resize_is_covered(self):
        self.tmux("resize-window", "-t", self.window, "-x", "100", "-y", "20")
        self.fresh_output()
        self.wait_refreshed()
        self.assertIn("fresh-output", self.capture(copy=True))

    def test_all_resized_copy_panes_refresh_without_switching_focus(self):
        right = self.tmux("list-panes", "-t", self.window, "-f", "#{pane_at_right}", "-F", "#{pane_id}").strip()
        self.tmux("copy-mode", "-t", right)
        self.tmux("select-pane", "-t", right)
        self.resize()
        self.wait_refreshed()
        self.wait_for(lambda: self.tmux("display-message", "-p", "-t", right, "#{@copy_refresh_pending}").strip() == "0")
        self.assertEqual(self.tmux("display-message", "-p", "-t", right, "#{pane_mode} #{pane_active}").strip(), "copy-mode 1")
        self.assertEqual(self.state("#{pane_mode} #{pane_active}"), "copy-mode 0")

    def test_resize_burst_is_debounced(self):
        for _ in range(4):
            self.resize()
            time.sleep(0.1)
            self.assertEqual(self.state("#{@copy_refresh_pending}"), "1")
        time.sleep(0.1)
        self.assertEqual(self.state("#{@copy_refresh_pending}"), "1")
        self.wait_refreshed()

    def test_resize_back_to_original_size_still_refreshes(self):
        size = self.state("#{pane_width}x#{pane_height}")
        self.resize()
        self.tmux("resize-pane", "-t", self.pane, "-L", "1")
        self.fresh_output()
        self.assertEqual(self.state("#{pane_width}x#{pane_height}"), size)
        self.wait_refreshed()
        self.assertIn("fresh-output", self.capture(copy=True))

    def test_layout_helper_is_covered(self):
        environment = dict(os.environ, TMUX=self.socket_path + ",0,0")
        subprocess.run(
            [str(self.root / ".config/tmux/layout-three-panes"), self.pane, "2"],
            env=environment, check=True,
        )
        self.fresh_output()
        self.wait_refreshed()
        self.assertIn("fresh-output", self.capture(copy=True))

    def test_exit_and_reenter_during_delay_is_not_refreshed(self):
        self.resize()
        self.tmux("send-keys", "-t", self.pane, "-X", "cancel")
        self.tmux("copy-mode", "-t", self.pane)
        self.fresh_output()
        time.sleep(0.45)
        self.assertNotIn("fresh-output", self.capture(copy=True))

    def test_config_reload_initializes_existing_panes(self):
        self.tmux("set-option", "-pu", "-t", self.pane, "@copy_refresh_size")
        self.tmux("source-file", str(self.root / ".tmux.conf"))
        self.assertEqual(self.state("#{@copy_refresh_size}"), self.state("#{pane_width}x#{pane_height}"))

    def test_stale_generation_does_not_refresh(self):
        generation = self.state("#{@copy_resize_generation}")
        self.resize()
        self.fresh_output()
        refresh.run(self.socket_path, self.window, generation)
        self.assertNotIn("fresh-output", self.capture(copy=True))
        self.wait_refreshed()
        self.assertIn("fresh-output", self.capture(copy=True))

    def test_exited_copy_mode_stays_exited(self):
        self.resize()
        self.tmux("send-keys", "-t", self.pane, "-X", "cancel")
        time.sleep(0.45)
        self.assertEqual(self.state("#{pane_in_mode}"), "0")

    def test_unchanged_copy_pane_and_normal_panes_are_untouched(self):
        right = self.tmux("list-panes", "-t", self.window, "-f", "#{pane_at_right}", "-F", "#{pane_id}").strip()
        self.tmux("split-window", "-d", "-v", "-t", right, "sleep 3600")
        time.sleep(0.35)
        self.fresh_output()
        before = self.state("#{pane_width}x#{pane_height}")
        self.tmux("resize-pane", "-t", right, "-D", "1")
        time.sleep(0.45)
        self.assertEqual(self.state("#{pane_width}x#{pane_height}"), before)
        self.assertNotIn("fresh-output", self.capture(copy=True))
        self.assertEqual(self.tmux("display-message", "-p", "-t", right, "#{pane_in_mode}").strip(), "0")


if __name__ == "__main__":
    unittest.main()
