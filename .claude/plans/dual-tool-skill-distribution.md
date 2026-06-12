# Dual-tool skill distribution architecture

**Started**: 2026-06-11
**Status**: planned
**Source**: `/brainstorm` (branch `docs/add-claude-md`)

## Goal

Package and distribute the Elian-Studio skill/agent toolkit so it works across **both
Claude Code and Codex**, for **public distribution**, with **per-skill à-la-carte install**,
and with the parity-maintenance burden automated away rather than done by hand.

## Decision

- **Selected: C→A staged.** Reach the end-state architecture (A: monorepo SSOT + generator
  that emits per-skill Claude plugins *and* a Codex skills tree) by way of a small spike (C:
  keep the single Claude bundle for now, but stand up the first-class Codex skills tree and
  the SSOT mechanism on one pilot skill first).
- **Rationale**: the chosen scope (public + Codex first-class + per-skill) only has one real
  end-state — A. But jumping straight to "16 per-skill plugins + a generator" is boil-the-ocean.
  C validates the risky unknowns (does plugin packaging follow symlinks? symlink-vs-copy for the
  shared SKILL.md? Codex install/update path?) on a 1-skill surface before we commit to the
  generator and the split.
- **Rejected options**:
  - **Pure dotfiles / drop the marketplace** — contradicts "public distribution". The Claude
    marketplace/plugin is the *only* public one-command-install + auto-update channel; keep it.
    (This settles thread #3: given public distribution, the plugin/marketplace IS the right
    Claude primitive.)
  - **A direct** (build the generator + split all 16 now) — correct end-state, but too much
    upfront risk/work before the SSOT and Codex mechanics are proven.
  - **B symlink, no generator** — viable *only if* Claude plugin packaging follows symlinks.
    That unknown gets tested in phase C; if symlinks survive, B becomes a lighter variant of A.

## Captured requirements

1. **Public distribution** — anyone can install. Keep the Claude marketplace + per-skill
   plugins as the public Claude channel (one-command install + `/plugin update` auto-update).
2. **Codex first-class for SKILLS** — ship a `codex/skills/<name>/SKILL.md` tree + a
   `setup.sh` that links into `~/.codex/skills` so `git pull` updates it. Retire the
   hand-mirrored `codex/prompts/` tree once skills work in Codex.
3. **Per-skill à-la-carte install + independent versioning** (end state, delivered in phase A).
4. **Single source of truth per skill** → zero manual drift between trees.
5. **Automated release ratchet** — N plugins × 2 trees is unsustainable by hand; the generator
   owns version/CHANGELOG/marketplace propagation.
6. Preserve repo invariants: English-only, never push to `main`, version discipline.

## Constraints / known limits (honest)

- **Agents stay Claude-only.** The 21 `agents/*.md` are Claude subagent (Task-spawn) format;
  Codex has no equivalent runtime (parity doc already marks `generate-teammate` Codex
  handoff-only). "Codex first-class" applies to **skills**, not agents.
- **Codex has no native auto-update.** No marketplace concept. Best achievable is git-pull-based
  (symlink `~/.codex/skills` → cloned repo, or `setup.sh` re-sync). This is option-independent.

## Phased plan

### Phase C — Spike on one pilot skill — DONE (pilot: `create-document`, 2026-06-11)
- [x] C1: Pilot = `create-document`. Canonical location = the plugin skill dir
      `plugins/elian-store/skills/create-document/` (real files; Claude needs them physically
      because plugin install copies the subtree — see verdict below).
- [x] C2: Verdict recorded. **Claude plugin install copies the plugin subtree to a versioned
      cache** (`~/.claude/plugins/cache/.../<ver>/`, no repo root, no `codex/`) → a repo-root
      symlink would NOT survive → plugin dir must hold real files (kills cross-boundary symlink
      SSOT / Option B for the Claude side). **Codex `~/.codex/skills` DOES follow symlinks**
      (proven: `~/.codex/skills/paperclip` → external repo resolves). So: plugin dir = SSOT;
      `codex/skills/create-document` = relative symlink into it; both read one `SKILL.md`.
- [x] C3: `codex/setup.sh` written (idempotent; backs up non-symlink targets to `.bak.<ts>`).
      Installs `~/.codex/skills/<name>` → `<repo>/codex/skills/<name>` symlink; `git pull` updates.
- [x] C4: Retired `codex/prompts/create-document.md`; updated parity doc, root `README.md`,
      `codex/README.md` (also fixed pre-existing `pr-writer` omission in codex/README lists).
- [x] C5: Validated. SKILL.md made host-agnostic (no `CLAUDE_PLUGIN_ROOT`/`CLAUDE_SKILL_DIR`
      hard dep). Codex-sim (both env vars unset): resolver finds render.py and a real
      `teammate-spawn` render returns exit 0 / verdict PASS / 116-line output. setup.sh replaced
      the stale broken `~/.codex/skills/create-document` copy with the working symlink.

### Phase A — Generator + thematic-cluster plugins (granularity decided 2026-06-12)

**Granularity = THEMATIC CLUSTERS, not pure per-skill.** Phase C + investigation proved the
skills compose, so per-skill plugins would break composition on Claude (each plugin has its own
`$CLAUDE_PLUGIN_ROOT`; no inter-plugin dependency mechanism):
- `create-document` is a render engine called by `decision-dashboard` + `generate-teammate`.
- `skills/_shared/execution-strategy.md` is used by `fix` + `improve` + `implement`.
- `agents/` (21) are plugin-level: `generate-teammate` needs 14 domain agents, `persona-review`
  needs the 7 `persona-*` agents.
So the installable unit is the composition cluster, not the single skill.

**SSOT stays `plugins/elian-store/skills/<name>/` + `agents/` + `skills/_shared/`** (no churn-move
to a top-level `skills/`). The generator reads a cluster manifest and emits derived trees.

**Proposed cluster manifest** (config — easy to revise; lives in `tools/clusters.json`):
| Plugin | Skills | Bundled agents | Codex-portable |
|---|---|---|---|
| `elian-artifacts` | create-document, decision-dashboard, generate-teammate, brainstorm | 14 domain agents | all but generate-teammate (handoff-only) |
| `elian-tdd` | implement, fix, improve (+ `_shared`) | — | yes |
| `elian-review` | review, persona-review, verify-implementation, manage-skills | 7 `persona-*` agents | yes |
| `elian-design` | design-ui, document-writer, ai-assisted-feature-development | — | design-ui, aafd (document-writer Claude-only) |
| `elian-harness` | harness-manager, pr-writer | — | pr-writer (harness-manager Claude-only) |

**BREAKING-CHANGE RISK:** splitting the published `elian-store` plugin orphans existing installs.
Generator emits to `dist/` (gitignored) — live `plugins/elian-store/` is untouched until a
deliberate cutover. Cutover strategy (deprecate elian-store as a meta-pointer vs hard cut) is a
separate decision, NOT in this kickoff.

- [x] A1: `tools/clusters.json` manifest + `tools/generate.py` generator. DONE — report-only by
      default; `--emit` writes `dist/`, `--apply-codex` creates symlinks. `dist/` gitignored.
- [x] A2: Generator capabilities DONE: (a) lint SKILL.md for bare `${CLAUDE_*}` inside bash fences —
      **caught 2 previously-missed broken skills (`manage-skills`, `verify-implementation`), now
      fixed**; (b) codex/skills symlink status (10 portable skills still "missing" = next migration);
      (c) emit 5 thematic plugins + `marketplace.json` to `dist/`; (d) validate emitted JSON + SKILL.md.
- [x] A3: DONE — emitted 5 plugins; composition preserved (elian-artifacts holds create-document +
      both callers + 14 agents; elian-tdd holds `_shared`; elian-review holds 7 persona agents);
      cross-validated with the repo ruby YAML/JSON smoke tests; no `__pycache__` leak.
- [x] A4 DONE (2026-06-12): `--bump {patch|minor|major}` bumps `plugin.json` + the marketplace
      `elian-store` entry (metadata.version untouched) and scaffolds a dated CHANGELOG stub; the
      default run gates **version drift** (fails if plugin.json != marketplace entry). Single command
      `tools/generate.py --bump patch --emit` = bump → build → validate. Tested 2.11.2→2.11.3, reverted.
- [x] Remaining-skill migration DONE (2026-06-12): migrated 9 of the 10 reported "missing" skills to
      `codex/skills/` symlinks (`--apply-codex`), retired their prompts, updated docs. `persona-review`
      reclassified to `prompt_only` (subagent dispatch is its core, like `generate-teammate`).
      **Codex catalog = 12 shared skills + 2 prompts**; `document-writer`/`harness-manager` Claude-only.
- [x] A5 DECIDED (2026-06-12): **no cutover** — keep `elian-store` as the single published plugin.
      The 5-plugin split fails the repo's own portfolio bar (no audience/permission/cadence
      divergence), reverses the v2.0.0 per-skill→bundle consolidation, and has no graceful migration
      path (marketplace lacks deprecate/replaces; removal would silently orphan installs). The split
      stays staged in `dist/`, gated on a future divergence trigger. Decision recorded in
      `docs/plugin-portfolio-hybrid-model.md` ("Split decision (2026-06-12)").

**Dual-tool distribution effort: COMPLETE.** Codex = 12 shared skills + 2 prompts (host-agnostic
SSOT, drift-free); `tools/generate.py` does lint + codex-sync + version-drift gate + release bump +
staged 5-plugin emit. The thematic split is a ready-when-needed capability, not a live distribution.

## Open questions
- ~~Does Claude Code plugin install follow symlinks?~~ **ANSWERED (C2):** install copies the
  plugin subtree to a versioned cache, so a repo-root symlink does not survive. Plugin dir holds
  real files; only the Codex side symlinks into it. Option B (cross-boundary symlink SSOT) is dead.
- ~~Does Codex `~/.codex/skills` follow symlinks?~~ **ANSWERED (C2): yes**, proven on this machine.
- **Still open (phase A):**
  - Per-skill plugins + per-plugin SessionStart update hook = N hooks per session. One shared updater?
  - Plugin **name collisions** in a public marketplace — generic names like `review` likely need an
    `elian-` namespace prefix.
  - `marketplace.json` `metadata.version` vs N per-entry versions at scale.
  - ~~Carry-over portability fix for `design-ui`, `decision-dashboard`, `generate-teammate`.~~
    **DONE (2026-06-12):** all three made host-agnostic (no bare `CLAUDE_PLUGIN_ROOT`/`CLAUDE_SKILL_DIR`).
    `design-ui` + `decision-dashboard` migrated to `codex/skills/` symlinks (prompts retired);
    `generate-teammate` kept as a prompt (Codex cannot reproduce teammate-spawn — handoff-only).
    Codex catalog is now 11 prompts + 3 shared skills. Validated under Codex-sim (env vars unset).
  - **Windows:** committed symlinks need `core.symlinks=true` on checkout; decide whether the
    generator should emit real copies for Windows installers instead of symlinks.

## Brainstorm record

### Probed questions
- Q: Audience (personal / team / public)? → A: **Public distribution**
- Q: How serious is Codex support (first-class / best-effort / shrink)? → A: **First-class (Claude-equal)**
- Q: Packaging granularity (one bundle / thematic / per-skill)? → A: **Per-skill individual**
- Q: Which architecture? → A: **C→A staged**

### Key reframe from Phase 1 recon
The Claude plugin/marketplace is not overhead — it is the public install + auto-update channel
(`/plugin install`, `/plugin update`, SessionStart version-check hook, plugin.json as cache key).
The real pain is (1) the manual 4-file release ratchet and (2) the Codex side being second-class
(manual `cp`, prompts-only, drift tracked by hand). The fix targets those, not the plugin itself.
