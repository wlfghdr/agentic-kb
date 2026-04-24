# agentic-kb

> **Make decisions and context travel at the same speed as creation.**
> AI-native, layered knowledge operations. Vendor-neutral. No database. No cloud backend. Lives in your repo, next to your code.

[![CI](https://github.com/wlfghdr/agentic-kb/actions/workflows/validate.yml/badge.svg)](https://github.com/wlfghdr/agentic-kb/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Spec version](https://img.shields.io/badge/spec-v4.0.0-green.svg)](CHANGELOG.md)

**One-page visual overview** → [`index.html`](index.html)

---

## The real problem

Your agents made you 10× faster at creating. Nothing made you faster at *deciding*.

Prototypes appear overnight. Specs write themselves. Ideas multiply. Branches multiply. Everyone on the team produces more than they used to produce in a week — and then nobody can keep up with *reviewing, synthesizing, and deciding* what's actually worth pursuing.

The bottleneck didn't move to design. It didn't move to quality. **It moved to convergence.**

Symptoms you'll recognize:

- *"We're shipping more than ever and somehow feel blurrier about where we're going."*
- *"I can't get to every direction fast enough to say yes or no."*
- *"My agents are aligned with me. Yours are aligned with you. We're not aligned with each other."*
- *"By the time leadership catches up with what's been built, another three things got built."*

If any of that sounds familiar — this is the piece of the fix we've been building.

## The fix, in one breath

One command — **`/kb`** — across any agentic IDE. A layered knowledge system where:

- **Knowledge flows up.** Promote from personal → team → org → marketplace.
- **Context flows down.** Vision, mission, goals, and decisions digest back into your daily work automatically.
- **An evaluation gate at every boundary.** Five questions. Nothing silently filed. Nothing silently dropped. Every decision traced and logged.
- **Decisions, ideas, and tasks are first-class objects** with lifecycles — not comments lost in a chat.

You capture. The agent files, cross-links, promotes, and keeps humans and agents on the same page. Literally.

## Proof, not promises

The core adoption question is simple: can a skeptical team prove the shared loop end to end without inventing process around the tool?

The narrow proof path is now:

1. install into one documented harness surface
2. scaffold a personal, team, and org workspace
3. capture one source and inspect the resulting files in git
4. promote once, digest once, and inspect the shared state
5. regenerate index, dashboard, and report artifacts
6. run the repo-owned regression fixtures that prove the same path in CI

That is the claim surface. Architecture matters, but adoption only gets real once the proof strip is short enough to run.

## Why it's built this way

**Vendor-neutral by design.** Claude Code and VS Code Copilot Chat have marketplace/native plugin installs. OpenCode, Gemini CLI, and Kiro IDE have installer-backed native command or skill entrypoints. Codex CLI uses the same repo contract via `AGENTS.md` plus a reusable `kb` skill in `.agents/skills/`. Switch IDE tomorrow, your KB comes with you. No harness-owned memory trap. No cloud tier required to keep your own context.

**No database. No cloud backend.** Plain Markdown in a git repo. Your KB versions like code, reviews like code, diffs like code. If GitHub, GitLab, or a local folder can read it, agentic-kb works. If the vendor disappears tomorrow, your knowledge is still on disk.

**Lean by construction.** One spec. Two reference skills. One reference agent. One cross-harness installer. No SaaS. No auth. No infra. Install in about a minute. Rip it out in five if it's not for you.

**Human + agent at the same speed.** This is the real claim: the system is designed so that a single human — an IC, a lead, or an exec — can stay in the loop with a swarm of agents *and* a team of other humans each running their own swarms, without becoming the bottleneck themselves.

## How it works

`agentic-kb` gives you a layered knowledge system that agents maintain. Every piece of material passes a **five-question evaluation gate** before it persists. You capture — the agent triages, files, cross-links, and keeps everything current.

### Five layers, one command

```
L1 Personal  ──promote──▶  L2 Team  ──promote──▶  L3 Org-Unit  ──publish──▶  L4 Marketplace
(required)    ◀──digest──           ◀──digest──              ◀──install──
                                                                                 ▲
                                                                                 │
                                                                          L5 Company
                                                                          (top-down)
```

Only **L1** is required. Higher layers are optional and declared in the user's config.

There is exactly one user-facing command: **`/kb`**. The core plugin ships stable knowledge-ops flows, and optional draft skills extend the same command with roadmap and journey subcommands when adopters opt in via config.

```
# Stable core flows
/kb                        → status
/kb [text/URL/path]        → capture + evaluate
/kb review                 → process inputs/
/kb promote [file]         → promote to team KB and complete local team review
/kb digest team            → pull team changes
/kb idea [text]            → create an idea (seed)
/kb develop [idea]         → sparring session on an idea
/kb decide [description]   → open a decision
/kb task                   → show focus items
/kb start-day              → morning briefing
/kb end-week               → Friday 15:00 summary
/kb present [topic]        → versioned HTML presentation (light + dark)
/kb setup                  → interactive onboarding

# Optional draft flows (installed with the plugin, not scaffolded by default)
/kb roadmap                → reconcile plan truth vs delivery reality
/kb journeys               → author and render journey specs + mocks
```

For roadmap adoption, keep the first proof path lean: start with exported GitHub or Jira markdown bound through `ticket-export-markdown`, prove the artifact flow locally, then add live tracker adapters and write-back only after the export-backed path is trusted.

### The evaluation gate

| Matches | Outcome |
|--------:|---------|
| 0/5 | Discard, logged with reason |
| 1–2/5 | Finding only (offer idea creation if novelty detected) |
| 3+/5 | Finding + topic update + possibly a new decision or idea |

Never silent. Every accept and reject carries a rationale.

## Getting started

Connect this repo as a marketplace in your IDE, then run `/kb setup` — that's it.

Marketplace install gives you the core plugin (`kb-management`, `kb-setup`, `kb-operator`) plus two opt-in draft skills (`kb-roadmap`, `kb-journeys`). The draft skills stay dormant until their config blocks are added to `.kb-config/layers.yaml` and `.kb-config/artifacts.yaml`.

### Claude Code

```
/plugin marketplace add https://github.com/wlfghdr/agentic-kb
/plugin install kb@agentic-kb
/kb setup
```

### VS Code Copilot Chat

Add to `settings.json`:

```json
{
  "chat.plugins.marketplaces": [
    "wlfghdr/agentic-kb"
  ]
}
```

Install from the Extensions view (reads [`plugin.json`](plugin.json)), then run `/kb setup` in Copilot Chat.

### Compatibility model

`agentic-kb` now distinguishes three setup tiers so additional harnesses can be documented consistently:

| Tier | Meaning | Current examples |
|------|---------|------------------|
| Marketplace/native plugin path | Native install path and documented day-to-day workflow with a working `/kb` slash command | Claude Code, VS Code Copilot Chat |
| Installer-supported native command/skill path | No marketplace yet, but `scripts/install --target <harness>` writes the harness's documented native surface | OpenCode, Gemini CLI, Kiro IDE |
| Compatible skill workflow | Same repo contract, but no custom `/kb` slash command; use `AGENTS.md` plus the harness skill picker or native skill invocation | Codex CLI |
| Rules-only harness | No slash-command slot for third-party commands — adopters use the scaffolded KB files as context but wire invocation manually | Cursor, Windsurf |
| Not feasible | The harness has no user-custom command hook, or is not a developer harness at all | Aider (no plugin system yet), raw Claude / Inflection Pi (no slash-command concept) |

### OpenCode

No official plugin marketplace yet. Clone and install manually:

```bash
git clone https://github.com/wlfghdr/agentic-kb
cd agentic-kb
scripts/install --target opencode --global
```

OpenCode natively reads `.claude/skills/` — a Claude Code install in the same workspace is picked up automatically. Then run `/kb setup`.

### Codex CLI

Codex reads `AGENTS.md` for project instructions and `.agents/skills/<name>/SKILL.md` for reusable workflows. The installer writes a repo-local or user-global `kb` skill for you:

```bash
scripts/install --target codex
scripts/install --target codex --global
```

Use the Codex skill picker or `$kb`; the workspace contract stays the same even though the invocation surface is a skill rather than a custom slash command.

### Gemini CLI

Gemini's custom commands are TOML files under `.gemini/commands/` (workspace) or `~/.gemini/commands/` (global). The installer emits a minimal wrapper whose `prompt` field embeds the full `kb` command body:

```bash
scripts/install --target gemini           # workspace-local
scripts/install --target gemini --global  # global
```

`/kb` is then a first-class Gemini CLI slash command.

### Kiro IDE

Kiro's documented reusable package format is `.kiro/skills/<name>/SKILL.md`, and those skills show up in the slash menu. The installer writes that skill for you:

```bash
scripts/install --target kiro
```

Type `/kb` in Kiro Chat and it routes through the installed `kb` skill.

### Cross-harness install (optional)

If you already have the skills in one harness and want to add them to another, the install script can do that. `/kb setup` will offer this during onboarding — no need to run it manually.

```bash
scripts/install --target vscode --global     # add to VS Code
scripts/install --target opencode --global   # add to OpenCode
scripts/install --target codex --global      # add the Codex kb skill (~/.agents/skills/kb/SKILL.md)
scripts/install --target gemini --global     # add to Gemini CLI (generates TOML)
scripts/install --target kiro --global       # add the Kiro kb skill (~/.kiro/skills/kb/SKILL.md)
scripts/install --target all --global        # all supported harnesses
```

## Repo layout

```
agentic-kb/
├── README.md
├── plugin.json               # root marketplace manifest
├── .claude-plugin/
│   └── marketplace.json      # Claude Code plugin marketplace manifest
├── plugins/
│   └── kb/
│       ├── plugin.json       # per-plugin manifest
│       ├── skills/           # canonical skill source tree
│       │   ├── kb-management/
│       │   ├── kb-setup/
│       │   ├── kb-roadmap/
│       │   └── kb-journeys/
│       └── agents/
│           └── kb-operator.md
├── docs/
│   ├── REFERENCE.md          # implementation-critical structure and contracts
│   ├── collaboration.md      # shared-workspace human collaboration contract
│   ├── first-run-acceptance.md
│   ├── examples/
│   ├── roadmap.md
│   └── glossary.md
├── index.html                    # visual one-pager (GitHub Pages root)
├── scripts/
│   ├── install               # cross-harness installer
│   ├── generate_plugins.py   # rebuilds plugins/ from marketplace.json
│   ├── generate-index.py     # generates root index.html for any KB layer
│   ├── check_consistency.py  # versions + internal links
│   ├── check_plugin_structure.py
│   └── check_html_artifacts.py
└── .github/                  # CI, issue/PR templates
```

## Where to start

1. [`index.html`](index.html) — open in a browser for a 2-minute visual overview.
2. [`docs/REFERENCE.md`](docs/REFERENCE.md) — architecture, layout, formats, and contracts.
3. [`docs/first-run-acceptance.md`](docs/first-run-acceptance.md) — the deterministic first-run acceptance path for onboarding and rollout checks.
4. [`docs/collaboration.md`](docs/collaboration.md) — the human collaboration contract for shared KB workspaces.
5. [`plugins/kb/skills/kb-management/references/output-contract.md`](plugins/kb/skills/kb-management/references/output-contract.md) — the collaboration-safe response contract for auditability and handoffs.
6. [`docs/examples/day-in-the-life.md`](docs/examples/day-in-the-life.md) — what it feels like in practice.
7. [`plugins/kb/skills/kb-management/SKILL.md`](plugins/kb/skills/kb-management/SKILL.md) — the full behavioral spec (this IS the spec).

## Status

| Area | Status |
|------|--------|
| Framework spec | Stable (v4.0.0), open items in [`docs/roadmap.md`](docs/roadmap.md) |
| Core plugin (`kb-management`, `kb-setup`, `kb-operator`) | Stable reference implementation |
| Optional draft skills | `kb-roadmap`, `kb-journeys` (draft, `v0.1.0`, opt-in) |
| Multi-harness installer | Working (Claude Code / VS Code / OpenCode / Gemini / Kiro / Codex skill path) |
| CI | Markdown lint, dead-link check, consistency, plugin structure, generator drift, HTML validation |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Every doc change updates the per-file changelog, the root [`CHANGELOG.md`](CHANGELOG.md), and CI must stay green. Rules for both humans and agents: [`AGENTS.md`](AGENTS.md).

## License

Apache License 2.0 — see [LICENSE](LICENSE).
