#!/usr/bin/env python3

"""Refresh resized copy-mode panes after the layout has settled."""

import shlex
import subprocess
import sys

from copy_mode_word import cells_from_capture


PENDING_OPTION = "@copy_refresh_pending"
GENERATION_OPTION = "@copy_resize_generation"
PANE_FORMAT = (
    "#{pane_id}\t#{pane_mode}\t#{pane_width}x#{pane_height}\t"
    "#{@copy_refresh_pending}\t#{copy_cursor_x}\t#{copy_cursor_y}\t"
    "#{scroll_position}\t#{pane_height}"
)


def page_top(old: list[str], new: list[str], top: int, fallback: int) -> int:
    # A short context disambiguates repeated lines without diffing all history.
    start, end = max(0, top - 1), min(len(old), top + 2)
    context = old[start:end]
    matches = [
        i + top - start for i in range(len(new) - len(context) + 1)
        if context and new[i:i + len(context)] == context
    ]
    return min(matches, key=lambda i: abs(i - top)) if matches else fallback


def run(socket: str, window: str, generation: str) -> None:
    def tmux(*args: str) -> str:
        return subprocess.check_output(
            ["tmux", "-S", socket, *args], text=True, stderr=subprocess.PIPE,
        )

    # The window may have been closed while the delayed job was waiting.
    windows = tmux("list-windows", "-a", "-F", "#{window_id}\t#{@copy_resize_generation}").splitlines()
    if f"{window}\t{generation}" not in windows:
        return

    for entry in tmux("list-panes", "-t", window, "-F", PANE_FORMAT).splitlines():
        pane, mode, size, pending, x, y, scroll, height = entry.split("\t")
        if mode != "copy-mode" or pending != "1":
            continue
        old = tmux("capture-pane", "-p", "-M", "-S", "-", "-E", "-", "-t", pane).splitlines()
        new = tmux("capture-pane", "-p", "-S", "-", "-E", "-", "-t", pane).splitlines()
        history = max(0, len(new) - int(height))
        top = len(old) - int(height) - int(scroll)
        target = page_top(old, new, top, history - int(scroll))
        target = max(0, min(history, target))

        # Do not undo a resize, cursor move, or copy-mode re-entry that happened
        # while capturing. Refresh never exits copy mode or switches panes.
        guard = (
            f"#{{&&:#{{==:#{{{GENERATION_OPTION}}},{generation}}},"
            f"#{{==:{PANE_FORMAT},{entry}}}}}"
        )
        # tmux 3.6a keeps the old offset when replacing the backing grid. If
        # history shrank, refresh itself can index a negative row and crash the
        # server, before we can restore the page. Zero is valid in both grids.
        offset = f"#{{e|-:#{{history_size}},{target}}}"
        offset = f"#{{?#{{e|<:#{{history_size}},{target}}},0,{offset}}}"
        commands = [
            ["send-keys", "-t", pane, "-X", "goto-line", "0"],
            ["send-keys", "-t", pane, "-X", "refresh-from-pane"],
            # History may grow or shrink after capture; clamp at execution time.
            ["run-shell", "-C", "-t", pane, f"send-keys -t {pane} -X goto-line {offset}"],
            ["display-message", "-p", "refreshed"],
        ]
        if tmux("if-shell", "-F", "-t", pane, guard, " ; ".join(map(shlex.join, commands))).strip() != "refreshed":
            continue

        current = tmux("display-message", "-p", "-t", pane, PANE_FORMAT).rstrip("\n")
        _, mode, current_size, pending, cx, cy, scroll, _ = current.split("\t")
        if mode != "copy-mode" or pending != "1" or current_size != size:
            continue
        commands = []
        if cy == y and cx != x:
            # Refresh can clamp x on a shorter line before goto-line restores
            # the page. Restore by character steps, not terminal-cell counts.
            row = str(int(cy) - int(scroll))
            text = tmux("capture-pane", "-p", "-M", "-S", row, "-E", row, "-t", pane)
            cells, _ = cells_from_capture(text, text)
            desired = max(i for i, cell in enumerate(cells) if cell.x <= int(x))
            actual = max(i for i, cell in enumerate(cells) if cell.x <= int(cx))
            if desired != actual:
                commands.append(["send-keys", "-t", pane, "-X", "-N", str(abs(desired - actual)),
                                 "cursor-right" if desired > actual else "cursor-left"])
        commands.append(["set-option", "-p", "-t", pane, PENDING_OPTION, "0"])
        guard = (
            f"#{{&&:#{{==:#{{{GENERATION_OPTION}}},{generation}}},"
            f"#{{==:{PANE_FORMAT},{current}}}}}"
        )
        tmux("if-shell", "-F", "-t", pane, guard, " ; ".join(map(shlex.join, commands)))


if __name__ == "__main__":
    try:
        run(*sys.argv[1:])
    except subprocess.CalledProcessError as error:
        # Closing the window/server during this background job is normal.
        if not error.stderr.startswith(("can't find pane:", "can't find window:", "no server running on")):
            sys.stderr.write(error.stderr)
            raise SystemExit(error.returncode)
