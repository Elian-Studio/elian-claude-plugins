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

### Phase A — Generalize to SSOT + generator (after C validates)
- [ ] A1: Decide SSOT layout (`skills/<name>/` as source of truth) and write the `build`
      generator: emits Claude per-skill plugins (`plugins/<name>/` + per-skill `plugin.json`
      + `marketplace.json` with N entries) and the Codex skills tree, and propagates
      version/CHANGELOG.
- [ ] A2: Resolve shared resources — where do `agents/`, `_shared/`, and `hooks/` live in a
      per-skill world? (Shared "elian-agents" plugin? bundle-per-skill? single shared updater
      instead of 16 SessionStart hooks?)
- [ ] A3: Migrate all 16 skills to SSOT; generate both trees.
- [ ] A4: Release automation — single command: bump → build → validate (YAML + JSON smoke tests).
- [ ] A5: Update README/docs for per-skill install; decide the fate of the `elian-store` bundle
      (deprecate, or keep as a documented "install these N" meta-entry).

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
