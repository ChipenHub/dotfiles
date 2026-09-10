---
name: conversation-commit
description: Create a focused Git commit when the user asks to commit, commit the changes, or make a Git commit. Commit only changes relevant to the current conversation and use the project's concise English commit-message format.
---

# Conversation Commit

When the user asks to commit, create one focused commit for the work relevant to the current conversation.

## Workflow

1. Inspect `git status --short`, the unstaged diff, and the staged diff.
2. Identify the files and hunks produced by or directly relevant to the current conversation.
3. Stage only those files or hunks. Never use `git add .`, `git add -A`, or `git commit -a`.
4. Leave unrelated modified, staged, and untracked files untouched. If a file mixes relevant and unrelated changes, stage only the relevant hunks.
5. Review `git diff --cached` before committing. Remove anything unrelated from the staged set without discarding its working-tree changes.
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
