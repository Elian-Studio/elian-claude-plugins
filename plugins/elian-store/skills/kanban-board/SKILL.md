---
name: kanban-board
description: >
  Generates a self-contained, interactive HTML Kanban board — draggable
  columns/cards, a card detail panel (assignee, due date, labels, checklist,
  comments, linked files), search/filters, and a theme switcher — from the
  project's own local task data: a spec.json from /intake-spec, a roadmap or
  PRD from /design-feature, a plan file under .claude/plans/, or tasks
  described directly in chat. No GitHub/GitLab/Jira connection is used; the
  board is one HTML file that runs offline with no server, and in-board edits
  persist via localStorage plus an Export/Import JSON control for committing
  snapshots back to the repo.

  Use when the user asks to make a kanban board, generate a board for a
  project or issue, turn a plan into a board, visualize tasks as a board,
  wants a Trello-style view of an existing plan or backlog, or wants to track
  ad-hoc internal tasks without wiring up an external issue tracker. Also use
  to refresh a board this skill already generated after its source changes.
when_to_use: >
  A project, feature, or plan already has — or is being given right now — a
  list of tasks to track, and the user wants a visual, draggable board rather
  than a markdown checklist or a Mermaid roadmap. Skip for a single flat TODO
  list with no need for columns/status, and skip anything that needs to sync
  with a real issue tracker (no GitHub/GitLab/Jira integration by design —
  point the user at that tracker's native board instead).
argument-hint: "[label] [source-file?] [output-dir?]"
allowed-tools: Bash(python3 *) Bash(open *) Bash(mkdir *) Bash(git branch*) Read Write Edit Glob Grep
disable-model-invocation: true
---

# Kanban Board Generator

Turn a project's task list into one self-contained, interactive HTML Kanban
board. No backend, no issue-tracker API — the board is a static file that
holds its own data and edits itself via `localStorage`, with an
Export/Import JSON control as the escape hatch for moving a snapshot back
into the repo.

## What this is not

This does **not** sync with GitHub Issues, GitLab Issues, or Jira. If the
user wants a board that stays live-synced with an external tracker, say so
plainly and point them at that tracker's own board view — building a sync
layer is out of scope by design (that's real integration work: auth, webhook
or polling, conflict resolution — not a lazy afternoon feature). This skill
covers the common internal case: a project has a plan, and the user wants to
*see and move* that plan, not wire it to an external system.

Each invocation produces **one board = one HTML file**. If the user wants
several boards (one per project), generate several files — there is no
multi-board dashboard shell to manage; that would be solving a problem
("track many boards centrally") the user didn't ask for.

## Where this fits in the workflow

```text
intake-spec / design-feature / .claude/plans/*.md / chat description
  -> kanban-board
  -> (user works the board in-browser; re-run this skill later to pull in new cards)
```

## Data model

The board is one JSON object: `title`, `theme`, `members[]`, `labels[]`,
`lists[]` (each with an ordered `cardIds`), and `cards{}` keyed by id. Full
field reference and a worked example: [references/board-schema.md](references/board-schema.md).

Keep ids short, stable, url-safe slugs (`c1`, `be`, `todo`) — they are the
merge key on regeneration and the localStorage/DOM key at render time.

Due dates carry a raw ISO `date`, not a precomputed "overdue" label — the
template computes soon/overdue/normal client-side against the viewer's real
clock, so status never goes stale between generation and viewing.

## Workflow

### 1. Resolve label and output paths

```bash
LABEL="${1:-$(git branch --show-current | grep -oE '[A-Za-z0-9._-]+$' || echo board)}"
OUT_DIR="${3:-claudedocs/kanban}"
TARGET_DIR="${OUT_DIR}/${LABEL}"
DATA="${TARGET_DIR}/board.json"
FILE="${TARGET_DIR}/board.html"
mkdir -p "${TARGET_DIR}"
```

### 2. Gather cards

Pick one source, in order of what's actually available — don't ask the user
to choose between options that don't apply:

- **Explicit source given** (`$2`, or the user names a file/skill output):
  read it. A `/intake-spec` `spec.json` maps `requirements[]` /
  `acceptanceCriteria[]` to cards in a `To do`/`In progress`/`Review`/`Done` list
  set. A `/design-feature` roadmap or PRD: pull the task/phase breakdown.
  A `.claude/plans/{issue}.md`: pull its checklist/step items.
- **`${DATA}` already exists** (regenerating): read it — see Merge below.
- **Nothing to read and no source named**: ask the user for a board title
  and either a short list of cards or "start empty" — don't invent tasks
  they didn't mention. Default lists: `To do`, `In progress`, `Review`, `Done`
  (matches the Kanflow reference this skill's visuals are based on; swap to
  English list names if the user's source/chat is in English).

### 3. Merge (regeneration only)

When `${DATA}` already exists, merge is **additive only**:

- Keep every existing card, list membership, checklist check-state, and
  comment exactly as-is — the user may have edited them in-browser and
  exported that JSON back over this file.
- Add cards for new source items whose derived id doesn't already exist in
  `cards{}` (append to the first/default list).
- Never overwrite an existing card's fields from the source, even if the
  source text changed — surface that as a note to the user instead of
  silently clobbering an edit they might have made. Overwriting on every
  regenerate would make in-board edits pointless.

### 4. Write the data file, then render

Write `${DATA}` (schema in [references/board-schema.md](references/board-schema.md)), then render:

```bash
python3 "${CLAUDE_PLUGIN_ROOT:-$(dirname "$0")/../..}/skills/kanban-board/scripts/build_board.py" \
  --data "${DATA}" \
  --out "${FILE}"
```

`build_board.py` validates cross-references (every `cardIds` entry exists in
`cards{}`, every `card.assignee` exists in `members[]`, every id in
`card.labels` exists in `labels[]`) before rendering — a dangling reference
would otherwise render as a silently blank chip in the browser. It fails
loudly with the offending id if validation doesn't pass; fix `${DATA}` and
re-run rather than editing the generated HTML by hand.

### 5. Report

Tell the user the path to `${FILE}`, that it opens directly in any browser
(`file://`, no server needed), and how persistence works: edits autosave to
that browser's localStorage; the "Export" button downloads the
current state as `board.json` — replace `${DATA}` with that download and
re-run this skill later to keep evolving the board without losing edits.
Open it only with explicit approval:

```bash
open "${FILE}"
```

## Forbidden

- Building any GitHub/GitLab/Jira API call, webhook, or polling loop for
  this skill — out of scope by design, not a missing feature.
- Hand-editing the generated `board.html` instead of `board.json` +
  `build_board.py` — edits get lost on the next regenerate and drift from
  the template.
- Inventing cards, assignees, or due dates the source/user never mentioned.
- Overwriting existing card fields on regenerate (see Merge above).
- Adding external JS framework or build-step dependencies to
  `assets/kanban-board-template.html` — it must stay a single file that
  opens with zero setup.

## Pitfalls

| Pitfall | Symptom | Prevention |
|---|---|---|
| Card/list/member/label id collisions across merges | Cards render duplicated or overwrite each other silently | Derive ids as stable slugs from source content (e.g. issue key, slugified title), never sequential counters that shift between runs |
| Regenerating clobbers user edits | User loses checklist progress or comments after a re-run | Follow the additive-only merge rule in step 3; never overwrite existing cards |
| Unescaped card text | A title/comment containing `<` or `&` breaks the rendered page | `build_board.py` only moves JSON as data (`JSON.stringify`-safe embed); the template's own render functions HTML-escape every field — don't change that when editing the template |
| Forgetting to mention persistence model | User expects edits to "just save to the repo" and is confused when they don't survive a fresh clone | Always explain the localStorage + Export/Import model when reporting the output path |

## Supporting files

| File | Role |
|---|---|
| [scripts/build_board.py](scripts/build_board.py) | Validates board data and renders it into the template |
| [assets/kanban-board-template.html](assets/kanban-board-template.html) | The single-file board app (vanilla JS/CSS, no framework, no build step) |
| [references/board-schema.md](references/board-schema.md) | Full JSON field reference |
| [references/example-board.json](references/example-board.json) | Worked example to copy the shape from |

## Self-check before publishing

- [ ] `build_board.py` ran clean (no dangling id errors).
- [ ] Every card came from the named source or the user's own words — nothing invented.
- [ ] Regeneration (if applicable) added cards without touching existing ones.
- [ ] User was told the output path and how persistence/export works.
- [ ] The file opens and renders with no server (`open` used only with approval).
