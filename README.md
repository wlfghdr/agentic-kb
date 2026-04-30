# agentic-kb

> **Make decisions and context travel at the same speed as creation.**
> AI-native, layered knowledge operations. Vendor-neutral. No database. No cloud backend. Lives in your repo, next to your code.

[![CI](https://github.com/wlfghdr/agentic-kb/actions/workflows/validate.yml/badge.svg)](https://github.com/wlfghdr/agentic-kb/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Spec version](https://img.shields.io/badge/spec-v5.5.1-green.svg)](CHANGELOG.md)

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

- **Knowledge flows up.** Promote from the anchor layer into named contributor layers.
- **Context flows down.** Vision, mission, goals, and decisions digest back into your daily work automatically.
- **An evaluation gate at every boundary.** Five questions. Nothing silently filed. Nothing silently dropped. Every decision traced and logged.
- **Decisions, ideas, and tasks are first-class objects** with lifecycles — not comments lost in a chat.
- **Product direction, delivery, and operations handoffs are explicit.** Roadmaps, journeys, briefs, specs, release records, and incident records keep cross-role work readable for product, design, engineering, QA, on-call, and leadership.

You capture. The agent files, cross-links, promotes, and keeps humans and agents on the same page. Literally.

## Where this meets you on the agentic curve

You don't have to be "fully agentic" for `agentic-kb` to pay off. The contract is the same at every adoption stage; the agent just does more of the filing work the higher you go.

| Stage | Who decides | Who files | What runs `agentic-kb` looks like |
|-------|-------------|-----------|------------------------------------|
| **1 — Capture discipline** (human-only baseline) | humans, every step | humans, by hand | git + markdown + the `agentic-kb` directory contract; no agents required. You get audit trail, decision lifecycle, and cross-role handoffs (briefs, specs, releases, incidents) for free, just by writing into the right files. |
| **2 — Agent-assisted triage** | humans, at every gate | agent proposes, human confirms | the `/kb` evaluation gate fires on capture; the agent suggests where things belong; humans approve before anything persists. Maps to **automation level 1**. |
| **3 — Bounded autonomous knowledge ops** | humans, at exception gates | agent files, promotes, digests on a schedule | scheduled rituals (`start-day`, `digest`, `end-week`), guarded auto-promote on confidence threshold, exception escalation. Maps to **automation levels 2–3**. |

`agentic-kb` is the **knowledge-ops layer** of an agentic enterprise: it owns Strategy, Product Direction, Design, and Learning artifacts (foundation, roadmaps, journeys, briefs, specs, decisions, findings, topics, reports) and pairs cleanly with any **repo-as-OS framework** that owns the work-flow side (signals, missions, PRs, releases). It works standalone too — capture-discipline-only is a valid stop, not a half-installed product.

The right move for most teams is **start at Stage 1, graduate when the workflow is steady, never skip ahead.** `kb-setup` asks where you are today and biases the proposal to the lightest scaffold that still makes the next stage easy.

## Proof, not promises

The core adoption question is simple: can a skeptical team prove the shared loop end to end without inventing process around the tool?

The narrow proof path is now:

1. install into one documented harness surface
2. scaffold one anchor layer plus one adjacent shared layer
3. capture one source and inspect the resulting files in git
4. promote once, digest once, and inspect the shared state
5. regenerate index, dashboard, and report artifacts
6. run the repo-owned regression fixtures that prove the same path in CI

That is the claim surface. Architecture matters, but adoption only gets real once the proof strip is short enough to run.

## Why it's built this way

**Vendor-neutral by design.** Claude Code and VS Code Copilot Chat have marketplace/native plugin installs. OpenCode, Gemini CLI, and Kiro IDE have installer-backed native command or skill entrypoints. Codex CLI uses the same repo contract via `AGENTS.md` plus a reusable `kb` skill in `.agents/skills/`. Switch IDE tomorrow, your KB comes with you. No harness-owned memory trap. No cloud tier required to keep your own context.

**No database. No cloud backend.** Plain Markdown in a git repo. Your KB versions like code, reviews like code, diffs like code. If GitHub, GitLab, or a local folder can read it, agentic-kb works. If the vendor disappears tomorrow, your knowledge is still on disk.

**Lean by construction.** One spec. Two reference skills. One reference agent. One cross-harness installer. No SaaS. No auth. No infra. Plugin install in about a minute. Full workspace setup and first scaffold in about 15–20. Rip it out in five if it's not for you.

**Human + agent at the same speed.** This is the real claim: the system is designed so that a single human — an IC, a lead, or an exec — can stay in the loop with a swarm of agents *and* a team of other humans each running their own swarms, without becoming the bottleneck themselves.

## How it works

`agentic-kb` gives you a layered knowledge system that agents maintain. Every piece of material passes a **five-question evaluation gate** before it persists. You capture — the agent triages, files, cross-links, and keeps everything current.

### Flexible layers, one command

```
anchor layer  ──promote──▶  team layer  ──promote──▶  org layer  ──promote──▶  company layer
 (any scope)   ◀──digest──               ◀──digest──             ◀──digest──

layer marketplace(s) attach where needed:

team layer ──publish──▶ team marketplace
org layer  ──publish──▶ org marketplace
```

At least one **contributor-capable layer** is required. A personal layer is recommended, but not mandatory. The user's anchor layer holds `.kb-config/layers.yaml`, and every other layer is declared there with `scope`, `role`, `parent`, `features`, `marketplace`, and `connections`.

There is exactly one user-facing command: **`/kb`**. The core plugin ships stable knowledge-ops flows. Product-management flows use the same command surface: `/kb setup` proposes roadmap and journey configuration when the user's role, goals, sources, or desired outputs call for them, and the adopter decides which layer owns those artifacts.

```
# Stable core flows
/kb                        → status
/kb [text/URL/path]        → capture + evaluate
/kb review                 → process inputs/
/kb promote [file] [layer] → promote to the next or named contributor layer
/kb digest [layer]         → pull parent-layer changes
/kb digest connections     → pull linked repo / tracker deltas
/kb migrate archives       → preview or apply year-based archive moves
/kb migrate layer-model    → preview or apply fixed-ladder to layer-graph migration
/kb note [text]            → create a working note
/kb note meeting [topic]   → start a meeting note
/kb idea [text]            → create an idea (seed)
/kb develop [idea]         → sparring session on an idea
/kb decide [description]   → open a decision
/kb task                   → show focus items
/kb start-day              → morning briefing
/kb end-week               → Friday 15:00 summary
/kb present [topic]        → versioned HTML presentation (light + dark)
/kb report progress [scope]→ cross-source progress report
/kb setup                  → interactive onboarding

# Product-management flows (installed with the plugin, scaffolded when setup derives them)
/kb roadmap                → reconcile plan truth vs delivery reality
/kb journeys               → author and render journey specs + mocks
```

For roadmap adoption, keep the first proof path lean: start with exported tracker markdown bound through `ticket-export-markdown`, prove the artifact flow locally, then add live tracker adapters and write-back only after the export-backed path is trusted. For journey adoption, start with one end-to-end journey owned by the same layer that owns the roadmap scope, then split across layers only after the ownership boundary is clear.

### The evaluation gate

| Matches | Outcome |
|--------:|---------|
| 0/5 | Discard, logged with reason |
| 1–2/5 | Finding only (offer idea creation if novelty detected) |
| 3+/5 | Finding + topic update + possibly a new decision or idea |

Never silent. Every accept and reject carries a rationale.

## Getting started

Connect this repo as a marketplace in your IDE, then run `/kb setup` — that's it.

Marketplace install gives you the core plugin (`kb-management`, `kb-setup`, `kb-operator`) plus two product-management draft skills (`kb-roadmap`, `kb-journeys`). The skills stay dormant until `/kb setup` derives and the user confirms matching config blocks in `.kb-config/layers.yaml` and `.kb-config/artifacts.yaml`, or until an expert adds those blocks manually.

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

`agentic-kb` distinguishes three supported setup tiers — plus two "not yet" buckets that document why some harnesses sit outside the supported matrix today:

| Tier | Meaning | Current examples |
|------|---------|------------------|
| Marketplace/native plugin path | Native install path and documented day-to-day workflow with a working `/kb` slash command | Claude Code, VS Code Copilot Chat |
| Installer-supported native command/skill path | No marketplace yet, but `scripts/install --target <harness>` writes the harness's documented native surface | OpenCode, Gemini CLI, Kiro IDE |
| Compatible skill workflow | Same repo contract, but no custom `/kb` slash command; use `AGENTS.md` plus the harness skill picker or native skill invocation | Codex CLI |

Not (yet) covered as a supported tier:

| Bucket | Why | Current examples |
|--------|-----|------------------|
| Rules-only harness | No slash-command slot for third-party commands — adopters can reuse the scaffolded KB files as context, but invocation is wired manually | Cursor, Windsurf |
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
│       ├── utils/            # optional reusable helpers for skills in this plugin
│       └── agents/
│           └── kb-operator.md
├── docs/
│   ├── REFERENCE.md          # implementation-critical structure and contracts
│   ├── operating-model.md    # role loops, artifact chain, and coverage gaps
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
├── tests/
│   └── fixtures/             # optional regression fixtures for safety/routing checks
└── .github/                  # CI, issue/PR templates
```

## Where to start

1. [`docs/REFERENCE.md`](docs/REFERENCE.md) — architecture, layout, formats, and contracts.
2. [`docs/operating-model.md`](docs/operating-model.md) — the software-engineering role model, artifact chain, and the delivery/operations gaps this workspace now names explicitly.
3. [`docs/first-run-acceptance.md`](docs/first-run-acceptance.md) — the deterministic first-run acceptance path for onboarding and rollout checks.
4. [`docs/examples/first-hour.md`](docs/examples/first-hour.md) — the fastest end-to-end walkthrough from install to the first useful cross-layer proof.
5. [`docs/collaboration.md`](docs/collaboration.md) — the human collaboration contract for shared KB workspaces.
6. [`plugins/kb/skills/kb-management/references/output-contract.md`](plugins/kb/skills/kb-management/references/output-contract.md) — the collaboration-safe response contract for auditability and handoffs.
7. [`docs/examples/day-in-the-life.md`](docs/examples/day-in-the-life.md) — what it feels like in practice.
8. [`plugins/kb/skills/kb-management/SKILL.md`](plugins/kb/skills/kb-management/SKILL.md) — the full behavioral spec (this IS the spec).

## Status

| Area | Status |
|------|--------|
| Framework spec | Stable (v5.5.1), open items in [`docs/roadmap.md`](docs/roadmap.md) |
| Core plugin (`kb-management`, `kb-setup`, `kb-operator`) | Stable reference implementation |
| Product-management draft skills | `kb-roadmap`, `kb-journeys` (draft, `v0.2.0`, setup-proposed by role/goals) |
| Multi-harness installer | Working (Claude Code / VS Code / OpenCode / Gemini / Kiro / Codex skill path) |
| CI | Markdown lint, dead-link check, consistency, plugin structure, generator drift, HTML validation |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Every doc change updates the per-file changelog, the root [`CHANGELOG.md`](CHANGELOG.md), and CI must stay green. Rules for both humans and agents: [`AGENTS.md`](AGENTS.md).

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-30 | Rolled the public framework status to 5.5.1 after correcting the HTML landing-page value proposition so product direction, roadmaps, journeys, delivery, and operations are visible in the top-level story and first-class building blocks | HTML value-prop correction |
| 2026-04-30 | Rolled the public framework status to 5.5.0 after making roadmap and journey work a setup-proposed product-management surface: `/kb setup` now derives ownership/config from role, goals, sources, and desired outputs instead of leaving the draft skills hidden behind manual config | Product-management surface integration |
| 2026-04-29 | Rolled the public framework status to 5.4.2 after the draft-skill discoverability fix: the packaged `/kb` dispatcher now routes `/kb roadmap` and `/kb journeys` to the matching draft skills, the kb-management trigger surface picks up roadmap/journey keywords, and the visual landing page advertises the two opt-in subcommands so marketplace adopters can find them | v5.4.2 draft-skill discoverability fix |
| 2026-04-27 | Rolled the public framework status to 5.4.1 after the documentation-gap follow-up: added dedicated connection lifecycle and publish contract references, clarified the repo-as-OS bridge field name to `connections.product-repos[]`, and documented VMG sourcing/update behavior in setup flow | 5.4.1 patch release |
| 2026-04-27 | Added the "Where this meets you on the agentic curve" section with the three-stage adoption ladder (capture discipline → agent-assisted triage → bounded autonomous), positioned `agentic-kb` as the knowledge-ops layer that pairs with any repo-as-OS framework, and rolled the public framework status to 5.4.0 | Soft-transition extension |
| 2026-04-26 | Added the operating-model entry point, surfaced the new delivery/operations handoff artifacts in the main value proposition, and rolled the public framework status to 5.3.0 | Software-engineering operating-model gap closure |
| 2026-04-25 | v5.2.0 release alignment — bumped the spec badge and Status row to match the new framework version that ships the kb-management trigger expansion and the kb-setup goal-oriented question flow | v5.2.0 trigger + setup rework |
| 2026-04-25 | Clarified the setup proof strip by separating the quick plugin install from the longer guided workspace scaffold and added the `first-hour` walkthrough to "Where to start" | Deep spec-audit follow-up |
| 2026-04-25 | Removed the "One-page visual overview → index.html" pointer from the header and the `index.html` entry from "Where to start" so the README is the canonical narrative entry point and the visual landing page stands on its own | Index marketing trim |
| 2026-04-25 | Concept-audit follow-up: relabeled the compatibility model so the "three setup tiers" wording matches the table (rules-only and not-feasible moved into a separate "not yet covered" block) | Concept-audit drift correction |
| 2026-04-25 | Updated the public command summary and release status for 5.1.0, including the new migration helper flows that close the remaining 5.0 follow-up gaps | v5.1.0 follow-up closeout |
