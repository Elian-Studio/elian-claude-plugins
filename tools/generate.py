#!/usr/bin/env python3
"""Phase A generator for the elian-claude-plugins thematic-cluster distribution.

Claude source: plugins/elian-store/skills/<name>/ + plugins/elian-store/agents/ +
skills/_shared/. Codex shared skills point to that source by symlink; prompt-only
adapters remain independent. Driven by tools/clusters.json. Report-only by default;
mutations are behind flags.

Usage:
  python3 tools/generate.py              # validate manifest + lint + codex status + cluster plan
  python3 tools/generate.py --emit       # also emit thematic plugins + marketplace.json to dist/
  python3 tools/generate.py --apply-codex  # also create missing codex/skills/<name> symlinks
  python3 tools/generate.py --bump patch --emit  # release: bump version + CHANGELOG stub, then build

Exit codes: 0 ok, 1 manifest invalid, 2 lint violations, 3 emit/validate failure, 4 version error.
Stdlib only (no pyyaml / external deps).
"""
import argparse
import datetime
import json
import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "tools" / "clusters.json"
PLUGIN_JSON = REPO / "plugins" / "elian-store" / ".claude-plugin" / "plugin.json"
MARKET_JSON = REPO / ".claude-plugin" / "marketplace.json"
CHANGELOG = REPO / "CHANGELOG.md"
SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

# Bare ${CLAUDE_PLUGIN_ROOT} / ${CLAUDE_SKILL_DIR} with NO ':' inside the braces
# (a ':-' / ':+' fallback is host-agnostic and allowed). Only checked inside bash fences.
BARE_VAR = re.compile(r"\$\{CLAUDE_(?:PLUGIN_ROOT|SKILL_DIR)\}")


def fail(code, msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def load_manifest():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return m


def discover_skills(skills_dir: Path):
    return sorted(
        p.name for p in skills_dir.iterdir()
        if p.is_dir() and not p.name.startswith(("_", "."))
    )


def validate_manifest(m, skills):
    errors = []
    skills_set = set(skills)
    assigned = {}
    for plugin, cfg in m["plugins"].items():
        for s in cfg["skills"]:
            if s not in skills_set:
                errors.append(f"{plugin}: lists unknown skill '{s}'")
            if s in assigned:
                errors.append(f"skill '{s}' assigned to both '{assigned[s]}' and '{plugin}'")
            assigned[s] = plugin
        grp = cfg.get("agents")
        if grp and grp not in m["agent_groups"]:
            errors.append(f"{plugin}: unknown agent group '{grp}'")
    orphans = skills_set - set(assigned)
    for s in sorted(orphans):
        errors.append(f"skill '{s}' is not assigned to any plugin")
    # agent files exist
    agents_dir = REPO / m["source"]["agents_dir"]
    for grp, names in m["agent_groups"].items():
        for a in names:
            if not (agents_dir / f"{a}.md").is_file():
                errors.append(f"agent group '{grp}': missing file {a}.md")
    # Codex disposition lists reference real skills and are mutually exclusive.
    disposition_owner = {}
    for key in ("claude_only", "prompt_only", "deferred"):
        for s in m["codex"].get(key, []):
            if s not in skills_set:
                errors.append(f"codex.{key}: unknown skill '{s}'")
            if s in disposition_owner:
                errors.append(
                    f"codex disposition overlap: '{s}' is in both "
                    f"'{disposition_owner[s]}' and '{key}'"
                )
            disposition_owner[s] = key
    return errors


def lint_skill(skill_md: Path):
    """Return list of (lineno, text) bare-var violations inside bash/sh fences."""
    violations = []
    in_bash = False
    for i, line in enumerate(skill_md.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            lang = stripped[3:].strip().lower()
            if not in_bash:
                in_bash = lang in ("bash", "sh", "shell")
            else:
                in_bash = False
            continue
        if in_bash and BARE_VAR.search(line):
            violations.append((i, line.strip()))
    return violations


def codex_disposition(skill, m):
    if skill in m["codex"].get("claude_only", []):
        return "claude-only"
    if skill in m["codex"].get("prompt_only", []):
        return "prompt"
    if skill in m["codex"].get("deferred", []):
        return "deferred"
    return "skill"


def codex_status(skills, m, lint_map):
    """Return list of (skill, state) for skills that should be codex symlinks."""
    skills_dir_rel = m["source"]["skills_dir"]
    rows = []
    for s in skills:
        if codex_disposition(s, m) != "skill":
            continue
        link = REPO / "codex" / "skills" / s
        want = Path("../..") / skills_dir_rel / s
        if lint_map.get(s):
            rows.append((s, "BLOCKED (lint)"))
        elif link.is_symlink() and os.readlink(link) == str(want):
            rows.append((s, "ok"))
        elif link.exists() or link.is_symlink():
            rows.append((s, "wrong-target"))
        else:
            rows.append((s, "missing"))
    return rows, skills_dir_rel


def apply_codex(rows, skills_dir_rel):
    created = 0
    for s, state in rows:
        if state != "missing":
            continue
        link = REPO / "codex" / "skills" / s
        link.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(str(Path("../..") / skills_dir_rel / s), str(link))
        print(f"  linked codex/skills/{s}")
        created += 1
    print(f"  ({created} symlink(s) created; prompt retirement + docs are still manual)")


def emit_dist(m, skills, lint_map):
    src_plugin = REPO / "plugins" / "elian-store" / ".claude-plugin" / "plugin.json"
    src_market = REPO / ".claude-plugin" / "marketplace.json"
    base = json.loads(src_plugin.read_text(encoding="utf-8"))
    market = json.loads(src_market.read_text(encoding="utf-8"))
    version = base["version"]
    skills_dir = REPO / m["source"]["skills_dir"]
    agents_dir = REPO / m["source"]["agents_dir"]
    shared_dir = REPO / m["source"]["shared_dir"]
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")

    dist = REPO / "dist" / "marketplace"
    if dist.exists():
        shutil.rmtree(dist)
    (dist / ".claude-plugin").mkdir(parents=True)

    entries = []
    for name, cfg in m["plugins"].items():
        pdir = dist / "plugins" / name
        (pdir / "skills").mkdir(parents=True)
        for s in cfg["skills"]:
            shutil.copytree(skills_dir / s, pdir / "skills" / s, ignore=ignore)
        if cfg.get("shared"):
            shutil.copytree(shared_dir, pdir / "skills" / "_shared", ignore=ignore)
        grp = cfg.get("agents")
        if grp:
            (pdir / "agents").mkdir()
            for a in m["agent_groups"][grp]:
                shutil.copy2(agents_dir / f"{a}.md", pdir / "agents" / f"{a}.md")
        plugin_json = {
            "name": name,
            "displayName": cfg["displayName"],
            "description": cfg["description"],
            "version": version,
            "author": base["author"],
            "homepage": base.get("homepage", ""),
            "repository": base.get("repository", ""),
            "license": base.get("license", "MIT"),
        }
        (pdir / ".claude-plugin").mkdir()
        (pdir / ".claude-plugin" / "plugin.json").write_text(
            json.dumps(plugin_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        entries.append({
            "name": name,
            "source": f"./plugins/{name}",
            "description": cfg["description"],
            "version": version,
            "author": {"name": base["author"]["name"]},
        })

    out_market = {
        "name": market["name"],
        "owner": market["owner"],
        "metadata": market["metadata"],
        "plugins": entries,
    }
    (dist / ".claude-plugin" / "marketplace.json").write_text(
        json.dumps(out_market, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return dist, entries


def validate_dist(dist):
    errors = []
    for jf in dist.rglob("*.json"):
        try:
            json.loads(jf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{jf.relative_to(dist)}: {e}")
    # every emitted skill has a SKILL.md
    for sk in dist.glob("plugins/*/skills/*"):
        if sk.name == "_shared":
            continue
        if not (sk / "SKILL.md").is_file():
            errors.append(f"{sk.relative_to(dist)}: missing SKILL.md")
    return errors


def read_versions():
    pj = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]
    mk = json.loads(MARKET_JSON.read_text(encoding="utf-8"))
    entry = next((p for p in mk["plugins"] if p["name"] == "elian-store"), None)
    return pj, (entry or {}).get("version"), mk["metadata"]["version"]


def bump_semver(version, level):
    m = SEMVER.match(version)
    if not m:
        fail(4, f"plugin version '{version}' is not X.Y.Z")
    major, minor, patch = (int(x) for x in m.groups())
    return {
        "major": f"{major + 1}.0.0",
        "minor": f"{major}.{minor + 1}.0",
        "patch": f"{major}.{minor}.{patch + 1}",
    }[level]


def _replace_version(path, old, new):
    """Replace exactly the one "version": "<old>" field (the elian-store entry / plugin).
    marketplace.json metadata.version differs from the plugin version, so this is unambiguous."""
    text = path.read_text(encoding="utf-8")
    needle = f'"version": "{old}"'
    n = text.count(needle)
    if n != 1:
        fail(4, f"{path.name}: expected exactly one {needle!r}, found {n}")
    path.write_text(text.replace(needle, f'"version": "{new}"'), encoding="utf-8")


def scaffold_changelog(newver, date):
    lines = CHANGELOG.read_text(encoding="utf-8").splitlines(keepends=True)
    for i, line in enumerate(lines):
        # Headings appear both bracketed (`### [3.0.0] — date`, the Keep a
        # Changelog form used by recent entries) and bare (`### 2.22.0 — date`).
        # Matching only the bare form skipped every recent entry and inserted
        # the stub in the middle of the file.
        if re.match(r"^### \[?\d+\.\d+\.\d+\]? ", line):  # first existing release heading
            lines.insert(i, f"### [{newver}] — {date}\n\n#### Changed\n- TODO: describe the change before opening the PR.\n\n")
            CHANGELOG.write_text("".join(lines), encoding="utf-8")
            return True
    return False


def do_bump(level, date):
    pj_ver, entry_ver, meta_ver = read_versions()
    if pj_ver != entry_ver:
        fail(4, f"version drift before bump: plugin.json={pj_ver} marketplace entry={entry_ver}")
    newver = bump_semver(pj_ver, level)
    _replace_version(PLUGIN_JSON, pj_ver, newver)
    _replace_version(MARKET_JSON, pj_ver, newver)
    scaffolded = scaffold_changelog(newver, date)
    print(f"Bumped elian-store {pj_ver} -> {newver} (plugin.json + marketplace entry).")
    print(f"  CHANGELOG: {'scaffolded a stub — fill it in' if scaffolded else 'NO insertion point; add an entry manually'}.")
    print(f"  marketplace metadata stays {meta_ver}; review README docs for this change.")


def main():
    ap = argparse.ArgumentParser(description="Phase A thematic-cluster generator")
    ap.add_argument("--emit", action="store_true", help="emit thematic plugins to dist/")
    ap.add_argument("--apply-codex", action="store_true", help="create missing codex/skills symlinks")
    ap.add_argument("--bump", choices=["patch", "minor", "major"], help="bump the elian-store version")
    ap.add_argument("--date", default=None, help="CHANGELOG release date (YYYY-MM-DD; default today)")
    args = ap.parse_args()

    m = load_manifest()
    skills_dir = REPO / m["source"]["skills_dir"]
    skills = discover_skills(skills_dir)
    print(f"Discovered {len(skills)} skills under {m['source']['skills_dir']}/")

    # 1) manifest
    errs = validate_manifest(m, skills)
    if errs:
        for e in errs:
            print(f"  manifest: {e}", file=sys.stderr)
        fail(1, f"manifest invalid ({len(errs)} error(s))")
    print("Manifest OK: every skill assigned to exactly one plugin; agents resolve.")

    # 2) lint — every plugin, not just the cluster source. A bare ${CLAUDE_*} is
    #    host-dependent wherever it lives, and a second plugin would otherwise ship unlinted.
    lint_map = {}
    for s in skills:
        v = lint_skill(skills_dir / s / "SKILL.md")
        if v:
            lint_map[s] = v
    for other in sorted((REPO / "plugins").iterdir()):
        other_skills = other / "skills"
        if not other_skills.is_dir() or other_skills == skills_dir:
            continue
        for s in discover_skills(other_skills):
            skill_md = other_skills / s / "SKILL.md"
            if not skill_md.is_file():
                continue
            v = lint_skill(skill_md)
            if v:
                lint_map[f"{other.name}/{s}"] = v
    if lint_map:
        print("\nLint — bare ${CLAUDE_PLUGIN_ROOT}/${CLAUDE_SKILL_DIR} in bash blocks:")
        for s, vs in lint_map.items():
            for ln, txt in vs:
                print(f"  {s}/SKILL.md:{ln}: {txt}")
    else:
        print("Lint OK: no bare CLAUDE_* in any bash block (all host-agnostic).")

    # 3) version + release
    pj_ver, entry_ver, meta_ver = read_versions()
    print(f"\nVersion: plugin.json={pj_ver}, marketplace entry={entry_ver}, metadata={meta_ver}")
    if args.bump:
        date = args.date or datetime.date.today().isoformat()
        do_bump(args.bump, date)
    elif pj_ver != entry_ver:
        fail(4, f"version drift: plugin.json={pj_ver} != marketplace entry={entry_ver}")
    else:
        print("  consistent (plugin.json == marketplace entry).")

    # 4) cluster plan
    print("\nCluster plan:")
    for name, cfg in m["plugins"].items():
        disp = [f"{s}[{codex_disposition(s, m)}]" for s in cfg["skills"]]
        extra = []
        if cfg.get("agents"):
            extra.append(f"{len(m['agent_groups'][cfg['agents']])} {cfg['agents']} agents")
        if cfg.get("shared"):
            extra.append("_shared")
        suffix = f"  (+{', '.join(extra)})" if extra else ""
        print(f"  {name}: {', '.join(disp)}{suffix}")

    # 4) codex status
    rows, skills_dir_rel = codex_status(skills, m, lint_map)
    print("\nCodex skills (symlink) status:")
    for s, state in rows:
        print(f"  {s}: {state}")
    missing = [s for s, st in rows if st == "missing"]
    if missing and not args.apply_codex:
        print(f"  -> {len(missing)} missing; run with --apply-codex to create "
              f"(then retire prompts + update docs manually)")
    if args.apply_codex:
        print("Applying codex symlinks:")
        apply_codex(rows, skills_dir_rel)

    # 5) emit
    if args.emit:
        dist, entries = emit_dist(m, skills, lint_map)
        derrs = validate_dist(dist)
        if derrs:
            for e in derrs:
                print(f"  dist: {e}", file=sys.stderr)
            fail(3, "emitted dist invalid")
        print(f"\nEmitted {len(entries)} plugin(s) to {dist.relative_to(REPO)}/ — JSON + SKILL.md OK.")

    if lint_map:
        fail(2, f"lint violations in {len(lint_map)} skill(s)")
    print("\nOK.")


if __name__ == "__main__":
    main()
