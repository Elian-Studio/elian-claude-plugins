# gstack-Based Skill Portfolio Review

Date: 2026-05-29

## Scope

Review this repository's Claude skill bundle and Codex prompt tree against `garrytan/gstack` as an operating-pattern reference, not as a byte-for-byte template.

References:

- `garrytan/gstack` repository: https://github.com/garrytan/gstack
- gstack skill catalog: https://github.com/garrytan/gstack/blob/main/docs/skills.md
- gstack root skill routing / preamble model: https://github.com/garrytan/gstack/blob/main/SKILL.md

## gstack Pattern Summary

gstack is strongest as a lifecycle portfolio. Its catalog covers product reframing, planning, engineering review, browser QA, shipping, deployment verification, canary monitoring, benchmarking, security, documentation, retrospectives, memory, and safety guardrails.

The relevant transferable patterns are:

| Pattern | gstack signal | What this repo should copy |
|---|---|---|
| Lifecycle coverage | `/office-hours`, `/spec`, `/review`, `/qa`, `/ship`, `/land-and-deploy`, `/canary`, `/retro` | Make gaps visible across product -> implementation -> QA -> release -> learning |
| Role clarity | each command has a specialist persona and one job | Keep every skill's public purpose narrow and non-overlapping |
| Artifact continuity | design/spec/review outputs feed downstream skills | Preserve durable outputs and handoff payloads |
| Browser-visible QA | `/browse`, `/qa`, `/design-review` use real pages/screenshots | Add a first-class QA/browser verification lane |
| Release discipline | `/ship`, `/land-and-deploy`, `/canary`, `/benchmark` | Separate release readiness from implementation |
| Learning loop | `/learn`, `/context-save`, `/context-restore`, `/retro` | Capture reusable project preferences and post-run learnings |
| Safety guardrails | `/careful`, `/freeze`, `/guard` | Keep destructive operations explicit and gated |

## Current Assessment

Verdict: **Structurally healthy with lifecycle gaps**.

The current bundle is structurally healthy: all frontmatter is expected to parse as YAML, and every bundled skill has scripts and/or references. However, compared with gstack's lifecycle coverage, the bundle is concentrated around planning, implementation, document generation, engineering review, and verification orchestration. It does not yet have first-class release, browser QA, post-deploy monitoring, benchmarking, security, or learning commands.

## Skill Matrix

| Current skill | gstack nearest role | Fit | Gap |
|---|---|---|---|
| `brainstorm` | `/office-hours`, `/spec` | Good | Could more explicitly emit backlog-ready spec handoff |
| `ai-assisted-feature-development` | `/spec`, plan reviews | Good | Broad scope; should remain planning/artifact focused, not implementation |
| `design-ui` | `/design-consultation`, `/design-html` | Mostly good | Needs real browser/design QA follow-up lane |
| `decision-dashboard` | plan review / decision artifact | Good | Strong artifact continuity; keep it narrow |
| `implement` | implementation phase before `/review` | Good | Downstream `/ship` is referenced but not present |
| `fix` | `/investigate`, `/qa` | Good | Has root-cause/TDD posture but lacks live browser QA loop |
| `improve` | improvement + review | Good | Needs measured before/after verification integration |
| `generate-teammate` | multi-agent routing | Platform-specific | Strong Claude fit; Codex parity should be plan-only unless delegation exists |
| `create-document` | doc generation utility | Good utility | Best kept as deterministic script wrapper |
| `manage-skills` | skill maintenance / learning hygiene | Good | Could learn from gstack's generated-doc/catalog-drift checks |
| `verify-implementation` | `/health`, verification orchestrator | Mostly good | Should not pretend to replace QA/release/canary |
| `persona-review` | `/review`, plan review variants | Good | Read-only critique is clear; complements but does not replace engineering review |
| `review` | `/review` | Good | Read-only engineering findings are covered; keep fixes and release behavior out of scope |

## Portfolio Gaps

| Gap | Why it matters | Recommended follow-up |
|---|---|---|
| Browser QA | gstack's `/qa` and `/browse` make UI verification concrete | Add `/qa` or `/browser-qa` with screenshot/report artifacts |
| Release readiness | gstack separates implementation from `/ship` | Add `/ship` for branch sanity, tests, changelog, PR creation |
| Merge/deploy verification | gstack has `/land-and-deploy` plus canary checks | Document as future, not immediate, unless deployment targets exist |
| Benchmark/performance | gstack tracks page load and before/after regressions | Add later only after QA/browser foundations exist |
| Security review | gstack has `/cso` for OWASP/STRIDE style audits | Add `/security-review` after review/QA baseline |
| Learning/memory | gstack has `/learn`, `/retro`, context save/restore | Add a lightweight learning capture pattern after workflows stabilize |
| Codex parity | gstack includes a `/codex` second-opinion bridge | Keep current Codex tree as prompt/config, not a plugin; port only high-value read-heavy workflows first |

## Recommended Follow-up PR Order

1. Add `/qa` or `/browser-qa`: browser-visible test/report workflow with screenshot artifacts and regression-test handoff.
2. Add `/ship`: branch sanity, local verification, changelog/version check, push/PR creation; no deploy.
3. Add `/learn` or `/retro`: capture repeated preferences, failure modes, and project-specific rules.
4. Add `/security-review`, `/benchmark`, and deploy/canary skills only after the above have real usage patterns.

Completed:

- `/review`: read-first engineering review with PR-ready findings and no release behavior.

## Operating Rule

Do not add every gstack command by name. Add a new skill only when this repository has a concrete local workflow, validation path, and artifact contract for it. Until then, document the gap rather than shipping a shallow command.
