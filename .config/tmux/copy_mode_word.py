#!/usr/bin/env python3

"""Unicode-aware Vim word motions and path text objects for tmux copy mode."""

from __future__ import annotations

import subprocess
import sys
import unicodedata
from bisect import bisect_left, bisect_right
from dataclasses import dataclass


PAIRS = {
    "double-quote": ('"', '"'),
    "single-quote": ("'", "'"),
    "backtick": ("`", "`"),
    "paren": ("(", ")"),
    "bracket": ("[", "]"),
    "brace": ("{", "}"),
    "angle": ("<", ">"),
}


@dataclass
class Cell:
    text: str
    x: int
    y: int
    column: int  # Number of cursor-right commands from this physical row's start.


def character_kind(char: str, path: bool = False) -> str:
    if char == "\n":
        return "newline"
    if char.isspace():
        return "space"
    name = unicodedata.name(char, "")
    category = unicodedata.category(char)
    if (name.startswith(("CJK UNIFIED IDEOGRAPH", "CJK COMPATIBILITY IDEOGRAPH"))
            or char == "〇"
            or (ord(char) > 127 and category.startswith("P"))
            or (category.startswith("S") and unicodedata.east_asian_width(char) in "WF")):
        return "single"
    if path or char.isalnum() or category.startswith("M"):
        return "word"
    return "symbol"


def cells_from_capture(
    physical: str, joined: str, cursor_row: int | None = None,
) -> tuple[list[Cell], list[int]]:
    """Map the frozen copy grid to characters, preserving soft wraps and spaces."""
    rows = physical.removesuffix("\n").split("\n")
    line_starts = []
    line_ends = []
    offset = logical_start = 0
    for y, row in enumerate(rows):
        line_starts.append(logical_start)
        if not joined.startswith(row, offset):
            raise ValueError("copy grid changed while reading")
        offset += len(row)
        line_ends.append(joined[offset:offset + 1] == "\n")
        if line_ends[-1]:
            offset += 1
            logical_start = y + 1

    first, last = 0, len(rows) - 1
    if cursor_row is not None:
        # Only tokenize the current logical line and its nearest nonblank
        # neighbours; a large scrollback should not slow down every keystroke.
        first = max(0, line_starts[cursor_row] - 1)
        while first > 0 and not rows[first].strip():
            first -= 1
        first = line_starts[first]
        last = cursor_row
        while last < len(rows) - 1 and not line_ends[last]:
            last += 1
        if last < len(rows) - 1:
            last += 1
        while last < len(rows) - 1 and (not rows[last].strip() or not line_ends[last]):
            last += 1

    cells = []
    for y in range(first, last + 1):
        x = column = 0
        for char in rows[y]:
            if unicodedata.category(char) in {"Mn", "Me", "Cf"} and cells and cells[-1].y == y:
                cells[-1].text += char
                continue
            cells.append(Cell(char, x, y, column))
            x += 2 if unicodedata.east_asian_width(char) in "WF" else 1
            column += 1
        if line_ends[y]:
            cells.append(Cell("\n", x, y, column))
    return cells, line_starts


def word_spans(cells: list[Cell], path: bool = False) -> list[tuple[int, int, str]]:
    spans = []
    for index, cell in enumerate(cells):
        kind = character_kind(cell.text[0], path)
        if spans and kind == spans[-1][2] and kind not in {"single", "newline"}:
            start, _, _ = spans[-1]
            spans[-1] = (start, index + 1, kind)
        else:
            spans.append((index, index + 1, kind))
    return spans


def word_target(cells: list[Cell], cursor: int, action: str, count: int = 1) -> tuple[int, int]:
    """Return inclusive selection bounds, or a single motion destination."""
    spans = word_spans(cells, action in {"ip", "path-end"})
    current = next(i for i, (start, end, _) in enumerate(spans) if start <= cursor < end)
    start, end, kind = spans[current]
    if action in {"b", "e", "w", "path-end"}:
        candidates = []
        for left, right, word_kind in spans:
            if word_kind in {"space", "newline"}:
                # Like Vim, w/b stop on empty lines, while e skips them.
                if not (action in {"b", "w"} and word_kind == "newline"
                        and (left == 0 or cells[left - 1].text == "\n")):
                    continue
            candidates.append(right - 1 if action in {"e", "path-end"} else left)
        if action == "b":
            before = bisect_left(candidates, cursor)
            target = candidates[max(0, before - count)] if before else 0
        else:
            after = bisect_right(candidates, cursor)
            target = candidates[min(len(candidates) - 1, after + count - 1)] if candidates else cursor
            target = max(cursor, target)
        return target, target

    if action == "aw":
        if kind in {"space", "newline"}:
            following = current + 1
            while following < len(spans) and spans[following][2] in {"space", "newline"}:
                following += 1
            if following < len(spans):
                end = spans[following][1]
        elif current + 1 < len(spans) and spans[current + 1][2] == "space":
            end = spans[current + 1][1]
        elif current > 1 and spans[current - 1][2] == "space" and spans[current - 2][2] != "newline":
            # Vim does not pull indentation into the first word on a line.
            start = spans[current - 1][0]
    return start, end - 1


def pair_target(cells: list[Cell], cursor: int, action: str) -> tuple[int, int] | None:
    """Find a quoted string or the innermost matching block around the cursor."""
    opening, closing = PAIRS[action[2:]]
    line_start = cursor
    while line_start > 0 and cells[line_start - 1].text != "\n":
        line_start -= 1
    line_end = cursor
    while line_end < len(cells) and cells[line_end].text != "\n":
        line_end += 1

    stack = []
    matches = []
    quotes = []
    escaped = False
    scan = range(line_start, line_end) if opening == closing else range(len(cells))
    for index in scan:
        char = cells[index].text
        if not escaped:
            if opening == closing and char == opening:
                quotes.append(index)
            elif char == opening:
                stack.append(index)
            elif char == closing and stack:
                matches.append((stack.pop(), index))
        escaped = char == "\\" and not escaped

    if opening == closing:
        position = bisect_left(quotes, cursor)
        if position < len(quotes) and quotes[position] == cursor:
            position -= position % 2
        else:
            position = max(0, position - 1)
        if position + 1 >= len(quotes):
            return None
        left, right = quotes[position:position + 2]
    else:
        enclosing = [(left, right) for left, right in matches if left <= cursor <= right]
        if enclosing:
            left, right = max(enclosing)
        else:
            following = [(left, right) for left, right in matches if cursor < left < line_end]
            if not following:
                return None
            left, right = min(following)

    if action.startswith("a-"):
        if opening == closing:
            # Vim's a-quote includes adjacent whitespace, unlike a-bracket.
            end = right
            while right + 1 < line_end and cells[right + 1].text.isspace():
                right += 1
            if right == end:
                while left > line_start and cells[left - 1].text.isspace():
                    left -= 1
        return left, right

    left += 1
    right -= 1
    if opening != closing:
        if left <= right and cells[left].text == "\n":
            left += 1
        # Do not include indentation belonging solely to the closing delimiter.
        end = right
        while end >= left and cells[end].text.isspace() and cells[end].text != "\n":
            end -= 1
        if end >= left and cells[end].text == "\n":
            right = end
    return left, right  # left > right is an empty inner object, not a delimiter.


def run(pane: str, action: str) -> None:
    def tmux(*args: str) -> str:
        return subprocess.check_output(["tmux", *args], text=True)

    state = tmux("display-message", "-p", "-t", pane,
                 "#{pane_in_mode} #{copy_cursor_x} #{copy_cursor_y} #{scroll_position} #{pane_height} #{selection_present} "
                 "#{?@copy_word_count,#{@copy_word_count},1} #{rectangle_toggle}").split()
    if len(state) != 8 or state[0] != "1":
        return
    _, x, y, scroll, height, selected, count, rectangle = map(int, state)
    pair = action[:2] in {"i-", "a-"} and action[2:] in PAIRS
    # -M reads copy mode's frozen backing grid, not the still-running pane.
    physical = tmux("capture-pane", "-p", "-M", "-N", "-T", "-S", "-", "-E", "-", "-t", pane)
    joined = tmux("capture-pane", "-p", "-M", "-J", "-S", "-", "-E", "-", "-t", pane)
    y += physical.count("\n") - height - scroll
    cells, line_starts = cells_from_capture(physical, joined, y if count == 1 and not pair else None)
    if not cells:
        return
    cursor = next((i for i, cell in reversed(list(enumerate(cells))) if (cell.y, cell.x) <= (y, x)), 0)
    if action == "extend-path":
        action = "path-end" if selected else "ip"
    target = pair_target(cells, cursor, action) if pair else word_target(cells, cursor, action, count)
    if target is None:
        tmux("send-keys", "-t", pane, "-N", "1")
        return
    start, end = target
    if start > end:
        tmux("send-keys", "-t", pane, "-X", "clear-selection")
        return
    commands: list[str] = []

    def send(command: str, *args: str, count: int = 1) -> None:
        if commands:
            commands.append(";")
        commands.extend(["send-keys", "-t", pane, "-X", "-N", str(count), command, *args])

    def move(index: int) -> None:
        nonlocal y
        cell = cells[index]
        send("start-of-line")
        y = line_starts[y]
        if cell.y != y:
            send("cursor-down" if cell.y > y else "cursor-up", count=abs(cell.y - y))
        if cell.column:
            send("cursor-right", count=cell.column)
        y = cell.y

    if pair or action in {"iw", "aw", "ip"}:
        send("clear-selection")
        move(start)
        send("begin-selection")
        send("selection-mode", "char")
        move(end)
        if rectangle:
            if cells[end].x < cells[start].x:
                send("other-end")
            # A rectangular right edge includes both cells of a wide glyph.
            send("cursor-right")
            send("cursor-left")
    else:
        send("selection-mode", "char")
        move(end)
    tmux(*commands)


if __name__ == "__main__":
    actions = {"b", "e", "w", "iw", "aw", "ip", "extend-path"}
    actions.update(prefix + name for prefix in ("i-", "a-") for name in PAIRS)
    if len(sys.argv) != 3 or sys.argv[2] not in actions:
        raise SystemExit(2)
    run(sys.argv[1], sys.argv[2])
