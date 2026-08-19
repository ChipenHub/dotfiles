---
title: Doc Audit Catalog
---

# Doc Audit Catalog

## Documentation Issues

- `DOC-contradiction`: new prose conflicts with unchanged text, frontmatter, schema, or earlier sections.
- `DOC-over-emphasis`: bold, emoji, all-caps, or warning density is out of proportion.
- `DOC-tonal-drift`: new row, bullet, or paragraph is much longer or more rhetorical than siblings.
- `DOC-list-parity`: one list item carries a qualifier or rationale that sibling items do not.
- `DOC-justifying-aside`: parenthetical or because-clause explains an obvious step.
- `DOC-defensive-caveat`: warning about a failure mode the reader is not currently facing.
- `DOC-hallucinated-ref`: uncommon command, flag, API, path, or symbol is unverified.
- `DOC-stale-reference`: referenced path, command, or snippet no longer matches.
- `DOC-duplicates-source`: doc repeats concrete identifiers owned by a source file.
- `DOC-catalog-narration`: top-level index describes details that belong in the target doc.
- `DOC-audience-mismatch`: agent-facing prose uses human-interactive cues or vice versa.
- `DOC-incident-leak`: reusable rule narrates the incident that caused it.
- `DOC-dangling-negation`: text defines itself by contrast to an alternative absent from the artifact.
- `DOC-style-drift`: heading, list, separator, or naming style does not match the file.
- `DOC-inverted-phrasing`: conditional or qualifier delays the subject.
- `DOC-patch-over-restructure`: a local append hides the need to regroup the section.
- `DOC-positional-fit`: new material sits near the edit site instead of thematic siblings.

## Code-Adjacent Documentation Issues

- `CODE-comment-mismatch`: docstring or comment no longer describes behavior.
- `CODE-narrative-comment`: comment restates obvious adjacent code.
- `CODE-sync-not-updated`: a code change creates a parallel update obligation in docs, config, schema, examples, or tests.

Do not flag style preferences unless a future reader would actually be misled or slowed down.
