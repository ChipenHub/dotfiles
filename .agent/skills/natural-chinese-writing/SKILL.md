---
name: natural-chinese-writing
description: Use only for explicit English-to-Chinese translation, natural Chinese rewriting, removal of translationese, or Chinese technical or Zhihu-style writing. Do not trigger merely because the conversation is in Chinese.
---

# Natural Chinese Writing

## Overview

Write Chinese that reads as native Chinese, not English mapped word by word.

## Translation Workflow

1. Read the full English source before translating.
2. Resolve ambiguous passages, terminology, and project-specific names first.
3. Translate in one complete pass while preserving formatting.
4. Run accuracy, fluency, and AI-slop passes.
5. Read the final Chinese without looking at English; if it sounds translated, revise again.

## Accuracy Pass

Fix meaning drift, omissions, added explanation, broken formatting, English punctuation in Chinese text, and incorrect technical terms.

## Fluency Pass

Fix English word order, unnatural collocations, overlong 的 chains, weak transitions, and phrases that require rereading.

## Chinese Technical Article Workflow

For long-form Chinese technical posts:

- Outline the narrative: problem, exploration, evidence, solution, takeaways.
- Use Chinese section numbering when appropriate: `## 一、`, `## 二、`.
- Keep technical English terms only where Chinese usage normally keeps them.
- Include real quantitative evidence and code references when the article depends on them.
- Check factual consistency across sections.
- Validate Markdown tables and code blocks if the output is a file.

Do not add AI authorship disclosure unless the user asks or the target venue requires it.
