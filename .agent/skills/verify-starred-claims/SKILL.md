---
name: verify-starred-claims
description: Use when the user directly appends `*` to the last word of a factual premise in ordinary prose to mark uncertainty, such as `current version is 3*`. Verify before acting; proceed silently if supported, otherwise stop and explain. Ignore formatting, code, globs, multiplication, footnotes, redaction, and decoration.
---

# Verify Starred Claims

Treat a trailing `*` in ordinary prose as the user's private uncertainty marker. Resolve it before acting, then either proceed silently or stop with a useful correction.

## Interpret the marker

1. Collect every valid trailing-asterisk marker in the user's latest request and any still-active request it extends.
2. Attach each marker to the smallest complete factual proposition immediately before it, not automatically to the whole message.
3. Include assumptions that materially affect the requested work: current state, causality, compatibility, availability, identity, quantities, dates, and technical behavior can all be claims.
4. If the grammar permits multiple scopes, investigate the plausible readings. Ask for clarification only when the different readings would change the action and context cannot resolve them safely.

Do not treat these uses as uncertainty markers:

- Markdown emphasis or list syntax
- Code, regular expressions, shell globs, pointer syntax, or multiplication
- Footnote markers, censored words, ASCII art, or decoration
- An asterisk reproduced literally inside quoted source material, unless the user clearly added it as their annotation

## Investigate before acting

Complete read-only investigation before making edits, sending messages, publishing, purchasing, or performing any other material action.

1. Rewrite each marked proposition internally as a precise, testable claim.
2. Inspect the most direct evidence available. Prefer repository files, tests, runtime output, and configuration for local technical claims; prefer current official or primary sources for external claims.
3. Check freshness whenever a fact can change. Search the web when current or niche external information is involved, and cite sources only if the eventual response must disclose a problem.
4. Cross-check consequential, disputed, or ambiguous claims with independent evidence where practical.
5. Distinguish an exact claim from a common approximation. Judge it at the precision required by the requested action.
6. Reach the best-supported verdict: `supported`, `contradicted`, or `unresolved`. Use `unresolved` only after reasonable investigation cannot determine the truth; never invent certainty.

For multiple markers, finish checking all of them before deciding whether to act. One contradicted or unresolved premise is enough to stop implementation.

## Decide and respond

### All marked claims are supported

Proceed with the user's requested task normally. Keep the verification invisible:

- Do not say that the claims were checked or confirmed.
- Do not praise or restate the marked claims merely to validate them.
- Do not add a fact-checking section, citations, or caveats solely because this skill ran.

Provide only the response or artifact the user originally requested.

### Any marked claim is contradicted

Stop before implementation. In a concise response:

1. Identify the contradicted claim.
2. Explain why it is wrong using the decisive evidence.
3. State the best-supported truth at the precision relevant to the task.
4. Offer concrete choices when more than one reasonable next step exists; otherwise state the required correction and wait for the user.

Do not expose private chain-of-thought. Report evidence and conclusions only. Keep supported marked claims silent when other claims fail.

### Any marked claim is unresolved

Stop before implementation. State what could not be determined, what evidence is missing or conflicting, and the smallest choice or additional information needed to continue.

## Examples

- `Upgrade this project to React 20* and fix the warnings.` Verify that React 20 exists and is appropriate before editing. If it does not, stop and give the actual available versions or migration choices.
- `Rename the parser; it has no callers outside this file*.` Search definitions and call sites first. If external callers exist, stop and show the relevant evidence.
- `Book the meeting for Friday because that is August 21*.` Check the calendar date. If correct, book it without mentioning the check; if incorrect, stop and offer the correct dates.
- `Use *.json files` and `**important**` contain non-triggering asterisks.
