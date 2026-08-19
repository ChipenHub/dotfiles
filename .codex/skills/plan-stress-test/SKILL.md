---
name: plan-stress-test
description: Use only when the user asks to be grilled or interviewed, challenge or stress-test a plan, design, or proposal, or resolve decisions one by one. Ask one question at a time; skip ordinary planning.
---

# Plan Stress Test

## Overview

Interview the user until the plan's decisions, dependencies, and risks are explicit.

## Rules

- Ask one question at a time.
- For each question, provide your recommended answer first.
- If a question can be answered by reading the codebase, inspect the codebase instead of asking.
- Walk dependencies in order; do not ask about a downstream choice before the upstream constraint is settled.
- Stop when the plan has clear assumptions, constraints, success criteria, and failure modes.

## Question Types

- Goal: What outcome proves this worked?
- Audience: Who consumes the output or API?
- Constraints: What cannot change?
- Ownership: Which module or team owns each responsibility?
- Data: What state is stored, derived, cached, or migrated?
- Failure: What happens on partial failure?
- Rollout: How can this ship safely?
- Test: What small verification proves the important path?

Do not turn the interview into a lecture. Each question should make the next design decision easier.
