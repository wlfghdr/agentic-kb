# agentic-kb

> AI-native, layered knowledge operations. A specification, a reference implementation, and a small set of portable skills for any agentic IDE.

[![CI](https://github.com/wlfghdr/agentic-kb/actions/workflows/validate.yml/badge.svg)](https://github.com/wlfghdr/agentic-kb/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Spec version](https://img.shields.io/badge/spec-v2.0.0-green.svg)](CHANGELOG.md)

**One-page visual overview** → [`index.html`](index.html) (open in a browser — light + dark themes, self-contained).

---

## The problem

Most knowledge bases rot. They start as wikis, turn into graveyards, and never help again:

- **Decay** — pages drift out of sync with reality; nobody trusts them; nobody maintains them.
- **Context loss** — decisions are buried in chat threads, meeting notes, inbox replies.
- **Manual curation fatigue** — triaging, tagging, cross-linking, archiving is a full-time job nobody has.
- **Cross-layer opacity** — personal notes, team workspaces, org strategy, company OKRs each live in silos.

## The solution

`agentic-kb` inverts the problem. Every piece of material passes a **five-question evaluation gate** before it persists. Agents do the bookkeeping; humans do the thinking.

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

## Install

### Claude Code

Inside Claude Code:

```
/plugin marketplace add https://github.com/<org>/agentic-kb
/plugin install kb@agentic-kb
```

### VS Code Copilot Chat

In `settings.json`:

```json
{
  "chat.plugins.marketplaces": [
    "<org>/agentic-kb"
  ]
}
```

Then install from the Extensions view — it reads the top-level [`plugin.json`](plugin.json).

### OpenCode

No official plugin marketplace yet. Clone and install:

```bash
git clone https://github.com/<org>/agentic-kb
cd agentic-kb
scripts/install --target opencode --global
```

OpenCode natively reads `.claude/skills/` — a Claude Code install in the same workspace is picked up automatically.

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
