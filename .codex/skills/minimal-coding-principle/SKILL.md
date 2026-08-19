---
name: minimal-coding-principle
description: MUST use alongside engineering-discipline when implementing or extending a feature, especially Android experiments, AB tests, settings gates, or feature flags. Keep changes local, preserve the disabled path, and avoid unrelated refactors or over-abstraction. Skip diagnosis or review without implementation.
---

# Minimal Coding Principle

Use this skill before implementing a new feature. Apply it as a coding discipline layer while investigating, editing, and verifying.

## Hard Rules

Treat these as non-negotiable unless the user explicitly overrides them.

- Solve the explicit feature request with the smallest safe change.
- Keep changes local, minimal, and directly tied to the requested feature.
- Preserve existing module boundaries, file structure, naming style, and surrounding conventions.
- Do not do drive-by refactors, unrelated cleanup, broad formatting, dependency churn, or architecture changes.
- Do not over-abstract: avoid splitting a readable linear flow into many tiny helper methods unless it clearly reduces meaningful duplication or isolates real complexity.
- Prefer clear grouped inline logic for UI construction, data binding, event handling, and business branching when that keeps the flow easier to read.
- Add comments only for non-obvious business intent, compatibility constraints, lifecycle risks, or tricky behavior.
- If multiple implementation paths depend on unknown product, business, architecture, or compatibility context, list the options and ask the user before editing.
- After substantive code edits, run the smallest practical verification and fix introduced errors.

## Change Strategy

- Prefer additive changes when they fit naturally and keep the flow clear.
- Do not force additive changes if a small edit to an existing method is clearer, safer, and less duplicative.
- Avoid duplicate or parallel logic just to avoid touching existing code.
- Keep file and module churn low; create new files only when the existing structure cannot hold the change clearly.
- If unrelated issues are discovered, mention them instead of fixing them unless they block the requested feature.
- Do not treat "this code could be better" as "this code should be changed now."

## Experiment Isolation

When the new feature involves an experiment, AB test, settings/config switch, or feature flag, every line of new or changed behavior must execute only when the experiment is enabled.

- Put all new behavior behind the experiment check, either inside a delegated new function or inside a branch block at the call site.
- Do not let new code execute on the original path when the experiment is off.
- Do not change existing behavior when the experiment is off by altering defaults, shared helper behavior, shared conditions, or common data preparation.
- Do not add parameters to an existing function to support experiment behavior when call-site branching plus a new function is practical.
- Prefer branch insertion at narrow choke points; keep the number of branch insertion points small.
- The experiment branch body may tolerate some duplication if that keeps the original path untouched and makes cleanup straightforward.

When a short-to-medium existing function needs changes in multiple places for an experiment, add a guard at the top and delegate to a full replacement function:

```kotlin
fun renderCard(card: Card) {
    if (ExperimentManager.isNewCardEnabled()) {
        renderCardV2(card)
        return
    }

    // Original flow remains unchanged below.
    val title = card.title
    val subtitle = card.subtitle
    val image = loadImage(card.imageUrl)
    val footer = buildFooter(card)
    bind(title, subtitle, image, footer)
}

fun renderCardV2(card: Card) {
    val title = card.title
    val badge = card.badge
    val image = loadResizedImage(card.imageUrl)
    val footer = buildFooterV2(card)
    bind(title, badge, image, footer)
}
```

For function variants, prefer a new function and a branch at the call site:

```kotlin
fun bind(holder: CardHolder, card: Card) {
    val vm = if (ExperimentManager.isBadgeEnabled()) {
        buildCardViewModelWithBadge(card)
    } else {
        buildCardViewModel(card)
    }
    holder.bind(vm)
}
```

## Abstraction Discipline

The most important rule: do not split a clear, readable process into too many tiny, more abstract processes.

- Do not create many small helper methods for logic that is already easy to read inline.
- Do not break a coherent linear flow into scattered methods that force readers to jump around.
- Never split an existing function by cutting it in the middle and extracting the second half into a new function.
- Use functional encapsulation only when it clearly improves reuse, isolates complex conditions, removes meaningful duplication, or makes the main flow easier to understand.
- A longer method with well-grouped blocks can be better than many shallow helpers.

## Code Organization

- Group related UI, layout, style, data binding, event handling, and business logic into readable blocks.
- Keep related operations close together unless extracting them provides clear functional value.
- Add short comments before non-obvious blocks to explain behavior, intent, or business boundaries.
- Comments should explain why the block exists, not repeat obvious code.

## Uncertain Plans

If several reasonable implementation approaches exist and the right one depends on unknown product, business, architecture, or compatibility context:

- Do not silently choose a business-sensitive path.
- List viable options with short tradeoffs.
- Ask the user to choose before editing.
- If the uncertainty is low risk and work can proceed safely, state the assumption briefly and keep the change minimal.

## Final Self-Check

Before finishing a new feature:

- Confirm the change modifies only what the feature requires.
- Confirm there are no drive-by refactors, unrelated cleanup, or broad formatting changes.
- Confirm readable flows stayed together and helper extraction is justified.
- Confirm existing style, structure, and module boundaries are preserved.
- Confirm user input was requested when the correct plan depended on unknown business context.
- If an experiment, AB test, settings/config switch, or feature flag is involved, scan every changed line and verify it is either the experiment guard itself or only reachable when the gate is enabled.
- Trace the original path with the gate off and confirm it behaves exactly as before.
