---
name: structural-code-search
description: Use ast-grep when code work needs multiline or syntax-aware matching, typed call-site discovery, coordinated renames, or codemods. Skip when a clear rg text search is sufficient.
---

# Structural Code Search

## Overview

Use `ast-grep` when `rg` stops being a clear, reliable query. Start with a small example, prove the rule matches it, then run it on the real tree.

## Workflow

1. State the target code shape and language.
2. Create or identify a tiny example that should match.
3. Write the simplest `ast-grep` pattern or YAML rule.
4. Test against the example.
5. Debug with `--debug-query=cst` or `--debug-query=pattern` when no matches appear.
6. Search the codebase only after the rule matches the example.

## Command Patterns

Simple pattern:

```bash
ast-grep run --pattern 'console.log($ARG)' --lang javascript .
```

Rule file:

```yaml
id: async-with-await
language: javascript
rule:
  kind: function_declaration
  has:
    pattern: await $EXPR
    stopBy: end
```

Run it:

```bash
ast-grep scan --rule rule.yml .
```

## Rule Habits

- Add `stopBy: end` for relational rules such as `inside` and `has` unless there is a specific boundary.
- Use `pattern` for simple nodes; use `kind` plus relations for structural questions.
- Use `all`, `any`, and `not` to compose complex filters.
- Use `--json` when the output will drive a codemod or follow-up script.

If ast-grep is unavailable, fall back to `rg` plus manual review and say that the structural query could not be run.
