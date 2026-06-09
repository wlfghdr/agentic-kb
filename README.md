# agentic-kb

> **Make decisions and context travel at the same speed as creation.**
> AI-native, layered knowledge operations. Vendor-neutral. No database. No cloud backend. Lives in your repo, next to your code.

[![CI](https://github.com/wlfghdr/agentic-kb/actions/workflows/validate.yml/badge.svg)](https://github.com/wlfghdr/agentic-kb/actions/workflows/validate.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Spec version](https://img.shields.io/badge/spec-v6.3.1-green.svg)](CHANGELOG.md)

---

## The agentic-* suite

`agentic-kb` works with any harness and any workflow framework — and it is also the **knowledge layer** of the agentic-* suite, three building blocks for running an agentic organization on Git:

| Repo | Role |
|------|------|
| [agentic-enterprise](https://github.com/wlfghdr/agentic-enterprise) | **The operating model** — governance layers, process loops, policies, and templates. Humans decide, agents execute, Git governs. |
| [agentic-kb](https://github.com/wlfghdr/agentic-kb) | **The knowledge layer** — layered, vendor-neutral knowledge ops via the `/kb` command (this repo). |
| [agentic-dev](https://github.com/wlfghdr/agentic-dev) | **The execution layer** — deterministic engineering triage and execution loop. |

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
| **3 — Bounded autonomous knowledge ops** | humans, at exception gates | agent files, promotes, digests on a cadence you wire | scheduled rituals (`start-day`, `digest`, `end-week`), guarded auto-promote on confidence threshold, exception escalation. Maps to **automation levels 2–3**. `agentic-kb` does not ship a scheduler — you wire OS cron, CI, or your harness's native automation to invoke `/kb`; the skill defines what runs, you own the trigger. |

`agentic-kb` is the **knowledge-ops layer** of an agentic enterprise: it owns Strategy, Product Direction, Design, and Learning artifacts (foundation, roadmaps, journeys, briefs, specs, decisions, findings, topics, reports) and pairs cleanly with any **repo-as-OS framework** that owns the work-flow side (signals, missions, PRs, releases) — for example [agentic-enterprise](https://github.com/wlfghdr/agentic-enterprise) with its execution loop [agentic-dev](https://github.com/wlfghdr/agentic-dev) (see [The agentic-* suite](#the-agentic--suite)). It works standalone too — capture-discipline-only is a valid stop, not a half-installed product.

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

**Lean by construction.** One spec. Reference behavioral specs that any compatible harness runs. One reference agent persona. One cross-harness installer. No SaaS. No auth. No infra. Plugin install in about a minute. Full workspace setup and first scaffold in about 15–20. [Rip it out in five](docs/uninstall.md) if it's not for you.

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

**Most used (start here).** New adopters do not need to learn the full surface to get value. After `/kb setup`, the wizard emits a curated 3–5 command shortlist tailored to your adoption stage. The five you'll use first in almost every setup:

```
/kb [text/URL/path]           → file something into the KB through the evaluation gate
/kb note meeting [topic]      → start a meeting note (also: /kb note retro [topic])
/kb decide [description]      → open a decision
/kb start-day                 → morning briefing
/kb status                    → triage scan / where do I stand right now?
```

The full subcommand surface (capture, promote, publish, digest, sync, decide, brief/spec/release/incident, rituals, audit, present/report, plus the product-management `/kb roadmap` and `/kb journeys` handoffs) lives in one canonical reference: [`plugins/kb/skills/kb-management/references/command-reference.md`](plugins/kb/skills/kb-management/references/command-reference.md). The README intentionally does not duplicate the full list — `command-reference.md` is the single source of truth, and CI checks that the dispatcher and reference stay in sync.

### Roadmap and journeys as one operating system

`agentic-kb` treats roadmap and journeys as connected but different control layers:

- **Roadmap** answers: what are we trying to move, what is actually moving, where is reality diverging, and what decision is needed now?
- **Journeys** answer: what behavior is the product or process supposed to deliver for which persona, through which path, and at what readiness?

A healthy operating model needs both:

- **top-down** from strategy, goals, milestones, and leadership intent
- **bottom-up** from engineering reality, prototypes, customer feedback, and daily work

In practice that means:

- a **joint roadmap** for lead-curated cross-scope progress, risks, scope changes, and decisions
- **detail roadmaps / engineering backlogs per workstream** for domain-owned progress, demos, refinements, and feedback calls
- **journeys** as the reference layer that explains what the work is supposed to make true in the product

For roadmap adoption, keep the first proof path lean: start with exported tracker markdown bound through `ticket-export-markdown`, prove the artifact flow locally, then add live tracker adapters and write-back only after the export-backed path is trusted. For journey adoption, start with one end-to-end journey owned by the same layer that owns the roadmap scope, then split across layers only after the ownership boundary is clear.

### GitHub as an operating backbone

If a team already uses GitHub Issues, GitHub Projects, and pull requests as its operating loop, `/kb setup` can generate a generic GitHub governance profile instead of leaving the adopter to invent one.

That profile includes:

- issue forms for feedback, ideas, decisions, tasks, bugs, features, roadmap items, content updates, and governance changes,
- a PR template that ties changes back to tracker items, KB artifacts, validation, changelog/version impact, and safe review,
- a governance workflow that checks issue-template syntax, unresolved placeholders, linked issues or explicit exceptions, optional version-impact labels, and repo-local skill presence,
- a generic path labeler,
- a repo-local tracker workflow skill that teaches agents the same issue/project/PR rules CI enforces,
- a manual checklist for native issue types, project/status fields, labels, milestones, branch protection, CODEOWNERS, parent/sub-issues, and required checks.

The profile stays generic: no organization names, no product-specific labels, no hardcoded project IDs. Setup fills or stages the adopter-specific values and keeps write-back confirmation-gated.

### The evaluation gate

| Matches | Outcome |
|--------:|---------|
| 0/5 | Discard, logged with reason |
| 1–2/5 | Finding only (offer idea creation if novelty detected) |
| 3+/5 | Finding + topic update + possibly a new decision or idea |

Never silent. Every accept and reject carries a rationale.

## Getting started

Connect this repo as a marketplace in your IDE, then run `/kb setup` — that's it.

Marketplace install gives you the core plugin (`kb-management`, `kb-setup`, `kb-operator`) plus two setup-proposed product-management skills (`kb-roadmap`, `kb-journeys`). Roadmap and journey flows activate only after `/kb setup` derives and the user confirms matching config blocks in `.kb-config/layers.yaml` and `.kb-config/artifacts.yaml`, or after an expert adds those blocks manually.

### Claude Code

```
/plugin marketplace add https://github.com/wlfghdr/agentic-kb
/plugin install kb@agentic-kb
/kb setup
```

### VS Code Copilot Chat

> **VS Code Agent plugins are a Microsoft Preview feature.** The `chat.plugins.marketplaces` setting and the plugins surface around it are documented at [code.visualstudio.com/docs/copilot/customization/agent-plugins](https://code.visualstudio.com/docs/copilot/customization/agent-plugins). API and behaviour may change before VS Code declares it stable. If you want a stable path today, use `scripts/install --target vscode` (writes `.github/prompts/kb.prompt.md` and `.github/instructions/kb.instructions.md` directly).

Add to **user-level** `settings.json` (workspace settings are not honored for this key):

```json
{
  "chat.plugins.marketplaces": [
    "wlfghdr/agentic-kb"
  ]
}
```

Install from the Extensions view (reads [`plugin.json`](plugin.json)), then run `/kb setup` in Copilot Chat.

### Compatibility model

`agentic-kb` distinguishes three supported setup tiers:

| Tier | Meaning | Current examples |
|------|---------|------------------|
| Marketplace/native plugin path | Native install path and documented day-to-day workflow with a working `/kb` slash command | Claude Code, VS Code Copilot Chat |
| Installer-supported native command/skill path | No marketplace yet, but `scripts/install --target <harness>` writes the harness's documented native surface | OpenCode, Gemini CLI, Kiro IDE |
| Compatible skill workflow | Same repo contract, but no custom `/kb` slash command; use `AGENTS.md` plus the harness skill picker or native skill invocation | Codex CLI |

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

The reading list is grouped by audience. Pick the row that matches what you are trying to do.

### If you just installed agentic-kb and want to use it

1. [`docs/examples/first-hour.md`](docs/examples/first-hour.md) — fastest end-to-end walkthrough: install → `/kb setup` → first capture → first promote.
2. [`docs/examples/day-in-the-life.md`](docs/examples/day-in-the-life.md) — what it feels like in practice for an engineer, a PM, an EM, and an on-call SRE.
3. [`docs/uninstall.md`](docs/uninstall.md) — clean exit door if it turns out not to be for you.

### If you want to understand the model before you commit

1. [`docs/REFERENCE.md`](docs/REFERENCE.md) — architecture, layout, formats, and contracts. The implementation-critical reference.
2. [`docs/operating-model.md`](docs/operating-model.md) — the software-engineering role model, artifact chain, and the delivery/operations gaps this workspace names explicitly.
3. [`docs/role-handbook.md`](docs/role-handbook.md) — role-by-role companion to the operating model.
4. [`docs/glossary.md`](docs/glossary.md) — authoritative term list. Read first if the spec uses a word you're not sure about.

### If you are deciding whether to roll it out to a team

1. [`docs/collaboration.md`](docs/collaboration.md) — human collaboration contract for shared KB workspaces.
2. [`plugins/kb/skills/kb-management/references/output-contract.md`](plugins/kb/skills/kb-management/references/output-contract.md) — collaboration-safe response contract for auditability and handoffs.
3. [`plugins/kb/skills/kb-management/SKILL.md`](plugins/kb/skills/kb-management/SKILL.md) — full behavioral spec. **This IS the spec.**

### If you are a maintainer or QA verifying a release

1. [`docs/first-run-acceptance.md`](docs/first-run-acceptance.md) — deterministic first-run acceptance path. Maintainer/QA checklist, not an onboarding doc — adopters use first-hour.md instead.
2. [`AGENTS.md`](AGENTS.md) — rules of engagement for both humans and agents working in this repo.
3. [`CONTRIBUTING.md`](CONTRIBUTING.md) — PR checklist, local CI commands, vendor-neutrality guard.

## Status

| Area | Status |
|------|--------|
| Framework spec | Stable (v6.3.1), open items in [`docs/roadmap.md`](docs/roadmap.md) |
| Core plugin (`kb-management`, `kb-setup`, `kb-operator`) | Stable behavioral spec (executed by the harness's agent; no runtime ships) |
| Product-management skills | `kb-roadmap`, `kb-journeys` (stable setup-proposed skills, enabled per owning layer) |
| Multi-harness installer | Working (Claude Code / VS Code / OpenCode / Gemini / Kiro / Codex skill path) |
| CI | Markdown lint, dead-link check, consistency, plugin structure, generator drift, HTML validation |



## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Every doc change updates the per-file changelog, the root [`CHANGELOG.md`](CHANGELOG.md), and CI must stay green. Rules for both humans and agents: [`AGENTS.md`](AGENTS.md).

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Changelog

Release history lives in [`CHANGELOG.md`](CHANGELOG.md). Pre-v5.0 history is archived in [`CHANGELOG.archive.md`](CHANGELOG.archive.md).
