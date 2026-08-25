---
name: memory-capture
description: Use only when the user explicitly asks to remember a rule for future tasks or sessions, avoid repeating a mistake in the future, save a durable lesson, or create a replay prompt. Skip current-task corrections, ordinary summaries, and retrospectives.
---

# Memory Capture

## Overview

Separate durable learning from temporary project state. Only save rules that will help a future Codex avoid repeated cost or mistakes.

## Keep

- User corrections that contradict default AI behavior.
- Mistakes likely to recur and costly to fix.
- Durable environment facts.
- Reusable workflows.
- Project lessons that generalize beyond a single in-flight change.
- Explicit "remember" requests.

## Drop

- In-flight plans.
- Narrow empirical results.
- Facts easily recovered from the repository.
- Hypotheses.
- Reverted decisions.
- Volatile details that will become stale.
- Generic AI best practices.

## Memory Bullet Shape

Write one durable claim in plain prose. Avoid task IDs, hashes, raw paths, and temporary names unless they are the durable fact.

## Minimal Replay Prompt

When asked to form a replay prompt:

1. Assume all current changes are reverted.
2. Describe the desired outcome, not the implementation details discovered in this session.
3. Include only context a fresh agent would need.
4. Avoid referring to artifacts that exist only because of this session.

If Codex memory is enabled in the environment, save only the final durable bullet. Otherwise, present the bullet for the user to store.
