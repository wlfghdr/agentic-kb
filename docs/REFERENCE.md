# Reference

> **Version:** 5.1.0

Implementation-critical details for building agentic-kb compatible tools. For the user guide, see [README.md](../README.md). For the human collaboration contract in shared workspaces, see [docs/collaboration.md](./collaboration.md). For behavioral specs, read the skill and agent files directly: [`plugins/kb/skills/kb-management/SKILL.md`](../plugins/kb/skills/kb-management/SKILL.md), [`plugins/kb/skills/kb-setup/SKILL.md`](../plugins/kb/skills/kb-setup/SKILL.md), [`plugins/kb/agents/kb-operator.md`](../plugins/kb/agents/kb-operator.md).

---

## 1. Architecture — Flexible Layer Graph

`agentic-kb` no longer assumes a fixed L1→L5 ladder. A workspace declares a **layer graph** in `.kb-config/layers.yaml`: each layer has a name, scope, role, parent edge, enabled features, and optional marketplace or external connections.

```text
┌────────────────────┐      promote / digest       ┌────────────────────┐
│ alice-personal     │ ─────────────────────────▶  │ team-observability │
│ scope: personal    │                            │ scope: team        │
│ role: contributor  │ ◀───────────────────────── │ role: contributor  │
└────────────────────┘                             └────────────────────┘
          │                                                   │
          │ promote / digest                                  │ promote / digest
          ▼                                                   ▼
┌────────────────────┐                             ┌────────────────────┐
│ engineering-org    │ ─────────────────────────▶  │ company-guidance   │
│ scope: org-unit    │                            │ scope: company     │
│ role: contributor  │ ◀───────────────────────── │ role: consumer     │
└────────────────────┘                             └────────────────────┘

Each layer may also attach its own marketplace and external connections.
```

Core rules:

- A workspace must declare **at least one contributor-capable layer**. A personal layer is recommended, but not required.
- One layer is designated the **anchor layer**. Its `.kb-config/` directory is the source of truth for the user's layer graph, automation, and artifact settings.
- `parent` defines the upward routing edge. `promote` walks up the parent chain; `digest` walks down it.
- `role: contributor | consumer` governs mutation rights. Promotion or publish to a consumer-only layer must refuse with a clear message.
- `features:` opt a layer into primitives: `inputs`, `findings`, `topics`, `ideas`, `decisions`, `tasks`, `notes`, `workstreams`, `foundation`, `reports`, `marketplace`, `roadmaps`, `journeys`.
- `marketplace` is **cross-cutting**, not a numbered layer. Any layer may publish to or consume from its own marketplace repo.
- Draft features (`roadmaps`, `journeys`) are enabled per layer, not globally.

### Contributor-scoped vs shared primitives

At multi-user layers, the primitive decides whether content stays contributor-scoped or becomes shared state.

| Primitive | Default mode at multi-user layers | Why |
|-----------|-----------------------------------|-----|
| `inputs` | contributor-scoped | Pre-gate raw material is not shared truth |
| `findings` | contributor-scoped | Immutable evidence keeps provenance |
| `ideas` | contributor-scoped | Ownership-bearing incubation object |
| `strategy-digests` | contributor-scoped | Each contributor tracks their own watermark |
| `topics` | configurable; default contributor-scoped | A living position may be personal or shared |
| `notes` | shared for meetings; configurable for general notes | Shared meetings need one canonical record |
| `decisions` | shared | A layer should have one decision artifact |
| `tasks` | shared | The backlog belongs to the layer |
| `workstreams` | shared | Workstream state is layer-level |
| `foundation` | shared | Naming, sources, stakeholders, VMG are canonical |
| `reports` | shared | Reports describe the layer, not one contributor |

Single-user layers flatten contributor-scoped primitives to the layer root.

---

## 2. The Evaluation Gate

Before persisting anything, the agent scores against five questions:

1. Does this strengthen a position?
2. Does this inform a decision?
3. Would you reference this again?
4. Is this actionable?
5. Is this materially new compared to existing topics?

The gate score is the count of `yes` answers across those five questions. VMG alignment is a separate prioritization signal, not a numeric bonus.

| Score | Outcome |
|-------|---------|
| 0/5 | Discard — log as `skipped` with reason |
| 1–2/5 | Finding only. Offer idea creation if novelty detected |
| 3+/5 | Finding + topic update + possibly decision or idea |

---

## 3. Workspace Layout

### Workspace root

```text
my-workspace/
├── AGENTS.md
├── CLAUDE.md → AGENTS.md
├── .github/                        # VS Code Copilot hooks, if installed
├── .claude/                        # Claude Code hooks, if installed
├── .opencode/                      # OpenCode hooks, if installed
├── anchor-kb/                      # the configured anchor layer
├── team-kb/                        # optional additional layer repos
├── org-kb/
└── company-kb/
```

The workspace root never implies a fixed layer count. It is just the container for one or more KB repos plus harness hooks.

### Layer repo layout

Every layer repo uses the same feature-oriented directory contract. Directories exist only when that feature is enabled for the layer.

```text
layer-kb/
├── AGENTS.md
├── README.md
├── .kb-config/                     # anchor layer only
│   ├── layers.yaml
│   ├── automation.yaml
│   └── artifacts.yaml
├── _kb-inputs/
│   └── digested/YYYY/MM/
├── _kb-references/
│   ├── topics/
│   ├── findings/YYYY/
│   ├── foundation/
│   ├── strategy-digests/YYYY/
│   ├── legacy/
│   └── reports/
├── _kb-notes/YYYY/
├── _kb-ideas/
│   ├── I-YYYY-MM-DD-slug.md
│   └── archive/YYYY/
├── _kb-decisions/
│   ├── D-YYYY-MM-DD-slug.md
│   └── archive/YYYY/
├── _kb-tasks/
│   ├── focus.md
│   ├── backlog.md
│   └── archive/YYYY/MM.md
├── .kb-log/YYYY-MM-DD.log          # MAY be nested as .kb-log/YYYY/YYYY-MM-DD.log
├── .kb-scripts/
├── _kb-workstreams/
├── _kb-roadmaps/
├── _kb-journeys/
├── index.html
├── dashboard.html
└── .nojekyll
```

### Multi-user layer pattern

Multi-user layers keep shared primitives at the repo root and contributor-scoped primitives under per-contributor or per-team directories.

```text
team-kb/
├── _kb-decisions/
├── _kb-tasks/
├── _kb-notes/                      # shared meeting notes by default
├── _kb-references/foundation/
├── alice/
│   ├── _kb-inputs/
│   ├── _kb-references/{findings/,topics/}
│   └── _kb-ideas/
└── bob/
```

### Required files by role

| Repo kind | Must exist |
|-----------|------------|
| Anchor layer | `AGENTS.md`, `.kb-config/layers.yaml`, one contributor-capable feature set, `.kb-log/`, `index.html` |
| Any shared layer | `AGENTS.md`, `README.md`, `.kb-log/`, all directories for its enabled shared features |
| Any multi-user layer with contributor-scoped features | per-contributor or per-team directories for those enabled features |
| Any layer publishing HTML | `.nojekyll`, `index.html`, `dashboard.html` |

Harness-specific `/kb` command or skill contract (written by `/plugin install` or `scripts/install --target <harness>`):

- Claude Code: `plugins/kb/commands/kb.md` (from marketplace) or `.claude/commands/kb.md` (from `scripts/install`)
- VS Code Copilot: `.github/prompts/kb.prompt.md` + `.github/instructions/kb.instructions.md`
- OpenCode: `.opencode/commands/kb.md` or shared `.claude/commands/` if Claude Code is co-installed
- Codex CLI: `.agents/skills/kb/SKILL.md` (workspace) or `~/.agents/skills/kb/SKILL.md` (global); invoke via the skill picker or `$kb`
- Gemini CLI: `.gemini/commands/kb.toml` (workspace) or `~/.gemini/commands/kb.toml` (global)
- Kiro IDE: `.kiro/skills/kb/SKILL.md` (workspace) or `~/.kiro/skills/kb/SKILL.md` (global)
- Rules-only harnesses: adopters reuse the repo contract but wire invocation manually

---

## 4. File Formats

### Finding (`_kb-references/findings/YYYY/YYYY-MM-DD-slug.md`)

```markdown
# Finding: <title>

**Date**: YYYY-MM-DD
**Workstream**: <name>
**Source**: <URL or note reference>
**Gate**: X/5 (reasons)
**Maturity**: raw | emerging | durable

## TL;DR
## Details
## Implications
## Stakeholders
```

Immutable after creation. Corrections create a new finding.

### Topic (`_kb-references/topics/<slug>.md`)

```markdown
# Topic: <name>

**Maturity**: raw | emerging | durable
**External anchors**: [links]

[... living prose, updated in place ...]

---
## Changelog
| Date | What changed | Source |
```

### Decision (`_kb-decisions/D-YYYY-MM-DD-slug.md`)

```markdown
# D-YYYY-MM-DD: <title>

- **Context**: why this choice is open
- **Options**: (a) …, (b) …
- **Stakeholders**: @names
- **RACI** (shared layers): R/A/C/I assignments
- **Blocking**: what this blocks
- **Due**: YYYY-MM-DD
- **Status**: gathering-evidence | under-discussion | proposed | decided | revisiting

## Evidence Trail
- date: event — link to finding or note

## Resolution (on archive only)
- **Outcome**: selected option
- **Rationale**: why
- **Date**: resolved date
```

Archived decisions live under `_kb-decisions/archive/YYYY/`.

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
- Relates to: topics, decisions, findings, notes
```

Archived ideas live under `_kb-ideas/archive/YYYY/`.

### Note (`_kb-notes/YYYY/MM-DD-slug.md`)

```markdown
---
type: meeting | note
date: YYYY-MM-DD
attendees: [@alice, @bob]
workstream: <name>
source: <optional link>
authors: [@alice]
---

# Note: <title>

## TL;DR
## Discussion / Notes
## Decisions made
## Action items
## Open questions
```

Meeting notes should be shared at multi-user layers unless the adopter intentionally configures otherwise.

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
- [ ] Task 1 <!-- source: finding-or-note · created: YYYY-MM-DD -->

## Waiting
- [ ] @person: what they owe you
```

Archived tasks live under `_kb-tasks/archive/YYYY/MM.md`.

### Log (`.kb-log/YYYY-MM-DD.log` or `.kb-log/YYYY/YYYY-MM-DD.log`)

```text
HH:MM:SSZ | operation | scope | target | details
```

Writers MAY keep flat daily logs or nest them by year. Readers must accept both.

Operations include: `capture`, `review`, `digest`, `digest-connections`, `promote`, `publish`, `note`, `note-end`, `update-topic`, `task-add`, `task-done`, `decide`, `decide-resolve`, `idea-create`, `idea-develop`, `idea-ship`, `audit`, `report`, `presentation`, `skipped`, `install`, `ritual-start-day`, `ritual-end-day`, `ritual-start-week`, `ritual-end-week`, `automation-failure`.

---

## 5. Configuration Files

All configuration lives in a `.kb-config/` directory inside the **anchor layer**. The anchor layer can be personal, team, org, or any other contributor-capable layer the user chooses as home base.

```text
.kb-config/
├── layers.yaml        # layer graph, roles, connections, marketplace refs  (required)
├── automation.yaml    # automation level + schedules                       (optional)
└── artifacts.yaml     # HTML artifact styling                              (optional)
```

### `.kb-config/layers.yaml`

```yaml
workspace:
  root: /path/to/workspace
  user: alice
  anchor-layer: alice-personal
  aliases:
    personal: alice-personal
    team: team-observability

layers:
  - name: alice-personal
    scope: personal
    role: contributor
    parent: team-observability
    path: .
    features: [inputs, findings, topics, ideas, decisions, tasks, notes, workstreams, foundation, reports]
    workstreams:
      - name: platform-signals
        themes: [observability, reliability]
    marketplace:
      repo: ../team-skills
      install-mode: marketplace
    connections:
      product-repos:
        - name: agentic-kb
          path: ../agentic-kb
          remote: wlfghdr/agentic-kb
          watch:
            - CHANGELOG.md
            - docs/REFERENCE.md
          ticket-pattern: '#\d+'
      trackers:
        - kind: github-issues
          repo: wlfghdr/agentic-kb
          scope: is:issue is:open
      reference-mode: link
      writeback:
        enabled: false
        capabilities: []

  - name: team-observability
    scope: team
    role: contributor
    parent: engineering-org
    path: ../team-observability-kb
    features: [findings, topics, ideas, decisions, tasks, notes, foundation, reports, marketplace]
    contributor-mode:
      findings: contributor-scoped
      topics: contributor-scoped
      notes: shared

  - name: engineering-org
    scope: org-unit
    role: contributor
    parent: company-guidance
    path: ../engineering-org-kb
    features: [decisions, tasks, foundation, reports, marketplace, roadmaps, journeys]
    roadmap:
      issue-trackers: []
    journeys:
      source-dir: _kb-journeys
      output-dir: _kb-journeys
      html-subdir: html

  - name: company-guidance
    scope: company
    role: consumer
    parent: null
    path: ../company-guidance-kb
    features: [foundation, decisions, reports]
```

Field contract:

- `name`: canonical layer identifier used in commands.
- `scope`: descriptive routing hint (`personal`, `team`, `org-unit`, `company`, or a custom scope).
- `role`: `contributor` or `consumer`.
- `parent`: the next upward layer in the graph, or `null`.
- `path`: repo-relative path to the layer repo.
- `features`: enabled primitives for that layer.
- `contributor-mode`: optional overrides for primitives that can be shared or contributor-scoped.
- `marketplace`: marketplace repo and install mode for that layer's published skills.
- `connections`: product repos, trackers, reference mode, and write-back policy for that layer.
- `roadmap` / `journeys`: draft-skill configuration blocks nested under the layer that enabled those features.

### `.kb-config/automation.yaml`

```yaml
level: 2

schedules:
  start-day: daily 08:00
  digest-parent: daily 08:00
  digest-connections: daily 08:15
  task-review: daily 08:30
  end-week: friday 15:00

auto-promote:
  enabled: false
  confidence-threshold: 4
  excluded-workstreams: []
```

### `.kb-config/artifacts.yaml`

```yaml
styling:
  source: template                   # builtin | website | template
  reference-url: https://example.org/brand
  reference-file: _kb-references/templates/presentation-template.html
  themes: [light, dark]
  default-theme: auto
  watermark:
    enabled: true
    position: intro-slide
    format: "v{version} · {date}"

dashboard:
  panels:
    - focus-tasks
    - pending-inputs
    - active-ideas
    - open-decisions
    - topics
    - recent-findings
    - recent-reports

html-template:
  base: kb-roadmap/templates/roadmap.html.hbs
  tokens: _kb-references/templates/brand/tokens.css

journeys-template:
  base: kb-journeys/templates/journey.html.hbs
  tokens: _kb-references/templates/brand/tokens.css
```

Recommended lean roadmap baseline: start with exported tracker markdown bound through `connections.trackers[]`, prove the artifact flow locally, then opt into live tracker adapters and write-back later.

### Migration helpers

Two explicit migration helpers close the remaining 5.0 follow-up path for older adopters:

- `/kb migrate layer-model` previews or applies the conversion from the retired fixed L1-L5 ladder to the list-based layer graph in `.kb-config/layers.yaml`.
- `/kb migrate archives` previews or applies the year-based archive moves for digests, tasks, decisions, ideas, findings, strategy digests, and optional daily logs.

Both helpers are dry-run first and only apply after confirmation.

---

## 6. HTML Artifacts

Two families:

| Family | Lifecycle | Filename |
|--------|-----------|----------|
| **Live overviews** (`dashboard.html`, root `index.html`) | Overwritten on every mutation | Stable names |
| **Historical** (presentations, reports, pitches, daily/weekly) | Immutable, versioned | Include version or date |

### Dashboard (command center)

`dashboard.html` is the owner-facing counterpart to `index.html`. Where the index lists generated artifacts, the dashboard surfaces **live KB state**: focus tasks, backlog, pending inputs, active ideas, open decisions, topics, recent findings / digests / reports, workstream freshness, and opt-in external work-items from declared `connections`.

- Script: `scripts/generate-dashboard.py`.
- Config: `.kb-config/artifacts.yaml` → `dashboard:` section.
- Regenerated as part of the same mutation flow as `index.html`.

### Shared contract

1. Subtle watermark: `v{version} · {date}` or `latest · {timestamp}`
2. Changelog appendix (final slide/section)
3. Light + dark theme with in-page toggle
4. Self-contained (all CSS/JS/images inline)
5. Accessible (semantic HTML, WCAG AA, keyboard nav)
6. If generation needs external reads, show a preflight summary first: declared sources, scope/time window or filters, read-only vs apply intent, and output paths; do not fetch until confirmed unless the command was explicitly invoked to execute or automation already authorizes it.
7. Do not declare the artifact done until a QA sweep passes in the generated output: theme toggle works, no unresolved placeholders remain, embedded assets resolve without network fetches, readability/contrast is acceptable in both themes, and keyboard affordances still work.

### Report slide composition

| Report | Slides |
|--------|--------|
| Weekly Status (boss) | Cover → Metrics → Progress → Decisions → Blocked → Ideas → Roadmap → Stakeholder Map → Closing |
| Daily Digest (standup) | Cover → Daily Digest |
| Pitch | Cover → Pitch → Comparison → Closing |
| Roadmap Status | Cover → Metrics → Kanban → Stakeholder Map → Closing |
| Progress | Cover → Headline → Shipped → In-flight → Slipped → Open Decisions → Action Items → Stakeholder Map → Closing |
| Topic Presentation | Cover → Content slides → Comparison → Closing |

`/kb report progress [scope]` consumes KB state plus any configured `connections:` for that scope. Progress reports must add a Sources appendix naming every repo, tracker, or export consulted and the watermark used for the delta.

### Ritual triggers

| Ritual | Artifact |
|--------|----------|
| `/kb end-day` | Daily Digest HTML |
| `/kb end-week` | Weekly Status HTML |

---

## 7. Security & Privacy

| Surface | Default | Rule |
|---------|---------|------|
| Contributor-only layer | Private | Never reference in public repos/artifacts |
| Shared team/org/company layer | Audience-scoped | Visible only to the owning audience |
| Layer marketplace | Shared | No PII, no credentials, no hidden URLs, only marketplace-available tools |
| Consumer-only layer | Read-down only | Digest is allowed; promote and publish must refuse |

### Promotion safety checks

- Promote between contributor-capable layers: warn on secrets, tokens, private URLs, and audience-fit mismatches.
- Promote or publish to a `role: consumer` layer: refuse with a clear message naming the next valid contributor layer.
- Publish to any layer marketplace: hard block on PII, credentials, hardcoded external URLs, or non-marketplace tools.

### Never capture

- Secrets (API keys, passwords, tokens, private keys)
- Raw PII (use aliases/opaque identifiers)
- Legal material without review

### Data residency

Everything is Git + Markdown + local agent. No external service required. Offline mode: local git remote, disable external `connections` reads, and treat every marketplace as manually synchronized.

---

## 8. Automation Levels

| Level | Behavior |
|-------|----------|
| **1 — Assisted** (default) | User triggers, agent processes, user confirms and commits |
| **2 — Semi-auto** | Events trigger processing; human approves promotions/publishes |
| **3 — Full-auto** | Autonomous loop: pull → detect → process → promote (if confidence threshold met) → commit → push → notify |

---

## 9. Plugin / Marketplace Package Layout

```text
marketplace-repo/
├── plugin.json               # root marketplace manifest
├── .claude-plugin/
│   └── marketplace.json      # Claude Code marketplace manifest
├── plugins/
│   └── <plugin>/
│       ├── plugin.json       # per-plugin manifest
│       ├── skills/<name>/
│       │   ├── SKILL.md
│       │   ├── templates/
│       │   └── references/
│       ├── utils/
│       └── agents/<name>.md
├── tests/
│   └── fixtures/
├── scripts/
│   ├── install.py
│   ├── check_consistency.py
│   └── generate_plugins.py
```

Every layer may point at a different marketplace repo via its `marketplace:` block. The package layout is the same regardless of whether that marketplace is team-scoped, org-scoped, or company-scoped.

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
| 2026-04-25 | Added explicit migration-helper coverage for the 5.1.0 closeout: the reference now names `/kb migrate layer-model` and `/kb migrate archives` as the sanctioned way to carry older KBs into the 5.x graph and year-based archive layout |
| 2026-04-25 | Reworked the core model for 5.0.0: replaced the fixed L1–L5 ladder with a flexible layer graph, moved marketplace to a per-layer cross-cutting block, added role-based promote/publish governance, year-based archive paths, the notes primitive, per-layer external connections, and the progress-report contract |
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
