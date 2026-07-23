---
name: create-document
description: When a skill or user needs to render structured HTML/MD from JSON, validate the data against a schema and substitute it into a bundled template.
when_to_use: "Use for repeated document generation, JSON-to-HTML/Markdown rendering, schema-gated card documents, and internal calls from decision-dashboard or generate-teammate. Trigger phrases: 'render this JSON as a document', 'create a dashboard from this data', 'JSON to HTML', 'JSON to Markdown', '/create-document'."
argument-hint: "--template <name> --data <json-path> --out <out-path>"
allowed-tools: Bash(python3 *) Bash(mkdir *) Bash(cp *) Bash(ls *) Read Write
disable-model-invocation: true
---

# Create Document

Render structured HTML or Markdown from JSON. This skill validates JSON data against a paired schema, then substitutes it into a bundled template.

It is a rendering engine, not a content authoring skill. Upstream skills create the content JSON; this skill validates and renders it.

## Where this fits in the workflow

```text
brainstorm / design / decision-dashboard / generate-teammate
  -> content JSON
  -> create-document
  -> validated HTML or Markdown
  -> review, user confirmation, or downstream skill
```

- Upstream skills prepare JSON.
- This skill validates the JSON and renders the matching template.
- Validation failure blocks output file creation.
- Downstream skills can trust successfully rendered artifacts as schema-checked inputs.

## Modes

Single mode: `render`.

The pipeline is deterministic:

```text
JSON -> schema validation -> template substitution -> output file
```

For validation only, call `scripts/validate.py` directly with schema and data paths.

## Standing rules

- Content creation belongs to the calling skill. Do not invent missing fields or ask the user for content.
- Validation failure means no output file.
- Use Python stdlib only. Do not add jinja2, pyyaml, or other template dependencies.
- Schema and template names are paired: `schemas/<name>.schema.json` with `templates/<name>.html` or `templates/<name>.md`.
- Prefer schema fixes over ad hoc template bypasses.

## Automated vs needs your taste

| Automated | Caller or user decides |
|---|---|
| Type, required, length, enum validation | Which template to render |
| `forbid`, `mustMatch`, and `endsWith` checks | Actual document content |
| `{{key}}` substitution and HTML escaping | New schema rules |
| Missing optional keys rendered as empty strings | Card ordering and copy tone |
| FOREACH block expansion | Whether to add a new template/schema pair |

If validation blocks a document, rewrite the data or schema deliberately. Do not bypass the gate.

## Boundaries

| This skill owns | This skill does not own |
|---|---|
| JSON structure validation | Interviewing the user |
| Schema-level forbidden-pattern checks | Extracting intent from chat |
| `{{key}}`, `{{{key}}}`, and FOREACH substitution | Designing new CSS or layouts |
| Output file writing | Deciding which content is correct |

## Directory structure

```text
create-document/
  scripts/
    render.py
    validate.py
  schemas/
    decision-dashboard.schema.json
    teammate-spawn.schema.json
  templates/
    decision-dashboard.html
    teammate-spawn.md
  references/
    before-after-card-authoring.md
    example-decision-card.json
    example-teammate-spawn.json
```

Supported use cases:

- `decision-dashboard`: HTML decision dashboard rendered for `/decision-dashboard`.
- `teammate-spawn`: Markdown teammate spawn plan rendered for `/generate-teammate`.

The legacy persona review output template has been removed from the active contract. Persona reviews must remain free-form and route through `/persona-review` subagents, not through a fixed five-block renderer.

## Interface

This skill runs on both Claude Code and Codex. Resolve its directory once, then reuse
`${SKILL_DIR}` in every command below:

```bash
# Claude Code sets CLAUDE_SKILL_DIR (direct call) or CLAUDE_PLUGIN_ROOT (internal call);
# Codex sets neither, so fall back to the Codex skills location.
SKILL_DIR="${CLAUDE_SKILL_DIR:-${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/create-document}}"
SKILL_DIR="${SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/create-document}"
```

```bash
python3 "${SKILL_DIR}/scripts/render.py" \
  --template <name> \
  --data <json-path> \
  --out <out-path>
```

| Option | Meaning |
|---|---|
| `--template <name>` | Loads paired template and schema by name |
| `--data <path>` | JSON data path |
| `--out <path>` | Output path |
| `--schema <name>` | Optional schema override |
| `--json` | Emit machine-readable result |

Exit codes:

- `0`: validation passed and file was created.
- `1`: validation failed; stderr lists field-level failures.
- `2`: usage error or missing file.

`$ARGUMENTS` follows the frontmatter argument hint: `--template ... --data ... --out ...`.

## Procedure

1. Load `schemas/<name>.schema.json`.
2. Load `--data` JSON.
3. Validate:
   - missing required fields
   - type mismatches
   - `forbid` regex hits
   - `mustMatch`, `endsWith`, `minLength`, `maxLength`, `minItems`, `maxItems`
   - `enum` and `pattern`
4. If validation passes, load the paired template.
5. Substitute:
   - `{{key}}`: escaped substitution
   - `{{{key}}}`: raw substitution for trusted caller-built HTML
   - `<!-- FOREACH key -->...<!-- END -->`: array iteration
6. Write `--out`, creating parent directories as needed.

## Schema format

The schema format supports a small JSON Schema subset plus local extensions:

- `type`
- `required`
- `properties`
- `items`
- `minLength` / `maxLength`
- `minItems` / `maxItems`
- `pattern`
- `enum`
- `forbid`
- `mustMatch`
- `endsWith`

See [schemas/decision-dashboard.schema.json](schemas/decision-dashboard.schema.json) for a complete example.

## Template rules

- `{{key}}` escapes HTML and supports dotted paths such as `background.situation`.
- `{{{key}}}` does not escape; use only for trusted caller-built fragments.
- FOREACH blocks iterate over arrays and can nest.
- Missing optional keys render as empty strings.
- Required missing keys should be caught by schema validation.

See [templates/decision-dashboard.html](templates/decision-dashboard.html) for nested FOREACH usage.

## Examples

Standalone render:

```bash
# SKILL_DIR resolved as in "## Interface".
python3 "${SKILL_DIR}/scripts/render.py" \
  --template decision-dashboard \
  --data ./decisions.json \
  --out claudedocs/PROJ-123/decisions.html
```

Internal call from decision-dashboard:

```bash
# Locate create-document from the calling skill (sibling skill on both hosts):
CD="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/create-document}"
CD="${CD:-${CODEX_HOME:-$HOME/.codex}/skills/create-document}"
python3 "${CD}/scripts/render.py" \
  --template decision-dashboard \
  --data "${TARGET_DIR}/decisions.json" \
  --out "${FILE}"
```

See:

- [references/before-after-card-authoring.md](references/before-after-card-authoring.md)
- [references/example-decision-card.json](references/example-decision-card.json)

## Downstream / persistent output

Generated files may become downstream inputs:

- decision-dashboard -> `decisions.html` -> user choices -> `decisions-final.json` -> implementation context.
- generate-teammate -> rendered teammate plan -> controlled subagent/team dispatch.

Therefore:

- Output paths follow the calling skill's convention.
- A rendered artifact implies schema validation passed.
- Do not treat failed partial output as usable context.

## Forbidden

- Generate document content or interview the user.
- Add external template libraries.
- Write output after validation failure.
- Render a template that has no paired schema.
- Bypass schema-forbidden patterns.
- Reintroduce the fixed persona review output renderer as an active contract.

## Pitfalls

| Pitfall | Symptom | Prevention |
|---|---|---|
| Template placeholder not in schema | Output silently leaves an empty field | Add the key to schema when adding a placeholder |
| Over-broad forbid regex | Valid English text is blocked | Use specific suffixes or scoped patterns |
| Raw substitution misuse | User input becomes unescaped HTML | Use `{{{key}}}` only for trusted caller-built fragments |
| FOREACH scope collision | Inner item hides an outer field | Prefer explicit field names |

## Auto-validation

`render.py` automatically runs validation. For validation only:

```bash
# SKILL_DIR resolved as in "## Interface".
python3 "${SKILL_DIR}/scripts/validate.py" \
  schemas/decision-dashboard.schema.json \
  ./decisions.json --json
```

## Self-check before publishing

Before rendering:

- [ ] `--data` is valid JSON.
- [ ] Paired schema and template exist.
- [ ] New forbidden patterns were added intentionally.
- [ ] FOREACH keys exist in the data.
- [ ] Raw substitutions use trusted fragments only.

After rendering:

- [ ] Exit code is 0.
- [ ] Output exists at the intended path.
- [ ] Optional downstream validators pass before handoff.
