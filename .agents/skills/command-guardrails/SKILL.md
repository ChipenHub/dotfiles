---
name: command-guardrails
description: Use before risky or destructive shell or Git operations, shell file writes, output suppression, or package-manager choices, and after substantive edits for safety review. Skip read-only inspection.
---

# Command Guardrails

## Overview

Apply these rules as a behavior layer and as the policy behind the installed Codex hooks in `~/.codex/hooks/archibate-universal`. The active scripts are `block_risky_bash.py`, `remind_uv_python.py`, and `post_edit_self_review.py`. The hook scripts enforce only the mechanical cases; the skill covers the judgment calls around them.

## Scope

Included:

- Dangerous shell targets and system commands.
- Destructive Git operations.
- Shell file writes that should be file edits.
- Output suppression and needless truncation.
- Package-manager preferences.
- Post-edit code/doc review checklists.

Excluded by user request:

- Browser automation, web scraping, Bilibili, media, image/model rendering, external API helpers, and long-task/background-task orchestration.

## Command Rules

Prefer a command that preserves information and is easy to inspect later.

- Do not redirect stdout/stderr to `/dev/null`; output noise is cheaper than blindness.
- Avoid trailing `| head` or `| tail` on expensive or non-idempotent commands. Prefer the producer's semantic limit, such as `rg -m`, `git log -n`, or a tool-native limit.
- Do not end shell commands with `&`. Use the runtime's session/background mechanism when backgrounding is truly needed.
- Do not write source files with `cat <<EOF > file`. Use Codex file-edit tools, usually `apply_patch`.
- For long inline scripts or heredocs, create a temporary script file and run it, instead of burying 80+ lines inside one shell command.
- Use `uv` instead of `pip` when `uv` is available and no active conda environment requires pip.
- Use `pnpm` instead of `npm` when `pnpm` is available.
- Prefer `uv run python` over bare `python` or `python3` outside an active virtual environment.

## Destructive Operations

Treat these as blocked unless the user explicitly asked for the exact action and the target has been verified:

- Disk format and partition tools: `mkfs`, `parted`, `fdisk`, `gdisk`, `sgdisk`, `cfdisk`, `wipefs`, and destructive `cryptsetup` operations.
- Writes to device/system paths: `/dev/<device>`, `/etc`, `/proc`, `/sys`, and `/boot`.
- Secure deletion: `shred`, `srm`, and `wipe`.
- Host power state: `shutdown`, `reboot`, `poweroff`, `halt`, `init 0/1/6`, `systemctl reboot`, and equivalent commands.
- Recursive permission or owner changes: `chmod -R` and `chown -R`.
- Broad cleanup: `docker * prune`, firewall flush/reset, `crontab -r`, and `killall`.

## Git Rules

Do not discard work or rewrite shared history silently.

- Block `git reset --hard`, `git clean -f`, `git checkout --`, `git checkout .`, `git restore <path>` without `--staged`, `git branch -D`, and `git rm -f` unless bypassed with a deliberate reason.
- Block `git commit --amend`, force-push, and remote branch deletion. Create a new commit instead of amending unless the user explicitly asked for history rewrite.
- Before any destructive Git bypass, inspect `git status --short` and confirm whether untracked or modified files belong to the user.

## Bypass Discipline

The installed hooks accept explicit bypass markers such as `BYPASS_RESET_HARD_CHECK`. Use a bypass only when the operation is intentional or the regex is a false positive. Put the marker in the shell command comment so future readers see that the bypass was deliberate.

## Post-Edit Audit

After substantive editing, re-read the changed region and silently fix issues before reporting done.

For code, check contradictions, style drift, debug leftovers, band-aids, over-defensive code, misplaced helpers, duplicated logic, and missing parallel updates to docs/tests/config.

For docs, check contradictions, stale references, over-explanation, defensive caveats, incident residue, audience mismatch, structural drift, and list/heading convention drift.

## Reference

- See `references/hook-mapping.md` for what was migrated, adapted, or deliberately excluded.
