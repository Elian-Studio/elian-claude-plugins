---
name: decision-dashboard
description: When 3+ pending decisions block PO/team progress, capture them in a printable HTML artifact so the team can decide in 5 minutes instead of long Slack threads. Replaces "decision fatigue scattered across messages" with "one page, all options, traceable choice + memo + downloadable JSON for downstream skills".
when_to_use: 3+ decisions pile up in a review (architecture / DDL / UX / consistency), the user says "make a decision dashboard" / "lay out the choices", or chat explanations are too long to inline. Skip for 1-2 decisions (just ask in chat).
argument-hint: [issue-id] [output-dir?] [mode?]
allowed-tools: Bash(cp *) Bash(sed *) Bash(grep *) Bash(awk *) Bash(diff *) Bash(open *) Bash(date *) Bash(git branch*) Bash(mkdir *) Bash(rm claudedocs/*) Bash(python3 *) Edit Read Write
---

# Decision Dashboard Generator

When 3+ decisions pile up and the decision-maker (PO / team lead) cannot read every chat thread to the bottom, this skill captures the decisions as a **single printable HTML artifact** so the team can pick A/B/C in 5 minutes. The decisions are then persisted as JSON for downstream skills.

---

## Where this fits in the workflow

```
brainstorm → design → ▶ DECISION-DASHBOARD ◀ → implement → review → ship
                          (artifact-forcing
                           moment for taste)
```

- **Upstream skills** (brainstorm / design / review) surface the decisions.
- **This skill** turns those decisions into a printable HTML page and persists them as JSON.
- **Downstream skills** (implement / ship) read `decisions/{ISSUE}-final.json` to know "what was decided and why" as context.

---

## What's automated vs what needs your taste

(Following gstack's "What can the model safely decide alone, and what needs human taste?" principle.)

| Claude decides automatically | User decides |
|------------------------------|--------------|
| Card numbering (c1, c2, …) | Per-card option choice (A/B/C/D) |
| P0/P1/P2 priority classification | Whether each option's definition is right |
| Option label rewrite (impl-term → outcome-term) | When to use "Other (custom input)" |
| LANGUAGE GATE filtering (block internal identifiers) | Defer / push a decision to a later session |
| Background's 3-sentence skeleton applied | Propose new options when offered ones don't fit |

If automation gets something wrong, the user corrects via memo. Cards with `D (Other)` selected and an empty memo are blocked from publishing.

---

## Modes

This skill supports two explicit modes. If the first argument matches a mode keyword, it's that mode; otherwise the default is `generate`.

### Mode 1: `generate` (default)

Create cards from 3+ decisions and produce the HTML dashboard.

**When**: first capture of decisions for an issue. New decisions accumulating.

**Output**: `{OUT_DIR}/{ISSUE}/decisions-{DATE}.html`

### Mode 2: `finalize`

Receive the JSON / MD result from the user, persist the decision, and clean up the disposable HTML.

**When**: the user finished selecting on the dashboard and says "apply these".

**Output**:
- `{OUT_DIR}/{ISSUE}/decisions-final.json` — **persistent**, consumed by downstream skills
- `{OUT_DIR}/{ISSUE}/decisions-{DATE}.html` — **deleted** (disposable UI layer)

---

## Auto-invoke vs explicit

**Auto-invoke**:
- 3+ decisions awaiting user confirmation
- One decision's explanation is too long to inline in chat
- Review output (consistency / architecture / DDL / UX) surfaces multiple decisions

**Explicit invocation**:
- `/elian-store:decision-dashboard`
- "make a decision dashboard", "lay out the choices"

**Do NOT invoke when**:
- 1-2 decisions → just ask in chat (AskUserQuestion or short Markdown)
- Simple yes/no confirmation → just ask
- One-way choice on an implementation suggestion → short answer

---

## Output location

Default path:
```
{output-dir}/{ISSUE_ID}/decisions-{YYYY-MM-DD-HHmm}.html
```

Without an issue ID:
```
{output-dir}/decisions/{descriptive-name}-{YYYY-MM-DD-HHmm}.html
```

`{output-dir}` precedence:
1. `$ARGUMENTS[1]` (explicit override)
2. `DECISIONS_DIR` env var
3. `claudedocs` (default)

Filenames include hour-minute (HHmm) so multiple runs in one day on one issue don't collide.

---

## Standing rules — card-body authoring

(These rules apply to every card always; they are standing instructions, not procedure.)

A decision document is **not a conversation**. The decision-maker (PO / team lead / future-self) doesn't read code. They have 5 minutes to pick A or B. So the card body (title / background / judgment axis / option labels) describes **product-perspective real situations** only.

### Forbidden in card body

| Forbidden category | Examples |
|--------------------|----------|
| Class / method names | `OrderRefundScheduler`, `isNightTime()`, `UserCampaignTagSendScheduler` |
| Table / column names | `user_lock`, `next_compute_dtm`, `send_dtm` |
| File paths / commit SHAs | `overview.md §4`, `architecture.html §04-2`, `59623a8e7` |
| Internal acronyms | `BULK`, `AUTO_RULE`, `send_source`, `FILTER_CRITERIA` |
| Requirement / decision IDs | `R3`, `R6`, `#38`, `#A4`, `decision #44` |
| Stack-specific names | `ShedLock`, `cron`, `@SchedulerLock`, `polling`, `@Scheduled` |
| Environment names | `stag`, `prod`, `PR` (use plain language: "before production deploy") |

> The example tokens are illustrative. Apply the same standard to your project's class names / stack and exclude them from card bodies.

The forbidden tokens are allowed **only inside the collapsible details panel** (`detail-trigger` + `detail-panel`) — that's the developer-rationale area.

### Background's 3-sentence skeleton

1. **What's happening in the product right now** — one concrete user-or-admin-perspective scene.
2. **Pain if no decision is made** — one concrete number or scenario. (e.g., "9,750 charged instead of 9,800")
3. **How the two options diverge in the user's experience** — what users feel.

### Option-label rules

End with **"what becomes different"**, not **"what we do"**.

| Bad (impl jargon) | Good (outcome) |
|-------------------|----------------|
| A. Generalize — `OrderRefundScheduler` handles source-agnostic | A. Both refunded together — auto-send failures recover immediately |
| A. Add upfront — pull in distributed-lock dep | A. Add now — multi-server rollout post-launch processes each request once |
| A. Replace with polling — expiry polling | A. Switch to immediate — admin condition changes apply right away |

### Judgment-question rule

Use a **decision question**, not an "axis". A 1-sentence question the decision-maker must answer. Avoid abstractions like "trade A for B"; use concrete situational questions: "When the admin changes the condition, should it apply right away, or is next-day acceptable?"

### "Other — custom input" option is mandatory

The last option of every card is always `D. Other — fill in below`. The memo accepts free text.

> Worked example: [`references/example-good-card.md`](references/example-good-card.md) — BEFORE / AFTER comparison.
> HTML snippet: [`references/example-card-snippet.html`](references/example-card-snippet.html) — copy-paste ready.

---

## Priority colors

| Class | Color | Meaning |
|-------|-------|---------|
| `pip-p0` / `pri-tag-p0` | Red | Blocks startup (decide now) |
| `pip-p1` / `pri-tag-p1` | Yellow | Implementation blocker |
| `pip-p2` / `pri-tag-p2` | Blue | Decidable after build starts |

Card numbers (cN) are a single sequence across priorities. `data-key` / `id` / `data-group` / `data-memo` must all match.

---

## Mode 1 procedure: `generate`

```bash
# 1. Set variables
ISSUE="${1:-$(git branch --show-current | grep -oE '[A-Z]+-[0-9]+' || echo decision)}"
OUT_DIR="${2:-${DECISIONS_DIR:-claudedocs}}"
DATE=$(date +%Y-%m-%d-%H%M)
TARGET_DIR="${OUT_DIR}/${ISSUE}"
FILE="${TARGET_DIR}/decisions-${DATE}.html"

# 2. Create output directory + copy template
mkdir -p "${TARGET_DIR}"
cp "${CLAUDE_SKILL_DIR}/template.html" "${FILE}"

# 3. Substitute simple placeholders
BRANCH=$(git branch --show-current 2>/dev/null || echo main)
sed -i '' \
  -e "s|{{ISSUE_ID}}|${ISSUE}|g" \
  -e "s|{{BRANCH}}|${BRANCH}|g" \
  -e "s|{{DATE}}|${DATE}|g" \
  -e "s|{{DASHBOARD_TITLE}}|Decision Dashboard|g" \
  -e "s|{{DASHBOARD_SUBTITLE}}|Review and pick the options below|g" \
  "${FILE}"
```

Then:
4. Collect decision items (from chat context or decision notes).
5. Classify each as P0 / P1 / P2.
6. `{{NAV_GROUPS}}` / `{{DECISION_SECTIONS}}` are large blocks — substitute via the **Edit tool** (`sed` doesn't handle multi-line well). Use `references/example-card-snippet.html` as the per-card pattern.
7. **Validate**: `python3 "${CLAUDE_SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}"` — all 4 gates must pass before publishing.
8. Open in browser: `open "${FILE}"`.
9. Tell the user: "Pick options in the browser → download JSON/MD → paste the path so we can finalize."

> `${CLAUDE_SKILL_DIR}` is auto-substituted by Claude Code with the skill's install path. The plugin lives in a cache directory, so do not hardcode absolute paths.

---

## Mode 2 procedure: `finalize`

User finished picking on the dashboard and downloaded the JSON / MD. They say "apply these".

```bash
# 1. Parse args: <ISSUE> <user-downloaded-json-path>
ISSUE="$1"
USER_JSON="$2"
OUT_DIR="${DECISIONS_DIR:-claudedocs}"
TARGET_DIR="${OUT_DIR}/${ISSUE}"
FINAL_JSON="${TARGET_DIR}/decisions-final.json"

# 2. Copy user JSON to persistent storage + add metadata
python3 "${CLAUDE_SKILL_DIR}/scripts/finalize.py" \
  --input "${USER_JSON}" \
  --output "${FINAL_JSON}" \
  --issue "${ISSUE}"

# (finalize.py is currently not bundled — Claude does the JSON transform inline:
#  for each card in user JSON, add {decided_at, source: dashboard} metadata and write to FINAL_JSON.)

# 3. Clean up the disposable HTML
rm "${TARGET_DIR}"/decisions-*.html

# 4. Report to user (see "End-of-skill reflection" below)
```

`decisions-final.json` schema:
```json
{
  "issue": "PROJ-123",
  "decided_at": "2026-04-28T10:30:00+09:00",
  "decisions": [
    {
      "card_id": "c1",
      "title": "...",
      "priority": "P0",
      "choice": "A",
      "choice_label": "...",
      "memo": "",
      "rejected_alternatives": [
        {"key": "B", "label": "..."},
        {"key": "C", "label": "..."}
      ],
      "judgment_question": "..."
    }
  ],
  "summary": {
    "total": 5,
    "by_priority": {"P0": 2, "P1": 2, "P2": 1},
    "other_chosen": 0
  }
}
```

Downstream skills (`/implement`, `/ship`, etc.) read this JSON for "what was decided and why" context.

---

## End-of-skill reflection (Mode 2 close)

**Don't praise. Observe patterns.**
(Following gstack's *"After /office-hours, the model reflects on what it noticed about how you think — not generic praise, but specific callbacks"*.)

Right after JSON persistence, report to the user in this shape:

```
5 decisions persisted. Patterns I noticed:

- 4 of 5 picks matched the recommended option → either the recommendation is well-calibrated,
  or the user was time-pressed. Try a future session without "recommended" labels and see if the rate holds.
- Both P0 picks chose "immediacy > load" → the user / product trends toward immediacy over latency.
  May be safe to default future axis-of-this-shape to immediacy.
- 0 memos written → either offered options fit perfectly, or memo authoring felt like overhead.
  If "Other (D)" picks are also 0%, the latter is likely.

Persisted at: {FINAL_JSON_PATH}
HTML cleaned up.
```

3 items, each = 1-sentence observation + 1-sentence hypothesis / suggestion. Hedge with "may be" / "worth comparing" so guesses don't read as facts.

---

## Forbidden

- ❌ Adding external CDN / library (Google Fonts is already bundled in the template — exception).
- ❌ Producing artifacts beyond the single HTML — except `decisions-final.json` in finalize mode (intentionally persistent).
- ❌ Editing the template's CSS variables (visual consistency).
- ❌ Separate review / version files (`decisions-{date}-v2.html`, etc.).
- ❌ **Nested HTML comments** (`<!-- ... <!-- ... --> ... -->`). The first `-->` closes the outer comment and exposes the rest. Inline notes use plain parentheses.
- ❌ Deleting the HTML before finalize (the user may not have decided yet).
- ❌ Publishing a card with `D (Other)` selected and an empty memo — request memo input first.

---

## Pitfall / Known issues (regression prevention)

### Pitfall 1: Nested HTML comment leak

**Symptom**: An example card / HTML hidden inside a comment is displayed at the top of the body area.

**Cause**: An outer `<!-- DECISION_SECTIONS:START guide -->` containing an inner `<!-- recommended only -->` — the inner's `-->` closes the outer.

**Prevention**: Remove every nested `<!-- -->` from the template body. New cards must use plain-text inline notes.

### Pitfall 2: Awkward scroll to collapsed cards

**Symptom**: Clicking a sidebar link shows only the small head right below the viewport top.

**Cause**: Card body collapsed via `max-height: 0` so the default `<a href="#cN">` anchors to the head's top.

**Prevention**: Template JS auto-expands the card on nav-link click and smooth-scrolls (`scrollTo({top: rect.top - 24})`). When adding nav-links, verify `data-id="cN"` matches the card.

### Pitfall 3: Confusing `${CLAUDE_PLUGIN_ROOT}` with `${CLAUDE_SKILL_DIR}`

**Symptom**: `cp ${CLAUDE_PLUGIN_ROOT}/skills/decision-dashboard/template.html …` fails on the cache path.

**Cause**: Inside a plugin SKILL.md, when referencing the skill's own assets, `CLAUDE_SKILL_DIR` is the safe variable.

**Prevention**: Always use `${CLAUDE_SKILL_DIR}/template.html`, `${CLAUDE_SKILL_DIR}/scripts/...`, `${CLAUDE_SKILL_DIR}/references/...`.

---

## Auto-validation

Validate the generated HTML against 4 gates. Failure blocks publishing.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}"
```

Chainable JSON output:
```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate-dashboard.py" "${FILE}" --json
```

Gates:
1. **placeholders** — 0 unresolved `{{...}}`.
2. **nested_comments** — 0 nested HTML comments.
3. **navlink_card_match** — every nav-link `data-id` matches an actual card `id`.
4. **language_gate** — 0 internal-identifier exposure in card body (`info-box`, `card-title`, `.opt`). The `.detail-panel` is exempt (developer-rationale area).

> The LANGUAGE GATE pattern list is editable directly in `scripts/validate-dashboard.py` at `LANGUAGE_GATE_PATTERNS`. Add your project's internal acronyms / framework annotations there.

---

## Supporting files

| File | Role |
|------|------|
| [`template.html`](template.html) | Master HTML template with `{{...}}` placeholders. Copy and substitute. |
| [`scripts/validate-dashboard.py`](scripts/validate-dashboard.py) | 4-gate validator. `--json` for chaining. stdlib only. |
| [`references/example-good-card.md`](references/example-good-card.md) | BEFORE / AFTER card comparison — own-rule violation vs pass. |
| [`references/example-card-snippet.html`](references/example-card-snippet.html) | A single good-card HTML fragment — paste into `{{DECISION_SECTIONS}}`. |

---

## Self-check before publishing (human-readable)

Before publishing, verify all 8 items:

- [ ] All 4 gates of `validate-dashboard.py` PASS.
- [ ] The decision-maker (PO / team lead) can understand every card body without reading code or DB.
- [ ] Every card background has at least one concrete number or scenario.
- [ ] Every judgment question is answerable on the spot.
- [ ] Every option label ends in "what becomes different".
- [ ] Every card ends with the "Other — custom input" option.
- [ ] Priority (P0 / P1 / P2) classification is reasonable.
- [ ] (Mode 2) `decisions-final.json` records every decision and rejected alternatives.
