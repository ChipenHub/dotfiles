"""Regression tests for pane opening, lock handoff, and fish job recovery."""

import os
from pathlib import Path
import runpy
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import Mock, patch


ENTER = runpy.run_path(Path(__file__).resolve().parents[1] / "copy-mode-enter")
open_in_pane = ENTER["open_in_pane"]
run_editor = ENTER["run_editor"]


class LauncherTests(unittest.TestCase):
    def test_foreground_nvim_is_reused_without_acquiring_a_lock(self):
        tmux = Mock(return_value="100\t/dev/tty-test\t1\t/server")
        claim = Mock()
        opener = Mock(return_value=True)
        with (
            patch.dict(open_in_pane.__globals__, {
                "tmux": tmux,
                "processes": Mock(return_value={200: (100, 200, 200, "S", "nvim")}),
                "replace_owner": claim,
            }),
            patch.dict(ENTER["OPEN_PATH"], {"open_in_nvim": opener}),
            patch.object(subprocess, "run", return_value=Mock(returncode=0, stdout="200\n")),
        ):
            open_in_pane("%1", "/socket", "client", Path("/tmp/file.txt"), 12, 3, 15)
        opener.assert_called_once_with("%1", "/server", Path("/tmp/file.txt"), 12, 3, 15)
        claim.assert_not_called()
        tmux.assert_called_with("/socket", "send-keys", "-t", "%1", "-X", "cancel")

    def test_start_failure_restores_registration_and_releases_owned_lock(self):
        release = Mock()
        with (
            tempfile.TemporaryDirectory(prefix="tmux-launcher-test-") as directory,
            patch.dict(os.environ, {"TMUX_PANE": "%1"}),
            patch.dict(run_editor.__globals__, {
                "replace_owner": Mock(return_value=True),
                "release_owner": release,
                "tmux": Mock(return_value="/original-server"),
                "message": Mock(),
            }),
            patch.object(subprocess, "run", side_effect=[FileNotFoundError(), Mock(returncode=0)]) as run,
        ):
            marker = Path(directory) / "editor"
            self.assertEqual(run_editor(str(marker), "/socket", "client", "123:request", "missing-editor"), 1)
            self.assertEqual(marker.read_text(), f"{os.getpid()}:request")
        release.assert_called_once_with("/socket", "%1", f"{os.getpid()}:request")
        self.assertEqual(run.call_args.args[0], [
            "tmux", "-S", "/socket", "set-option", "-p", "-t", "%1", "@nvim_server", "/original-server",
        ])

    def test_expired_request_does_not_launch_or_clear_another_lock(self):
        with (
            patch.dict(os.environ, {"TMUX_PANE": "%1"}),
            patch.dict(run_editor.__globals__, {
                "replace_owner": Mock(return_value=False),
                "release_owner": Mock(),
                "message": Mock(),
            }),
            patch.object(subprocess, "run") as run,
        ):
            self.assertEqual(run_editor("/unused", "/socket", "client", "123:request", "nvim"), 1)
            run.assert_not_called()
            run_editor.__globals__["release_owner"].assert_not_called()


@unittest.skipUnless(shutil.which("tmux") and shutil.which("fish"), "tmux and fish are required")
class PaneOpeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix="tmux-pane-open-test-")
        cls.socket = str(Path(cls.directory.name) / "socket")
        cls.tmux("-f", "/dev/null", "new-session", "-d", "-s", "test", "sleep 3600")

    @classmethod
    def tearDownClass(cls):
        cls.tmux("kill-server")  # Only the isolated server created above.
        cls.directory.cleanup()

    @classmethod
    def tmux(cls, *args):
        return subprocess.check_output(["tmux", "-S", cls.socket, *args], text=True).strip()

    def setUp(self):
        self.work = tempfile.TemporaryDirectory(dir=self.directory.name)
        self.ready = Path(self.work.name) / "editor-pid"
        self.pane = self.tmux("new-window", "-d", "-P", "-F", "#{pane_id}",
                              shutil.which("fish"), "--no-config", "--interactive")
        self.shell_pid = int(self.tmux("display-message", "-p", "-t", self.pane, "#{pane_pid}"))
        self.tty = self.tmux("display-message", "-p", "-t", self.pane, "#{pane_tty}")
        self.wait_for(lambda: ENTER["foreground"](self.tty, self.shell_pid) == self.shell_pid)
        self.environment = patch.dict(os.environ, {"TMUX": f"{self.socket},0,0"})
        self.environment.start()
        self.program = [sys.executable, "-c", (
            "import os,signal,sys,time; from pathlib import Path; "
            "signal.signal(signal.SIGUSR1, lambda *_: sys.exit(0)); "
            f"Path({str(self.ready)!r}).write_text(str(os.getpid())); time.sleep(60)"
        )]

    def tearDown(self):
        # Killing this test's pane terminates only its fish and foreground job.
        self.tmux("kill-pane", "-t", self.pane)
        self.environment.stop()
        self.work.cleanup()

    def wait_for(self, predicate):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(0.02)
        self.fail("timed out waiting for pane state")

    def owner(self):
        return self.tmux("show-options", "-pqv", "-t", self.pane, "@open_path_in_pane")

    def open(self, program=None):
        with patch.dict(ENTER["OPEN_PATH"], {"nvim_command": Mock(return_value=program or self.program)}):
            open_in_pane(self.pane, self.socket, "test-client", Path("/tmp/file.txt"), None, None, None)

    def finish_editor(self):
        self.wait_for(lambda: self.ready.exists() and self.ready.read_text().isdigit())
        os.kill(int(self.ready.read_text()), signal.SIGUSR1)
        self.wait_for(lambda: not self.owner())

    def test_controller_returns_while_editor_runs_and_launcher_releases_lock(self):
        self.tmux("copy-mode", "-t", self.pane)
        self.open()
        owner = self.owner()
        launcher = int(owner.split(":", 1)[0])
        self.assertNotEqual(launcher, os.getpid())
        os.kill(launcher, 0)
        self.assertEqual(self.tmux("display-message", "-p", "-t", self.pane, "#{pane_in_mode}"), "0")
        # Controller cleanup must not remove the launcher's transferred lock.
        ENTER["release_owner"](self.socket, self.pane, f"{os.getpid()}:{owner.split(':', 1)[1]}")
        self.assertEqual(self.owner(), owner)
        self.finish_editor()

    def test_dead_owner_is_reclaimed(self):
        process = subprocess.Popen([sys.executable, "-c", "pass"])
        process.wait(timeout=5)
        self.tmux("set-option", "-p", "-t", self.pane, "@open_path_in_pane", str(process.pid))
        self.open()
        self.assertNotEqual(self.owner(), str(process.pid))
        self.finish_editor()

    def test_live_owner_is_not_stolen(self):
        owner = f"{os.getpid()}:live"
        self.tmux("set-option", "-p", "-t", self.pane, "@open_path_in_pane", owner)
        with self.assertRaisesRegex(ENTER["CannotOpen"], "already being opened"):
            self.open()
        self.assertEqual(self.owner(), owner)
        self.assertFalse(self.ready.exists())

    def test_compare_and_replace_rejects_a_changed_owner(self):
        self.tmux("set-option", "-p", "-t", self.pane, "@open_path_in_pane", "123:new")
        self.assertFalse(ENTER["replace_owner"](self.socket, self.pane, "123:old", "456:replacement"))
        ENTER["release_owner"](self.socket, self.pane, "123:old")
        self.assertEqual(self.owner(), "123:new")

    def test_killed_launcher_does_not_leave_permanent_busy_state(self):
        self.open()
        self.wait_for(lambda: self.ready.exists() and self.ready.read_text().isdigit())
        owner = self.owner()
        os.kill(int(owner.split(":", 1)[0]), signal.SIGKILL)
        os.kill(int(self.ready.read_text()), signal.SIGUSR1)
        self.wait_for(lambda: ENTER["foreground"](self.tty, self.shell_pid) == self.shell_pid)
        self.assertEqual(self.owner(), owner)  # SIGKILL cannot run finally.
        self.ready.unlink()
        self.open()
        self.assertNotEqual(self.owner(), owner)
        self.finish_editor()

    def test_failed_editor_start_clears_lock(self):
        self.open([str(Path(self.work.name) / "missing-editor")])
        self.wait_for(lambda: not self.owner())
        self.wait_for(lambda: ENTER["foreground"](self.tty, self.shell_pid) == self.shell_pid)

    def start_job(self):
        ready = Path(self.work.name) / "job-pid"
        command = shlex.join([sys.executable, "-c", (
            "import os,time; from pathlib import Path; "
            f"Path({str(ready)!r}).write_text(str(os.getpid())); time.sleep(60)"
        )])
        ENTER["send_command"](self.socket, self.pane, command)
        self.wait_for(lambda: ready.exists() and ready.read_text().isdigit())
        return int(ready.read_text())

    def test_start_timeout_recovers_suspended_job_and_releases_lock(self):
        job = self.start_job()
        send_command = ENTER["send_command"]

        def skip_launch(socket, pane, command):
            if command.startswith("builtin fg "):
                send_command(socket, pane, command)

        try:
            with patch.dict(open_in_pane.__globals__, {"send_command": skip_launch}):
                with self.assertRaisesRegex(ENTER["CannotOpen"], "did not start Neovim"):
                    self.open()
            self.assertEqual(self.owner(), "")
            self.wait_for(lambda: ENTER["foreground"](self.tty, self.shell_pid) == job)
        finally:
            os.kill(job, signal.SIGTERM)

    def test_foreground_job_resumes_after_editor_exits_or_fails_to_start(self):
        for fail_start in (False, True):
            with self.subTest(fail_start=fail_start):
                job = self.start_job()
                try:
                    self.open([str(Path(self.work.name) / "missing-editor")] if fail_start else None)
                    if not fail_start:
                        self.assertIn("T", ENTER["processes"](self.tty)[job][3])
                        self.finish_editor()
                    self.wait_for(lambda: not self.owner())
                    self.wait_for(lambda: ENTER["foreground"](self.tty, self.shell_pid) == job)
                    self.assertNotIn("T", ENTER["processes"](self.tty)[job][3])
                finally:
                    os.kill(job, signal.SIGTERM)
                    self.wait_for(lambda: ENTER["foreground"](self.tty, self.shell_pid) == self.shell_pid)
                    (Path(self.work.name) / "job-pid").unlink()


if __name__ == "__main__":
    unittest.main()
