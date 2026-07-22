# Blueprints by document type

The style is identical regardless of type. Only the **structure (section layout)** follows the
type. The blueprints below are a starting point — add and drop sections to fit the real content.
Never invent filler to fill an empty section.

---

## Analysis · report · summary

A document that shares the result of an analysis or investigation. The core is "what did we find,
and therefore what will we do".

```
Title (--title) + subtitle + meta (date, Type=Analysis report, author)
[--toc recommended]

## Summary (TL;DR)
  - The conclusion and key recommendation in 3-5 lines. A busy reader should be able to stop here.
  - If there are numbers, use KPI tiles.

## Background / context
  - Why this analysis happened. The problem situation.

## Measurements / findings
  - Data, tables, KPIs. Objective facts.
  - Put important caveats in a callout (`> [!WARNING]`).

## Analysis / interpretation
  - Causes, patterns, what it means.

## Recommendations / actions
  - Prioritized actions. A numbered list, or a table (owner / due date).

## (Optional) Appendix
  - Raw data goes in a collapsible <details>.
```

---

## Technical · design document

Explains how a system behaves, its API, its architecture. Code snippets and accuracy are what matter.

```
Title + subtitle + meta (date, Type=Design document, related issue)
[--toc recommended]

## Overview
  - What and why. Define the scope in one paragraph.

## Components / architecture
  - List components in a card grid, or lay out responsibilities in a table.
  - If a diagram is needed, use an image (figure) or a text tree.

## Behaviour / flow
  - Request → response flow. A step list (.steps) or a numbered list.

## API / interface (if applicable)
  - Table: method | path | request | response | status codes.
  - Example requests/responses in code blocks (json/bash).

## Data model (if applicable)
  - A table, or a code block (SQL / type definitions).

## Decisions / trade-offs
  - Why it was built this way. AS-IS/TO-BE goes in a two-column comparison (.cols2).

## Caveats / edge cases
  - Emphasize with callouts.
```

---

## Guide · tutorial · manual

A document that teaches the reader to follow along. Order and clarity are the whole point.

```
Title + subtitle + meta (audience, time required, ...)
[--toc recommended — if long]

## What you can do with this
  - The end state in one or two lines. (Motivation.)

## Prerequisites
  - What is needed (versions, permissions, tools).

## Step by step
  - Use the .steps component: each step = action + explanation + command.
  - Commands in code blocks. Showing example output helps.
  - Pitfalls go in `> [!CAUTION]`, tricks in `> [!TIP]`.

## Verification
  - How to confirm it worked.

## Troubleshooting (FAQ)
  - Table: symptom | cause | fix. Or a <details> Q&A.

## Next steps
  - Related documents and deeper links.
```

---

## General (no fixed type)

When there is no set mold. Follow the natural flow of the content.

```
Title + subtitle + meta (date)

## (Sections that fit the content)
  - Put the most important conclusion/point at the top.
  - Parallel items → cards, numbers → KPIs, sequences → step lists, comparisons → table or two columns.
  - One idea per screen. Keep sections short and scannable.
```

---

## Shared principles

- **Title goes in `--title`; the body's top level is H2.** Do not add another H1 in the body.
- **Summary first.** Readers want the conclusion up front.
- **Make it scannable.** Prefer subheadings, lists, and tables over long paragraphs.
- **Self-contained.** No conversation-dependent phrasing like "just now" or "above".
- **Components only when the content demands them.** No decorative card grids or KPI spam.
