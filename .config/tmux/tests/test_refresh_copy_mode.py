"""Isolated-server tests for 300ms resize debounce and numeric restoration."""

import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import refresh_copy_mode as refresh


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
        cls.tmux("kill-server")  # Only this class's unique server.
        cls.home.cleanup()

    @classmethod
    def tmux(cls, *args):
        return subprocess.check_output(["tmux", "-L", cls.socket, *args], text=True)

    def setUp(self):
        self.program = (
            "import os,signal,time; "
            "signal.signal(signal.SIGUSR1, lambda *_: os.write(1, b'fresh-output\\r\\n')); "
            "signal.signal(signal.SIGUSR2, lambda *_: os.write(1, b'\\x1b[3J')); "
            "os.write(1, ''.join(f'row-{i:03d} 中文 contents\\r\\n' for i in range(60)).encode()); "
            "time.sleep(3600)"
        )
        self.pane = self.tmux("new-window", "-d", "-P", "-F", "#{pane_id}", sys.executable, "-c", self.program).strip()
        self.window = self.state("#{window_id}")
        self.wait_for(lambda: "row-059" in self.capture())
        self.other = self.tmux("split-window", "-d", "-h", "-t", self.pane, "-P", "-F", "#{pane_id}",
                               sys.executable, "-c", self.program).strip()
        self.wait_for(lambda: "row-059" in self.capture(pane=self.other))
        self.tmux("copy-mode", "-t", self.pane)
        self.tmux("send-keys", "-t", self.pane, "-X", "goto-line", "20")
        self.tmux("send-keys", "-t", self.pane, "-X", "top-line")
        self.tmux("send-keys", "-t", self.pane, "-X", "-N", "3", "cursor-down")
        self.tmux("send-keys", "-t", self.pane, "-X", "-N", "10", "cursor-right")
        time.sleep(0.4)
        self.wait_refreshed(self.pane)

    def tearDown(self):
        self.tmux("kill-window", "-t", self.window)

    def state(self, fmt, pane=None):
        return self.tmux("display-message", "-p", "-t", pane or self.pane, fmt).strip()

    def capture(self, copy=False, pane=None):
        return self.tmux("capture-pane", "-p", *(["-M"] if copy else []), "-S", "-", "-E", "-", "-t", pane or self.pane)

    def wait_for(self, predicate):
        for _ in range(200):
            if predicate():
                return
            time.sleep(0.01)
        self.fail("timed out waiting for tmux")

    def wait_refreshed(self, pane):
        self.wait_for(lambda: self.state("#{E:@copy_refresh_pending}", pane) == "0")

    def position(self, pane=None):
        return self.state("#{copy_cursor_x},#{copy_cursor_y},#{scroll_position}", pane)

    def watch_mode_changes(self, pane):
        name = "TEST_MODES_" + pane[1:]
        self.tmux("set-environment", "-gh", name, "0")
        command = ["set-environment", "-ghF", name, f"#{{e|+:#{{{name}}},1}}"]
        self.tmux("set-hook", "-p", "-t", pane, "pane-mode-changed[92]", shlex.join(command))

    def mode_changes(self, pane):
        return self.state("#{TEST_MODES_" + pane[1:] + "}", pane)

    def test_reenters_and_restores_position_recorded_after_resize(self):
        self.watch_mode_changes(self.pane)
        self.tmux("resize-pane", "-t", self.pane, "-R", "1")
        # This is deliberately the post-resize position, not the old text anchor.
        self.tmux("send-keys", "-t", self.pane, "-X", "cursor-down")
        x, y, scroll = map(int, self.position().split(","))
        frozen = self.capture(copy=True).splitlines()
        height = int(self.state("#{pane_height}"))
        top = len(frozen) - height - scroll
        page = frozen[top:top + height]
        os.kill(int(self.state("#{pane_pid}")), signal.SIGUSR1)
        self.wait_for(lambda: "fresh-output" in self.capture())
        self.assertNotIn("fresh-output", self.capture(copy=True))
        self.wait_refreshed(self.pane)
        self.assertEqual(self.mode_changes(self.pane), "2")
        current = self.capture(copy=True).splitlines()
        new_x, new_y, new_scroll = map(int, self.position().split(","))
        new_top = len(current) - height - new_scroll
        self.assertEqual((new_x, new_y), (x, y))
        self.assertEqual(new_top, top)
        self.assertEqual(current[new_top:new_top + height], page)
        self.assertEqual(self.capture(copy=True), self.capture())

    def test_history_shrink_still_replaces_snapshot(self):
        self.tmux("resize-pane", "-t", self.pane, "-R", "1")
        os.kill(int(self.state("#{pane_pid}")), signal.SIGUSR2)
        self.wait_for(lambda: self.state("#{history_size}") == "0")
        self.wait_refreshed(self.pane)
        self.assertEqual(self.state("#{pane_mode}"), "copy-mode")
        self.assertEqual(self.state("#{scroll_position}"), "0")
        self.assertEqual(self.capture(copy=True), self.capture())

    def test_burst_is_debounced_for_300ms(self):
        self.watch_mode_changes(self.pane)
        for _ in range(6):
            self.tmux("resize-pane", "-t", self.pane, "-R", "1")
            time.sleep(0.05)
            self.assertEqual(self.mode_changes(self.pane), "0")
        time.sleep(0.15)
        self.assertEqual(self.mode_changes(self.pane), "0")
        self.wait_refreshed(self.pane)
        self.assertEqual(self.mode_changes(self.pane), "2")

    def test_round_trip_size_is_not_missed(self):
        self.watch_mode_changes(self.pane)
        self.tmux("resize-pane", "-t", self.pane, "-R", "1")
        self.tmux("resize-pane", "-t", self.pane, "-L", "1")
        self.wait_refreshed(self.pane)
        self.assertEqual(self.mode_changes(self.pane), "2")

    def test_actual_prefix_space_refreshes_inactive_panes_too(self):
        third = self.tmux("split-window", "-d", "-v", "-t", self.other, "-P", "-F", "#{pane_id}",
                          sys.executable, "-c", self.program).strip()
        self.wait_for(lambda: "row-059" in self.capture(pane=third))
        panes = [self.pane, self.other, third]
        for pane in panes[1:]:
            self.tmux("copy-mode", "-t", pane)
        self.tmux("select-window", "-t", self.window)
        client = subprocess.Popen(["tmux", "-L", self.socket, "-C", "attach-session", "-t", "refresh"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            self.wait_for(lambda: self.tmux("list-clients", "-F", "#{client_name}").strip())
            name = self.tmux("list-clients", "-F", "#{client_name}").strip()
            time.sleep(0.4)
            for active in panes:
                for pane in panes:
                    self.watch_mode_changes(pane)
                self.tmux("select-pane", "-t", active)
                before = {p: self.state("#{pane_width}x#{pane_height}", p) for p in panes}
                self.tmux("send-keys", "-c", name, "-K", "C-s", "Space")
                self.wait_for(lambda: any(self.state("#{pane_width}x#{pane_height}", p) != before[p] for p in panes))
                for pane in panes:
                    self.wait_refreshed(pane)
                    changed = self.state("#{pane_width}x#{pane_height}", pane) != before[pane]
                    self.assertEqual(self.mode_changes(pane), "2" if changed else "0")
                    self.assertEqual(self.state("#{pane_active}", pane), "1" if pane == active else "0")
        finally:
            client.communicate(timeout=5)

    def test_unchanged_copy_pane_and_normal_panes_are_not_reentered(self):
        self.tmux("split-window", "-d", "-v", "-t", self.other, "sleep 3600")
        time.sleep(0.4)
        self.watch_mode_changes(self.pane)
        self.watch_mode_changes(self.other)
        self.tmux("resize-pane", "-t", self.other, "-D", "1")
        self.wait_refreshed(self.other)
        self.assertEqual(self.mode_changes(self.pane), "0")
        self.assertEqual(self.mode_changes(self.other), "0")
        self.assertEqual(self.state("#{pane_mode}", self.other), "")

    def test_terminal_resize_refreshes_both_copy_panes(self):
        self.tmux("copy-mode", "-t", self.other)
        for pane in [self.pane, self.other]:
            self.watch_mode_changes(pane)
        self.tmux("resize-window", "-t", self.window, "-x", "90", "-y", "20")
        for pane in [self.pane, self.other]:
            self.wait_refreshed(pane)
            self.assertEqual(self.mode_changes(pane), "2")

    def test_exited_copy_mode_stays_exited(self):
        self.tmux("resize-pane", "-t", self.pane, "-R", "1")
        self.tmux("send-keys", "-t", self.pane, "-X", "cancel")
        self.wait_refreshed(self.pane)
        self.assertEqual(self.state("#{pane_mode}"), "")

    def test_stale_worker_does_nothing(self):
        generation = self.state("#{E:@copy_resize_generation}")
        self.watch_mode_changes(self.pane)
        self.tmux("resize-pane", "-t", self.pane, "-R", "1")
        refresh.run(self.socket_path, self.window, generation)
        self.assertEqual(self.mode_changes(self.pane), "0")
        self.wait_refreshed(self.pane)

    def test_resize_tracking_does_not_write_options(self):
        pane_options = self.tmux("show-options", "-p", "-t", self.pane)
        window_options = self.tmux("show-options", "-w", "-t", self.window)
        self.tmux("resize-pane", "-t", self.pane, "-R", "1")
        self.wait_refreshed(self.pane)
        self.assertEqual(self.tmux("show-options", "-p", "-t", self.pane), pane_options)
        self.assertEqual(self.tmux("show-options", "-w", "-t", self.window), window_options)

    def test_drag_starts_only_one_worker_after_quiet(self):
        with tempfile.TemporaryDirectory(prefix="tmux-worker-spy-") as directory:
            trace = Path(directory) / "starts"
            launcher = Path(directory) / "python3"
            launcher.write_text('#!/bin/sh\nprintf "started\\n" >> "$REFRESH_TRACE"\n'
                                f'exec {shlex.quote(sys.executable)} "$@"\n')
            launcher.chmod(0o755)
            self.tmux("set-environment", "-t", "refresh", "PATH", directory + os.pathsep + os.environ["PATH"])
            self.tmux("set-environment", "-t", "refresh", "REFRESH_TRACE", str(trace))
            try:
                for _ in range(10):
                    self.tmux("resize-pane", "-t", self.pane, "-R", "1")
                    time.sleep(0.05)
                self.assertFalse(trace.exists())
                self.wait_refreshed(self.pane)
                self.assertEqual(trace.read_text().splitlines(), ["started"])
            finally:
                self.tmux("set-environment", "-t", "refresh", "PATH", os.environ["PATH"])
                self.tmux("set-environment", "-u", "-t", "refresh", "REFRESH_TRACE")


if __name__ == "__main__":
    unittest.main()
