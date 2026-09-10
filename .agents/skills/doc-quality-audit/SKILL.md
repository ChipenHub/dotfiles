---
name: doc-quality-audit
description: Use after editing SKILL.md, AGENTS.md, CLAUDE.md, prompt, memory, hook, or substantial technical docs, or for an explicit doc-quality review. Find bloat, contradictions, stale references, and AI residue; skip prose polishing.
---

# Doc Quality Audit

## Overview

Audit docs as a future cold reader. Keep only content that changes behavior, removes real ambiguity, or records a durable rule.

## Trim Bias

Trim:

- Rationale repeated more than once.
- Lists or tag sets restated across sections.
- Parentheticals explaining obvious terms.
- Warnings about workflows the reader is not in.
- Behavior already self-documented by code or a nearby source of truth.
- Incident details that explain why a rule exists instead of stating the rule.
- New entries longer or more qualified than sibling entries.

## Audit Pass

1. Read the changed region and 2-3 nearby siblings.
2. Check whether the new content belongs where it was inserted.
3. Verify uncommon file paths, commands, flags, symbols, or API names against primary sources.
4. Check for contradiction with frontmatter, tables, schemas, earlier sections, and linked code.
5. Remove over-emphasis, defensive caveats, duplicated source-of-truth detail, and template prose.
6. Prefer regrouping to appending one more exception.

## Finding Categories

Use `references/doc-audit-catalog.md` for the detailed catalog when the document is agent-facing or high-impact.

## Report Style

If reviewing, lead with findings. If editing directly, silently fix high-confidence issues and report the scope.
