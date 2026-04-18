# Marketplace & Skills — Multi-Harness Distribution

> **Version:** 0.2 | **Last updated:** 2026-04-18

This document specifies how the reference implementation is **packaged**, **distributed**, and **consumed** across harnesses. Targets as of early 2026:

- **Claude Code** (via plugin marketplaces — [`.claude-plugin/marketplace.json`][ccm])
- **VS Code Copilot Chat** (via [Agent Skills][vss] + [Agent Plugins][vsp])
- **OpenCode** (via [Agent Skills][ocs], [Agents][oca], and [Commands][occ])

The spec defines a single source layout that every harness can consume natively. The harness-specific manifests (`.claude-plugin/marketplace.json`, top-level `plugin.json` for VS Code, per-plugin `.claude-plugin/plugin.json`) sit alongside the canonical sources and are generated/maintained by the marketplace tooling.

## Terms

| Term | Meaning |
|------|---------|
| **Skill** | Directory with `SKILL.md` (YAML frontmatter + Markdown). Cross-agent portable. |
| **Agent** | Markdown file with frontmatter that composes skills into a persona. File: `<name>.md`. |
| **Plugin** | A bundle of skills + agents + commands + (optionally) hooks and MCP servers, declared by a manifest. |
| **Marketplace** | A repo that lists one or more plugins via a marketplace manifest. |
| **Harness** | The agentic IDE / CLI consuming the artifacts (Claude Code, VS Code Copilot, OpenCode). |

## Required Repo Layout

```
my-marketplace/
├── README.md
├── .claude-plugin/
│   └── marketplace.json           # Claude Code marketplace index (canonical)
├── plugin.json                    # Top-level manifest — used by VS Code Agent Plugins
├── skills/                        # Cross-agent skills (source of truth)
│   ├── kb-management/
│   │   ├── SKILL.md               # frontmatter: name, description (required)
│   │   ├── references/            # load-on-demand supplementary docs
│   │   └── templates/
│   └── kb-setup/
├── agents/                        # cross-agent agents (file-per-agent)
│   └── kb-operator.md             # frontmatter: name, description (required)
├── plugins/                       # assembled Claude Code plugins (generated)
│   └── kb/
│       ├── .claude-plugin/
│       │   └── plugin.json        # per-plugin manifest
│       ├── skills/                # symlinks (POSIX) / copies (Windows) of top-level skills
│       └── agents/
└── scripts/
    ├── install                    # user-facing installer (wraps install.py)
    ├── install.py                 # cross-harness install logic
    └── generate_plugins.py        # rebuilds ./plugins/ from marketplace.json
```

### Single-source principle

**Skills and agents at the top level are the source of truth.** `plugins/` is a generated artifact — never hand-edit. The generator uses symlinks on POSIX, copies on Windows.

## Skill Format

`SKILL.md` with YAML frontmatter. Minimum required fields are the **intersection** of what all three harnesses require (so one file works everywhere):

```markdown
---
name: kb-management                # required, kebab-case, matches directory
description: >                     # required, ≤1024 chars; used by model auto-invocation
  Lean, layered knowledge management driven by `/kb`. Captures inputs,
  applies a five-question evaluation gate, tracks decisions, manages tasks,
  and generates versioned HTML artifacts. Install to get the `/kb` command.
version: 0.1.0                     # optional; surfaced in marketplace listings
triggers:                          # optional; used as auto-invocation hints
  - "/kb"
  - "knowledge base"
license: Apache-2.0
---

# Skill: …
```

### Frontmatter notes per harness

- **Claude Code** requires `name`; `description` is strongly recommended (used for skill-picker).
- **VS Code Copilot** requires `name` and `description` (description ≤1024 chars, used for auto-invocation match).
- **OpenCode** requires `name` (regex `^[a-z0-9]+(-[a-z0-9]+)*$`, 1–64 chars) and `description` (1–1024 chars). Unknown fields are ignored, so `triggers`/`version` are safe.

Use the same frontmatter for all three. Don't diverge per harness.

### Body — progressive disclosure

1. **Top**: one paragraph — when to invoke, what it does, primary command.
2. **Middle**: operational rules, compact enough to fit in one prompt turn.
3. **Bottom**: links to `references/` for long-form context — loaded only when needed.

Keep the `SKILL.md` body under ~5,000 tokens.

## Agent Format

`agents/<name>.md` with frontmatter. The filename (without `.md`) must match `name`:

```markdown
---
name: kb-operator
description: Autonomous knowledge-operations persona. Runs rituals, processes inputs, maintains decisions and tasks, generates HTML artifacts.
uses:
  - kb-management
  - kb-setup
mode: primary                      # OpenCode: primary | subagent | all
license: Apache-2.0
---

# Agent: …
```

**Note on the file extension**: earlier versions of this spec used `<name>.agent.md`. That convention is specific to some VS Code tooling and is **not** recognized by Claude Code or OpenCode. The spec now uses `<name>.md` for cross-agent compatibility; the VS Code installer renames on copy (`agents/<name>.agent.md`) to satisfy that harness.

## The Marketplace Manifest — `.claude-plugin/marketplace.json`

This is the **Claude Code–native** file. Structure (per Claude Code docs):

```json
{
  "name": "agentic-kb",
  "description": "AI-native layered knowledge ops.",
  "owner": { "name": "you", "url": "https://github.com/you/repo" },
  "metadata": { "version": "0.1.0", "license": "Apache-2.0" },
  "plugins": [
    {
      "name": "kb",
      "source": "./plugins/kb",
      "description": "…",
      "version": "0.1.0",
      "keywords": ["knowledge-management", "kb"]
    }
  ]
}
```

`source` options (per Claude Code plugin-marketplace spec):

- Relative path inside the repo: `"./plugins/kb"`.
- GitHub: `{ "source": "github", "repo": "owner/repo", "ref": "branch" }`.
- Git URL: `{ "source": "url", "url": "https://…", "ref": "main" }`.
- Git subdirectory: `{ "source": "git-subdir", "url": "…", "path": "tools/plugin" }`.
- npm: `{ "source": "npm", "package": "@org/plugin" }`.

## The Per-Plugin Manifest — `<plugin-root>/.claude-plugin/plugin.json`

Every plugin directory materialized under `plugins/<name>/` contains its own Claude Code manifest:

```json
{
  "name": "kb",
  "description": "Knowledge-ops plugin: kb-management + kb-setup + kb-operator.",
  "version": "0.1.0",
  "author": "agentic-kb contributors",
  "license": "Apache-2.0",
  "keywords": ["knowledge-management", "kb"]
}
```

The plugin's `skills/` and `agents/` directories are symlinks/copies of the repo-level sources — generated automatically.

## The Top-Level Manifest — `plugin.json` (for VS Code Agent Plugins)

At the repo root, a `plugin.json` is picked up by VS Code Copilot Chat via `chat.plugins.marketplaces`:

```json
{
  "name": "agentic-kb",
  "version": "0.1.0",
  "description": "…",
  "skills":       [{ "name": "kb-management", "path": "skills/kb-management" }],
  "agents":       [{ "name": "kb-operator",    "path": "agents/kb-operator.md" }],
  "prompts":      [{ "name": "kb",             "path": "skills/kb-setup/templates/kb.prompt.md" }],
  "instructions": [{ "name": "kb",             "path": "skills/kb-setup/templates/kb.instructions.md" }]
}
```

## Installation — Three Paths, One Source

### Claude Code (preferred for Claude Code users)

```
/plugin marketplace add https://github.com/<org>/<repo>
/plugin install kb@agentic-kb
```

Or, for development installs, clone the repo and `scripts/install --target claude` (symlinks into `.claude/` or `~/.claude/`).

### VS Code Copilot Chat

Add the repo to `chat.plugins.marketplaces` in `settings.json`:

```json
{
  "chat.plugins.marketplaces": [
    "<org>/<repo>"
  ]
}
```

VS Code reads the top-level `plugin.json` and offers one-click install from the Extensions view. For direct workspace setup, `scripts/install --target vscode` copies to `.github/{skills,agents,prompts,instructions}/`.

### OpenCode

There is no official OpenCode plugin marketplace or install-from-URL command as of early 2026. Two supported paths:

1. **Clone + install** — `scripts/install --target opencode [--global]` copies/symlinks into `.opencode/{skills,agents,commands}/` (workspace) or `~/.config/opencode/{skills,agents,commands}/` (user-global).
2. **Reference-in-place** — OpenCode natively reads `.claude/skills/<name>/SKILL.md`, so an install made for Claude Code also works for OpenCode in the same workspace.

## Slash Commands

Each harness registers slash commands differently:

| Harness | Mechanism |
|---------|-----------|
| Claude Code | `commands/<name>.md` in the plugin, or skills auto-register as `/<skill-name>` |
| VS Code Copilot | `.github/prompts/<name>.prompt.md` → `/<name>` |
| OpenCode | `.opencode/commands/<name>.md` → `/<name>` |

Our `skills/kb-setup/templates/kb.prompt.md` ships as the prompt / command body. The installer copies it into the right directory for each target.

## CI Guarantees

The reference implementation's CI runs:

- **Plugin structure** — `scripts/check_plugin_structure.py` validates every skill + agent + both manifests.
- **Generator drift** — regenerates `plugins/` from `.claude-plugin/marketplace.json` and fails if the working tree diverges.
- **Markdown lint + dead-link check** — every doc, every link.
- **Consistency + versioning** — every long-lived file carries version + `## Changelog`.

## Safety Rules for Published Skills

Skills destined for a public marketplace MUST NOT contain:

- **PII**: names, emails, internal handles.
- **Credentials**: keys, tokens, passwords.
- **Hardcoded external URLs to restricted resources**: use the consumer KB's `sources.md` aliases.
- **Dangerous shell commands**: anything that deletes, force-pushes, drops, or modifies system state outside the workspace without opt-in.
- **Hidden tool dependencies**: tools not declared in frontmatter or not available in the target marketplace.

CI on the marketplace repo MUST validate these.

## Versioning

Each skill has its own `version` in frontmatter. The marketplace-level `version` in `.claude-plugin/marketplace.json`/`metadata` tracks the aggregate. Bump rules mirror [CHANGELOG.md](../../CHANGELOG.md) — PATCH / MINOR / MAJOR.

[ccm]: https://code.claude.com/docs/en/plugin-marketplaces.md
[vss]: https://code.visualstudio.com/docs/copilot/customization/agent-skills
[vsp]: https://code.visualstudio.com/docs/copilot/customization/agent-plugins
[ocs]: https://opencode.ai/docs/skills/
[oca]: https://opencode.ai/docs/agents/
[occ]: https://opencode.ai/docs/commands/

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | v0.2 — rewrote for compliance with Claude Code plugin marketplaces, VS Code Agent Skills/Plugins, and OpenCode skills/agents/commands | Harness docs cited above |
| 2026-04-18 | v0.1 — initial draft | Spec bootstrapping |
