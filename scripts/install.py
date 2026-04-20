#!/usr/bin/env python3
"""
Install agentic-kb skills, agents, and prompt/instruction files into the
selected harness.

Paths per harness (as of late 2025 / early 2026):

  claude-code
    - User-global:  ~/.claude/skills/<name>/, ~/.claude/agents/<name>.md,
                    ~/.claude/commands/<name>.md
    - Project:      .claude/skills/<name>/, .claude/agents/<name>.md,
                    .claude/commands/<name>.md
    - Recommended install path for marketplaces:
        /plugin marketplace add <github-url>   (from inside Claude Code)
        /plugin install kb@agentic-kb

  opencode
    - User-global:  ~/.config/opencode/skills/<name>/,
                    ~/.config/opencode/agents/<name>.md,
                    ~/.config/opencode/commands/<name>.md
    - Project:      .opencode/skills/, .opencode/agents/, .opencode/commands/
    - Note: OpenCode also reads .claude/skills/<name>/SKILL.md for
            cross-agent compatibility.

  vscode  (GitHub Copilot Chat — Agent Skills + Agent Plugins)
    - Workspace:    .github/skills/<name>/ (preferred — Agent Skill),
                    .github/prompts/<name>.prompt.md (slash command),
                    .github/instructions/<name>.instructions.md (scoped rules),
                    .github/agents/<name>.agent.md (custom agent persona).
    - User:         ~/.copilot/skills/, ~/.copilot/agents/,
                    ~/.copilot/prompts/, ~/.copilot/instructions/.
    - Easiest for users: add this repo to chat.plugins.marketplaces in
      settings.json and install via the Extensions view (reads plugin.json).

Symlinks on POSIX, copies on Windows (or when symlinks fail).

Usage examples:
  scripts/install                                 # auto-detect harness, install all
  scripts/install --target claude                 # workspace .claude/
  scripts/install --target claude --global        # ~/.claude/
  scripts/install --target opencode --global
  scripts/install --target vscode                 # workspace .github/
  scripts/install --force
  scripts/install --target all --global

Only copies/links content from this repo. Never runs anything on the user's
machine beyond file operations.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VSCODE_PLUGIN_JSON = REPO / "plugin.json"

IS_WINDOWS = os.name == "nt"


def discover_skill_agent_paths(pj: dict) -> tuple[dict[str, Path], dict[str, Path]]:
    """Walk plugins/<name>/ declared in root plugin.json and return maps
    {skill_name: path} and {agent_name: path}."""
    skills: dict[str, Path] = {}
    agents: dict[str, Path] = {}
    for plugin_entry in pj.get("plugins", []) or []:
        base = REPO / plugin_entry["path"]
        sdir = base / "skills"
        adir = base / "agents"
        if sdir.is_dir():
            for p in sdir.iterdir():
                if p.is_dir():
                    skills.setdefault(p.name, p)
        if adir.is_dir():
            for p in adir.glob("*.md"):
                agents.setdefault(p.stem, p)
    return skills, agents


def workspace_targets() -> dict:
    return {
        "claude": {
            "base_local": REPO.cwd() / ".claude",
            "base_global": Path(os.path.expanduser("~/.claude")),
            "layout": {"skills": "skills", "agents": "agents", "commands": "commands"},
        },
        "opencode": {
            "base_local": REPO.cwd() / ".opencode",
            "base_global": Path(os.path.expanduser("~/.config/opencode")),
            "layout": {"skills": "skills", "agents": "agents", "commands": "commands"},
        },
        "vscode": {
            "base_local": REPO.cwd() / ".github",
            "base_global": Path(os.path.expanduser("~/.copilot")),
            "layout": {
                "skills": "skills",
                "agents": "agents",
                "prompts": "prompts",
                "instructions": "instructions",
            },
        },
    }


def detect_targets() -> list[str]:
    hits: list[str] = []
    cwd = Path.cwd()
    for name, probes in {
        "claude": [cwd / ".claude", Path(os.path.expanduser("~/.claude"))],
        "opencode": [cwd / ".opencode", Path(os.path.expanduser("~/.config/opencode"))],
        "vscode": [cwd / ".github", cwd / ".vscode", Path(os.path.expanduser("~/.copilot"))],
    }.items():
        if any(p.exists() for p in probes):
            hits.append(name)
    return hits or ["claude"]


def link_or_copy(src: Path, dst: Path, force: bool) -> None:
    if dst.exists() or dst.is_symlink():
        if not force:
            print(f"  skip (exists): {dst}")
            return
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    dst.parent.mkdir(parents=True, exist_ok=True)
    if IS_WINDOWS:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        print(f"  copied: {src.name} -> {dst}")
        return
    rel = os.path.relpath(src, dst.parent)
    try:
        dst.symlink_to(rel)
        print(f"  linked: {src.name} -> {dst}")
    except OSError:
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        print(f"  copied (symlink failed): {src.name} -> {dst}")


def install_claude_or_opencode(target: str, base: Path, layout: dict,
                               skills: list[str], agents: list[str],
                               skill_paths: dict[str, Path], agent_paths: dict[str, Path],
                               commands_src: list[tuple[str, Path]], force: bool) -> None:
    print(f"\nInstalling into {base} ({target})")
    for s in skills:
        src = skill_paths.get(s)
        if src and src.is_dir():
            link_or_copy(src, base / layout["skills"] / s, force)
    for a in agents:
        src = agent_paths.get(a)
        if src and src.is_file():
            link_or_copy(src, base / layout["agents"] / f"{a}.md", force)
    # commands: .md files whose body is the prompt template
    for name, src in commands_src:
        if src.is_file():
            link_or_copy(src, base / layout["commands"] / f"{name}.md", force)


def install_vscode(base: Path, skills: list[str], agents: list[str],
                   skill_paths: dict[str, Path], agent_paths: dict[str, Path],
                   prompts_src: list[tuple[str, Path]],
                   instructions_src: list[tuple[str, Path]], force: bool) -> None:
    print(f"\nInstalling into {base} (vscode)")
    for s in skills:
        src = skill_paths.get(s)
        if src and src.is_dir():
            link_or_copy(src, base / "skills" / s, force)
    for a in agents:
        src = agent_paths.get(a)
        if src and src.is_file():
            # VS Code convention uses .agent.md for custom agent personas
            link_or_copy(src, base / "agents" / f"{a}.agent.md", force)
    for name, src in prompts_src:
        if src.is_file():
            link_or_copy(src, base / "prompts" / f"{name}.prompt.md", force)
    for name, src in instructions_src:
        if src.is_file():
            link_or_copy(src, base / "instructions" / f"{name}.instructions.md", force)
    print(
        "\n  Tip: for one-click install, add this repo to chat.plugins.marketplaces\n"
        "       in your VS Code settings.json and use the Extensions view."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Install agentic-kb artifacts into a harness.")
    parser.add_argument(
        "--target",
        choices=["claude", "opencode", "vscode", "all", "auto"],
        default="auto",
        help="Which harness to install into (default: auto-detect).",
    )
    parser.add_argument("--global", dest="globally", action="store_true",
                        help="Install into the user-global harness directory.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing installs.")
    parser.add_argument("items", nargs="*",
                        help="Specific skills/agents to install (default: everything in plugin.json).")
    args = parser.parse_args()

    if not VSCODE_PLUGIN_JSON.is_file():
        print("ERROR: plugin.json not found at repo root", file=sys.stderr)
        return 1
    pj = json.loads(VSCODE_PLUGIN_JSON.read_text(encoding="utf-8"))

    skill_paths, agent_paths = discover_skill_agent_paths(pj)

    # Resolve skills + agents: root plugin.json may list them directly
    # (legacy: "skills"/"agents" keys) or indirectly via per-plugin manifests
    # (current: "plugins" key → each plugin's plugin.json has "x-skills"/"x-agents").
    all_skills: list[str] = [s["name"] for s in pj.get("skills", []) or []]
    all_agents: list[str] = [a["name"] for a in pj.get("agents", []) or []]
    if not all_skills and not all_agents:
        # Current layout: resolve from per-plugin manifests
        for plugin_entry in pj.get("plugins", []) or []:
            plugin_path = REPO / plugin_entry["path"] / "plugin.json"
            if plugin_path.is_file():
                ppj = json.loads(plugin_path.read_text(encoding="utf-8"))
                all_skills.extend(ppj.get("x-skills", []) or [])
                all_agents.extend(ppj.get("x-agents", []) or [])
        # Fallback: enumerate from discovered paths
        if not all_skills:
            all_skills = sorted(skill_paths.keys())
        if not all_agents:
            all_agents = sorted(agent_paths.keys())
    prompts = [(p["name"], REPO / p["path"]) for p in pj.get("prompts", []) or []]
    instructions = [(i["name"], REPO / i["path"]) for i in pj.get("instructions", []) or []]

    if args.items:
        req = set(args.items)
        skills = [s for s in all_skills if s in req]
        agents = [a for a in all_agents if a in req]
        unknown = req - set(skills) - set(agents)
        if unknown:
            print(f"ERROR: unknown item(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 1
    else:
        skills = all_skills
        agents = all_agents

    targets = {
        "auto": detect_targets(),
        "all": ["claude", "opencode", "vscode"],
    }.get(args.target, [args.target])

    cfg = workspace_targets()
    for t in targets:
        base = cfg[t]["base_global"] if args.globally else cfg[t]["base_local"]
        if t == "vscode":
            install_vscode(base, skills, agents, skill_paths, agent_paths, prompts, instructions, args.force)
        else:
            layout = cfg[t]["layout"]
            # For claude/opencode, each prompt becomes a "command" (slash command).
            install_claude_or_opencode(t, base, layout, skills, agents, skill_paths, agent_paths, prompts, args.force)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
