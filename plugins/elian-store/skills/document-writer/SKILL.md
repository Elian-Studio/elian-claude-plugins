---
name: document-writer
description: >-
  Turn any content into a single self-contained HTML document (or Markdown when asked) in one
  fixed house style. Use it whenever the result is "something a person will read or keep" —
  analysis results, investigations, research, reports, technical design explanations,
  guides/tutorials, meeting write-ups, summaries. Reach for it when the user says "turn this
  into a document", "write it up as a report", "export as HTML", "document this", "make a
  shareable write-up", "save this as a file", "summary document", or wants a just-finished
  analysis, investigation, or implementation left behind as something shareable. It applies
  even when the word "document" is never used — if there is a reader, it is a document, not a
  code comment. (For rendering a fixed JSON payload through a schema-based template, use
  create-document — that is the render engine other skills call internally. This skill is the
  general-purpose author that turns arbitrary content into a well-presented document.)
---

# Document Writer

A general-purpose writer that turns arbitrary content into a **clean single HTML document in a
fixed house style**. The core value is that every document comes out in the same tone (warm
off-white background, ink body text, one blue accent), so a set of them reads like it was made
by the same person.

## How it works

Write the content **as Markdown**, then the bundled script `scripts/build_doc.py` converts it
into a **self-contained single HTML file** with the fixed house CSS inlined. Zero external
dependencies — it opens anywhere and can be shared or printed to PDF as is.

Rich components (callouts, KPI tiles, cards, comparison grids) go in as **raw HTML blocks**
inside the Markdown. The converter passes block-level HTML through untouched, so you get
Markdown's convenience and custom layout at the same time. All visual style lives in one CSS
file, so **never write inline `style=` attributes or invent new colors/fonts** — combine the
documented classes and the tone matches automatically.

## Workflow

### 1. Decide the format
- **HTML by default.** Absent any instruction, produce a self-contained HTML document.
- If the user asks for "MD" or "markdown" → take the [Markdown-only](#markdown-only-path) path.
- If the user asks for "PDF" → build the HTML, then point them at browser printing or the
  `make-pdf` skill (this skill stops at HTML).

### 2. Pick the document type and structure
Each type has a section layout that works well. Read `references/doc-types.md` and follow the
matching blueprint (analysis/report / technical/design / guide/tutorial / general). The
blueprint is a starting point — adjust it to the actual content. The style is identical
regardless of type; only the structure differs.

### 3. Write the content as Markdown
Write the body into a temporary `.md` file. Standard Markdown (headings, lists, tables, code
fences, blockquotes, links, images) plus GitHub-style callouts `> [!NOTE]` `> [!TIP]`
`> [!WARNING]` `> [!CAUTION]` `> [!IMPORTANT]` `> [!INFO]`.
For rich components, copy from the class catalog in `references/components.md` and paste it in
as raw HTML.

- Do not put an H1 (`#`) in the body — the title comes from `--title` (the script builds the header).
- Sections are H2 (`##`), subsections H3 (`###`).
- No conversation-dependent phrasing ("as we just saw", "mentioned above"). The document must
  stand on its own.
- No emoji beyond the callout icons unless the user asks for them.

### 4. Build
```bash
# SKILL_DIR = this skill's own directory on either host:
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/document-writer}}"
SKILL_DIR="${SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/document-writer}"
python3 "${SKILL_DIR}/scripts/build_doc.py" CONTENT.md \
  --title "Document title" \
  --subtitle "One-line subtitle (optional)" \
  --meta "Date=2026-06-07" --meta "Type=Analysis report" --meta "Author=Daniel" \
  --toc \
  --out claudedocs/payment-latency-report.html
```
- `--meta "key=value"` becomes a tag chip in the header (repeatable). Date and type are usually enough.
- `--toc` builds a table of contents from the H2/H3 headings. Recommended for 3+ sections, skip it on short documents.
- `--out` defaults to the project's **`claudedocs/`** (CLAUDE.md convention: reports, analyses,
  and summaries live there). Use a descriptive `kebab-case.html` filename. If the user specifies
  a path, follow it.

### 5. Wrap up
- Clean up the temporary `.md` (unless the user asked to keep the document source).
- Tell the user the **path of the generated HTML** and suggest opening it in a browser to check.
- Don't force it into one shot — if the content structure is ambiguous, confirm briefly first.

## Rich components

`references/components.md` holds a copy-paste catalog: callouts / cards and card grids / KPI
tiles / two-column comparison / step lists / badges and tags / data tables.
**Rule: do not write new CSS or inline styles — combine only the documented classes.** That is
what keeps every document in the same tone. If a layout genuinely isn't in the catalog, extend
minimally and only by reusing the existing color variables (`var(--accent)` and friends).

## Markdown-only path

If the user wants MD, skip the script and write a clean `.md` directly with `Write`.
- One H1 (the title) + a meta line (date / type) + a `---` rule + H2 sections.
- Use tables, code blocks (with a language), callouts (`> [!NOTE]`), and collapsible `<details>`.
- No absolute paths, no context-dependent phrasing. Images go in an `images/` directory next to
  the document, referenced relatively.

## Quality bar (anti-slop)

This skill exists to produce a consistent, tidy look. Hold that line:
- Keep the house palette (warm grays + one blue). No purple gradients, neon, or random accents.
- Keep the bundled font stack (Pretendard/system). Do not add Inter/Roboto/Arial.
- Don't overuse card grids — grids are for genuinely parallel items; narrative goes in body paragraphs.
- KPI tiles and badges only when a real number or status exists. Never invent a metric to fill one.
- Tables are for comparison and list data. A single row is just a sentence.

## build_doc.py flag summary

| Flag | Meaning |
|------|---------|
| `CONTENT.md` (positional) | The body Markdown file |
| `--title` | Document title. Without it, the body's first `# H1` is promoted to the title |
| `--subtitle` | One-line subtitle under the title |
| `--meta "key=value"` | Header tag chip (repeatable). `--meta "value"` renders the value alone as a chip |
| `--toc` | Insert an automatic table of contents from H2/H3 |
| `--out PATH` | Output path (default: title-slug.html, recommended: `claudedocs/...`) |
| `--lang` | `<html lang>`, defaults to `ko` |
| `--body-html PATH` | Use a raw HTML body fragment instead of Markdown (advanced) |
| `--selftest` | Run the converter's self-check and exit |

If something looks wrong, check the converter first with
`python3 "${SKILL_DIR}/scripts/build_doc.py" --selftest`.
