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


class RowAnchorTests(unittest.TestCase):
    def test_appended_output_does_not_move_anchor(self):
        old = [str(i) for i in range(20)]
        self.assertEqual(refresh.find_row(old, old + ["new"], 5), 5)

    def test_trimmed_history(self):
        old = [str(i) for i in range(20)]
        self.assertEqual(refresh.find_row(old, old[3:] + ["new"], 5), 2)

    def test_context_disambiguates_repeated_lines(self):
        old = ["a", "same", "b", "c", "same", "d"]
        self.assertEqual(refresh.find_row(old, old[3:], 4), 1)

    def test_replaced_or_ambiguous_content_is_not_guessed(self):
        self.assertIsNone(refresh.find_row(["old"], ["new"], 0))
        self.assertIsNone(refresh.find_row(["same"] * 50, ["same"] * 60, 25))

    def test_neighbours_can_change_around_a_unique_cursor_line(self):
        self.assertEqual(refresh.find_row(["a", "cursor", "b"], ["c", "cursor", "d"], 1), 1)


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
        self.program = program
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

    def cursor_anchor(self):
        physical = self.tmux("capture-pane", "-p", "-M", "-N", "-T", "-S", "-", "-E", "-", "-t", self.pane)
        joined = self.tmux("capture-pane", "-p", "-M", "-J", "-S", "-", "-E", "-", "-t", self.pane)
        cells, starts = refresh.cells_from_capture(physical, joined)
        x, y, scroll, height = map(int, self.state("#{copy_cursor_x} #{copy_cursor_y} #{scroll_position} #{pane_height}").split())
        row = physical.count("\n") - height - scroll + y
        first = next(i for i, cell in enumerate(cells) if cell.y == starts[row])
        last = next(i for i in range(first, len(cells)) if cells[i].text == "\n")
        cursor = max(i for i, cell in enumerate(cells) if (cell.y, cell.x) <= (row, x))
        return "".join(cell.text for cell in cells[first:last]), "".join(cell.text for cell in cells[first:cursor])

    def test_refresh_keeps_pre_resize_page_and_cursor_without_exiting_mode(self):
        self.tmux("set-hook", "-p", "-t", self.pane, "pane-mode-changed[92]", "set-option -p @unexpected_mode_change yes")
        page = self.page()
        cursor = self.state("#{copy_cursor_x},#{copy_cursor_y}")
        self.resize()
        self.fresh_output()
        self.assertNotIn("fresh-output", self.capture(copy=True))
        self.wait_refreshed()
        self.assertIn("fresh-output", self.capture(copy=True))
        self.assertEqual(self.page(), page)
        self.assertEqual(self.state("#{copy_cursor_x},#{copy_cursor_y}"), cursor)
        self.assertEqual(self.state("#{pane_mode}"), "copy-mode")
        self.assertEqual(self.state("#{@unexpected_mode_change}"), "")

    def test_wrapped_resize_round_trips_keep_original_character_and_screen_row(self):
        # The cursor must cross onto a continuation row in the narrower pane.
        self.tmux("send-keys", "-t", self.pane, "-X", "-N", "7", "cursor-right")
        page = self.page()
        anchor = self.cursor_anchor()
        y = self.state("#{copy_cursor_y}")
        for width in [17, 40, 17, 40]:
            with self.subTest(width=width):
                self.tmux("resize-pane", "-t", self.pane, "-x", str(width))
                self.wait_refreshed()
                self.assertEqual(self.cursor_anchor(), anchor)
                self.assertEqual(self.state("#{copy_cursor_y}"), y)
        self.assertEqual(self.page(), page)

    def test_history_cleared_while_scrolled_does_not_crash_server(self):
        cursor = self.state("#{copy_cursor_x},#{copy_cursor_y},#{scroll_position}")
        self.resize()
        frozen = self.capture(copy=True)
        self.assertGreater(int(self.state("#{scroll_position}")), 0)
        os.kill(int(self.state("#{pane_pid}")), signal.SIGUSR2)
        self.wait_for(lambda: self.state("#{history_size}") == "0")
        self.assertEqual(self.state("#{pane_mode}"), "copy-mode")
        self.wait_refreshed()
        self.assertEqual(self.state("#{pane_mode}"), "copy-mode")
        self.assertEqual(self.capture(copy=True), frozen)
        self.assertEqual(self.state("#{copy_cursor_x},#{copy_cursor_y},#{scroll_position}"), cursor)

    def test_history_shrink_after_capture_does_not_crash_server(self):
        # Invoke the worker directly so the race is deterministic, not timed.
        self.tmux("set-hook", "-gu", "window-layout-changed[91]")
        try:
            self.tmux("set-option", "-p", "-t", self.pane, "@copy_refresh_pending", "1")
            frozen = self.capture(copy=True)
            cursor = self.state("#{copy_cursor_x},#{copy_cursor_y},#{scroll_position}")
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
            self.assertEqual(self.state("#{pane_mode} #{@copy_refresh_pending}"), "copy-mode 0")
            self.assertEqual(self.capture(copy=True), frozen)
            self.assertEqual(self.state("#{copy_cursor_x},#{copy_cursor_y},#{scroll_position}"), cursor)
        finally:
            self.tmux("source-file", str(self.root / ".tmux.conf"))

    def test_height_round_trip_restores_screen_row_even_after_clipping(self):
        self.tmux("send-keys", "-t", self.pane, "-X", "-N", "10", "cursor-down")
        anchor = self.cursor_anchor()
        y = int(self.state("#{copy_cursor_y}"))
        height = self.state("#{window_height}")
        self.assertGreater(y, 8)
        for target in ["8", height, "8", height]:
            with self.subTest(height=target):
                self.tmux("resize-window", "-t", self.window, "-y", target)
                self.wait_refreshed()
                self.assertEqual(self.cursor_anchor(), anchor)
                self.assertEqual(int(self.state("#{copy_cursor_y}")), min(y, int(self.state("#{pane_height}")) - 1))

    def test_terminal_resize_is_covered(self):
        self.tmux("resize-window", "-t", self.window, "-x", "100", "-y", "20")
        self.fresh_output()
        self.wait_refreshed()
        self.assertIn("fresh-output", self.capture(copy=True))

    def prepare_three_copy_panes(self):
        primary = self.pane
        right = self.tmux("list-panes", "-t", self.window, "-f", "#{pane_at_right}", "-F", "#{pane_id}").strip()
        # These are processes in this test's isolated server, not user panes.
        self.tmux("respawn-pane", "-k", "-t", right, sys.executable, "-c", self.program)
        third = self.tmux("split-window", "-d", "-v", "-t", right, "-P", "-F", "#{pane_id}", sys.executable, "-c", self.program).strip()
        panes = [primary, right, third]
        expected = {}
        try:
            for i, pane in enumerate(panes):
                self.pane = pane
                self.wait_for(lambda: "row-059" in self.capture())
                self.tmux("copy-mode", "-t", pane)
                self.tmux("send-keys", "-t", pane, "-X", "goto-line", "20")
                self.tmux("send-keys", "-t", pane, "-X", "top-line")
                self.tmux("send-keys", "-t", pane, "-X", "-N", str(i + 2), "cursor-down")
                expected[pane] = (self.cursor_anchor(), self.state("#{copy_cursor_y}"))
        finally:
            self.pane = primary
        time.sleep(0.4)
        return panes, expected

    def test_all_resized_copy_panes_refresh_without_switching_focus(self):
        panes, expected = self.prepare_three_copy_panes()
        primary = self.pane
        try:
            for active in panes:
                before = dict(line.split() for line in self.tmux(
                    "list-panes", "-t", self.window, "-F", "#{pane_id} #{pane_width}x#{pane_height}",
                ).splitlines())
                subprocess.run(
                    [str(self.root / ".config/tmux/layout-three-panes"), active, "3"],
                    env=dict(os.environ, TMUX=self.socket_path + ",0,0"), check=True,
                )
                for pane in panes:
                    self.pane = pane
                    self.fresh_output()
                for pane in panes:
                    self.pane = pane
                    self.wait_refreshed()
                    self.assertEqual((self.cursor_anchor(), self.state("#{copy_cursor_y}")), expected[pane], pane)
                    self.assertEqual(self.state("#{pane_active}"), "1" if pane == active else "0")
                    if self.state("#{pane_width}x#{pane_height}") != before[pane]:
                        self.assertEqual(self.capture(copy=True).count("fresh-output"), self.capture().count("fresh-output"), pane)
        finally:
            self.pane = primary

    def test_inactive_stale_pane_restores_viewport_without_replacing_snapshot(self):
        panes, expected = self.prepare_three_copy_panes()
        primary, stale, _ = panes
        try:
            self.pane = stale
            os.kill(int(self.state("#{pane_pid}")), signal.SIGUSR2)
            self.wait_for(lambda: self.state("#{history_size}") == "0")
            subprocess.run(
                [str(self.root / ".config/tmux/layout-three-panes"), primary, "3"],
                env=dict(os.environ, TMUX=self.socket_path + ",0,0"), check=True,
            )
            for pane in panes:
                self.pane = pane
                self.fresh_output()
            for pane in panes:
                self.pane = pane
                self.wait_refreshed()
                self.assertEqual((self.cursor_anchor(), self.state("#{copy_cursor_y}")), expected[pane], pane)
                self.assertEqual(self.state("#{pane_active}"), "1" if pane == primary else "0")
                if pane == stale:
                    self.assertNotIn("fresh-output", self.capture(copy=True))
                else:
                    self.assertIn("fresh-output", self.capture(copy=True))
        finally:
            self.pane = primary

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

    def test_real_prefix_space_restores_all_panes_when_focus_changes(self):
        panes, _ = self.prepare_three_copy_panes()
        primary = self.pane
        self.tmux("select-window", "-t", self.window)
        client = subprocess.Popen(
            ["tmux", "-L", self.socket, "-C", "attach-session", "-t", "refresh"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            self.wait_for(lambda: self.tmux("list-clients", "-F", "#{client_name}").strip())
            name = self.tmux("list-clients", "-F", "#{client_name}").strip()
            time.sleep(0.4)  # Attaching can itself resize the window.
            expected = {}
            for i, pane in enumerate(panes):
                self.pane = pane
                self.tmux("send-keys", "-t", pane, "-X", "top-line")
                self.tmux("send-keys", "-t", pane, "-X", "-N", str(i + 2), "cursor-down")
                expected[pane] = (self.cursor_anchor(), self.state("#{copy_cursor_y}"))
            for active in panes + [primary]:
                self.pane = active
                self.tmux("select-pane", "-t", active)
                size = self.state("#{pane_width}x#{pane_height}")
                self.tmux("send-keys", "-c", name, "-K", "C-s", "Space")
                self.wait_for(lambda: self.state("#{pane_width}x#{pane_height}") != size)
                for pane in panes:
                    self.pane = pane
                    self.wait_refreshed()
                    self.assertEqual((self.cursor_anchor(), self.state("#{copy_cursor_y}")), expected[pane], pane)
                    self.assertEqual(self.state("#{pane_active}"), "1" if pane == active else "0")
        finally:
            self.pane = primary
            client.communicate(timeout=5)

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

    def test_user_motion_during_debounce_cancels_restoration(self):
        self.resize()
        self.tmux("send-keys", "-t", self.pane, "-X", "cursor-down")
        cursor = self.state("#{copy_cursor_x},#{copy_cursor_y},#{scroll_position}")
        self.fresh_output()
        time.sleep(0.45)
        self.assertEqual(self.state("#{copy_cursor_x},#{copy_cursor_y},#{scroll_position}"), cursor)
        self.assertNotIn("fresh-output", self.capture(copy=True))

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
