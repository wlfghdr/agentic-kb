# Reference

> **Version:** 4.1.0

Implementation-critical details for building agentic-kb compatible tools. For the user guide, see [README.md](../README.md). For the human collaboration contract in shared workspaces, see [docs/collaboration.md](./collaboration.md). For behavioral specs, read the skill and agent files directly: [`plugins/kb/skills/kb-management/SKILL.md`](../plugins/kb/skills/kb-management/SKILL.md), [`plugins/kb/skills/kb-setup/SKILL.md`](../plugins/kb/skills/kb-setup/SKILL.md), [`plugins/kb/agents/kb-operator.md`](../plugins/kb/agents/kb-operator.md).

---

## 1. Architecture — Five Layers

```
┌──────────────┐   ┌──────────────┐   ┌───────────────┐   ┌──────────────┐   ┌─────────────┐
│  L1 Personal │──►│   L2 Team    │──►│  L3 Org-Unit  │──►│L4 Marketplace│◄──│ L5 Company  │
│  (required)  │   │  (optional)  │   │   (optional)  │   │  (optional)  │   │ (top-down)  │
│              │   │  (multiple)  │   │               │   │              │   │             │
│ _kb-inputs/  │   │<you>/_kb-inp │   │<team>/_kb-inp │   │ plugins/<nm> │   │ OKRs, MCG   │
│ _kb-referenc/│   │<you>/_kb-ref │   │<team>/_kb-ref │   │              │   │ strategy    │
│ _kb-ideas/   │   │ _kb-decision/│   │ _kb-decision/ │   │ plugins/<nm> │   │ directives  │
│ _kb-decision/│   │ _kb-tasks/   │   │ _kb-workstrm/ │   │              │   │             │
│ _kb-tasks/   │   │ .kb-log/     │   │ _kb-tasks/    │   │              │   │             │
│ _kb-workstrm/│   │              │   │ .kb-log/      │   │              │   │             │
│ .kb-log/     │   │              │   │               │   │              │   │             │
└──────────────┘   └──────────────┘   └───────────────┘   └──────────────┘   └─────────────┘
```

- Only **L1** is required. Higher layers are optional, declared in `.kb-config/layers.yaml`.
- Content flows **up** via `promote` / `publish`; **down** via `digest`.
- VMG (vision/mission/goals) bleeds **top-down** during digest: L3 org VMG → L2 team VMG → L1 personal VMG. Each layer's `_kb-references/foundation/vmg.md` is optional; the personal KB's is the merged view.
- L5 is top-down only — no promotions accepted.
- Every upward flow passes the evaluation gate.
- Optional draft primitives extend L1 with `_kb-roadmaps/` and `_kb-journeys/` when adopters opt in. They remain outside the default scaffold until configured.

---

## 2. The Evaluation Gate

Before persisting anything, the agent scores against five questions:

1. Does this strengthen a position?
2. Does this inform a decision?
3. Would you reference this again?
4. Is this actionable?
5. Is this materially new compared to existing topics?

The gate score is the count of "yes" answers across those five questions. VMG alignment is a separate prioritization signal, not a numeric bonus.

| Score | Outcome |
|-------|---------|
| 0/5 | Discard — log as `skipped` with reason |
| 1–2/5 | Finding only. Offer idea creation if novelty detected |
| 3+/5 | Finding + topic update + possibly decision or idea |

---

## 3. Workspace Layout

### Workspace root

```
my-workspace/
├── AGENTS.md                       # master index (all repos, keyword lookup)
├── CLAUDE.md → AGENTS.md           # symlink
├── .github/                        # VS Code Copilot workspace hooks (optional)
│   ├── prompts/kb.prompt.md
│   └── instructions/kb.instructions.md
├── .claude/                        # Claude Code harness (if installed)
├── .opencode/                      # OpenCode harness (if installed)
├── my-kb/                          # L1 Personal KB
├── team-kb/                        # L2 Team KB (optional)
├── org-unit-kb/                    # L3 Org-Unit KB (optional)
└── marketplace/                    # L4 Marketplace (optional)
```

Note: all configuration YAMLs live inside the personal KB under `.kb-config/` — not at workspace root.

### Personal KB (L1)

```
my-kb/
├── AGENTS.md
├── README.md
├── .kb-config/
│   ├── layers.yaml                 # layer index, workspace aliases, VMG
│   ├── automation.yaml             # automation level + schedules
│   └── artifacts.yaml              # HTML artifact styling
├── _kb-inputs/                        # THE INBOX — drop anything here
│   └── digested/YYYY-MM/
├── _kb-references/
│   ├── topics/                     # living positions (updated in place)
│   ├── findings/                   # dated snapshots (immutable)
│   ├── foundation/
│   │   ├── me.md
│   │   ├── context.md
│   │   ├── vmg.md                  # vision, mission & goals
│   │   ├── sources.md
│   │   ├── stakeholders.md
│   │   └── naming.md
│   ├── strategy-digests/           # per-layer digest findings + `.last-digest` watermark
│   ├── legacy/                     # archived material
│   └── reports/                    # generated HTML artifacts
├── _kb-ideas/
│   ├── I-YYYY-MM-DD-slug.md
│   └── archive/
├── _kb-decisions/
│   ├── D-YYYY-MM-DD-slug.md       # active decisions live at root
│   └── archive/
├── _kb-tasks/
│   ├── focus.md                    # max 6 items
│   ├── backlog.md
│   └── archive/YYYY-MM.md
├── .kb-log/YYYY-MM-DD.log
├── .kb-scripts/                    # optional utility scripts
├── _kb-workstreams/<name>.md
├── _kb-roadmaps/                   # optional; `kb-roadmap` output root
└── _kb-journeys/                   # optional; `kb-journeys` source + HTML root
```

### Team KB (L2)

```
team-kb/
├── AGENTS.md, README.md
├── _kb-references/foundation/vmg.md   # team-level vision/mission/goals
├── _kb-decisions/{archive}/
├── _kb-tasks/{focus.md,backlog.md}
├── .kb-log/
├── alice/
│   ├── _kb-inputs/ (+ digested/)
│   └── _kb-references/{topics/,findings/}
└── bob/ ...
```

### Org-Unit KB (L3)

Same as L2 but contributor units are teams, not people:

```
org-unit-kb/
├── _kb-references/foundation/vmg.md   # org-level vision/mission/goals
├── _kb-decisions/, _kb-tasks/, _kb-workstreams/, .kb-log/
├── team-alpha/{_kb-inputs/,_kb-references/}
└── team-beta/{_kb-inputs/,_kb-references/}
```

### Required files per layer

| Layer | Must exist |
|-------|-----------|
| L1 | `AGENTS.md`, `.kb-config/layers.yaml`, `_kb-inputs/`, `_kb-references/{topics,findings,foundation}/`, `_kb-ideas/`, `_kb-decisions/`, `_kb-tasks/focus.md`, `.kb-log/` |
| L2 | `AGENTS.md`, `_kb-decisions/`, `_kb-tasks/focus.md`, `.kb-log/`, per-contributor dirs |
| L3 | `AGENTS.md`, `_kb-decisions/`, `_kb-tasks/focus.md`, `_kb-workstreams/`, `.kb-log/`, per-team dirs |
| Root | `AGENTS.md`, `CLAUDE.md → AGENTS.md`; add harness-specific prompt/instruction files only when that harness uses them |

Note: `.kb-config/automation.yaml` and `.kb-config/artifacts.yaml` are optional — defaults apply when absent.

Harness-specific `/kb` command or skill contract (written by `/plugin install` or `scripts/install --target <harness>`):

- Claude Code: `plugins/kb/commands/kb.md` (from marketplace) or `.claude/commands/kb.md` (from `scripts/install`)
- VS Code Copilot: `.github/prompts/kb.prompt.md` + `.github/instructions/kb.instructions.md`
- OpenCode: `.opencode/commands/kb.md` (installer) or picked up via `.claude/commands/` if Claude Code is co-installed
- Codex CLI: `.agents/skills/kb/SKILL.md` (workspace) or `~/.agents/skills/kb/SKILL.md` (global). Codex reads `AGENTS.md` plus installed skills; invoke `kb` through the skill picker or `$kb`, not a custom `/kb` slash command.
- Gemini CLI: `.gemini/commands/kb.toml` (workspace) or `~/.gemini/commands/kb.toml` (global). Generated by the installer from `plugins/kb/commands/kb.md`; Gemini's custom-command format requires TOML
- Kiro IDE: `.kiro/skills/kb/SKILL.md` (workspace) or `~/.kiro/skills/kb/SKILL.md` (global). Kiro exposes skills in the slash menu, so `kb` remains a native entrypoint there.
- Rules-only harnesses (Cursor, Windsurf): no direct slash-command slot; adopters reference the scaffolded KB files via rules/rulebooks and invoke manually

Optional draft directories: `_kb-roadmaps/` is created only when `kb-roadmap` is configured; `_kb-journeys/` is created only when `kb-journeys` is configured.

---

## 4. File Formats

### Finding (`_kb-references/findings/YYYY-MM-DD-slug.md`)

```markdown
# Finding: <title>

**Date**: YYYY-MM-DD
**Workstream**: <name>
**Source**: <URL or meeting reference>
**Gate**: X/5 (reasons)

## TL;DR
## Details
## Implications
## Stakeholders
```

Immutable after creation. Corrections create a new finding.

### Topic (`_kb-references/topics/<slug>.md`)

```markdown
# Topic: <name>

**External anchors**: [links]

[... living prose, updated in place ...]

---
## Changelog
| Date | What changed | Source |
```

One file per topic. Inline changelog required.

### Decision (`_kb-decisions/D-YYYY-MM-DD-slug.md`)

```markdown
# D-YYYY-MM-DD: <title>

- **Context**: why this choice is open
- **Options**: (a) …, (b) …
- **Stakeholders**: @names
- **RACI** (team/org only): R/A/C/I assignments
- **Blocking**: what this blocks
- **Due**: YYYY-MM-DD
- **Status**: gathering-evidence | under-discussion | proposed | decided

## Evidence Trail
- date: event — link to finding

## Resolution (on archive only)
- **Outcome**: selected option
- **Rationale**: why
- **Date**: resolved date
```

### Idea (`_kb-ideas/I-YYYY-MM-DD-slug.md`)

```markdown
# Idea: <title>

**Stage**: seed | growing | ready | shipped | archived
**Created**: YYYY-MM-DD
**Workstream**: <name>
**Sparring rounds**: N

## Seed
[initial thought]

## Development Log
| Date | What | Trigger |

## Connections
- Relates to: topics, decisions, findings
```

### Workstream (`_kb-workstreams/<name>.md`)

```markdown
# Workstream: <name>

**Themes**: keyword list
**Active decisions**: D-id list
**Key topics**: file list

## Current State
## Active Threads
## Cross-Workstream Dependencies
```

### Focus / Backlog (`_kb-tasks/focus.md`, `_kb-tasks/backlog.md`)

```markdown
# Focus
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Waiting
- [ ] @person: what they owe you
```

### Log (`.kb-log/YYYY-MM-DD.log`)

```
HH:MM:SSZ | operation | scope | target | details
```

Operations: `capture`, `digest`, `publish`, `promote`, `update-topic`, `task-add`, `task-done`, `decide`, `decide-resolve`, `idea-create`, `idea-develop`, `idea-ship`, `stakeholder-update`, `audit`, `report`, `presentation`, `skipped`, `install`, `ritual-start-day`, `ritual-end-day`, `ritual-start-week`, `ritual-end-week`, `automation-failure`.

Scopes: `personal`, `team-kb`, `org-unit`, `marketplace`, `personal→team`, `team→personal`, `personal→marketplace`, `team-kb/<contributor>`, `workspace`.

---

## 5. Configuration Files

All configuration lives in a `.kb-config/` directory inside the personal KB (L1). Higher-layer KBs (L2/L3) do **not** need configuration — they are plain repos with the required directory structure. The personal KB's `layers.yaml` is the single source of truth for layer topology; all commands (`/kb promote`, `/kb digest`, `/kb sync`) originate from L1.

```
.kb-config/
├── layers.yaml        # layer index, workspace aliases, VMG  (required)
├── automation.yaml    # automation level + schedules          (optional)
└── artifacts.yaml     # HTML artifact styling                 (optional)
```

### `.kb-config/layers.yaml`

```yaml
workspace:
  root: /path/to/workspace
  user: alice
  aliases:
    kb: my-kb
    tk: team-kb

layers:
  personal:
    path: .
    workstreams:
      - name: reliability
        themes: [slo, incident, postmortem]
  team:
    - name: my-team
      path: ../team-kb
      contributor: alice
  org-unit:
    name: platform
    path: ../org-kb
    team: team-alpha
  marketplace:
    source: https://github.com/org/marketplace
    install-mode: marketplace   # marketplace | clone
```

### `.kb-config/automation.yaml`

```yaml
level: 2                            # 1=manual, 2=semi-auto, 3=full-auto

schedules:
  start-day: daily 08:00
  team-digest: daily 08:00
  task-review: daily 08:30
  end-week: friday 15:00

auto-promote:
  enabled: false                    # level 3 only
  confidence-threshold: 4           # gate score ≥ 4 for auto-promote
  excluded-workstreams: []
```

### `.kb-config/artifacts.yaml`

```yaml
styling:
  source: website                   # builtin | website | template
  reference-url: https://example.org/brand
  reference-file: null              # path if source=template
  themes: [light, dark]
  default-theme: auto               # auto | light | dark
  watermark:
    enabled: true
    position: intro-slide
    format: "v{version} · {date}"
```

### Optional draft-skill config blocks

The same config files also host optional draft primitives:

- `.kb-config/layers.yaml` may add top-level `roadmap:` and `journeys:` blocks.
- `.kb-config/artifacts.yaml` may add `html-template:` and `journeys-template:` blocks for roadmap and journey rendering.

These blocks are ignored unless the corresponding skills are installed and configured.

Recommended lean roadmap baseline: start with exported tracker markdown bound through `ticket-export-markdown` for GitHub- and Jira-originated work, prove the artifact flow locally, then opt into live tracker adapters and write-back later.

---

## 6. HTML Artifacts

Two families:

| Family | Lifecycle | Filename |
|--------|-----------|----------|
| **Live overviews** (`dashboard.html`, root `index.html`) | Overwritten on every mutation | Stable names |
| **Historical** (presentations, reports, pitches, daily/weekly) | Immutable, versioned | Include version or date |

### Dashboard (command center)

`dashboard.html` is the owner-facing counterpart to `index.html`. Where
the index lists generated artifacts, the dashboard surfaces **live KB
state**: focus tasks, backlog, pending inputs, active ideas, open
decisions, topics, recent findings / digests / reports, workstream
freshness, and — opt-in — external work-items from GitHub (`gh` CLI) and Jira
(jira-sync-style markdown export).

- Script: `scripts/generate-dashboard.py` (copy into `.kb-scripts/` like `generate-index.py`).
- Config: `.kb-config/artifacts.yaml` → `dashboard:` section. Panels list is ordered; unknown or empty panels are skipped.
- External panels are OFF by default. Adopters opt in per tool and configure the data source. No vendor lock-in: Jira is read from a configurable directory of frontmatter-bearing markdown files, not a vendor API.
- Regenerated as part of the same mutation flow as overviews and `index.html` (see `kb-management` rule 9–10).

### Shared contract

1. Subtle watermark: `v{version} · {date}` or `latest · {timestamp}`
2. Changelog appendix (final slide/section)
3. Light + dark theme with in-page toggle
4. Self-contained (all CSS/JS/images inline)
5. Accessible (semantic HTML, WCAG AA, keyboard nav)
6. If generation needs external reads, show a preflight summary first: declared sources, scope/time window or filters, read-only vs apply intent, and output paths; do not fetch until confirmed unless the command was explicitly invoked to execute or automation already authorizes it.
7. Do not declare the artifact done until a QA sweep passes in the generated output: theme toggle works, no unresolved placeholders remain, embedded assets resolve without network fetches, readability/contrast is acceptable in both themes, and keyboard affordances still work.

### Report slide composition

The `report.html` template has 12 slide types. Agents pick per purpose:

| Report | Slides |
|--------|--------|
| Weekly Status (boss) | Cover → Metrics → Progress → Decisions → Blocked → Ideas → Roadmap → Stakeholder Map → Closing |
| Daily Digest (standup) | Cover → Daily Digest |
| Pitch | Cover → Pitch → Comparison → Closing |
| Roadmap Status | Cover → Metrics → Kanban → Stakeholder Map → Closing |
| Topic Presentation | Cover → Content slides → Comparison → Closing |

### Ritual triggers

| Ritual | Artifact |
|--------|----------|
| `/kb end-day` | Daily Digest HTML |
| `/kb end-week` | Weekly Status HTML |

---

## 7. Security & Privacy

| Layer | Default | Rule |
|-------|---------|------|
| L1 Personal | Private | Never reference in public repos/artifacts |
| L2 Team | Team-private | Visible within team only |
| L3 Org-Unit | Org-private | Visible within org unit |
| L4 Marketplace | Shared | No PII, no credentials, no hidden URLs, only marketplace-available tools |
| L5 Company | Top-down | Consumed into L1 |

### Promotion safety checks

- **L1 → L2**: warn on secrets, tokens, private URLs.
- **→ L4 (publish)**: hard block on PII, credentials, hardcoded external URLs, non-marketplace tools.

### Never capture

- Secrets (API keys, passwords, tokens, private keys)
- Raw PII (use aliases/opaque identifiers)
- Legal material without review

### Data residency

Everything is Git + Markdown + local agent. No external service required. Offline mode: local git remote, disable marketplace auto-install, disable L5 propagation.

---

## 8. Automation Levels

| Level | Behavior |
|-------|----------|
| **1 — Assisted** (default) | User triggers, agent processes, user confirms and commits |
| **2 — Semi-auto** | Events trigger processing; human approves promotions/publishes |
| **3 — Full-auto** | Autonomous loop: pull → detect → process → promote (if confidence threshold met) → commit → push → notify |

---

## 9. Marketplace Package Layout

```
marketplace-repo/
├── plugin.json               # root marketplace manifest
├── .claude-plugin/
│   └── marketplace.json      # Claude Code marketplace manifest
├── plugins/
│   └── <plugin>/
│       ├── plugin.json       # per-plugin manifest
│       ├── skills/<name>/
│       │   ├── SKILL.md      # frontmatter + instructions
│       │   ├── templates/    # optional
│       │   └── references/   # optional
│       ├── utils/            # optional reusable helpers for skills in this plugin
│       └── agents/<name>.md
├── tests/
│   └── fixtures/             # optional regression fixtures for safety/routing checks
├── scripts/
│   ├── install.py
│   ├── check_consistency.py
│   └── generate_plugins.py
```

Skills require: `name`, `description`, `version`, `triggers`, `tools`, `author`, `license` in YAML frontmatter.

Optional frontmatter fields with generic cross-harness value:

- `utils` — plugin-local reusable helpers the skill depends on (wrapper scripts, validators, exporters, sanitizers).
- `incompatible_with` — other skills or plugins that must not be installed together because their trigger phrases or command surfaces overlap.

For skills that encode safety rules, policy checks, scoring, or routing logic, the marketplace repo should also ship deterministic regression fixtures under `tests/fixtures/` so prompt or model changes can be checked against known clean, violating, and ambiguous cases.

---

## 10. Harness Support

| Harness tier | Harness | Skill location | Agent location | Config / notes |
|--------------|---------|----------------|----------------|----------------|
| Marketplace/native plugin path | VS Code Copilot | `.github/skills/<name>/SKILL.md` | `.github/agents/<name>.agent.md` | `.github/prompts/`, `.github/instructions/` |
| Marketplace/native plugin path | Claude Code | `.claude/skills/<name>/SKILL.md` | `.claude/agents/<name>.md` | `.claude/settings.json` |
| Installer-supported native command path | OpenCode | `.opencode/skills/<name>/SKILL.md` | `.opencode/agents/<name>.md` | `.opencode/commands/<name>.md` for `/kb` |
| Installer-supported native command path | Gemini CLI | n/a | n/a | `.gemini/commands/<name>.toml` for `/kb` |
| Installer-supported native skill path | Kiro IDE | `.kiro/skills/<name>/SKILL.md` | n/a | skills appear in the slash menu |
| Compatible skill workflow | Codex CLI | `.agents/skills/<name>/SKILL.md` | n/a | `AGENTS.md` + skill picker / `$kb`; no custom `/kb` slash command |
| Partial/manual path | Other CLIs / IDEs | adopter-defined | adopter-defined | Can use the KB file model, but command wiring and automation may need manual setup. |

`scripts/install.py` and `scripts/generate_plugins.py` handle cross-harness distribution from one source tree for marketplace-backed and installer-supported harnesses. Compatible Codex workflows reuse the same workspace contract through `AGENTS.md` plus repo/user skill directories.

---

## Changelog

| Date | What changed |
|------|-------------|
| 2026-04-25 | Added generic marketplace guidance for plugin-local utilities, explicit incompatibility metadata, and fixture-backed regression checks for policy/routing-heavy skills; version bumped to 4.1.0 |
| 2026-04-25 | Version aligned to 4.0.0 for the v4.0.0 framework release |
| 2026-04-25 | Added explicit preflight-fetch and post-generation QA rules to the HTML artifact contract so external-source reads and artifact completion gates are part of the normative spec |
| 2026-04-24 | Corrected Codex and Kiro support details to the documented skill-based locations (`.agents/skills/`, `.kiro/skills/`), expanded the harness matrix to include Gemini/Kiro installer-backed paths, and added the export-backed roadmap proof recommendation |
| 2026-04-22 | Dashboard command-center contract now explicitly includes topics as a first-class live panel so accreting knowledge is visible alongside decisions, ideas, and findings |
| 2026-04-22 | Added `_kb-references/strategy-digests/` to the §3 workspace layout so the digest watermark and per-layer digest findings have a declared home |
| 2026-04-22 | Collapsed the HTML-artifact families table to the two that actually ship — `dashboard.html` + root `index.html` — after dropping the phantom `inventory.html` / `open-decisions.html` / `open-tasks.html` overviews whose signals already live in `dashboard.html` panels |
| 2026-04-22 | Corrected the workspace-root required-files row so `.github/prompts/kb.prompt.md` is no longer universal, and added the harness-specific workspace prompt/instruction note for VS Code, Claude Code, OpenCode, and compatible CLI workflows |
| 2026-04-22 | Reframed evaluation-gate Q5 as positive novelty and removed the obsolete VMG score bonus so the rubric matches the detailed gate reference and skill behavior |
| 2026-04-22 | Added Codex CLI to the harness support model as a compatible CLI workflow, clarified first-class vs partial/manual support tiers |
| 2026-04-22 | Fixed markdown-lint violations (indented heading/list, extra table column), removed stale doc-drift source column |
| 2026-04-22 | Added optional roadmap/journey layout coverage and updated the marketplace layout to the `plugins/<plugin>/` source tree |
| 2026-04-20 | Linked the dedicated collaboration guide for shared-workspace human operating norms |
| 2026-04-19 | Initial — consolidated from 23 concept/spec docs |
