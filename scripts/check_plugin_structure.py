#!/usr/bin/env python3
"""
Validate the structure of skills/, agents/, and the plugin marketplace.

Rules (enforced):
  - Every skills/<name>/ must contain SKILL.md with YAML frontmatter including
    required fields: name, description.
    Optional fields we still validate when present: version (X.Y.Z), triggers (non-empty list).
  - Every agents/<name>.md must have YAML frontmatter with required fields:
    name, description. Optional: uses.
  - .claude-plugin/marketplace.json must exist, be valid JSON, and conform to
    the Claude Code marketplace schema: name (string), plugins (list), each
    plugin with name + source.
  - The top-level plugin.json (used by VS Code Agent Plugins and as a
    cross-agent manifest) must exist with name, version, description.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO / "plugins"
CLAUDE_MARKETPLACE = REPO / ".claude-plugin" / "marketplace.json"
VSCODE_PLUGIN = REPO / "plugin.json"

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)

REQUIRED_SKILL_FIELDS = {"name", "description"}
REQUIRED_AGENT_FIELDS = {"name", "description"}


def parse_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1)) or {}
        return data if isinstance(data, dict) else None
    except yaml.YAMLError:
        return None


def _iter_plugin_dirs() -> list[Path]:
    if not PLUGINS_DIR.is_dir():
        return []
    return sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir())


def check_skills() -> tuple[list[str], set[str]]:
    errors: list[str] = []
    declared: set[str] = set()
    plugin_dirs = _iter_plugin_dirs()
    if not plugin_dirs:
        errors.append("MISSING: plugins/ directory (no plugin subdirectories found)")
        return errors, declared
    for plugin_dir in plugin_dirs:
        sdir = plugin_dir / "skills"
        if not sdir.is_dir():
            continue
        for skill_dir in sorted(p for p in sdir.iterdir() if p.is_dir()):
            skill_md = skill_dir / "SKILL.md"
            rel = skill_md.relative_to(REPO)
            if not skill_md.is_file():
                errors.append(f"MISSING: {rel}")
                continue
            fm = parse_frontmatter(skill_md)
            if fm is None:
                errors.append(f"BAD frontmatter: {rel}")
                continue
            missing = REQUIRED_SKILL_FIELDS - fm.keys()
            if missing:
                errors.append(f"{rel}: missing required fields {sorted(missing)}")
            if fm.get("name") != skill_dir.name:
                errors.append(
                    f"{rel}: frontmatter name={fm.get('name')!r} does not match dir {skill_dir.name!r}"
                )
            if "triggers" in fm:
                triggers = fm["triggers"]
                if not isinstance(triggers, list) or not triggers:
                    errors.append(f"{rel}: triggers, if present, must be a non-empty list")
            if "version" in fm:
                v = fm["version"]
                if not isinstance(v, str) or not re.fullmatch(r"\d+\.\d+\.\d+", v):
                    errors.append(f"{rel}: version must be X.Y.Z, got {v!r}")
            declared.add(skill_dir.name)
    return errors, declared


def check_agents() -> tuple[list[str], set[str]]:
    errors: list[str] = []
    declared: set[str] = set()
    for plugin_dir in _iter_plugin_dirs():
        adir = plugin_dir / "agents"
        if not adir.is_dir():
            continue
        for agent_path in sorted(adir.glob("*.md")):
            rel = agent_path.relative_to(REPO)
            fm = parse_frontmatter(agent_path)
            if fm is None:
                errors.append(f"BAD frontmatter: {rel}")
                continue
            missing = REQUIRED_AGENT_FIELDS - fm.keys()
            if missing:
                errors.append(f"{rel}: missing required fields {sorted(missing)}")
            if fm.get("name") != agent_path.stem:
                errors.append(
                    f"{rel}: name={fm.get('name')!r} does not match filename {agent_path.stem!r}"
                )
            declared.add(agent_path.stem)
    return errors, declared


def check_claude_marketplace(skills_decl: set[str], agents_decl: set[str]) -> list[str]:
    errors: list[str] = []
    if not CLAUDE_MARKETPLACE.is_file():
        errors.append(f"MISSING: {CLAUDE_MARKETPLACE.relative_to(REPO)}")
        return errors
    try:
        data = json.loads(CLAUDE_MARKETPLACE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"{CLAUDE_MARKETPLACE.relative_to(REPO)}: invalid JSON: {e}")
        return errors

    for required in ("name", "plugins"):
        if required not in data:
            errors.append(
                f"{CLAUDE_MARKETPLACE.relative_to(REPO)}: missing required field {required!r}"
            )

    plugins = data.get("plugins") or []
    if not isinstance(plugins, list):
        errors.append(f"{CLAUDE_MARKETPLACE.relative_to(REPO)}: 'plugins' must be a list")
        return errors

    referenced_skills: set[str] = set()
    referenced_agents: set[str] = set()
    for plugin in plugins:
        if not isinstance(plugin, dict):
            errors.append("marketplace.json: plugin entries must be objects")
            continue
        for k in ("name", "source"):
            if k not in plugin:
                errors.append(f"plugin {plugin.get('name', '?')!r}: missing {k!r}")
        # Only plugins with skills/agents explicitly declared contribute to coverage;
        # auto-inclusion is allowed but we still want all declared skills/agents
        # covered somewhere.
        for s in plugin.get("skills") or []:
            referenced_skills.add(s)
        for a in plugin.get("agents") or []:
            referenced_agents.add(a)

    # If any plugin auto-includes everything (skills/agents key absent), coverage is satisfied.
    auto = any(
        ("skills" not in p or "agents" not in p) for p in plugins if isinstance(p, dict)
    )
    if not auto:
        missing_skills = skills_decl - referenced_skills
        if missing_skills:
            errors.append(
                f"marketplace.json: skills {sorted(missing_skills)} exist on disk but are not referenced by any plugin"
            )
        missing_agents = agents_decl - referenced_agents
        if missing_agents:
            errors.append(
                f"marketplace.json: agents {sorted(missing_agents)} exist on disk but are not referenced by any plugin"
            )

    # Stale references (listed but not on disk) are always an error.
    stale_skills = referenced_skills - skills_decl
    if stale_skills:
        errors.append(
            f"marketplace.json: references skills {sorted(stale_skills)} that do not exist on disk"
        )
    stale_agents = referenced_agents - agents_decl
    if stale_agents:
        errors.append(
            f"marketplace.json: references agents {sorted(stale_agents)} that do not exist on disk"
        )

    return errors


def check_vscode_plugin() -> list[str]:
    errors: list[str] = []
    if not VSCODE_PLUGIN.is_file():
        errors.append(f"MISSING: {VSCODE_PLUGIN.relative_to(REPO)}")
        return errors
    try:
        data = json.loads(VSCODE_PLUGIN.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"plugin.json: invalid JSON: {e}")
        return errors
    for required in ("name", "version", "description"):
        if required not in data:
            errors.append(f"plugin.json: missing required field {required!r}")
    # Validate every referenced file path exists.
    for key in ("skills", "agents", "prompts", "instructions", "plugins"):
        for entry in data.get(key, []) or []:
            if not isinstance(entry, dict):
                continue
            p = entry.get("path")
            if p and not (REPO / p).exists():
                errors.append(f"plugin.json: {key} entry {entry.get('name')!r} path missing: {p}")
    # Validate per-plugin manifests when using the "plugins" key
    for plugin_entry in data.get("plugins", []) or []:
        if not isinstance(plugin_entry, dict):
            continue
        p = plugin_entry.get("path")
        if p:
            manifest = REPO / p / "plugin.json"
            if not manifest.is_file():
                errors.append(f"plugin.json: plugin {plugin_entry.get('name')!r} missing {p}/plugin.json")
    return errors


def main() -> int:
    skill_errors, skills_decl = check_skills()
    agent_errors, agents_decl = check_agents()
    claude_errors = check_claude_marketplace(skills_decl, agents_decl)
    vscode_errors = check_vscode_plugin()
    all_errors = skill_errors + agent_errors + claude_errors + vscode_errors
    if all_errors:
        print("Plugin-structure check failed:\n")
        for e in all_errors:
            print(f"  ✗ {e}")
        print(f"\nTotal: {len(all_errors)} error(s).")
        return 1
    print(f"Plugin-structure check: OK ({len(skills_decl)} skill(s), {len(agents_decl)} agent(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
