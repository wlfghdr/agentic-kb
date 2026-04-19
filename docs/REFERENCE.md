# Reference

> **Version:** 3.0

Implementation-critical details for building agentic-kb compatible tools. For the user guide, see [README.md](../README.md). For behavioral specs, read the skill and agent files directly: [`skills/kb-management/SKILL.md`](../skills/kb-management/SKILL.md), [`skills/kb-setup/SKILL.md`](../skills/kb-setup/SKILL.md), [`agents/kb-operator.md`](../agents/kb-operator.md).

---

## 1. Architecture — Five Layers

```
┌──────────────┐   ┌──────────────┐   ┌───────────────┐   ┌──────────────┐   ┌─────────────┐
│  L1 Personal │──►│   L2 Team    │──►│  L3 Org-Unit  │──►│L4 Marketplace│◄──│ L5 Company  │
│  (required)  │   │  (optional)  │   │   (optional)  │   │  (optional)  │   │ (top-down)  │
│              │   │  (multiple)  │   │               │   │              │   │             │
│ _inputs/     │   │ <you>/_inputs│   │ <team>/_inputs│   │ skills/<name>│   │ OKRs, MCG   │
│ _references/ │   │ <you>/output │   │ <team>/output │   │ agents/<name>│   │ strategy    │
│ _ideas/      │   │ _decisions/  │   │ _decisions/   │   │ plugins/<nm> │   │ directives  │
│ _decisions/  │   │ _tasks/      │   │ _workstreams/ │   │              │   │             │
│ _tasks/      │   │ .kb-log/     │   │ _tasks/       │   │              │   │             │
│ _workstreams/│   │              │   │ .kb-log/      │   │              │   │             │
│ .kb-log/     │   │              │   │               │   │              │   │             │
└──────────────┘   └──────────────┘   └───────────────┘   └──────────────┘   └─────────────┘
```

- Only **L1** is required. Higher layers are optional, declared in `.kb-config.yaml`.
- Content flows **up** via `promote` / `publish`; **down** via `digest`.
- L5 is top-down only — no promotions accepted.
- Every upward flow passes the evaluation gate.

---

## 2. The Evaluation Gate

Before persisting anything, the agent scores against five questions:

1. Does this strengthen a position?
2. Does this inform a decision?
3. Would you reference this again?
4. Is this actionable?
5. Does this already exist?

**+1 bonus** if it aligns with declared VMG goals.

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
├── .kb-config.yaml                 # layer config
├── .kb-automation.yaml             # automation level + schedules
├── .kb-artifacts.yaml              # HTML styling config
├── .github/prompts/kb.prompt.md
├── .github/instructions/kb.instructions.md
├── .claude/                        # Claude Code harness
├── .opencode/                      # OpenCode harness
├── my-kb/                          # L1 Personal KB
├── team-kb/                        # L2 Team KB (optional)
├── org-unit-kb/                    # L3 Org-Unit KB (optional)
└── marketplace/                    # L4 Marketplace (optional)
```

### Personal KB (L1)

```
my-kb/
├── AGENTS.md
├── README.md
├── .kb-config.yaml
├── .kb-automation.yaml
├── _inputs/                        # THE INBOX — drop anything here
│   └── digested/YYYY-MM/
├── _references/
│   ├── topics/                     # living positions (updated in place)
│   ├── findings/                   # dated snapshots (immutable)
│   ├── foundation/
│   │   ├── me.md
│   │   ├── context.md
│   │   ├── sources.md
│   │   ├── stakeholders.md
│   │   └── naming.md
│   ├── legacy/                     # archived material
│   └── reports/                    # generated HTML artifacts
├── _ideas/
│   ├── I-YYYY-MM-DD-slug.md
│   └── archive/
├── _decisions/
│   ├── active/D-YYYY-MM-DD-slug.md
│   └── archive/
├── _tasks/
│   ├── focus.md                    # max 3 items
│   ├── backlog.md
│   └── archive/YYYY-MM.md
├── .kb-log/YYYY-MM-DD.log
├── .kb-scripts/                    # optional utility scripts
└── _workstreams/<name>.md
```

### Team KB (L2)

```
team-kb/
├── AGENTS.md, README.md
├── _decisions/{active,archive}/
├── _tasks/{focus.md,backlog.md}
├── .kb-log/
├── alice/
│   ├── _inputs/ (+ digested/)
│   └── outputs/{topics/,findings/}
└── bob/ ...
```

### Org-Unit KB (L3)

Same as L2 but contributor units are teams, not people:

```
org-unit-kb/
├── _decisions/, _tasks/, _workstreams/, .kb-log/
├── team-alpha/{_inputs/,outputs/}
└── team-beta/{_inputs/,outputs/}
```

### Required files per layer

| Layer | Must exist |
|-------|-----------|
| L1 | `AGENTS.md`, `.kb-config.yaml`, `_inputs/`, `_references/{topics,findings,foundation}/`, `_ideas/`, `_decisions/active/`, `_tasks/focus.md`, `.kb-log/` |
| L2 | `AGENTS.md`, `_decisions/active/`, `_tasks/focus.md`, `.kb-log/`, per-contributor dirs |
| L3 | `AGENTS.md`, `_decisions/active/`, `_tasks/focus.md`, `_workstreams/`, `.kb-log/`, per-team dirs |
| Root | `AGENTS.md`, `CLAUDE.md → AGENTS.md`, `.github/prompts/kb.prompt.md` |

---

## 4. File Formats

### Finding (`_references/findings/YYYY-MM-DD-slug.md`)

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

### Topic (`_references/topics/<slug>.md`)

```markdown
# Topic: <name>

**External anchors**: [links]

[... living prose, updated in place ...]

---
## Changelog
| Date | What changed | Source |
```

One file per topic. Inline changelog required.

### Decision (`_decisions/active/D-YYYY-MM-DD-slug.md`)

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

### Idea (`_ideas/I-YYYY-MM-DD-slug.md`)

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

### Workstream (`_workstreams/<name>.md`)

```markdown
# Workstream: <name>

**Themes**: keyword list
**Active decisions**: D-id list
**Key topics**: file list

## Current State
## Active Threads
## Cross-Workstream Dependencies
```

### Focus / Backlog (`_tasks/focus.md`, `_tasks/backlog.md`)

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

### `.kb-config.yaml`

```yaml
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

workspace:
  aliases:
    kb: my-kb
    tk: team-kb

vmg:
  vision: "..."
  mission: "..."
  goals:
    - id: G-2026-Q2-1
      description: "..."
      horizon: quarter
      status: active
```

### `.kb-automation.yaml`

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

### `.kb-artifacts.yaml`

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

---

## 6. HTML Artifacts

Two families:

| Family | Lifecycle | Filename |
|--------|-----------|----------|
| **Overviews** (inventory, open-decisions, open-tasks, index) | Overwritten on every mutation | Stable names |
| **Historical** (presentations, reports, pitches, daily/weekly) | Immutable, versioned | Include version or date |

### Shared contract

1. Subtle watermark: `v{version} · {date}` or `latest · {timestamp}`
2. Changelog appendix (final slide/section)
3. Light + dark theme with in-page toggle
4. Self-contained (all CSS/JS/images inline)
5. Accessible (semantic HTML, WCAG AA, keyboard nav)

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
├── skills/<name>/
│   ├── SKILL.md              # frontmatter + instructions
│   ├── templates/            # optional
│   └── _references/           # optional
├── agents/<name>.md
├── plugins/<harness>/        # generated per-harness mirrors
├── scripts/
│   ├── install.py
│   ├── check_consistency.py
│   └── generate_plugins.py
└── plugin.json               # marketplace metadata
```

Skills require: `name`, `description`, `version`, `triggers`, `tools`, `author`, `license` in YAML frontmatter.

---

## 10. Harness Support

| Harness | Skill location | Agent location | Config |
|---------|---------------|----------------|--------|
| VS Code Copilot | `.github/skills/<name>/SKILL.md` | `.github/agents/<name>.agent.md` | `.github/prompts/`, `.github/instructions/` |
| Claude Code | `.claude/skills/<name>/SKILL.md` | `.claude/agents/<name>.md` | `.claude/settings.json` |
| OpenCode | `.opencode/skills/<name>/SKILL.md` | `.opencode/agents/<name>.md` | `.opencode/config.yaml` |

`scripts/install.py` and `scripts/generate_plugins.py` handle cross-harness distribution from one source tree.

---

## Changelog

| Date | What changed |
|------|-------------|
| 2026-04-19 | Initial — consolidated from 23 concept/spec docs |
