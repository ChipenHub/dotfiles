---
name: engineering-discipline
description: Use for repository implementation, debugging, refactoring, code review, code-path exploration, or implementation planning. Investigate first, match local patterns, fix root causes, keep scope focused, and run small tests. Skip architecture design or critique and non-code work.
---

# Engineering Discipline

## Overview

Use this skill as a pragmatic coding behavior overlay. It is not a domain tool; it is a way to work.

## Defaults

- Investigate before naming a root cause. Trace the behavior end to end, then state what was found.
- Run cheap probes before heavy work. Start with the smallest command or test that can falsify the current theory.
- Match siblings before adding entries to lists, enums, config tables, recipes, docs, or UI surfaces.
- Prefer the repository's existing helpers and patterns over new abstraction.
- Solve the underlying issue. Avoid hardcoded incident fixes, compatibility shims, swallowed errors, and patch-over-refactor shapes.
- Keep scope coherent. Do not mix formatting churn, unrelated renames, or drive-by refactors into a focused fix.
- Re-read edited regions before declaring done.

## Tool Habits

- Use `rg` before slower text search.
- Use structured parsers or AST tools when plain text matching becomes brittle.
- Use `uv run` for Python commands when practical.
- Use `pnpm` when the project supports it.
- Avoid output suppression and line-truncating pipes unless there is a real reason.
- Batch independent reads when useful, but never batch calls whose arguments depend on earlier outputs.

## Debug Loop

1. Reproduce or observe the failure.
2. Read the owning code path and 2-3 neighboring examples.
3. Form the narrowest testable hypothesis.
4. Add instrumentation or run a probe when evidence is missing.
5. If 3-5 probes do not converge, summarize evidence and stop grinding.
6. Patch the root cause and run the smallest relevant verification.

## Code Review Stance

When asked to review, lead with findings ordered by severity. Ground each finding in a concrete file/line or behavior. Prioritize bugs, regressions, missing tests, data loss, security, and contract mismatches over style.

## Completion Standard

Before final response, know what changed, what was verified, and what was not verified. If tests could not run, say so directly.
