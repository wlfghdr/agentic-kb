#!/usr/bin/env python3
"""
Generate the per-plugin directory tree (plugins/<name>/) from the canonical
`.claude-plugin/marketplace.json` + top-level `skills/` and `agents/` sources.

Each plugin declared in marketplace.json gets:
  plugins/<name>/
  ├── .claude-plugin/
  │   └── plugin.json         # per-plugin manifest (Claude Code spec)
  ├── skills/                 # symlinks (POSIX) or copies (Windows) of ../../skills/<skill>/
  └── agents/                 # symlinks or copies of ../../agents/<agent>.md

References for the Claude Code plugin + marketplace spec:
  https://code.claude.com/docs/en/plugins.md
  https://code.claude.com/docs/en/plugin-marketplaces.md

Running this script a second time with no source changes must produce no git
diff. CI asserts this to catch drift between sources and generated artifacts.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKETPLACE_JSON = REPO / ".claude-plugin" / "marketplace.json"
SKILLS_DIR = REPO / "skills"
AGENTS_DIR = REPO / "agents"
PLUGINS_DIR = REPO / "plugins"

IS_WINDOWS = os.name == "nt"


def load_marketplace() -> dict:
    with MARKETPLACE_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_skills_and_agents(plugin: dict) -> tuple[list[str], list[str]]:
    """A plugin entry may declare skills/agents explicitly; otherwise we include
    everything under skills/ and agents/."""
    skills = plugin.get("skills")
    agents = plugin.get("agents")
    if skills is None:
        skills = sorted(p.name for p in SKILLS_DIR.iterdir() if p.is_dir())
    if agents is None:
        agents = sorted(p.stem for p in AGENTS_DIR.glob("*.md"))
    return skills, agents


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def symlink_or_copy(src: Path, dst: Path) -> None:
    if IS_WINDOWS:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return
    rel = os.path.relpath(src, dst.parent)
    try:
        dst.symlink_to(rel)
    except OSError:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def build_plugin(plugin: dict) -> None:
    name = plugin["name"]
    source = plugin.get("source") or f"./plugins/{name}"
    # We only materialize plugins whose source is a relative path inside this repo.
    if not isinstance(source, str) or not source.startswith("./"):
        print(f"  skip materializing {name!r} (non-local source: {source!r})")
        return

    plugin_path = (REPO / source.lstrip("./")).resolve()
    try:
        plugin_path.relative_to(REPO)
    except ValueError:
        print(f"ERROR: plugin {name!r} source escapes the repo: {source!r}")
        sys.exit(1)

    reset_dir(plugin_path)
    (plugin_path / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (plugin_path / "skills").mkdir(parents=True, exist_ok=True)
    (plugin_path / "agents").mkdir(parents=True, exist_ok=True)

    skills, agents = resolve_skills_and_agents(plugin)

    for skill in skills:
        src = SKILLS_DIR / skill
        if not src.is_dir():
            print(f"ERROR: skill {skill!r} referenced by plugin {name!r} does not exist")
            sys.exit(1)
        symlink_or_copy(src, plugin_path / "skills" / skill)

    for agent in agents:
        src = AGENTS_DIR / f"{agent}.md"
        if not src.is_file():
            print(f"ERROR: agent {agent!r} referenced by plugin {name!r} does not exist")
            sys.exit(1)
        symlink_or_copy(src, plugin_path / "agents" / f"{agent}.md")

    # Per-plugin manifest — this is the file Claude Code reads on install.
    manifest = {
        "name": name,
        "description": plugin.get("description", ""),
        "version": plugin.get("version", "0.0.0"),
    }
    for optional in ("author", "homepage", "license", "keywords", "category"):
        if plugin.get(optional) is not None:
            manifest[optional] = plugin[optional]
    (plugin_path / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    if not MARKETPLACE_JSON.is_file():
        print(f"ERROR: {MARKETPLACE_JSON.relative_to(REPO)} not found")
        return 1

    marketplace = load_marketplace()

    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    # Clear plugins that no longer exist in marketplace.json
    declared = {p["name"] for p in marketplace.get("plugins", []) or []}
    for existing in [p for p in PLUGINS_DIR.iterdir() if p.is_dir()]:
        if existing.name not in declared:
            shutil.rmtree(existing)

    for plugin in marketplace.get("plugins", []) or []:
        build_plugin(plugin)

    n = len(marketplace.get("plugins", []) or [])
    print(f"Generated {n} plugin directory/ies under plugins/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
