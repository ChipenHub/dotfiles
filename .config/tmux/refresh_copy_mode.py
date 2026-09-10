#!/usr/bin/env python3

"""Refresh resized copy-mode panes without losing the cursor's content anchor."""

import shlex
import subprocess
import sys

from copy_mode_word import cells_from_capture


PENDING_OPTION = "@copy_refresh_pending"
GENERATION_OPTION = "@copy_resize_generation"
PANE_FORMAT = (
    "#{pane_id}\t#{pane_mode}\t#{pane_width}x#{pane_height}\t"
    "#{@copy_refresh_pending}\t#{copy_cursor_x}\t#{copy_cursor_y}\t"
    "#{scroll_position}\t#{pane_height}\t#{@copy_refresh_y}\t#{@copy_refresh_running}"
)


def find_row(old: list[str], new: list[str], row: int) -> int | None:
    """Locate the cursor line unambiguously; never guess by its old row number."""
    if not 0 <= row < len(old):
        return None
    for radius in (1, 3, 10, 0):
        start, end = max(0, row - radius), min(len(old), row + radius + 1)
        context = old[start:end]
        matches = [
            i + row - start for i in range(len(new) - len(context) + 1)
            if new[i:i + len(context)] == context
        ]
        if len(matches) == 1:
            return matches[0]
    return None


def run(socket: str, window: str, generation: str) -> None:
    def tmux(*args: str) -> str:
        return subprocess.check_output(
            ["tmux", "-S", socket, *args], text=True, stderr=subprocess.PIPE,
        )

    def guarded(entry: str, commands: list[list[str]], extra: str = "1") -> str:
        pane = entry.split("\t", 1)[0]
        guard = (
            f"#{{&&:#{{==:#{{{GENERATION_OPTION}}},{generation}}},"
            f"#{{&&:#{{==:{PANE_FORMAT},{entry}}},{extra}}}}}"
        )
        return tmux("if-shell", "-F", "-t", pane, guard, " ; ".join(map(shlex.join, commands)))

    # The window may have been closed while the delayed job was waiting.
    windows = tmux("list-windows", "-a", "-F", "#{window_id}\t#{@copy_resize_generation}").splitlines()
    if f"{window}\t{generation}" not in windows:
        return

    for entry in tmux("list-panes", "-t", window, "-F", PANE_FORMAT).splitlines():
        pane, mode, size, pending, x, y, scroll, height, saved_y, _ = entry.split("\t")
        if mode != "copy-mode" or pending != "1":
            continue
        clear_pending = ["set-option", "-p", "-t", pane, PENDING_OPTION, "0"]
        old = tmux("capture-pane", "-p", "-M", "-S", "-", "-E", "-", "-t", pane).splitlines()
        new = tmux("capture-pane", "-p", "-S", "-", "-E", "-", "-t", pane).splitlines()
        live_history = max(0, len(new) - int(height))
        frozen_history = max(0, len(old) - int(height))
        cursor = frozen_history - int(scroll) + int(y)
        target_row = find_row(old, new, cursor)
        # Updating live content is optional; restoring the resized viewport is
        # not. Old inactive panes often have anchors absent from the live grid.
        attempts = []
        if target_row is not None:
            attempts.append((target_row, live_history, True))
        attempts.append((cursor, frozen_history, False))
        for target_row, history, replace_grid in attempts:
            # tmux reflows the cursor's content position but can move it to row
            # zero. Keep the screen row chosen before resizing, even on fallback.
            wanted_y = min(int(saved_y or y), int(height) - 1)
            top = max(0, min(history, target_row - wanted_y))
            wanted_y = target_row - top
            commands = [["set-option", "-p", "-t", pane, "@copy_refresh_running", generation]]
            if replace_grid:
                offset = f"#{{e|-:#{{history_size}},{top}}}"
                offset = f"#{{?#{{e|<:#{{history_size}},{top}}},0,{offset}}}"
                commands.extend([
                    # tmux 3.6a can crash refreshing a shrunken grid with a stale offset.
                    ["send-keys", "-t", pane, "-X", "goto-line", "0"],
                    ["send-keys", "-t", pane, "-X", "refresh-from-pane"],
                    ["run-shell", "-C", "-t", pane, f"send-keys -t {pane} -X goto-line {offset}"],
                ])
            else:
                # history_size describes the live grid, not this frozen snapshot.
                commands.append(["send-keys", "-t", pane, "-X", "goto-line", str(history - top)])
            commands.append(["send-keys", "-t", pane, "-X", "-N", "1", "top-line"])
            if wanted_y:
                commands.append(["send-keys", "-t", pane, "-X", "-N", str(wanted_y), "cursor-down"])
            commands.append(["display-message", "-p", "restored"])
            extra = f"#{{==:#{{history_size}},{history}}}" if replace_grid else "1"
            if guarded(entry, commands, extra).strip() == "restored":
                break
        else:
            # Both attempts remain conditional on this pane's unchanged input
            # state and layout generation, so user navigation still wins.
            continue

        try:
            current = tmux("display-message", "-p", "-t", pane, PANE_FORMAT).rstrip("\n")
            _, mode, current_size, pending, cx, cy, scroll, _, _, running = current.split("\t")
            if mode != "copy-mode" or pending != "1" or current_size != size or running != generation:
                continue
            commands = []
            if int(cy) == wanted_y and cx != x:
                # Page restoration can clamp x on an intermediate shorter line.
                # Move by characters, not cells, so Chinese/combining text works.
                row = str(int(cy) - int(scroll))
                text = tmux("capture-pane", "-p", "-M", "-S", row, "-E", row, "-t", pane)
                cells, _ = cells_from_capture(text, text)
                desired = max(i for i, cell in enumerate(cells) if cell.x <= int(x))
                actual = max(i for i, cell in enumerate(cells) if cell.x <= int(cx))
                if desired != actual:
                    commands.append(["send-keys", "-t", pane, "-X", "-N", str(abs(desired - actual)),
                                     "cursor-right" if desired > actual else "cursor-left"])
            commands.append(clear_pending)
            guarded(current, commands)
        finally:
            tmux("if-shell", "-F", "-t", pane,
                 f"#{{==:#{{@copy_refresh_running}},{generation}}}",
                 f"set-option -p -t {pane} @copy_refresh_running 0")


if __name__ == "__main__":
    try:
        run(*sys.argv[1:])
    except subprocess.CalledProcessError as error:
        # Closing the window/server during this background job is normal.
        if not error.stderr.startswith(("can't find pane:", "can't find window:", "no server running on")):
            sys.stderr.write(error.stderr)
            raise SystemExit(error.returncode)
