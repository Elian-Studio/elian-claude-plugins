# Issue history — narrative template

The canonical template for writing an issue's development history **for a human reader**.
Someone opening the issue for the first time should be able to answer four questions
within about two minutes:

1. What changed (What)
2. Why it was done (Why)
3. How it was verified (Verification)
4. What is left (Follow-up)

## Where it lives / who writes it

- **Location**: the **body** of the issue page in the configured task database — the same
  page a person opens when they search for the issue key. Not a child page, not a database.
- **Writer**: `/issue-close`, and only `/issue-close`. `/issue-open` seeds §1 metadata and
  §3 background at kickoff; the close interview supplies the Why in §4/§5/§9.
- One writer is a deliberate constraint. Two writers means two copies of the supersede
  rules below, and they drift apart.
- Per-commit detail belongs in the collapsed §10 audit toggle, not in the body. History is
  for humans, not machines — the body is a curated story, not a commit dump.

## Design principles

| Principle | Applied as | Source |
|---|---|---|
| Summary first (inverted pyramid) | §1 meta → §2 summary carries the two-minute payload | NN/g inverted pyramid, Google CL descriptions |
| State the Why (code only shows the What) | §3 background, §4 decisions | ADR (Nygard), Google "why over what" |
| Active voice + problem, why best, known downside | §4 decisions and approach | Google CL descriptions |
| Alternatives encouraged, not mandatory | §5 is written when it exists, omitted when it does not | MADR — do not manufacture alternatives |
| Curated changes, no commit dump | §6 changes | Keep a Changelog, AWS ADR |
| Explanation-oriented | tone throughout | Diátaxis Explanation |
| Supersede rather than overwrite | section-scoped replacement, frozen after close | AWS ADR process |

---

## Body template (top to bottom)

```markdown
## Metadata
| Issue | Status | Domain | Period | PR |
|-------|--------|--------|--------|-----|
| [KEY-123](tracker-link) | In progress | <domains> | 2026-06-12 ~ 2026-06-22 | server !131, worker !21 |

## Summary (TL;DR)
<What plus why, two to four plain sentences. No unexplained acronyms or assumed context.>

## Background / Why
<Why this work was needed — the problem and motivation. One or two numbers or symptoms if
they exist. Link the tracker requirement rather than restating it.>

## Decisions and approach
<Active voice: what was done, how, and why that was the best option. State the key design
decisions and their known trade-offs honestly.>
«Diagram — pick one: sequenceDiagram (interaction) · flowchart (AS-IS→TO-BE) ·
stateDiagram (state axis). Rules in "Visual elements" below.»

## Alternatives considered
<Options weighed and dropped, with the reason for dropping them. If there is no record,
omit this section entirely or write one line: "Alternatives considered: (not recorded)".>
<details><summary>Alternative detail</summary>

- **Option A** — dropped because: ...
- **Option B** — dropped because: ...
</details>

## Changes
<No commit dump. Curated prose grouped by area, with links to PRs and code.>
- **Backend** — <one paragraph>
- **Frontend** — <one paragraph>
- **Worker / Infra** — <one paragraph>

## Verification
<How it was tested or measured. Before/after numbers, charts, reproduction steps.
Hand-authored comparison blocks, charts, and embedded databases belong here.>

## Outcome / trade-offs
<What actually happened, remaining debt, and follow-up work including the operations track.>

## References
- Tracker: [KEY-123](...)
- PR: server !131, worker !21
- Related decisions / ADRs: #110, #111

<details><summary>📋 Commit log (audit trail)</summary>

Per-commit detail lives in the audit database, filtered by branch:
[Audit log →](<audit database url>?filter=branch=<branch>)
</details>
```

- §1–§2 are the two-minute test. §3–§9 are the explanation layer. §10 is demoted machine detail.
- §5 is optional. If §7 contains hand-authored charts or databases, it is excluded from
  automatic updates — see rule 5 below.

---

## Visual elements

How something was decided and built reads faster as a picture than as prose. When the flow,
structure, state, or decision is non-obvious, put a diagram in the body.

| What | Where | Form |
|---|---|---|
| Interaction flow (enqueue→worker→reconcile) | §Decisions | Mermaid `sequenceDiagram` |
| Structural change AS-IS→TO-BE | §Decisions / §Changes | Mermaid `flowchart` with before/after subgraphs |
| Quantitative or qualitative before/after | §Decisions / §Verification | Comparison table (AS-IS \| TO-BE columns) |
| State transitions | §Decisions | Mermaid `stateDiagram-v2` |
| Component/module relationships | §Changes | Mermaid `flowchart` / `classDiagram` |
| Metrics (wall time, throughput) | §Verification | Chart image |

**Prefer native Mermaid code blocks** — Notion renders them and they stay editable. Use an
image URL only when a static asset is genuinely needed.

**Notion Mermaid rules**: quote labels containing parentheses or colons — `A["Notion (App)"]`.
Line breaks are `<br>`, not `\n`. Do not escape inside the code block.

---

## Supersede safety rules (the writer must follow these)

Updating the narrative is a supersede, not an edit — replace only the changed section and
preserve everything else byte for byte.

1. **Anchor on the `## Section heading` line, always.** Never use body prose as the selection —
   similar-looking paragraphs get replaced by mistake.
2. **Scope the replacement from that `##` to just before the next `##`.**
3. **Never use the page root or the whole body as the selection.** Wholesale overwrite is
   forbidden. This is the one failure that cannot be undone — a hand-written section replaced
   in full is gone.
4. **If the anchor is missing**, fall back to `insert_content_after` on the preceding section
   rather than `replace_content`.
5. **Never auto-replace user-owned blocks.** Hand-authored charts, callouts, and embedded
   databases live under §Verification, and automatic updates must not target that heading.
   Mark them with `<!-- user-owned: do not auto-replace -->` when it helps.
6. **Freeze after close.** Once status is the configured `done` value, append a single
   `> Final note — YYYY-MM-DD` line under §2 instead of rewriting sections.

### Upsert procedure (`/issue-close` step 5-1)

1. `notion-fetch` the issue page body.
2. Check for the `## Summary (TL;DR)` marker:
   - **absent** → seed the whole template after the title/properties with `insert_content_after`
     (map any existing overview/result headings into §2/§3/§6).
   - **present** → section-scoped `replace_content` for changed sections only, per rules 1–4.
3. Show the draft to the user before writing.

## Non-interactive path (no interview)

When there is no human to interview, do not skip the narrative — seed it best-effort:

- §Summary, §Background, §Changes, §Verification: extract from commit messages,
  `git diff --stat`, and PR titles/descriptions.
- §Decisions **Why** and §Alternatives: if the commit bodies and PR description contain no
  evidence, **do not infer it.** Leave a `> [TODO: confirm intent with a human — why this
  approach]` callout. Neither blank nor fabricated.
- Visuals: add a diagram if the flow is visible from commits/PRs, a chart if metrics exist.
  Otherwise omit.
- The next interactive `/issue-close` fills the TODO callouts and supersedes.

> Principle: keep the format even when automated, and mark what you do not know honestly.
