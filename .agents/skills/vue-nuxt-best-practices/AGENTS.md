# Vue Nuxt Best Practices Maintainer Guide

This skill pack is for Vue 3 and Nuxt 3/4 applications. Do not add React, Next.js, or Vercel-platform-specific rules unless they are explicitly framed as a contrast or migration note.

## Repository Pattern

Follow the Vercel agent-skills pattern:

- `SKILL.md` is the on-demand entrypoint and router.
- `rules/` contains focused rule files.
- `references/` contains supporting documentation links and notes.
- Keep long explanations out of `SKILL.md`.

## Rule File Requirements

Each rule file should include:

- YAML frontmatter with `title`, `impact`, and `tags`
- a short rule statement
- when to apply it
- incorrect and correct examples when code shape matters
- verification guidance
- official references when behavior is version-sensitive

Impact values:

- `CRITICAL`
- `HIGH`
- `MEDIUM-HIGH`
- `MEDIUM`
- `LOW-MEDIUM`
- `LOW`

## Quality Bar

- Prefer official Vue and Nuxt behavior over community folklore.
- Separate confirmed code evidence from assumptions.
- Avoid broad client-only or global-state fallbacks.
- Keep examples concise and valid for Vue 3/Nuxt 3+.
- Do not claim tests were run unless there is evidence.
