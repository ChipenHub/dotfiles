---
title: Hook Mapping
---

# Hook Mapping

## Migrated Into Active Codex Hooks

- `no-dangerous-ops.sh` -> `block_risky_bash.py`: dangerous disk, device, system-path, power, firewall, Docker prune, crontab, recursive permission, secure-delete, and process-kill checks.
- `no-destructive-git.sh` -> `block_risky_bash.py`: working-tree discard and untracked-file deletion checks.
- `no-git-amend.sh` -> `block_risky_bash.py`: amend, force-push, and remote branch delete checks.
- `no-devnull-redirect.sh` -> `block_risky_bash.py`: blocks redirection to `/dev/null`.
- `no-cat-write.sh` -> `block_risky_bash.py`: blocks `cat` heredoc file writes and points to Codex file-edit tools.
- `no-heredoc.sh` -> `block_risky_bash.py`: blocks very large inline scripts and heredocs.
- `no-background-ampersand.sh` -> `block_risky_bash.py`: blocks shell backgrounding with `&`.
- `no-pip-npm.sh` -> `block_risky_bash.py`: nudges `uv` and `pnpm` when available.
- `no-head-tail-pipe.sh` -> `block_risky_bash.py`: adds one session-scoped advisory for trailing `| head` or `| tail`.
- `prefer-uv-run.sh` -> `remind_uv_python.py`: adds a post-command reminder for bare Python.
- `reread-after-edit.sh` -> `post_edit_self_review.py`: adds code/doc self-audit context after `apply_patch`.

## Deliberately Excluded

- Browser/search/scraping hints: `hint-skill-agent-browser.sh`, `hint-skill-jina-ai.sh`, `hint-skill-read-url.sh`, and `websearch-followup-hint.sh`.
- Long-task/background orchestration: `hint-skill-babysit.sh`, `track-babysit-skill-load.sh`, `cache-keepalive-hint.sh`, `task-output-timeout-cap.sh`, `python-unbuffered.sh`, and background head/tail hard blocks.
- Claude-specific orchestration: `explore-model-sonnet.sh`, `no-worktree-team.sh`, and `hint-agent-claude-code-guide.sh`.
- Claude-specific tool surfaces: `no-multi-question.sh`, `no-schedule-wakeup-deadzone.sh`, and `track-sent-file.sh`.
- Model audit hooks: `audit-edits.py` and fresh-eye Claude/Codex wrappers. Their rule catalog was converted into lighter Codex skills and post-edit context, not a model-spawning stop hook.

## Codex Adaptations

- Claude's `Read`/`Write` tool language was translated to Codex's `apply_patch` and shell workflow.
- Hook output uses Codex `hookSpecificOutput` JSON.
- User-level hooks are registered in `~/.codex/hooks.json`; Codex may require `/hooks` trust before the new definitions run.
