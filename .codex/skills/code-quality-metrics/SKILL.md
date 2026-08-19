---
name: code-quality-metrics
description: Use when the user asks whether code is too complex, maintainable, or safe to change, or requests complexity or refactor thresholds. Measure size, nesting, parameters, coupling, cohesion, and cyclomatic or cognitive complexity. Skip ordinary edits and reviews.
---

# Code Quality Metrics

## Overview

Use metrics as a refactoring signal, not as a substitute for reading code. Prefer the metric that matches the risk: branching, comprehension, size, coupling, or cohesion.

## Thresholds

| Metric | Good | Warning | Critical |
|---|---:|---:|---:|
| Cyclomatic complexity | <=10 | 11-20 | >20 |
| Cognitive complexity | <=15 | 16-24 | >=25 |
| Method logical lines | <=30 | 31-50 | >50 |
| Class lines | <=300 | 301-500 | >500 |
| Parameters | <=3 | 4-5 | >5 |
| Nesting depth | <=3 | 4 | >4 |

## How To Interpret

- Cyclomatic complexity counts independent control-flow paths.
- Cognitive complexity penalizes nesting and human comprehension cost.
- Maintainability index combines size, complexity, and volume; use it as a rough trend, not a pass/fail gate.
- High coupling means changes have wider blast radius.
- Low cohesion means a type or module likely owns more than one responsibility.

## Useful Commands

Python:

```bash
uv run radon cc src/ -a -s
uv run radon mi src/ -s
```

JavaScript/TypeScript:

```bash
pnpm exec eslint --rule 'complexity: ["error", 10]' src/
```

## Refactor Direction

When a metric crosses warning levels, first split nested decisions, name intermediate results, group parameters, extract cohesive helpers, and add tests around behavior. When it crosses critical levels, prefer redesign over local patching.
