# Board data schema

One JSON object, written to `board.json` and rendered by `scripts/build_board.py`
into the single-file app in `assets/kanban-board-template.html`. Worked example:
[example-board.json](example-board.json).

## Top level

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | yes | Shown in the header and browser tab title. |
| `id` | string | no | Slug used as the localStorage key and export filename. Auto-derived from `title` if omitted — set it explicitly if you regenerate a board and want to keep the same slug even after a title edit. |
| `theme` | `"cobalt"` \| `"sage"` \| `"grape"` | no | Defaults to `cobalt`. Purely cosmetic; the user can also switch it in the browser (persisted). |
| `members` | array | no | `{ "id": "ks", "name": "Seojun Kim" }`. Avatar color is auto-derived from `id`, no color field needed. |
| `labels` | array | no | `{ "id": "be", "name": "Backend", "color": "#1d4ed8", "bg": "#dbeafe" }`. `color`/`bg` optional — auto-derived from `id` if omitted; set them explicitly when a label's meaning benefits from a fixed color (e.g. always render "Bug" in red). |
| `lists` | array | **yes**, non-empty | Columns, left to right in array order. |
| `cards` | object | **yes** | Keyed by card id. Every id must be referenced by exactly one list's `cardIds` — an unreferenced card is rejected as an orphan, a card referenced by two lists is rejected as a conflict. |

## `lists[]`

```json
{ "id": "todo", "title": "To do", "cardIds": ["c1", "c2"] }
```

`cardIds` order is display order top-to-bottom. The stats bar (done/in progress/overdue
rollup) treats list id `done` as "completed" and `doing` as "in progress" —
using those two ids unlocks the rollup; any other ids still work fine, the
board just shows the total count without the done/doing/overdue split.

## `cards{}`

```json
"c1": {
  "title": "JWT refresh token flow",
  "desc": "Longer description, plain text (line breaks preserved).",
  "assignee": "ks",
  "due": "2026-07-05",
  "labels": ["be"],
  "checklist": [{ "text": "Issue endpoint", "done": true }],
  "comments": [{ "author": "pd", "text": "...", "time": "yesterday" }],
  "files": [{ "name": "design.png", "url": "" }]
}
```

| Field | Type | Notes |
|---|---|---|
| `title` | string | required |
| `desc` | string | plain text, no markdown rendering |
| `assignee` | string \| `null` | must match a `members[].id` |
| `due` | `"YYYY-MM-DD"` \| `null` | **raw date only** — the template computes overdue/soon/normal client-side against the viewer's real clock each time the page loads, so never write a precomputed status or label here |
| `labels` | string[] | each must match a `labels[].id` |
| `checklist` | array | `{ "text": "...", "done": bool }` |
| `comments` | array | `{ "author": "...", "text": "...", "time": "..." }` — `author` is a **display name string**, not a `members[].id` (the renderer doesn't resolve it against `members[]`); `time` is a free display string (`"yesterday"`, `"2026-07-01"`), not parsed |
| `files` | array | `{ "name": "...", "url": "..." }` — `url` optional; a link the user can already reach (repo-relative path, doc URL). This is not a file upload — don't invent a URL that doesn't exist. |

## Deliberately not in the schema

- **No external issue-tracker ids/URLs.** This skill doesn't sync with
  GitHub/GitLab/Jira — don't add a `sourceUrl` field implying two-way sync
  that doesn't exist.
- **No per-card color override beyond labels.** Keep card visuals derived
  from labels/theme, not one-off inline colors — that's how every generated
  board stays visually consistent.
- **No board-level member/label management from the browser UI.** New
  members/labels are added by re-running this skill with updated
  `board.json`, not from inside the rendered page — the in-browser UI only
  lets the user add cards/lists/checklist items/comments/links to the set
  already defined at generation time.
