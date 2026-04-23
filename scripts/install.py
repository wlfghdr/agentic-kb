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
  scripts/install --target codex --global         # ~/.codex/prompts/ (global-only)
  scripts/install --target gemini --global        # ~/.gemini/commands/*.toml (generated)
  scripts/install --target kiro                   # .kiro/agents/ (works as slash-cmd)
  scripts/install --force
  scripts/install --target all --global           # claude + opencode + vscode + codex + gemini + kiro

Only copies/links content from this repo. Never runs anything on the user's
machine beyond file operations.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VSCODE_PLUGIN_JSON = REPO / "plugin.json"

IS_WINDOWS = os.name == "nt"
VERSION_LINE_RE = re.compile(r"^version:\s*([^\s]+)\s*$")


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
        # Codex CLI — markdown prompts only (no skills/agents); per Codex
        # design these live in `~/.codex/prompts/`. Local project prompts
        # are not discovered by Codex as of v0.4.
        "codex": {
            "base_local": REPO.cwd() / ".codex",
            "base_global": Path(os.path.expanduser("~/.codex")),
            "layout": {"prompts": "prompts"},
        },
        # Gemini CLI — custom commands are TOML files under
        # `.gemini/commands/` (local) or `~/.gemini/commands/` (global).
        # This installer emits a minimal TOML wrapper whose `prompt` field
        # embeds the markdown command body.
        "gemini": {
            "base_local": REPO.cwd() / ".gemini",
            "base_global": Path(os.path.expanduser("~/.gemini")),
            "layout": {"commands": "commands"},
        },
        # Kiro IDE — "custom agents" double as slash commands. Files live
        # in `.kiro/agents/` (local) or `~/.kiro/agents/` (global).
        "kiro": {
            "base_local": REPO.cwd() / ".kiro",
            "base_global": Path(os.path.expanduser("~/.kiro")),
            "layout": {"agents": "agents"},
        },
    }


def detect_targets() -> list[str]:
    hits: list[str] = []
    cwd = Path.cwd()
    for name, probes in {
        "claude": [cwd / ".claude", Path(os.path.expanduser("~/.claude"))],
        "opencode": [cwd / ".opencode", Path(os.path.expanduser("~/.config/opencode"))],
        "vscode": [cwd / ".github", cwd / ".vscode", Path(os.path.expanduser("~/.copilot"))],
        "codex": [Path(os.path.expanduser("~/.codex"))],
        "gemini": [cwd / ".gemini", Path(os.path.expanduser("~/.gemini"))],
        "kiro": [cwd / ".kiro", Path(os.path.expanduser("~/.kiro"))],
    }.items():
        if any(p.exists() for p in probes):
            hits.append(name)
    return hits or ["claude"]


def read_frontmatter_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            return None
        match = VERSION_LINE_RE.match(stripped)
        if match:
            return match.group(1).strip("\"'")
    return None


def versioned_artifact_path(path: Path) -> Path | None:
    if path.is_symlink():
        try:
            path = path.resolve(strict=True)
        except FileNotFoundError:
            return None
    elif not path.exists():
        return None
    if path.is_dir():
        skill_doc = path / "SKILL.md"
        return skill_doc if skill_doc.is_file() else None
    if path.is_file() and path.suffix.lower() == ".md":
        return path
    return None


def artifact_version(path: Path) -> str | None:
    doc = versioned_artifact_path(path)
    if doc is None:
        return None
    return read_frontmatter_version(doc)


def parse_version(version: str | None) -> tuple[int, ...] | None:
    if version is None:
        return None
    parts = version.split(".")
    if not parts or any(not part.isdigit() for part in parts):
        return None
    return tuple(int(part) for part in parts)


def compare_versions(left: str | None, right: str | None) -> int | None:
    left_parts = parse_version(left)
    right_parts = parse_version(right)
    if left_parts is None or right_parts is None:
        return None
    width = max(len(left_parts), len(right_parts))
    left_padded = left_parts + (0,) * (width - len(left_parts))
    right_padded = right_parts + (0,) * (width - len(right_parts))
    if left_padded > right_padded:
        return 1
    if left_padded < right_padded:
        return -1
    return 0


def link_or_copy(src: Path, dst: Path, force: bool) -> None:
    if dst.exists() or dst.is_symlink():
        if not force:
            src_version = artifact_version(src)
            dst_version = artifact_version(dst)
            version_cmp = compare_versions(src_version, dst_version)
            if version_cmp == 0 and src_version is not None:
                print(f"  up-to-date (v{src_version}): {dst}")
            elif version_cmp == 1 and dst_version is not None and src_version is not None:
                print(
                    f"  stale (v{dst_version} -> v{src_version}): {dst} "
                    "(run with --force to reinstall / update)"
                )
            elif version_cmp == -1 and dst_version is not None and src_version is not None:
                print(
                    f"  newer installed (v{dst_version} > v{src_version}): {dst} "
                    "(run with --force to reinstall / downgrade)"
                )
            else:
                print(
                    f"  skip (exists): {dst} "
                    "(run with --force to reinstall / update)"
                )
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


def _strip_markdown_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Return ({frontmatter-keys-as-strings}, body) for a markdown file."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    fm: dict[str, str] = {}
    for i, line in enumerate(lines[1:], start=1):
        stripped = line.rstrip()
        if stripped == "---":
            body = "\n".join(lines[i + 1:]).lstrip("\n")
            return fm, body
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", stripped)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return {}, text


def install_codex(base: Path, commands_src: list[tuple[str, Path]], force: bool) -> None:
    """Install markdown command files into `<base>/prompts/` for Codex CLI.

    Codex discovers any `.md` in `~/.codex/prompts/` and registers
    `/prompts:<filename>` (and often just `/<filename>`). The command body
    minus YAML frontmatter becomes the prompt.
    """
    print(f"\nInstalling into {base} (codex)")
    out_dir = base / "prompts"
    for name, src in commands_src:
        if not src.is_file():
            continue
        _, body = _strip_markdown_frontmatter(src.read_text(encoding="utf-8"))
        dst = out_dir / f"{name}.md"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not force:
            print(f"  skip (exists): {dst} (run with --force to overwrite)")
            continue
        dst.write_text(body, encoding="utf-8")
        print(f"  wrote: {dst}")


def install_gemini(base: Path, commands_src: list[tuple[str, Path]], force: bool) -> None:
    """Install a TOML wrapper per command into `<base>/commands/` for Gemini CLI.

    Gemini's custom-command format is TOML. We emit a minimal wrapper
    (`description` + multi-line `prompt`) whose prompt is the markdown
    body of the command. Frontmatter `description` field (if present) is
    reused as the TOML description.
    """
    print(f"\nInstalling into {base} (gemini)")
    out_dir = base / "commands"
    for name, src in commands_src:
        if not src.is_file():
            continue
        fm, body = _strip_markdown_frontmatter(src.read_text(encoding="utf-8"))
        desc = fm.get("description", "").replace("\n", " ")
        safe_desc = desc.replace('"', '\\"')
        safe_body = body.replace('"""', '\\"\\"\\"')
        toml = (
            f'description = "{safe_desc}"\n'
            f'prompt = """\n{safe_body}\n"""\n'
        )
        dst = out_dir / f"{name}.toml"
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not force:
            print(f"  skip (exists): {dst} (run with --force to overwrite)")
            continue
        dst.write_text(toml, encoding="utf-8")
        print(f"  wrote: {dst}")


def install_kiro(base: Path, commands_src: list[tuple[str, Path]], force: bool) -> None:
    """Install markdown command files as Kiro custom agents.

    Kiro's custom agents in `.kiro/agents/` (or `~/.kiro/agents/`) surface
    as `/<name>` slash commands. Markdown body + YAML frontmatter pass
    through unchanged; Kiro ignores frontmatter keys it doesn't know.
    """
    print(f"\nInstalling into {base} (kiro)")
    out_dir = base / "agents"
    for name, src in commands_src:
        if src.is_file():
            link_or_copy(src, out_dir / f"{name}.md", force)


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
        choices=["claude", "opencode", "vscode", "codex", "gemini", "kiro", "all", "auto"],
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
        "all": ["claude", "opencode", "vscode", "codex", "gemini", "kiro"],
    }.get(args.target, [args.target])

    cfg = workspace_targets()
    for t in targets:
        base = cfg[t]["base_global"] if args.globally else cfg[t]["base_local"]
        if t == "vscode":
            install_vscode(base, skills, agents, skill_paths, agent_paths, prompts, instructions, args.force)
        elif t == "codex":
            # Codex discovers prompts only in ~/.codex/prompts — no local.
            install_codex(cfg[t]["base_global"], prompts, args.force)
        elif t == "gemini":
            install_gemini(base, prompts, args.force)
        elif t == "kiro":
            install_kiro(base, prompts, args.force)
        else:
            layout = cfg[t]["layout"]
            # For claude/opencode, each prompt becomes a "command" (slash command).
            install_claude_or_opencode(t, base, layout, skills, agents, skill_paths, agent_paths, prompts, args.force)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
