---
name: skill-dispatcher
description: "Opt-in router for elian-store. When explicitly invoked, inspect the user's request and recommend the smallest relevant skill path instead of relying on per-skill trigger discovery alone."
when_to_use: "Use only when the user explicitly asks which elian-store skill to use, invokes /skill-dispatcher, or wants a routing recommendation before starting work. Do NOT auto-invoke for ordinary coding, review, planning, or documentation requests; choose the relevant skill directly when intent is already clear."
argument-hint: "<request-or-goal> [--mode quick|full]"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
---

# /skill-dispatcher - Opt-in elian-store router

This skill helps a user choose the right `elian-store` skill before work starts. It is deliberately opt-in: do not use it as a mandatory preamble, do not expand scope on behalf of the user, and do not invoke downstream skills automatically.

## Parameters

| Option | Meaning | Default |
|---|---|---|
| `<request-or-goal>` | The user's task, question, or unclear goal | Current conversation |
| `--mode quick\|full` | `quick` returns one recommendation; `full` returns ranked alternatives | `quick` |

## Core Rules

- Be a router, not an orchestrator. Recommend the next skill; do not run it.
- Prefer the smallest skill that fits the stated intent.
- If the user already named a skill, validate the fit and call out only material mismatches.
- Keep recommendations grounded in the current `plugins/elian-store/skills/*/SKILL.md` frontmatter and purpose text.
- Respect platform boundaries. If a flow depends on Claude subagents, MCP, hooks, or global harness files, say so before recommending it for Codex.
- Default to "no special skill needed" when the task is small, self-contained, or already clear.

## Procedure

1. Parse the request:
   - goal: planning, coding, fixing, improving, reviewing, verifying, documenting, designing, harness maintenance, PR writing, decision support, or teammate planning
   - side effects: read-only, write-artifact, code-changing, external/system-changing
   - ambiguity: clear, fuzzy, or blocked by decisions
   - platform: Claude plugin, Codex, or unknown
2. Read relevant skill frontmatter or nearby purpose text when the fit is not obvious.
3. Choose the recommendation:
   - `brainstorm` for fuzzy ideas or ambiguous requests before implementation.
   - `decision-dashboard` for three or more pending decisions that need a concise artifact.
   - `ai-assisted-feature-development` for feature framing/spec/test/context artifacts before code.
   - `design-ui` for UI/UX design artifacts before implementation.
   - `implement` for new feature work with approval-gated TDD.
   - `fix` for confirmed bugs needing root-cause analysis and regression tests.
   - `improve` for behavior-changing improvements to something that already works.
   - `review` for read-only engineering review of code, diffs, PRs, or files.
   - `verify-implementation` for pre-ship verification orchestration.
   - `manage-skills` for verify-skill drift maintenance.
   - `generate-teammate` for deciding direct/subagent/team execution and rendering handoff prompts.
   - `create-document` for schema-validated JSON-to-HTML/Markdown rendering.
   - `document-writer` for polished self-contained HTML/Markdown documents.
   - `persona-review` for persona-lens critique of a plan, document, or idea.
   - `harness-manager` for Claude/Codex global harness drift.
   - `pr-writer` for PR/MR title and body drafting.
   - `skill-dispatcher` only for this routing step.
4. Return the routing recommendation. Stop after the recommendation unless the user explicitly asks to continue with the selected skill.

## Output Contract

For `--mode quick`:

```text
Recommendation: /elian-store:<skill>
Why: <one or two concrete reasons>
Boundary: <what this skill should not absorb>
Next command: /elian-store:<skill> <suggested arguments>
```

For `--mode full`:

```text
Primary: /elian-store:<skill>
Why: <reason>

Alternatives:
- /elian-store:<skill>: <when this would be better>
- No special skill: <when direct work is enough>

Platform notes:
- <Claude/Codex limitation or "None">
```

If no skill is appropriate:

```text
Recommendation: no special skill
Why: <reason>
Next step: <direct action>
```

## Forbidden

- Do not require every task to pass through this skill.
- Do not chain into another skill without user confirmation.
- Do not create a new process when the request clearly maps to one existing skill.
- Do not use Korean trigger phrases or non-English skill metadata.
- Do not claim hard enforcement. This is an LLM-level routing aid, not an architectural gate.
