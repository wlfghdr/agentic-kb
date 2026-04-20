#!/usr/bin/env python3
"""
Regenerate per-plugin `plugin.json` manifests under `plugins/<name>/` from the
canonical `.claude-plugin/marketplace.json`.

Each plugin's skills/agents are the **real directories** under
`plugins/<name>/skills/` and `plugins/<name>/agents/` — no symlinks, no
top-level mirror. This avoids double-registration in harnesses that
recursively scan for `SKILL.md`.

Running this script a second time with no source changes must produce no git
diff. CI asserts this to catch drift.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKETPLACE_JSON = REPO / ".claude-plugin" / "marketplace.json"
PLUGINS_DIR = REPO / "plugins"


def load_marketplace() -> dict:
    with MARKETPLACE_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def discover(plugin_path: Path) -> tuple[list[str], list[str]]:
    sdir = plugin_path / "skills"
    adir = plugin_path / "agents"
    skills = sorted(p.name for p in sdir.iterdir() if p.is_dir()) if sdir.is_dir() else []
    agents = sorted(p.stem for p in adir.glob("*.md")) if adir.is_dir() else []
    return skills, agents


def build_plugin(plugin: dict) -> None:
    name = plugin["name"]
    source = plugin.get("source") or f"./plugins/{name}"
    if not isinstance(source, str) or not source.startswith("./"):
        print(f"  skip materializing {name!r} (non-local source: {source!r})")
        return

    plugin_path = (REPO / source.lstrip("./")).resolve()
    try:
        plugin_path.relative_to(REPO)
    except ValueError:
        print(f"ERROR: plugin {name!r} source escapes the repo: {source!r}")
        sys.exit(1)

    if not plugin_path.is_dir():
        print(f"ERROR: plugin directory missing: {plugin_path.relative_to(REPO)}")
        sys.exit(1)

    skills = plugin.get("skills")
    agents = plugin.get("agents")
    discovered_skills, discovered_agents = discover(plugin_path)
    if skills is None:
        skills = discovered_skills
    if agents is None:
        agents = discovered_agents

    # Validate declared skills/agents exist on disk
    for s in skills:
        if not (plugin_path / "skills" / s).is_dir():
            print(f"ERROR: skill {s!r} declared by plugin {name!r} not found under {plugin_path / 'skills'}")
            sys.exit(1)
    for a in agents:
        if not (plugin_path / "agents" / f"{a}.md").is_file():
            print(f"ERROR: agent {a!r} declared by plugin {name!r} not found under {plugin_path / 'agents'}")
            sys.exit(1)

    manifest = {
        "name": name,
        "description": plugin.get("description", ""),
        "version": plugin.get("version", "0.0.0"),
    }
    for optional in ("author", "homepage", "license", "keywords", "category"):
        if plugin.get(optional) is not None:
            manifest[optional] = plugin[optional]
    manifest["x-skills"] = skills
    manifest["x-agents"] = agents
    (plugin_path / "plugin.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    if not MARKETPLACE_JSON.is_file():
        print(f"ERROR: {MARKETPLACE_JSON.relative_to(REPO)} not found")
        return 1

    marketplace = load_marketplace()
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)

    declared = {p["name"] for p in marketplace.get("plugins", []) or []}
    for existing in [p for p in PLUGINS_DIR.iterdir() if p.is_dir()]:
        if existing.name not in declared:
            print(f"WARN: plugin dir {existing.name!r} not declared in marketplace.json (leaving in place)")

    for plugin in marketplace.get("plugins", []) or []:
        build_plugin(plugin)

    n = len(marketplace.get("plugins", []) or [])
    print(f"Refreshed {n} plugin manifest(s) under plugins/")
    return 0


if __name__ == "__main__":
    sys.exit(main())

