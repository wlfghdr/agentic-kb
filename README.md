# agentic-kb

> AI-native, layered knowledge operations. A specification, a reference implementation, and a small set of portable skills for any agentic IDE.

[![CI](https://github.com/wlfghdr/agentic-kb/actions/workflows/validate.yml/badge.svg)](https://github.com/wlfghdr/agentic-kb/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Spec version](https://img.shields.io/badge/spec-v2.0.0-green.svg)](CHANGELOG.md)

**One-page visual overview** → [`index.html`](index.html)

---

## Does this sound familiar?

- *"How do I actually work AI-natively — with agents, not just chat?"*
- *"How does my team share knowledge so agents can use it — not just humans?"*
- *"Where do decisions, positions, and context go so they survive across sessions, tools, and people?"*
- *"Is there something I can just install and start using — one command, not a month-long rollout?"*

If yes: that's what `agentic-kb` solves. One command — `/kb` — and the agent handles capture, evaluation, cross-referencing, and promotion across layers. You think, the agent does the bookkeeping.

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

There is exactly one user-facing command: **`/kb`**. The agent infers the layer and action from context.

```
/kb                        → status
/kb [text/URL/path]        → capture + evaluate
/kb review                 → process inputs/
/kb promote [file]         → push to team KB
/kb digest team            → pull team changes
/kb decide [description]   → open a decision
/kb start-day              → morning briefing
/kb end-week               → Friday 15:00 summary
/kb present [topic]        → versioned HTML presentation (light + dark)
/kb setup                  → interactive onboarding
```

### The evaluation gate

| Matches | Outcome |
|--------:|---------|
| 0/5 | Discard, logged with reason |
| 1–2/5 | Finding only (dated snapshot) |
| 3+/5 | Finding + topic update + possibly a new decision |

Never silent. Every accept and reject carries a rationale.

## Getting started

Connect this repo as a marketplace in your IDE, then run `/kb setup` — that's it.

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

### OpenCode

No official plugin marketplace yet. Clone and install manually:

```bash
git clone https://github.com/wlfghdr/agentic-kb
cd agentic-kb
scripts/install --target opencode --global
```

OpenCode natively reads `.claude/skills/` — a Claude Code install in the same workspace is picked up automatically. Then run `/kb setup`.

### Cross-harness install (optional)

If you already have the skills in one harness and want to add them to another, the install script can do that. `/kb setup` will offer this during onboarding — no need to run it manually.

```bash
scripts/install --target vscode --global     # add to VS Code
scripts/install --target opencode --global   # add to OpenCode
scripts/install --target all --global        # all harnesses
```

## Repo layout

```
agentic-kb/
├── README.md
├── plugin.json               # VS Code Agent Plugin manifest
├── .claude-plugin/
│   └── marketplace.json      # Claude Code plugin marketplace manifest
├── skills/                   # cross-agent skills (source of truth)
│   ├── kb-management/
│   └── kb-setup/
├── agents/
│   └── kb-operator.md
├── plugins/                  # generated from marketplace.json
│   └── kb/
├── docs/
│   ├── concept/              # principles, architecture, memory model, decisions, flows, …
│   ├── spec/                 # workspace layout, commands, rituals, marketplace, harnesses, HTML artifacts
│   ├── examples/
│   ├── roadmap.md
│   └── glossary.md
├── index.html                    # visual one-pager (GitHub Pages root)
├── scripts/
│   ├── install               # cross-harness installer
│   ├── generate_plugins.py   # rebuilds plugins/ from marketplace.json
│   ├── check_consistency.py  # versions + internal links
│   ├── check_plugin_structure.py
│   └── check_html_artifacts.py
└── .github/                  # CI, issue/PR templates
```

## Where to start

1. [`index.html`](index.html) — open in a browser for a 2-minute visual overview.
2. [`docs/concept/01-overview.md`](docs/concept/01-overview.md) — principles + mental model.
3. [`docs/concept/02-architecture.md`](docs/concept/02-architecture.md) — the five layers.
4. [`docs/spec/commands.md`](docs/spec/commands.md) — the full `/kb` surface.
5. [`docs/examples/day-in-the-life.md`](docs/examples/day-in-the-life.md) — what it feels like in practice.

## Status

| Area | Status |
|------|--------|
| Concept | Stable (v2.0) |
| Spec | Stable (v2.0), open items in [`docs/roadmap.md`](docs/roadmap.md) |
| Reference skills (`kb-management`, `kb-setup`) | Scaffolded |
| Reference agent (`kb-operator`) | Scaffolded |
| Multi-harness installer | Working (Claude Code / VS Code / OpenCode) |
| CI | Markdown lint, dead-link check, consistency, plugin structure, generator drift, HTML validation |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Every doc change updates the per-file changelog, the root [`CHANGELOG.md`](CHANGELOG.md), and CI must stay green. Rules for both humans and agents: [`AGENTS.md`](AGENTS.md).

## License

Apache License 2.0 — see [LICENSE](LICENSE).
