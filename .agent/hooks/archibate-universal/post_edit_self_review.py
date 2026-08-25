#!/usr/bin/env python3
"""Inject a post-edit code and documentation self-review checklist."""

from __future__ import annotations

import json
import re
import sys


DOC_EXTS = {".md", ".markdown", ".rst", ".txt", ".adoc", ".org", ".tex"}
CODE_EXTS = {
    ".py",
    ".pyi",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".go",
    ".rs",
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hpp",
    ".java",
    ".kt",
    ".scala",
    ".rb",
    ".php",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".lua",
    ".vim",
    ".el",
    ".clj",
    ".ex",
    ".exs",
    ".swift",
    ".m",
    ".mm",
    ".r",
    ".sql",
    ".html",
    ".htm",
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".vue",
    ".svelte",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".cmake",
    ".dockerfile",
}
CODE_NAMES = {
    "cmakelists.txt",
    "dockerfile",
    "makefile",
    "justfile",
    "pipfile",
    "gemfile",
    "rakefile",
    ".gitignore",
    ".dockerignore",
}


def classify(path: str) -> str:
    name = path.rsplit("/", 1)[-1].lower()
    if name in CODE_NAMES:
        return "CODE"
    dot = "." + name.rsplit(".", 1)[-1] if "." in name else ""
    if dot in DOC_EXTS:
        return "DOC"
    if dot in CODE_EXTS:
        return "CODE"
    if name.startswith(".env"):
        return "CODE"
    return "OTHER"


def extract_files_from_patch(patch: str) -> list[str]:
    files = []
    for match in re.finditer(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", patch, re.MULTILINE):
        path = match.group(1).strip()
        if path not in files:
            files.append(path)
    return files


def build_context(files: list[str]) -> str | None:
    docs = [p for p in files if classify(p) == "DOC"]
    code = [p for p in files if classify(p) == "CODE"]
    if not docs and not code:
        return None

    parts = ["Re-read edited regions before continuing; silently fix high-confidence issues."]
    if code:
        parts.append(
            "CODE files: "
            + ", ".join(code[:8])
            + ". Check contradictions, comment mismatch, style drift, debug leftovers, over-defensive code, band-aids, misplaced helpers, duplicated logic, and missing docs/tests/config updates."
        )
    if docs:
        parts.append(
            "DOC files: "
            + ", ".join(docs[:8])
            + ". Check contradictions, stale references, over-explanation, defensive caveats, incident residue, audience mismatch, tonal/list drift, and patch-over-restructure."
        )
    return "\n".join(parts)


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return

    tool_name = event.get("tool_name", "")
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return

    files: list[str] = []

    if tool_name == "apply_patch":
        patch = tool_input.get("command")
        if isinstance(patch, str):
            files = extract_files_from_patch(patch)
    elif tool_name in ("Edit", "Write"):
        file_path = tool_input.get("file_path")
        if isinstance(file_path, str) and file_path:
            files = [file_path]

    if not files:
        return

    context = build_context(files)
    if not context:
        return

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": context,
                }
            }
        )
    )


if __name__ == "__main__":
    main()