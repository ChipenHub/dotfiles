#!/usr/bin/env python3
"""Re-enter resized copy-mode panes, preserving their current history row."""

import shlex
import subprocess
import sys

from copy_mode_word import cells_from_capture

PANE_FORMAT = (
    "#{pane_id}\t#{pane_mode}\t#{pane_width}x#{pane_height}\t"
    "#{copy_cursor_x}\t#{copy_cursor_y}\t#{scroll_position}\t#{E:@copy_refresh_pending}"
)


def run(socket: str, window: str, generation: str) -> None:
    def tmux(*args: str) -> str:
        return subprocess.check_output(
            ["tmux", "-S", socket, *args], text=True, stderr=subprocess.PIPE,
        )

    def guarded(state: str, commands: list[list[str]]) -> str:
        pane = state.split("\t", 1)[0]
        condition = (
            f"#{{&&:#{{==:#{{E:@copy_resize_generation}},{generation}}},"
            f"#{{==:{PANE_FORMAT},{state}}}}}"
        )
        return tmux("if-shell", "-F", "-t", pane, condition, " ; ".join(map(shlex.join, commands)))

    windows = tmux("list-windows", "-a", "-F", "#{window_id}\t#{E:@copy_resize_generation}").splitlines()
    if f"{window}\t{generation}" not in windows:
        return
    for state in tmux("list-panes", "-t", window, "-F", PANE_FORMAT).splitlines():
        pane, mode, size, x, y, scroll, pending = state.split("\t")
        if pending != "1":
            continue
        clear = ["set-environment", "-gh", "COPY_REFRESH_PENDING_" + pane[1:], "0"]
        if mode != "copy-mode":
            guarded(state, [clear])
            continue
        # scroll_position is relative to the frozen history's bottom, not a
        # row number. Count its rows so appended output cannot move the page.
        height = int(size.split("x")[1])
        rows = tmux("capture-pane", "-p", "-M", "-S", "-", "-E", "-", "-t", pane).count("\n")
        top = max(0, rows - height - int(scroll))
        offset = f"#{{e|-:#{{history_size}},{top}}}"
        offset = f"#{{?#{{e|<:#{{history_size}},{top}}},0,{offset}}}"
        commands = [
            ["send-keys", "-t", pane, "-X", "cancel"],
            ["copy-mode", "-t", pane],
            # Expand after re-entry, using the history size of the new snapshot.
            ["run-shell", "-C", "-t", pane, f"send-keys -t {pane} -X goto-line {offset}"],
            ["send-keys", "-t", pane, "-X", "top-line"],
        ]
        if int(y):
            commands.append(["send-keys", "-t", pane, "-X", "-N", y, "cursor-down"])
        commands.extend([
            ["send-keys", "-t", pane, "-X", "start-of-line"],
            ["display-message", "-p", "restored"],
        ])
        if guarded(state, commands).strip() != "restored":
            continue

        current = tmux("display-message", "-p", "-t", pane, PANE_FORMAT).rstrip("\n")
        _, mode, current_size, _, cy, offset, _ = current.split("\t")
        if mode != "copy-mode" or current_size != size:
            continue
        # Native cursor-right counts characters, not terminal cells. Read only
        # the destination line to restore x correctly for tabs and wide text.
        row = str(int(cy) - int(offset))
        text = tmux("capture-pane", "-p", "-M", "-S", row, "-E", row, "-t", pane)
        cells, _ = cells_from_capture(text, text)
        steps = max((i for i, cell in enumerate(cells) if cell.x <= int(x)), default=0)
        commands = []
        if steps:
            commands.append(["send-keys", "-t", pane, "-X", "-N", str(steps), "cursor-right"])
        commands.append(clear)
        guarded(current, commands)


if __name__ == "__main__":
    try:
        run(*sys.argv[1:])
    except subprocess.CalledProcessError as error:
        # A pane or window can disappear while the delayed job is running.
        if not error.stderr.startswith(("can't find pane:", "can't find window:", "no server running on")):
            sys.stderr.write(error.stderr)
            raise SystemExit(error.returncode)
