#!/usr/bin/env python3
"""Remind Codex to prefer uv for Python script execution."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    if event.get("tool_name") != "Bash":
        return
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return
    command = tool_input.get("command")
    if not isinstance(command, str) or not command:
        return
    if os.environ.get("VIRTUAL_ENV") or os.environ.get("CONDA_PREFIX"):
        return
    if not shutil.which("uv"):
        return
    if re.search(r"\buv\s+run\b", command):
        return
    if not re.search(r"(?m)(^|[;&|()])\s*python3?\s+", command):
        return
    if re.search(r"\bpython3?\s+(-V|--version|--help|-c\b)", command):
        return
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": "Prefer `uv run python` instead of bare `python` or `python3` outside an active virtual environment.",
                }
            }
        )
    )


if __name__ == "__main__":
    main()
