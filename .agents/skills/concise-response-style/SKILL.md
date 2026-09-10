---
name: concise-response-style
description: Use only when the user explicitly asks for a short answer, one sentence, TLDR, a brief verdict, a headline, or less detail. Return the smallest useful answer.
---

# Concise Response Style

## Overview

Answer with the smallest shape that preserves the useful signal.

## One-Claim Mode

Use one claim, at most 40 words, when the user wants a verdict or status. Avoid preamble, option lists, hedge parentheticals, and internal plumbing.

Do not mention invented code identifiers unless the user needs them. Translate internal details into user-domain language.

## TLDR Mode

When asked for TLDR, output one line:

```text
TLDR: <verdict under 20 words>
```

No new information, caveats, or bullets.

## Open Discussion Exception

For open-ended discussion, use 2-3 short sentences and no more than 3 options. End with one recommendation, not a menu.

If the user asked for a code explanation, concise does not mean hiding required file references.
