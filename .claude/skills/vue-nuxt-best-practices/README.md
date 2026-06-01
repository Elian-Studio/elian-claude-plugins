# Vue Nuxt Best Practices

A rules-based Agent Skill pack for writing, reviewing, refactoring, and optimizing Vue 3 and Nuxt 3/4 applications.

The structure follows the same broad pattern as Vercel's `agent-skills`: `SKILL.md` routes the agent, while `rules/` holds focused guidance that can be loaded only when relevant.

## Structure

- `SKILL.md` - skill entrypoint and rule router
- `AGENTS.md` - maintainer guidance for this skill pack
- `metadata.json` - skill metadata and rule categories
- `rules/` - one focused rule file per area
- `references/` - official documentation links and version-sensitive references

## Rule Areas

- SSR and hydration
- Nuxt data fetching
- Vue component architecture
- Vue/Nuxt performance
- Nitro server boundaries
- State management
- Accessibility and UX
- Testing

## Creating A New Rule

1. Copy `rules/_template.md` to `rules/<area>-<topic>.md`.
2. Use one of the section prefixes in `rules/_sections.md`.
3. Keep the rule narrowly scoped.
4. Include evidence, incorrect/correct examples, and verification guidance when applicable.
5. Link official Vue/Nuxt docs when behavior is version-sensitive.

## Intended Use

Use this pack when an agent is working on Vue 3 or Nuxt 3/4 code and needs framework-specific guidance rather than React/Next.js defaults.
