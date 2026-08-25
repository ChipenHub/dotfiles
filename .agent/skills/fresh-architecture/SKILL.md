---
name: fresh-architecture
description: Use when the user asks for architecture design, greenfield or from-scratch redesign, architecture comparison, or critique. Reason from requirements rather than current code; skip routine implementation and migration-only work.
---

# Fresh Architecture

## Overview

Reason forward from requirements. Existing code is evidence, not the frame.

## Mindset

Stop when the design starts from any of these:

- "The current code does X, so the new design should look similar."
- "We need to stay backward-compatible with X."
- "The existing module boundary already exists, so reuse it."
- "This is already wired up, so keep it."
- "Let's avoid disruption" when disruption is not itself a requirement.

If a current pattern survives, it survives because it is the right answer from first principles.

## Output Shape

1. Problem: 1-3 lines describing what the system must do.
2. Components: 3-7 boxes with one-sentence responsibilities and why this number of boxes is right.
3. Contracts: interfaces, data shapes, messages, or API boundaries between components.
4. Data and state: what is stored where, lifecycle, consistency model, ownership.
5. Rejected alternatives: at least one materially different shape and why it loses.
6. Current design critique, if a codebase exists: what is right, what is wrong, what is load-bearing, and what is incidental.

## Boundary

Do not include a migration plan unless the user asks. Architecture and migration are separate products.
