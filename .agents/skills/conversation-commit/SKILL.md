---
name: conversation-commit
description: Create a focused Git commit or stash when the user asks to commit or stash changes. Include only changes relevant to the current conversation, preserve unrelated work, and use a concise English message based on the actual change.
---

# Conversation Git Changes

When the user asks to commit or stash, operate only on work relevant to the current conversation unless they explicitly identify a broader scope.

## Commit Workflow

1. Inspect `git status --short`, the unstaged diff, and the staged diff.
2. Identify the files and hunks produced by or directly relevant to the current conversation. Agent-generated test files and test classes are for local verification only and must not be committed, even when relevant. Exclude test classes added inside existing files as well as standalone test files.
3. Stage only those files or hunks. Never use `git add .`, `git add -A`, or `git commit -a`.
4. Leave unrelated modified, staged, and untracked files untouched. If a file mixes relevant and unrelated changes, stage only the relevant hunks.
5. Review `git diff --cached` before committing. Remove anything unrelated and any agent-generated test files or test-class additions from the staged set without discarding their working-tree changes.
6. If no relevant changes remain, do not create an empty commit.
7. Create a new commit; do not amend or rewrite existing commits unless the user explicitly requests it.
8. Report the commit hash, message, and committed files.

## Commit Message

Use one concise line in this form:

```text
<type>: <lowercase English description>
```

Choose the narrowest conventional type, such as `fix`, `feat`, `refactor`, `test`, `docs`, or `chore`. Do not add a scope or trailing period unless the repository clearly requires it.

Reference format:

```text
fix: fix video_to_image_generate_action tracker report when import video automantically
```

## Stash Workflow

1. Inspect `git status --short`, the unstaged diff, and the staged diff before stashing.
2. Identify files and hunks produced by or directly relevant to the current conversation. Do not stash unrelated modified, staged, or untracked files.
3. If the requested scope is ambiguous, summarize the candidate changes and ask rather than stashing the entire worktree.
4. Stash only the relevant paths. Include untracked files only when they are relevant; never include ignored files unless the user explicitly requests them.
5. If a file mixes relevant and unrelated hunks, use patch selection or ask the user instead of stashing the whole file.
6. Preserve the user's existing staged/unstaged organization where practical, and verify `git status --short` after the operation.
7. Report the stash reference, message, and stashed files.

## Stash Message

Derive a concise English message from the actual change, preferably in this form:

```text
WIP: <specific change>
```

Use concrete feature or fix language such as `WIP: add image generation tracking`. Do not use generic messages such as `stash current workspace`, `work in progress`, or `temporary changes`.
