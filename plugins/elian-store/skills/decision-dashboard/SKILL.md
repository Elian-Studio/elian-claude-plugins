---
name: decision-dashboard
description: "When 3+ pending decisions block PO/team progress, capture them in a printable HTML artifact so the team can decide in 5 minutes instead of long chat threads. Replaces scattered decision fatigue with one page, all options, traceable choice, memo, and downloadable JSON for downstream skills."
when_to_use: "Use when 3+ architecture, DDL, UX, consistency, or product decisions pile up in review; when the user asks to make a decision dashboard or lay out the choices; or when chat explanations are too long to inline. Skip for 1-2 decisions and ask directly in chat."
argument-hint: "[issue-id] [output-dir?] [mode?]"
allowed-tools: Bash(cp *) Bash(open *) Bash(date *) Bash(git branch*) Bash(mkdir *) Bash(rm claudedocs/*) Bash(python3 *) Edit Read Write
---

# Decision Dashboard Generator

Create a printable HTML artifact for three or more pending decisions. The decision-maker should be able to choose A/B/C/D in about five minutes, then export a JSON record that downstream skills can use.

This skill owns content assembly: collect decision candidates from context, write the JSON, then delegate JSON validation and rendering to `create-document`.

## Where this fits in the workflow

```text
brainstorm / design / review
  -> decision-dashboard
  -> implement / review / ship
```

- **Upstream**: brainstorm, design, or review surfaces multiple decisions.
- **This skill**: turns those decisions into a schema-validated dashboard and final JSON.
- **Downstream**: implementation and shipping skills read `decisions/{ISSUE}-final.json` to understand what was decided and why.

## What's automated vs what needs your taste

| Automated | User decides |
|---|---|
| Card numbering | Per-card option choice |
| P0/P1/P2 priority draft | Whether each option is correctly framed |
| Option labels rewritten from implementation terms to outcome terms | When to use Other / custom input |
| Language gate filtering of internal identifiers | Whether to defer a decision |
| Background skeleton | Whether new options are needed |

If automation is wrong, the user corrects via memo or revised options. A card with `D (Other)` and an empty memo must not be published as final.

## Modes

- `generate` (default): create JSON, validate it, render the HTML dashboard.
- `finalize`: merge user-exported choices with original card data, persist final JSON, and clean disposable HTML.

## Auto-invoke vs explicit

Use automatically when:

- Three or more decisions need confirmation.
- One decision explanation is too long to keep in chat.
- Review output surfaces several architecture, DDL, consistency, or UX decisions.

Explicit triggers:

- `/elian-store:decision-dashboard`
- "make a decision dashboard"
- "lay out the choices"

Do not invoke for:

- One or two decisions.
- Simple yes/no confirmation.
- A one-way implementation recommendation that can be answered in chat.

## Output location

Default:

```text
{output-dir}/{ISSUE_ID}/decisions-{YYYY-MM-DD-HHmm}.html
```

Output directory precedence:

1. `$ARGUMENTS[1]`
2. `DECISIONS_DIR`
3. `claudedocs`

Filenames include hour and minute to avoid collisions.

## Card-body authoring rules

Decision cards are for a decision-maker who may not know the code. Card body text must describe product-perspective situations, not implementation internals.

`create-document` enforces the main data rules with `decision-dashboard.schema.json`. The rendered HTML is then checked by `scripts/validate-dashboard.py`.

### Forbidden in card body

| Category | Examples |
|---|---|
| Class or method names | `OrderRefundScheduler`, `isNightTime()` |
| Table or column names | `user_lock`, `next_compute_dtm` |
| File paths or commit hashes | `overview.md`, `59623a8e7` |
| Internal acronyms | `BULK`, `AUTO_RULE`, `send_source` |
| Requirement or decision IDs | `R3`, `#38`, `decision #44` |
| Stack-specific names | `ShedLock`, `cron`, `@SchedulerLock` |
| Environment names | `stag`, `prod` |

The `detail-panel` developer rationale area is the exception; it may include technical identifiers.

### Background skeleton

Each card uses three JSON fields:

1. `background.situation`: a concrete product scene.
2. `background.pain`: the cost of not deciding; must include a number or concrete cost word such as fail, miss, delay, or blocked.
3. `background.divergence`: how the user's experience changes depending on the choice.

### Option-label rules

Option labels should end with what becomes different, not what code will be written.

| Bad | Good |
|---|---|
| Generalize scheduler | Both failed sends recover immediately |
| Add distributed lock dependency | Multi-server rollout processes each request once |
| Replace with polling | Admin condition changes apply right away |

### Judgment-question rule

Use one decision question ending in `?`. Avoid abstract axes. Ask the concrete choice the decision-maker must make.

### Other option

`D (Other)` is injected by the template. The JSON includes only A/B/C options unless there is a deliberate schema change.

Worked examples:

- [references/example-good-card.md](references/example-good-card.md)
- [../create-document/references/example-decision-card.json](../create-document/references/example-decision-card.json)

## Priority colors

| Class | Meaning |
|---|---|
| `p0` | Blocks startup; decide now |
| `p1` | Implementation blocker |
| `p2` | Can be decided after build starts |

The JSON `priority` value is lowercase `p0`, `p1`, or `p2`. Display labels are separate.

## Mode 1 procedure: `generate`

1. Set paths:

```bash
ISSUE="${1:-$(git branch --show-current | grep -oE '[A-Z]+-[0-9]+' || echo decision)}"
OUT_DIR="${2:-${DECISIONS_DIR:-claudedocs}}"
DATE=$(date +%Y-%m-%d-%H%M)
TARGET_DIR="${OUT_DIR}/${ISSUE}"
FILE="${TARGET_DIR}/decisions-${DATE}.html"
JSON="${TARGET_DIR}/decisions.json"
mkdir -p "${TARGET_DIR}"
```

2. Write `${JSON}` from the current context.

Card shape:

```json
{
  "issue": "PROJ-123",
  "branch": "feat/...",
  "date": "2026-05-22-1430",
  "title": "Decision dashboard",
  "subtitle": "Review and choose A/B/C",
  "priority_groups": [
    {
      "priority": "p0",
      "label": "P0 - blocks start",
      "cards": [
        {
          "card_id": "c1",
          "num": 1,
          "open_class": " open",
          "title": "Card title with no internal identifiers",
          "background": {
            "situation": "Concrete product scene",
            "pain": "Cost with a number or concrete failure/delay wording",
            "divergence": "How the user experience differs"
          },
          "judgment_question": "What should the user experience be?",
          "options": [
            {"key": "A", "label": "Outcome-focused label", "rec_badge": "<span class=\"rec-badge\">Recommended</span>"},
            {"key": "B", "label": "Outcome-focused label"},
            {"key": "C", "label": "Outcome-focused label"}
          ]
        }
      ]
    }
  ]
}
```

3. Render through `create-document`:

```bash
# Locate create-document (sibling skill on both Claude Code and Codex):
CD="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/create-document}"
CD="${CD:-${CODEX_HOME:-$HOME/.codex}/skills/create-document}"
python3 "${CD}/scripts/render.py" \
  --template decision-dashboard \
  --data "${JSON}" \
  --out "${FILE}"
```

4. Validate rendered HTML:

```bash
# SKILL_DIR = this skill's own directory on either host:
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/decision-dashboard}}"
SKILL_DIR="${SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/decision-dashboard}"
python3 "${SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}"
```

5. Open the file only with user approval:

```bash
open "${FILE}"
```

6. Tell the user to choose options in the dashboard and provide the downloaded JSON or Markdown path for finalize.

## Mode 2 procedure: `finalize`

Input:

```bash
ISSUE="$1"
USER_JSON="$2"
OUT_DIR="${DECISIONS_DIR:-claudedocs}"
TARGET_DIR="${OUT_DIR}/${ISSUE}"
ORIGINAL_JSON="${TARGET_DIR}/decisions.json"
FINAL_JSON="${TARGET_DIR}/decisions-final.json"
```

Merge user choices with original card data:

- Iterate `decisions[]` from the user's export.
- Add original `judgment_question`, recommendation, and rejected alternatives.
- Compute `summary.total`, `summary.by_priority`, `summary.other_chosen`, and `summary.recommended_match_rate`.
- Write `decisions-final.json`.

Clean disposable HTML only after final JSON is written:

```bash
rm "${TARGET_DIR}"/decisions-*.html
```

Keep the original `decisions.json` unless the user explicitly asks to remove it; it is useful for audit and recovery.

## End-of-skill reflection

After finalize, report observations rather than praise:

```text
Persisted 5 decisions.

Patterns noticed:
- Recommended option matched 4/5 choices, which may mean the recommendations were calibrated or the user was time-constrained.
- All P0 choices favored immediacy over load, which may be useful as a default axis for the next decision set.
- 0 custom memos may mean the options fit, or memo entry may be too much friction.

Persisted at: <FINAL_JSON_PATH>
Disposable HTML cleaned up.
```

Use three short observations at most, with hedged language.

## Forbidden

- Hand-write HTML card blocks instead of JSON.
- Add external CDN or JS libraries.
- Modify `create-document/templates/decision-dashboard.html` as part of ordinary generation.
- Create separate review/version HTML files.
- Delete disposable HTML before the user has decided.
- Publish a final decision where `D (Other)` has an empty memo.
- Put implementation identifiers in card body outside the detail panel.

## Pitfalls

| Pitfall | Symptom | Prevention |
|---|---|---|
| Hard-coding `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_SKILL_DIR}` (both unset on Codex) | Wrong script path on non-Claude hosts | Resolve `SKILL_DIR` with the `:+`/`:-` fallback shown above; own scripts use `SKILL_DIR`, create-document uses the sibling `CD` resolver |
| Internal identifiers leak into JSON | Schema or language gate fails | Rewrite card text from product perspective |
| Missing `open_class` | All cards render collapsed | First card uses `" open"`, others use empty string |
| Recommendation badge on every option | Recommendation loses meaning | Add `rec_badge` only to one option |
| Empty Other memo in final export | Decision cannot be interpreted | Ask for memo before finalize |

## Auto-validation

Stage 1: input JSON validation through create-document.

Stage 2: rendered HTML validation:

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/decision-dashboard}}"
SKILL_DIR="${SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/decision-dashboard}"
python3 "${SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}"
python3 "${SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}" --json
```

HTML gates:

1. `placeholders`: no unresolved `{{...}}`.
2. `nested_comments`: no nested HTML comments.
3. `navlink_card_match`: every nav-link target matches a card.
4. `language_gate`: no internal identifiers in card body.

## Supporting files

| File | Role |
|---|---|
| [scripts/validate-dashboard.py](scripts/validate-dashboard.py) | Rendered HTML validator |
| [references/example-good-card.md](references/example-good-card.md) | BEFORE/AFTER card comparison |
| [references/example-card-snippet.html](references/example-card-snippet.html) | Legacy single-card HTML design reference |
| [../create-document/templates/decision-dashboard.html](../create-document/templates/decision-dashboard.html) | Master HTML template |
| [../create-document/schemas/decision-dashboard.schema.json](../create-document/schemas/decision-dashboard.schema.json) | Input JSON schema |
| [../create-document/references/example-decision-card.json](../create-document/references/example-decision-card.json) | Good JSON example |

## Self-check before publishing

- [ ] Stage 1 create-document render validation passes.
- [ ] Stage 2 dashboard validator passes all four gates.
- [ ] A non-technical decision-maker can understand every card body.
- [ ] Every `background.pain` includes concrete cost language.
- [ ] Every judgment question is answerable.
- [ ] Option labels state outcomes.
- [ ] Only the first card uses `open_class: " open"`.
- [ ] Priority classification is reasonable.
- [ ] Final JSON records choices and rejected alternatives.
