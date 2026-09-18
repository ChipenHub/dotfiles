#!/usr/bin/env python3

"""Run a prompted command and keep quick results visible in a tmux pane."""

from __future__ import annotations

import os
import subprocess
import sys
import termios
import time
import tty


QUICK_COMMAND_SECONDS = 3.0


def wait_for_key(returncode: int, elapsed: float) -> None:
    status = "finished" if returncode == 0 else f"exited {returncode}"
    print(
        f"\n[{status} in {elapsed:.1f}s — press any key to close]",
        end="",
        flush=True,
    )

    fd = sys.stdin.fileno()
    attributes = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        os.read(fd, 1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, attributes)
        print()


def main() -> int:
    if len(sys.argv) != 2:
        return 2

    started = time.monotonic()
    try:
        result = subprocess.run(
            [os.environ.get("SHELL", "/bin/sh"), "-c", sys.argv[1]],
            check=False,
        )
    except KeyboardInterrupt:
        return 130

    elapsed = time.monotonic() - started
    if elapsed < QUICK_COMMAND_SECONDS and sys.stdin.isatty():
        wait_for_key(result.returncode, elapsed)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
