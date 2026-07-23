#!/usr/bin/env python3
"""Static repository validator for the Elian skill and plugin marketplace.

The validator intentionally checks repository definitions rather than local installation,
authentication, MCP connectivity, or host-specific skill availability.

Exit codes:
  0  all checks passed
  1  one or more validation failures
  2  invalid CLI usage or an unreadable repository
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote


HANGUL_RE = re.compile(r"[가-힣]")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*]\(([^)\n]+)\)")
FRONTMATTER_KEY_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(?:\s*(.*))?$")
SIDE_EFFECT_TOOL_RE = re.compile(
    r"(?:^|[\s,\[])(?:Write|Edit|TeamCreate|TaskCreate|TaskUpdate|SendMessage|"
    r"Bash\(gh pr (?:review|comment)|Bash\(glab mr (?:note|approve)|"
    r"Bash\(git (?:checkout|merge|push|worktree)(?:\s|\*\))|"
    r"Bash\((?:cp|mkdir|mv|rm|python3)(?:\s|\*\)))"
)
UNSAFE_TOOL_PATTERNS = {
    "Bash(*)": re.compile(r"\bBash\(\*\)"),
    "unbounded git": re.compile(r"\bBash\(git \*\)"),
    "unbounded shell": re.compile(r"\bBash\((?:bash|sh) \*\)"),
    "wildcard deletion": re.compile(r"\bBash\(rm [^)]*\*\)"),
    "privilege escalation": re.compile(r"\bBash\(sudo"),
}
READ_ONLY_REVIEW_AGENTS = {"engineering-reviewer"}
HIGH_IMPACT_SKILLS = {"finish-branch", "harness-manager"}
# PR/MR posting commands must never be pre-allowlisted: posting a review is a
# hard-to-reverse external write that has to pass an explicit confirm plus a
# capability approval, not run silently because it sits in allowed-tools.
POSTING_TOOL_RE = re.compile(r"Bash\((?:gh pr (?:review|comment)|glab mr (?:note|approve))")


@dataclass(frozen=True)
class Finding:
    check: str
    path: str
    message: str
    severity: str = "error"


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse the top-level scalar/list subset used by repository frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}

    result: dict[str, str] = {}
    i = 1
    while i < end:
        match = FRONTMATTER_KEY_RE.match(lines[i])
        if not match:
            i += 1
            continue
        key, raw = match.group(1), (match.group(2) or "").strip()
        i += 1
        continuation: list[str] = []
        while i < end and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
            stripped = lines[i].strip()
            if stripped.startswith("- "):
                stripped = stripped[2:].strip()
            continuation.append(stripped)
            i += 1
        if raw in {">", ">-", "|", "|-"}:
            value = " ".join(part for part in continuation if part)
        elif continuation:
            value = " ".join([raw, *continuation]).strip()
        else:
            value = raw
        result[key] = _strip_quotes(value)
    return result


def strip_fenced_code(text: str) -> str:
    """Remove fenced code so example paths are not treated as live links."""
    kept: list[str] = []
    in_fence = False
    marker = ""
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            current = stripped[:3]
            if not in_fence:
                in_fence = True
                marker = current
            elif current == marker:
                in_fence = False
                marker = ""
            continue
        if not in_fence:
            kept.append(line)
    return "\n".join(kept)


class RepositoryValidator:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.findings: list[Finding] = []

    def add(self, check: str, path: Path | str, message: str, severity: str = "error") -> None:
        if isinstance(path, Path):
            try:
                display = str(path.resolve().relative_to(self.root))
            except ValueError:
                display = str(path)
        else:
            display = path
        self.findings.append(Finding(check, display, message, severity))

    def _load_json(self, path: Path, check: str) -> object | None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.add(check, path, f"invalid JSON: {exc}")
            return None

    def skill_directories(self) -> list[Path]:
        skills_dir = self.root / "plugins" / "elian-store" / "skills"
        if not skills_dir.is_dir():
            self.add("skill-contract", skills_dir, "skills directory does not exist")
            return []
        return sorted(
            path
            for path in skills_dir.iterdir()
            if path.is_dir() and not path.name.startswith(("_", "."))
        )

    def validate_skill_contracts(self) -> None:
        seen: dict[str, Path] = {}
        for skill_dir in self.skill_directories():
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                self.add("skill-contract", skill_dir, "SKILL.md is missing")
                continue
            text = skill_md.read_text(encoding="utf-8")
            metadata = parse_frontmatter(text)
            if not metadata:
                self.add("skill-contract", skill_md, "valid top-of-file frontmatter is missing")
                continue

            name = metadata.get("name", "")
            if name != skill_dir.name:
                self.add(
                    "skill-contract",
                    skill_md,
                    f"frontmatter name '{name}' does not match directory '{skill_dir.name}'",
                )
            if name in seen:
                self.add(
                    "skill-contract",
                    skill_md,
                    f"duplicate skill name '{name}' also used by {seen[name].relative_to(self.root)}",
                )
            elif name:
                seen[name] = skill_md

            line_count = len(text.splitlines())
            if line_count >= 500:
                self.add(
                    "skill-contract",
                    skill_md,
                    f"SKILL.md has {line_count} lines; the repository limit is under 500",
                )

            description = metadata.get("description", "")
            when_to_use = metadata.get("when_to_use", "")
            if not description:
                self.add("skill-contract", skill_md, "description is missing")
            if len(description) + len(when_to_use) > 1536:
                self.add(
                    "skill-contract",
                    skill_md,
                    "description + when_to_use exceeds the 1,536-character limit",
                )

            allowed_tools = metadata.get("allowed-tools", "")
            for label, pattern in UNSAFE_TOOL_PATTERNS.items():
                if pattern.search(allowed_tools):
                    self.add("tool-policy", skill_md, f"unsafe allowed-tools pattern: {label}")
            if POSTING_TOOL_RE.search(allowed_tools):
                self.add(
                    "tool-policy",
                    skill_md,
                    "PR/MR posting commands must not be pre-allowlisted; posting requires an explicit confirm plus a capability approval",
                )
            if SIDE_EFFECT_TOOL_RE.search(allowed_tools) or name in HIGH_IMPACT_SKILLS:
                if metadata.get("disable-model-invocation", "").lower() != "true":
                    self.add(
                        "side-effect-gate",
                        skill_md,
                        "a side-effect-capable skill must set disable-model-invocation: true",
                    )

    def validate_agents(self) -> None:
        agents_dir = self.root / "plugins" / "elian-store" / "agents"
        for agent_md in sorted(agents_dir.glob("*.md")):
            if not (
                agent_md.name.startswith("persona-")
                or agent_md.stem in READ_ONLY_REVIEW_AGENTS
            ):
                continue
            metadata = parse_frontmatter(agent_md.read_text(encoding="utf-8"))
            tools = metadata.get("tools", "")
            forbidden = [
                tool
                for tool in ("Write", "Edit", "Bash", "Agent", "TeamCreate", "SendMessage")
                if re.search(rf"(?:^|[\s,\[]){re.escape(tool)}(?:$|[\s,\]])", tools)
            ]
            if forbidden:
                self.add(
                    "agent-boundary",
                    agent_md,
                    f"read-only reviewer exposes mutation tools: {', '.join(forbidden)}",
                )

    def validate_cluster_manifest(self) -> None:
        manifest_path = self.root / "tools" / "clusters.json"
        manifest = self._load_json(manifest_path, "cluster-manifest")
        if not isinstance(manifest, dict):
            return
        skills = {path.name for path in self.skill_directories()}
        assigned: dict[str, str] = {}
        plugins = manifest.get("plugins", {})
        for plugin_name, config in plugins.items():
            for skill in config.get("skills", []):
                if skill not in skills:
                    self.add(
                        "cluster-manifest",
                        manifest_path,
                        f"{plugin_name} references unknown skill '{skill}'",
                    )
                if skill in assigned:
                    self.add(
                        "cluster-manifest",
                        manifest_path,
                        f"skill '{skill}' is assigned to both {assigned[skill]} and {plugin_name}",
                    )
                assigned[skill] = plugin_name
            group = config.get("agents")
            if group and group not in manifest.get("agent_groups", {}):
                self.add(
                    "cluster-manifest",
                    manifest_path,
                    f"{plugin_name} references unknown agent group '{group}'",
                )
        for orphan in sorted(skills - set(assigned)):
            self.add("cluster-manifest", manifest_path, f"skill '{orphan}' is unassigned")

        agents_dir = self.root / manifest.get("source", {}).get(
            "agents_dir", "plugins/elian-store/agents"
        )
        for group, names in manifest.get("agent_groups", {}).items():
            for name in names:
                if not (agents_dir / f"{name}.md").is_file():
                    self.add(
                        "cluster-manifest",
                        manifest_path,
                        f"agent group '{group}' references missing agent '{name}'",
                    )

        owners: dict[str, str] = {}
        codex = manifest.get("codex", {})
        for disposition in ("claude_only", "prompt_only", "deferred"):
            for skill in codex.get(disposition, []):
                if skill not in skills:
                    self.add(
                        "codex-disposition",
                        manifest_path,
                        f"{disposition} references unknown skill '{skill}'",
                    )
                if skill in owners:
                    self.add(
                        "codex-disposition",
                        manifest_path,
                        f"skill '{skill}' appears in both {owners[skill]} and {disposition}",
                    )
                owners[skill] = disposition

        # A skill with an explicit disposition (claude_only / prompt_only / deferred)
        # is not shipped to Codex, so it must not also carry a codex/skills symlink.
        for skill in sorted(owners):
            link = self.root / "codex" / "skills" / skill
            if link.is_symlink() or link.exists():
                self.add(
                    "codex-disposition",
                    link,
                    f"'{skill}' is {owners[skill]} and must not ship a codex/skills symlink",
                )

        skills_dir_rel = Path(
            manifest.get("source", {}).get("skills_dir", "plugins/elian-store/skills")
        )
        for skill in sorted(skills - set(owners)):
            link = self.root / "codex" / "skills" / skill
            expected = Path("../..") / skills_dir_rel / skill
            if not link.is_symlink():
                self.add(
                    "codex-disposition",
                    link,
                    "shared Codex skill must be an explicit symlink",
                )
            elif Path(link.readlink()) != expected:
                self.add(
                    "codex-disposition",
                    link,
                    f"symlink target is {link.readlink()}, expected {expected}",
                )

    def validate_versions(self) -> None:
        plugin_path = self.root / "plugins" / "elian-store" / ".claude-plugin" / "plugin.json"
        market_path = self.root / ".claude-plugin" / "marketplace.json"
        plugin = self._load_json(plugin_path, "version-parity")
        market = self._load_json(market_path, "version-parity")
        if not isinstance(plugin, dict) or not isinstance(market, dict):
            return
        entry = next(
            (
                item
                for item in market.get("plugins", [])
                if isinstance(item, dict) and item.get("name") == plugin.get("name")
            ),
            None,
        )
        if entry is None:
            self.add("version-parity", market_path, "elian-store marketplace entry is missing")
        elif entry.get("version") != plugin.get("version"):
            self.add(
                "version-parity",
                market_path,
                f"marketplace version {entry.get('version')} does not match plugin version {plugin.get('version')}",
            )

    def _markdown_files(self) -> Iterable[Path]:
        excluded_parts = {
            ".git",
            ".idea",
            ".playwright-mcp",
            "claudedocs",
            "dist",
            "__pycache__",
        }
        for path in self.root.rglob("*.md"):
            if path.is_symlink() or any(part in excluded_parts for part in path.parts):
                continue
            yield path

    def validate_links(self) -> None:
        for markdown in self._markdown_files():
            text = strip_fenced_code(markdown.read_text(encoding="utf-8"))
            for match in MARKDOWN_LINK_RE.finditer(text):
                raw_target = match.group(1).strip()
                if raw_target.startswith("<") and raw_target.endswith(">"):
                    raw_target = raw_target[1:-1]
                target = raw_target.split(maxsplit=1)[0].strip("'\"")
                if not target or target.startswith(("#", "/", "http://", "https://", "mailto:", "data:")):
                    continue
                target = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not target or any(char in target for char in "{}<>"):
                    continue
                resolved = (markdown.parent / target).resolve()
                if not resolved.exists():
                    self.add("relative-link", markdown, f"relative link target does not exist: {target}")

    def _policy_files(self) -> Iterable[Path]:
        explicit = [
            self.root / "AGENTS.md",
            self.root / "CLAUDE.md",
            self.root / "CONTRIBUTING.md",
            self.root / "README.md",
            self.root / "TODOS.md",
            self.root / ".gitignore",
        ]
        for path in explicit:
            if path.is_file():
                yield path

        roots = [
            self.root / "docs",
            self.root / "codex",
            self.root / "plugins" / "elian-store" / "skills",
        ]
        allowed_suffixes = {".md", ".html", ".json", ".toml", ".css"}
        for base in roots:
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if not path.is_file() or path.is_symlink() or path.suffix not in allowed_suffixes:
                    continue
                if "scripts" in path.parts or path.name == "CHANGELOG.md":
                    continue
                yield path

    def validate_english_policy(self) -> None:
        seen: set[Path] = set()
        for path in self._policy_files():
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if HANGUL_RE.search(line):
                    self.add(
                        "english-policy",
                        path,
                        f"line {line_number} contains Korean text in distribution content",
                    )

    def validate_source_syntax(self) -> None:
        excluded_parts = {".git", ".idea", ".playwright-mcp", "dist", "claudedocs", "__pycache__"}
        for path in self.root.rglob("*.py"):
            if any(part in excluded_parts for part in path.parts):
                continue
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (OSError, SyntaxError) as exc:
                self.add("python-syntax", path, str(exc))

        shell = shutil.which("bash")
        if shell:
            for path in self.root.rglob("*.sh"):
                if any(part in excluded_parts for part in path.parts):
                    continue
                result = subprocess.run(
                    [shell, "-n", str(path)], capture_output=True, text=True, check=False
                )
                if result.returncode:
                    self.add("shell-syntax", path, result.stderr.strip() or "bash -n failed")
        else:
            self.add("shell-syntax", "bash", "bash is unavailable; shell syntax was not checked", "warning")

        node = shutil.which("node")
        if node:
            for path in self.root.rglob("*.js"):
                if any(part in excluded_parts for part in path.parts):
                    continue
                result = subprocess.run(
                    [node, "--check", str(path)], capture_output=True, text=True, check=False
                )
                if result.returncode:
                    self.add("javascript-syntax", path, result.stderr.strip() or "node --check failed")
        else:
            self.add(
                "javascript-syntax",
                "node",
                "node is unavailable; JavaScript syntax was not checked",
                "warning",
            )

    def validate_all(self) -> list[Finding]:
        self.validate_skill_contracts()
        self.validate_agents()
        self.validate_cluster_manifest()
        self.validate_versions()
        self.validate_links()
        self.validate_english_policy()
        self.validate_source_syntax()
        return self.findings


def build_report(root: Path, findings: list[Finding]) -> dict[str, object]:
    errors = [finding for finding in findings if finding.severity == "error"]
    warnings = [finding for finding in findings if finding.severity == "warning"]
    return {
        "repository": str(root.resolve()),
        "verdict": "PASS" if not errors else "FAIL",
        "errorCount": len(errors),
        "warningCount": len(warnings),
        "findings": [asdict(finding) for finding in findings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository root (defaults to this script's parent repository)",
    )
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        parser.error(f"repository root does not exist: {args.root}")

    validator = RepositoryValidator(args.root)
    report = build_report(args.root, validator.validate_all())
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(
            f"Repository validation: {report['verdict']} "
            f"({report['errorCount']} errors, {report['warningCount']} warnings)"
        )
        for finding in report["findings"]:
            print(
                f"[{finding['severity'].upper()}] {finding['check']}: "
                f"{finding['path']}: {finding['message']}"
            )
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
