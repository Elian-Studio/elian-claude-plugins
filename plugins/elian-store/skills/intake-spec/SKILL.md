---
name: intake-spec
description: >
  Front door for any feature, fix, or refactor: captures requirements and
  optionally links to a GitHub / GitLab / JIRA issue. Works without any issue
  tracker — requirements text alone is sufficient. Auto-detects authenticated
  providers (gh, glab, JIRA MCP) and fetches issue context when available.
  Produces a structured spec.json and hands off to /design-feature.

  Use at the very start of any non-trivial work. Trigger phrases: "I want to
  build X", "let's plan Y", "plan this requirement", "start from this issue",
  or when the user pastes a GitHub / GitLab / JIRA URL or issue key and wants
  to turn it into a design spec. Also use when no issue exists at all — just
  describe the requirement and this skill structures it.
when_to_use: >
  User is starting a new feature, fix, or design exploration without a JIRA
  dependency. Phrases: "plan this feature", "intake this requirement", "let's
  design X", "start from scratch with this idea", "I have a GitHub issue for
  this", "here's the GitLab ticket". Also triggers when a GitHub / GitLab /
  JIRA URL or bare issue key is pasted and the user says "let's work on this"
  or "start from here". If the user already has a spec.json, skip directly to
  /design-feature.
argument-hint: "[<issue-url-or-key>] [--label <slug>]"
allowed-tools: Bash(bash *) Bash(sh *) Bash(gh issue view*) Bash(glab issue view*) Bash(mkdir *) Bash(cat *) Read Write Glob ToolSearch
---

# intake-spec — Requirements Front Door

## Purpose

Capture what needs to be built, link it to an issue tracker if one exists, and
produce a `spec.json` that `design-feature` can consume.

The pipeline never starts coding — that is downstream. This skill ends when
the user has a structured spec and knows where the design pipeline picks up.

## Phase 0 — Parse input

Extract from the user message:

- **Issue URL or key** — any of:
  - `https://github.com/<org>/<repo>/issues/<n>`
  - `https://gitlab.com/<path>/-/issues/<n>` or `<org>/<repo>#<n>` or `!<n>`
  - `MPT-####`, `PROJ-####` (JIRA format)
  - bare `#<n>` (infer from current git remote)
- **--label <slug>** — override the generated label (used as the folder name)
- **Free text** — if no URL/key, treat the entire input as the requirement

If the input contains an issue reference → Phase A.
Otherwise → Phase B.

## Phase A — Issue fetch (optional)

### A1. Detect available provider

```bash
bash "${SKILL_DIR}/scripts/detect_provider.sh"
```

Returns one of: `gitlab`, `github`, `jira`, `none`.

| Provider | Command |
|----------|---------|
| `github` | `gh issue view <number> --repo <org/repo> --json title,body,labels,state` |
| `gitlab` | `glab issue view <number> --repo <namespace/project> -F json` |
| `jira`   | Use `mcp__atlassian__getJiraIssue` — load via ToolSearch first |
| `none`   | Skip issue fetch; treat the pasted text as the requirement body |

### A2. Absorb issue content

Read: title, description/body, acceptance criteria, labels, state.

Summarise in one paragraph and show the user: *"This issue is about X. I understand it as: [summary]. Is that right?"*

Correct the summary if the user pushes back, then continue to Phase C.

## Phase B — Requirements interview

No issue tracker. Gather the minimum needed for a good spec.

Ask at most **one question per turn**. Prioritise the biggest unknown first.
Questions to work through (stop when you have enough):

1. What problem does this solve for the user, and how do they handle it today?
2. What is the simplest version that would be good enough?
3. What must explicitly NOT be included (scope boundary)?
4. Are there performance, security, or integration constraints?
5. Who are the primary users / stakeholders of this feature?

Read the codebase when you can answer a question yourself — do not ask the
user for information that grep or Read can find.

Once you have enough, confirm: *"Here is what I'm capturing — [summary]. Ready to write the spec?"*

## Phase C — Write spec.json

Generate the label if not supplied: prefer the issue key (e.g., `GH-42`,
`GL-99`, `MPT-9419`), otherwise slugify the title (e.g., `feat-auth-redesign`).

Write to: `claudedocs/plans/<label>/spec.json`

```json
{
  "label": "<issue-key-or-slug>",
  "title": "One-line title",
  "provider": "github|gitlab|jira|none",
  "issueUrl": "https://...",
  "requirements": [
    "Requirement sentence 1",
    "Requirement sentence 2"
  ],
  "constraints": [
    "Must not break existing X",
    "Must work offline"
  ],
  "outOfScope": [
    "Payments are out of scope for this iteration"
  ],
  "context": "Relevant codebase findings: service X does Y, table Z exists"
}
```

All fields except `issueUrl` are required. `requirements` must have at least
one item. `outOfScope` can be empty (`[]`) if nothing was explicitly excluded.

Show the spec to the user. Offer to edit before proceeding.

## Phase D — Hand off

Once the spec is confirmed:

```
spec saved → claudedocs/plans/<label>/spec.json

Next step:
  /design-feature <label>

Or with a start point:
  /design-feature <label> --start-from phase3
```

Do not start design work here. Hand off cleanly.

## Standing rules

- Never fabricate issue content. If provider detection fails, report it and
  fall through to Phase B (free-text interview).
- One question at a time in Phase B. Batching questions reduces answer quality.
- Read the codebase first; ask the user second.
- The spec is a contract, not a summary. `requirements` items must be specific
  enough that a developer can later check whether they are satisfied.
- `outOfScope` is as important as `requirements` — it prevents scope creep
  during design.
