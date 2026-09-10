#!/usr/bin/env python3
"""Block risky Bash and Git commands before Codex runs them."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path


def load_event() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def command_text(event: dict) -> str:
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command")
    return command if isinstance(command, str) else ""


def has(marker: str, command: str) -> bool:
    return marker in command


def emit_deny(marker: str, reason: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"{reason}\n\n"
                f"If legitimate or false-positive, add `# {marker}` to the command."
            ),
        }
    }
    print(json.dumps(payload))
    raise SystemExit(0)


def emit_context(context: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": context,
                }
            }
        )
    )
    raise SystemExit(0)


def cmd_re(name: str) -> str:
    return rf"(?m)(^|[;&|()]|\bthen\b|\belse\b|\bdo\b)\s*(sudo\s+(?:-\S+\s+)*)?{name}\b"


def grep(pattern: str, command: str, flags: int = 0) -> bool:
    return re.search(pattern, command, flags) is not None


def blocks_dangerous_ops(command: str) -> None:
    fastpath = re.compile(
        r"\b(mkfs|parted|fdisk|gdisk|sgdisk|cfdisk|wipefs|cryptsetup|shred|srm|wipe|"
        r"shutdown|reboot|poweroff|halt|init|telinit|systemctl|chmod|chown|docker|"
        r"iptables|ip6tables|nft|ufw|crontab|killall|kill|tee|cp|mv|install|dd)\b|"
        r"/dev/|/etc/|/proc/|/sys/|/boot/|>"
    )
    if not fastpath.search(command):
        return

    if (
        grep(cmd_re(r"(mkfs(\.[A-Za-z0-9]+)?|parted|fdisk|gdisk|sgdisk|cfdisk|wipefs)"), command)
        and "--dry-run" not in command
        and not has("BYPASS_DISK_FORMAT_CHECK", command)
    ):
        emit_deny(
            "BYPASS_DISK_FORMAT_CHECK",
            "Do not run disk-format or partition-edit tools without a dry run and explicit target verification.",
        )

    if (
        grep(cmd_re("cryptsetup") + r"[^|;&]*\b(luksFormat|erase|reencrypt)\b", command)
        and "--dry-run" not in command
        and not has("BYPASS_DISK_FORMAT_CHECK", command)
    ):
        emit_deny(
            "BYPASS_DISK_FORMAT_CHECK",
            "Do not run destructive cryptsetup operations without header backup and explicit device verification.",
        )

    safe_dev = r"(?!(null|zero|random|urandom|full|console|stderr|stdout|stdin|ptmx)(?![/.\w])|tty\w*(?![/.\w])|fd/\w+(?![/.\w])|pts/\w+(?![/.\w]))"
    if (
        grep(rf"\bof=/dev/{safe_dev}\S", command)
        or grep(rf">>?\s*/dev/{safe_dev}\S", command)
        or grep(rf"\btee\b[^|;&]*\s/dev/{safe_dev}\S", command)
        or grep(rf"\b(cp|mv|install)\b[^|;&]*\s/dev/{safe_dev}\S+\s*($|[|;&])", command)
    ) and not has("BYPASS_BLOCKDEV_WRITE_CHECK", command):
        emit_deny(
            "BYPASS_BLOCKDEV_WRITE_CHECK",
            "Do not write to a /dev device path; one wrong target can overwrite a live disk.",
        )

    sys_path = r"(/etc|/proc|/sys|/boot)/"
    if (
        grep(rf"\bof={sys_path}\S", command)
        or grep(rf">>?\s*{sys_path}\S", command)
        or grep(rf"\btee\b[^|;&]*\s{sys_path}\S", command)
        or grep(rf"\b(cp|mv|install)\b[^|;&]*\s{sys_path}\S+\s*($|[|;&])", command)
    ) and not has("BYPASS_SYSPATH_WRITE_CHECK", command):
        emit_deny(
            "BYPASS_SYSPATH_WRITE_CHECK",
            "Do not write directly to /etc, /proc, /sys, or /boot from a shell command.",
        )

    if (
        grep(cmd_re(r"(shred|srm|wipe)") + r"(\s|$|[;&|])", command)
        and not has("BYPASS_SECURE_DELETE_CHECK", command)
    ):
        emit_deny(
            "BYPASS_SECURE_DELETE_CHECK",
            "Do not use secure-delete tools unless the user explicitly requested irreversible erasure.",
        )

    power_patterns = [
        cmd_re(r"(shutdown|reboot|poweroff|halt)"),
        cmd_re(r"(tel)?init") + r"\s+[016]\b",
        cmd_re("systemctl") + r"\s+(poweroff|reboot|halt|kexec|hibernate|suspend)\b",
        cmd_re("kill") + r"\s+(-9|-KILL|-SIGKILL)\s+-?1\b",
    ]
    if any(grep(p, command) for p in power_patterns) and not has("BYPASS_POWER_STATE_CHECK", command):
        emit_deny(
            "BYPASS_POWER_STATE_CHECK",
            "Do not change host power state or kill init from Codex.",
        )

    if (
        grep(cmd_re(r"(chmod|chown)") + r"[^|;&]*\s-[A-Za-z]*R[A-Za-z]*\b", command)
        and not has("BYPASS_RECURSIVE_PERMS_CHECK", command)
    ):
        emit_deny(
            "BYPASS_RECURSIVE_PERMS_CHECK",
            "Do not run recursive chmod/chown without a tightly verified target.",
        )

    if (
        grep(cmd_re("docker") + r"\s+(system|volume|image|container|network)\s+prune\b", command)
        and not has("BYPASS_DOCKER_PRUNE_CHECK", command)
    ):
        emit_deny(
            "BYPASS_DOCKER_PRUNE_CHECK",
            "Do not run broad docker prune commands; list and remove specific resources.",
        )

    firewall = [
        cmd_re(r"ip6?tables") + r"[^|;&]*\s(-[A-Za-z]*[FX][A-Za-z]*\b|--flush\b|--delete-chain\b)",
        cmd_re("nft") + r"\s+flush\s+ruleset\b",
        cmd_re("ufw") + r"\s+(--force\s+)?reset\b",
    ]
    if any(grep(p, command) for p in firewall) and not has("BYPASS_FIREWALL_WIPE_CHECK", command):
        emit_deny(
            "BYPASS_FIREWALL_WIPE_CHECK",
            "Do not flush firewall rules from Codex; this can lock out remote access.",
        )

    if (
        grep(cmd_re("crontab") + r"[^|;&]*\s(-[A-Za-z]*r[A-Za-z]*|--remove)\b", command)
        and not has("BYPASS_CRONTAB_REMOVE_CHECK", command)
    ):
        emit_deny(
            "BYPASS_CRONTAB_REMOVE_CHECK",
            "Do not run crontab -r; back up and edit specific entries instead.",
        )

    if grep(cmd_re("killall"), command) and not has("BYPASS_KILLALL_CHECK", command):
        emit_deny(
            "BYPASS_KILLALL_CHECK",
            "Do not use killall; select specific PIDs after inspection.",
        )


def blocks_destructive_git(command: str) -> None:
    if not re.search(r"\bgit\b", command):
        return
    checks = [
        (cmd_re("git") + r"\s+reset\b[^|;&]*\s--hard\b", "BYPASS_RESET_HARD_CHECK", "Do not use git reset --hard; it discards working-tree and index changes."),
        (cmd_re("git") + r"\s+clean\b[^|;&]*\s-[A-Za-z]*f[A-Za-z]*\b", "BYPASS_GIT_CLEAN_CHECK", "Do not use git clean -f; it deletes untracked files that may be user work."),
        (cmd_re("git") + r"\s+branch\b[^|;&]*\s-D\b", "BYPASS_BRANCH_DELETE_CHECK", "Do not use git branch -D; it force-deletes branches with unmerged commits."),
        (cmd_re("git") + r"\s+checkout\b[^|;&]*(\s--(\s|$)|\s\.(\s|$))", "BYPASS_CHECKOUT_DISCARD_CHECK", "Do not use git checkout -- or git checkout .; these discard working-tree changes."),
        (cmd_re("git") + r"\s+commit\b[^|;&]*--amend\b", "BYPASS_AMEND_CHECK", "Do not use git commit --amend; create a new commit instead."),
        (cmd_re("git") + r"\s+push\b[^|;&]*(\s--force(-with-lease|-if-includes)?\b|\s-[A-Za-z]*f\b)", "BYPASS_FORCE_PUSH_CHECK", "Do not force-push from Codex unless explicitly requested."),
        (cmd_re("git") + r"\s+push\b[^|;&]*(\s--delete\b|\s-[A-Za-z]*d\b|\s:[\w./-]+)", "BYPASS_PUSH_DELETE_CHECK", "Do not delete remote branches from Codex unless explicitly requested."),
    ]
    for pattern, marker, reason in checks:
        if grep(pattern, command) and not has(marker, command):
            emit_deny(marker, reason)

    if (
        grep(cmd_re("git") + r"\s+restore\b", command)
        and not grep(r"git\s+restore\b[^|;&]*\s(--staged|-S)\b", command)
        and not has("BYPASS_RESTORE_CHECK", command)
    ):
        emit_deny("BYPASS_RESTORE_CHECK", "Do not use git restore <path> without --staged; it discards working-tree changes.")

    if (
        grep(cmd_re("git") + r"\s+rm\b[^|;&]*\s(-[A-Za-z]*f[A-Za-z]*|--force)\b", command)
        and not grep(r"git\s+rm\b[^|;&]*\s--cached\b", command)
        and not has("BYPASS_GIT_RM_FORCE_CHECK", command)
    ):
        emit_deny("BYPASS_GIT_RM_FORCE_CHECK", "Do not use git rm -f; it overrides Git's safety check for uncommitted modifications.")


def blocks_shell_habits(command: str) -> None:
    if grep(r">\s*/dev/null\b", command) and not has("BYPASS_DEVNULL_CHECK", command):
        emit_deny("BYPASS_DEVNULL_CHECK", "Do not redirect output to /dev/null; keep output visible to Codex.")

    if (
        grep(r"(?m)(^|[;&|()])\s*cat\b.*<<", command)
        and grep(r"(?m)(^|[;&|()])\s*cat\b.*(>\s*\S|>>\s*\S|\|\s*tee\b)", command)
        and not grep(r"\bgit\s+commit\b", command)
        and not has("BYPASS_CAT_WRITE", command)
    ):
        emit_deny("BYPASS_CAT_WRITE", "Use apply_patch or Codex file-edit tools instead of cat heredoc for file writes.")

    if grep(r"(?m)[^&]&\s*$", command) and not has("BYPASS_BACKGROUND_CHECK", command):
        emit_deny("BYPASS_BACKGROUND_CHECK", "Do not background shell commands with trailing &; use a managed session/background mechanism.")

    if heredoc_or_inline_too_large(command) and not (
        has("BYPASS_HEREDOC_RESTRICTION", command) or has("BYPASS_INLINE_SCRIPT_RESTRICTION", command)
    ):
        emit_deny(
            "BYPASS_HEREDOC_RESTRICTION",
            "Large inline scripts or heredocs are hard to audit; create a script file and run it.",
        )

    if (
        "CONDA_PREFIX" not in os.environ
        and shutil.which("uv")
        and grep(cmd_re(r"pip3?") + r"(\s|$)", command)
        and not has("BYPASS_PACKAGE_MANAGER_CHECK", command)
    ):
        emit_deny(
            "BYPASS_PACKAGE_MANAGER_CHECK",
            "Use uv instead of pip: `uv add`, `uv pip install`, or `uv pip freeze`.",
        )

    if (
        shutil.which("pnpm")
        and grep(cmd_re("npm") + r"(\s|$)", command)
        and not has("BYPASS_PACKAGE_MANAGER_CHECK", command)
    ):
        emit_deny(
            "BYPASS_PACKAGE_MANAGER_CHECK",
            "Use pnpm instead of npm when pnpm is available.",
        )


def heredoc_or_inline_too_large(command: str, max_lines: int = 80) -> bool:
    if "<<<<" in command:
        return False
    if "<<" in command:
        lines = command.splitlines()
        for idx, line in enumerate(lines):
            match = re.search(r"<<[-'\"]?\s*([A-Za-z_][A-Za-z0-9_]*)", line)
            if not match:
                continue
            marker = match.group(1)
            count = 0
            for body_line in lines[idx + 1 :]:
                if body_line.strip() == marker:
                    break
                count += 1
            if count > max_lines and not re.search(r"\bgit\s+commit\b", command):
                return True

    for match in re.finditer(r"-c\s+(['\"])(.*?)\1", command, re.DOTALL):
        if match.group(2).count("\n") + 1 > max_lines:
            return True
    return False


def maybe_warn_head_tail(command: str, event: dict) -> None:
    if not grep(r"(?m)(^|[^|])\|\s*(head|tail)\b[^|]*$", command):
        return
    session_id = str(event.get("session_id") or "unknown")
    stamp_dir = Path(tempfile.gettempdir()) / f"codex-{os.getuid()}-state" / "archibate-head-tail"
    stamp_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    stamp = stamp_dir / session_id
    if stamp.exists():
        return
    stamp.write_text("1")
    emit_context(
        "Trailing `| head` or `| tail` can discard useful output before Codex sees it. "
        "Prefer a producer-native limit such as `rg -m N`, `git log -n N`, or the tool's own limit flag."
    )


def main() -> None:
    event = load_event()
    if event.get("tool_name") != "Bash":
        return
    command = command_text(event)
    if not command:
        return
    blocks_dangerous_ops(command)
    blocks_destructive_git(command)
    blocks_shell_habits(command)
    maybe_warn_head_tail(command, event)


if __name__ == "__main__":
    main()
