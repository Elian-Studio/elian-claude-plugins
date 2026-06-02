# /create-document - Schema-validated document rendering (Codex Port)

Install path: `~/.codex/prompts/create-document.md`.

Invocation:

```text
/create-document --template <name> --data <json-path> --out <out-path> [--schema <name>] [--json]
```

Arguments arrive as `$ARGUMENTS`.

This is the Codex-native companion to `plugins/elian-store/skills/create-document/SKILL.md`. The `codex/` tree is independent, so Claude skill changes require manual parity review.

Read-only contract: do not edit files, create files, stage, commit, push, or run destructive commands. Output the rendered artifact or a concise validation report only. If implementation work is needed, hand off to `/implement`, `/fix`, `/improve`, or `/verify-implementation` and stop.

## Purpose

Render a structured HTML or Markdown document from caller-provided JSON by validating the data against the paired schema first, then substituting it into the selected template.

This is a rendering engine, not a content authoring skill and not an implementation skill. Upstream work prepares the JSON. This prompt validates and renders only.

## Common Contract

1. Validate before rendering. Invalid data blocks output.
2. Do not invent missing content, repair structure by guesswork, or ask the user to write the document body from scratch.
3. Use the selected schema/template pair as the source of truth.
4. Keep the pipeline deterministic: schema check, then render, then deliver.
5. If the request needs code or product implementation, hand off instead of absorbing that work.
6. End with one next question, next action, or validation result.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `--template <name>` | Template/schema pair to render | required |
| `--data <json-path>` | JSON input path or caller-provided JSON payload | required |
| `--out <path>` | Intended output path for the rendered artifact | required |
| `--schema <name>` | Explicit schema override when needed | template name |
| `--json` | Emit machine-readable validation/render status | off |

`$ARGUMENTS` always wins over any local default.

## Workflow

```text
Phase 1: Input recognition
Phase 2: Schema/template resolution
Phase 3: Validation
Phase 4: Rendering
Phase 5: Delivery
```

### Phase 1: Input recognition

Determine whether the caller supplied:

- a template name
- a JSON file path
- an output path
- an explicit schema override

If any required input is missing, ask the single most important question and stop.

### Phase 2: Schema/template resolution

Resolve the paired schema and template for the selected name.

- `decision-dashboard` -> HTML dashboard artifact
- `teammate-spawn` -> Markdown teammate spawn artifact

If a paired schema/template does not exist, stop and report that the request is unsupported.

### Phase 3: Validation

Validate the JSON before rendering.

Check for:

- missing required fields
- type mismatches
- enum violations
- pattern violations
- length and item-count bounds
- forbidden patterns or reserved content when defined by the schema

Validation failure means no artifact output.

### Phase 4: Rendering

Render only after validation passes.

- Preserve the schema-defined field names and shape.
- Do not infer absent content.
- Do not mix in implementation work, CSS redesign, or product decisions.
- Treat the output as a deterministic artifact, not a draft.

### Phase 5: Delivery

Return the rendered artifact or a compact validation report.

If the caller asked for a path-oriented handoff, report the intended output path and the validation status instead of inventing a file write outside the prompt contract.

## Output Contract

Default output:

```text
Document summary
- Template: <name>
- Schema: <name>
- Validation: <passed / failed>
- Output: <path or none>

Key decisions
- <rendering decision 1>
- <rendering decision 2>

Open questions
- <unresolved input or missing field>

Next
- <next question or next action>
```

Validation failure output:

```text
Validation summary
- Template: <name>
- Schema: <name>
- Status: failed

Problems
- <field-level failure 1>
- <field-level failure 2>

Next
- Provide corrected JSON or choose a supported template
```

## Supported Use Cases

- `decision-dashboard`: artifact-first HTML decision dashboard generation.
- `teammate-spawn`: artifact-first Markdown teammate spawn plan generation.

The legacy fixed five-block review renderer is not part of the active contract. Persona review remains a separate prompt path and must stay free-form.

## Forbidden

- Inventing missing document content.
- Skipping validation.
- Rendering unsupported template/schema pairs.
- Reintroducing the legacy fixed review-output contract.
- Mixing implementation work into document generation.
- Writing files or modifying the repository.

## Pre-Output Self-Check

- [ ] Required inputs are present.
- [ ] Schema/template pair is supported.
- [ ] Validation ran before rendering.
- [ ] Missing fields were not invented.
- [ ] The output ends with one next question or next action.
