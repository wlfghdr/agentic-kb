# Reference

> **Version:** 6.3.0

Implementation-critical details for building agentic-kb compatible tools. For the user guide, see [README.md](../README.md). For the software-engineering role and artifact model, see [docs/operating-model.md](./operating-model.md). For the role-by-role daily companion to the operating model, see [docs/role-handbook.md](./role-handbook.md). For the deterministic onboarding proof, see [docs/first-run-acceptance.md](./first-run-acceptance.md) and [docs/examples/first-hour.md](./examples/first-hour.md). For the human collaboration contract in shared workspaces, see [docs/collaboration.md](./collaboration.md). For concurrent-write rules (promote collisions, backlink mutation, topic merges), see [docs/concurrency.md](./concurrency.md). For behavioral specs, read the skill and agent files directly: [`plugins/kb/skills/kb-management/SKILL.md`](../plugins/kb/skills/kb-management/SKILL.md), [`plugins/kb/skills/kb-setup/SKILL.md`](../plugins/kb/skills/kb-setup/SKILL.md), [`plugins/kb/agents/kb-operator.md`](../plugins/kb/agents/kb-operator.md).

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
- `role: contributor | consumer` governs shared mutation rights. Consumer layers may receive digests and expose read-down guidance, but promotion or publish targeting a consumer-only layer must refuse with a clear message.
- `features:` opt a layer into primitives: `inputs`, `findings`, `topics`, `ideas`, `decisions`, `tasks`, `notes`, `workstreams`, `foundation`, `reports`, `delivery`, `operations`, `marketplace`, `roadmaps`, `journeys`.
- `marketplace` is **cross-cutting**, not a numbered layer. Any layer may publish to or consume from its own marketplace repo.
- Product-management features (`roadmaps`, `journeys`) are enabled per layer, not globally. `/kb setup` proposes them when the user's role, goals, sources, or desired outputs imply product-direction work, and asks which layer should own them before writing config.

### Two orthogonal axes: layer role and artifact visibility

> **Do not conflate these.** Layer role and artifact visibility are independent. A `contributor` layer can hold `contributor-scoped` artifacts (private to one author until promoted) **or** `shared` artifacts (one canonical record per layer) — both at the same time, on different primitives. Getting this wrong is how a contributor's private finding ends up visible to the whole team before they meant to share it.

#### Axis 1 — Layer role (mutation rights)

- `role: contributor` — the layer may originate shared mutations. `promote` and `publish` can target it.
- `role: consumer` — the layer may receive digests and be read, but it must refuse `promote` and `publish` as a target.

Layer role is a property of the layer.

#### Axis 2 — Artifact visibility (who reads it inside a multi-user layer)

- `contributor-scoped` — the file belongs to one contributor, lives under a contributor directory, is not other contributors' canonical state. Visible to the author and (depending on git permissions) to others as a peer's draft, not as layer truth.
- `shared` — one canonical record per layer, visible as layer truth to every reader. Edits are layer mutations.

Artifact visibility is a property of the primitive **on that layer**. At a single-user layer the distinction collapses and `contributor-scoped` flattens to the layer root.

#### Default visibility per primitive at multi-user layers

| Primitive | Default at multi-user contributor layers | Why |
|-----------|------------------------------------------|-----|
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
| `roadmaps` | shared | Roadmaps describe a layer's planning truth and delivery reality, not one contributor's private view |
| `journeys` | shared by default; configurable for contributor-scoped research drafts | Shared journeys define the product, service, or process experience that roadmap items should move forward |

Single-user layers flatten contributor-scoped primitives to the layer root.

`kb-setup` phase 3 must surface these defaults in the proposed plan before the user confirms — adopters should never have to read this table to discover that `findings` and `ideas` default to contributor-scoped on a team layer.

Decision and task promotion have an additional ownership rule: the layer that owns the scope and accountable decider/owner owns the canonical record. If a decision or task is promoted and the target layer now owns the same question or work item, the source-layer record must be closed, archived, or replaced with a backlink to the canonical target record. Keep separate source-layer items only when the source and target layers have genuinely different scopes, recommendations, accountable owners, or sub-task responsibilities.

### Capture-time layer routing

> **Direct cross-layer capture is allowed and sometimes correct. Agent-inferred cross-layer capture requires confirmation.** Captures do not have to land in the private/anchor layer first and propagate upward through `/kb promote`. Direct routing is parallel to promotion, not a substitute — it answers where an artifact should live the **first time it is written**, when the destination is already clear.

Every `/kb [text/URL/path]` invocation picks one of three routing modes:

1. **Default (active layer)** — no explicit target and no strong reflection signal. Capture lands in the active layer (the anchor unless context already selected a different contributor-capable layer). No extra confirmation; the standard mutation transparency rules apply.
2. **Explicit** — the user named a target layer in the invocation, **or** a `capture-routing:` rule in `.kb-config/layers.yaml` matches the input source/pattern/workstream. Capture lands directly in the named layer. No extra confirmation; the routing was user-declared. The agent cites the matching rule (path + line or rule index) in the response and in `.kb-log/`.
3. **Reflection-driven** — no explicit target was named, but the input's content, source, or context matches the strong-signal rubric in `capture-routing.md` for a non-default contributor-capable layer. The agent **proposes** the target, names the reason, and **waits for human confirmation** before mutating. Do not write to a non-default target on inferred intent alone, and do not "soft-write" to a staging area as a fallback. Weak or ambiguous signals fall through to default.

The default mode is the floor: when neither (2) nor a configured rule fires, captures land in the active layer and the agent proceeds without an extra prompt. A previous confirmation for the same target does not give the agent standing permission — the supported way to make a target sticky is a `capture-routing:` rule (mode 2), not implicit memory.

Direct routing is wrong (fall back to default + later promote) when material may need redaction before it is layer-visible, when the artifact will likely be reshaped substantially as the author thinks it through, when the target layer is `role: consumer`, when the target layer has not enabled the relevant feature, or when the target's `primitive-storage` resolves to `tracker` for the primitive type.

Direct routing is an interactive flow gated on the user. It does **not** apply to automation level 3's scheduled auto-promote, which remains scoped to the parent-edge walk per §6. Teams that want recurring inputs to land in a non-default layer on a schedule should declare a `capture-routing:` rule.

Full contract, schema, audit rule K16 (`capture-routing-unconfirmed`), and response shapes: [`plugins/kb/skills/kb-management/references/capture-routing.md`](../plugins/kb/skills/kb-management/references/capture-routing.md).

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
├── _kb-delivery/
│   ├── briefs/
│   └── specs/
├── _kb-operations/
│   ├── releases/YYYY/
│   └── incidents/YYYY/
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
type: meeting | note | retro
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

#### Retro variant

When `type: retro`, use the retro section shape instead of the meeting shape. Retros are notes with a known structure used for sprint, project/launch, post-incident, and quarterly reflection. The retro frontmatter adds `cadence`, `facilitator`, and `period`; the body uses the sections below.

```markdown
---
type: retro
date: YYYY-MM-DD
cadence: sprint | bi-weekly | project | post-launch | post-incident | quarterly
facilitator: @name
attendees: [@names]
workstream: <name>
period: <window or event the retro reflects on>
source: <optional link>
authors: [@names]
status: open | tracked | closed
---

# Retro: <title>

## Context
## What went well
## What didn't
## What we changed already
## What we will change
## Open questions
## Linked artifacts
```

Retros live under `_kb-notes/YYYY/` next to meeting notes. They do not require a new feature flag — `notes` is already the enabling feature. The template the skill instantiates is `plugins/kb/skills/kb-management/templates/retro.md`. Action items from *What we will change* must be promoted into the layer's `_kb-tasks/backlog.md` or `_kb-decisions/` before the retro is considered closed, so the session produces tracked commitments instead of dissolving into "false convergence" (see [`docs/collaboration.md`](./collaboration.md)).

#### Retro closure lifecycle

The `status:` frontmatter declares where a retro is in its lifecycle. It is not just a label — `/kb start-day`, `/kb start-week`, and `/kb audit` all read it.

| Status | Meaning | Transition trigger |
|--------|---------|---------------------|
| `open` | Retro was written; commitments from *What we will change* have not yet been tracked as tasks or decisions | Set automatically when `/kb note retro` first creates the file |
| `tracked` | Every action item under *What we will change* is linked to a task in `_kb-tasks/` (or a decision in `_kb-decisions/`); no untracked commitments remain | Set by `/kb note end` on a retro once `## Linked artifacts` cites a backlog item or decision for each `## What we will change` bullet, or by the user on confirmation |
| `closed` | Every linked task is `done`/archived and every linked decision is `resolved`; the retro's commitments are fully discharged | Set by `/kb audit`, by the user, or automatically by the next-cadence retro that supersedes this one |

Rules:

- A retro is **never silently closed**. The status moves only on an explicit signal (user confirmation, `/kb note end`, `/kb audit`, or the supersession rule below).
- A retro that closes (via `/kb note end`) without any commitments is held at `status: open` and surfaces the "false convergence" Gate note, not at `status: closed`. `closed` requires evidence of discharged commitments, not absence of them.
- `/kb audit` rule K12 (see [`plugins/kb/skills/kb-management/references/audit.md`](../plugins/kb/skills/kb-management/references/audit.md)) reports `open` retros older than 7 days with no `status: tracked` move, and `tracked` retros whose linked tasks/decisions have been done/resolved (eligible for `closed`).
- `/kb start-week` surfaces unfinished retro commitments (any retro in `status: tracked` with at least one open linked task/decision) as part of its weekly briefing.
- Supersession: when a new retro for the same cadence and workstream is written, the previous one's status auto-advances from `tracked` to `closed` if its linked commitments are resolved. Untracked commitments stay `open` regardless of supersession — the new retro inherits the open items in `## Context`.
- Retros do not move to `_kb-notes/archive/`. They stay in their `YYYY/` directory; the `status:` field is the index used by audits.

### Brief (`_kb-delivery/briefs/YYYY-MM-DD-slug.md`)

```markdown
# Brief: <title>

**Status**: draft | active | superseded | complete
**Owner**: @name
**Stakeholders**: @names
**Workstream**: <name>
**Outcome window**: <date or quarter>

## Problem
## Why now
## Scope
## Non-goals
## Success signals
## Dependencies and handoffs

---
## Changelog
| Date | What changed | Source |
```

Briefs are direction-setting handoff artifacts. They explain why work matters, why now, and what outcome is expected without prescribing the full implementation shape. The inline changelog is required because briefs are living documents, not snapshots — they get refined as direction sharpens.

### Spec (`_kb-delivery/specs/YYYY-MM-DD-slug.md`)

```markdown
# Spec: <title>

**Status**: draft | proposed | accepted | superseded
**Owner**: @name
**Brief**: <link to originating brief>
**Linked decisions**: D-id list
**Workstream**: <name>

## Context
## Requirements
## Proposed shape
## Risks and trade-offs
## Rollout and migration
## Verification
## Open questions

---
## Changelog
| Date | What changed | Source |
```

Specs are design-decision artifacts. They connect briefs, findings, decisions, and delivery work into a reviewable implementation proposal. The inline changelog tracks how the design moved from `draft` toward `accepted` and what was learned along the way.

### Release record (`_kb-operations/releases/YYYY/YYYY-MM-DD-slug.md`)

```markdown
# Release: <title>

**Date**: YYYY-MM-DD
**Status**: planned | in-progress | shipped | rolled-back
**Owner**: @name
**Audience**: <who is affected>
**Linked spec**: <link to driving spec>
**Workstream**: <name>

## Scope
## Rollout plan
## Verification
## Rollback plan
## Communications
## Follow-up
```

Release records make delivery state auditable across engineering, QA, release coordination, and leadership. Once shipped, the record becomes append-only apart from clearly marked corrections.

### Incident record (`_kb-operations/incidents/YYYY/YYYY-MM-DD-slug.md`)

```markdown
# Incident: <title>

**Opened**: YYYY-MM-DD HH:MM
**Severity**: sev-1 | sev-2 | sev-3 | sev-4
**Status**: active | mitigated | resolved | follow-up
**Owners**: @names
**Services**: <affected services or surfaces>
**Workstream**: <name>

## Impact
## Detection
## Timeline
## Mitigations
## Root cause hypotheses
## Follow-up tasks
## Linked artifacts
```

Incident records are operational interruption artifacts. They may be updated while active, but once resolved they should remain append-only apart from clearly marked corrections.

### Backlink (promoted-record stub)

When a decision, task, or other shared artifact is promoted upward and the target layer now owns the same scope (see §1 ownership rule), the source-layer record is **not** deleted. Its path stays stable so existing references keep resolving. The body is replaced with a standardized backlink stub so that humans, audits, and migration helpers can all detect it with one pattern.

```markdown
---
status: promoted
canonical: ../../../team-observability-kb/_kb-decisions/D-2026-05-18-pricing-tier.md
promoted-at: 2026-05-18
promoted-by: @alice
---

# D-2026-05-15: <original title>

> **This record has been promoted.** The canonical version lives at
> `../../../team-observability-kb/_kb-decisions/D-2026-05-18-pricing-tier.md`.
> Edit there, not here.
```

Field contract:

- `status: promoted` is the only stable status value used for the backlink stub. It replaces the original primitive-specific status (`decided`, `doing`, etc.) once the canonical record moves.
- `canonical:` is a repo-relative POSIX path to the target file. Cross-layer links use the path the contributor would type from this file (`../../<other-layer-kb>/...`). Absolute paths from the workspace root are also accepted.
- `promoted-at:` is the ISO date of the promote operation.
- `promoted-by:` is optional but recommended at multi-user layers so audits can trace who moved the record.
- The body keeps the original `# <id-or-title>` line so historical links still resolve, then a single block-quoted banner pointing at the canonical record. Any further prose, evidence trail, or development log content moves to the canonical record before the backlink is written; nothing duplicative stays behind.

The same shape applies to promoted tasks (whose stub may live in `_kb-tasks/archive/YYYY/MM.md` as a one-line table entry citing `canonical:`) and to ideas/findings that are promoted as part of a decision/task ownership move. Findings remain immutable on the source layer when only their *evidence* is cited upward — the backlink stub is for records whose *canonical ownership* shifted.

`/kb audit` rule K11 (see [`plugins/kb/skills/kb-management/references/audit.md`](../plugins/kb/skills/kb-management/references/audit.md)) checks that every `status: promoted` record has a resolvable `canonical:` target. Migration helpers (`/kb migrate layer-model`, `/kb migrate archives`) rewrite the relative path in the stub when a layer moves, using this format as the canonical anchor.

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
    features: [inputs, findings, topics, ideas, decisions, tasks, notes, workstreams, foundation, reports, delivery]
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
      # writeback.enabled is RESERVED for a future version. In v6.1.0 the
      # only supported reference-mode is `link` (read-only digests); the
      # writeback block is recognized by the schema but has no effect.
      # Setting `enabled: true` is a no-op today. See "Connections
      # write-back (reserved)" in the spec for the planned contract.
      writeback:
        enabled: false
        capabilities: []
    primitive-storage:
      decisions:
        mode: files
        file-dir: _kb-decisions
      tasks:
        mode: files
        file-dir: _kb-tasks
      ideas:
        mode: files
        file-dir: _kb-ideas

  - name: team-observability
    scope: team
    role: contributor
    parent: engineering-org
    path: ../team-observability-kb
    features: [findings, topics, ideas, decisions, tasks, notes, foundation, reports, delivery, operations, marketplace]
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
- `role`: `contributor` or `consumer`; consumer layers are read-down destinations, not promote/publish targets.
- `parent`: the next upward layer in the graph, or `null`.
- `path`: repo-relative path to the layer repo.
- `features`: enabled primitives for that layer.
- `contributor-mode`: optional overrides for primitives that can be shared or contributor-scoped.
- `marketplace`: marketplace repo and install mode for that layer's published skills.
- `connections`: product repos, trackers, reference mode, and write-back policy for that layer.
- `primitive-storage`: per-primitive ownership map declaring whether decisions, tasks, ideas, feature intake, and roadmap items are canonical in KB files, in a configured tracker, or in a hybrid file-to-tracker promotion flow.
- `roadmap` / `journeys`: product-management configuration blocks nested under the layer that enabled those features. Setup derives and confirms the owning layer; hand-edits must keep the block beside the layer whose `features` include `roadmaps` or `journeys`.

### Primitive storage and tracker backbones

First-class primitives do not all need to use the same operational backbone. Private or early-stage work stays file-backed by default. Shared process and operational artifacts default to GitHub Issues as the canonical operational home for decisions, tasks, feature intake, and roadmap items, with KB files retaining synthesis, evidence, reports, summaries, and backlinks. A layer may still declare `files` or `hybrid` explicitly when that is the confirmed ownership model.

`primitive-storage` is the ownership map. It complements `connections.trackers[]`: the tracker connection says how to reach the external system, while `primitive-storage` says which primitive family the external system owns.

```yaml
layers:
  - name: team-kb
    features: [findings, topics, decisions, tasks, notes, reports, roadmaps]
    connections:
      trackers:
        - name: team-work
          kind: github-issues
          repo: org/team-work
          project: Team Planning
          scope: is:issue
          issue-types: [Feedback, Idea, Decision, Task, Feature, Roadmap Item]
          status-values: [Todo, In Progress, In Review, Done]
      writeback:
        enabled: false
        capabilities: []
    primitive-storage:
      decisions:
        mode: tracker
        tracker: team-work
        kind: Decision
        summary-dir: _kb-decisions
      tasks:
        mode: tracker
        tracker: team-work
        kind: Task
        summary-dir: _kb-tasks
      ideas:
        mode: hybrid
        tracker: team-work
        kind: Idea
        file-dir: _kb-ideas
      feature-intake:
        mode: tracker
        tracker: team-work
        kind: Feature
      roadmap-items:
        mode: tracker
        tracker: team-work
        kind: Roadmap Item
```

Valid modes:

| Mode | Canonical operational home | Required setup behavior |
|------|----------------------------|-------------------------|
| `files` | KB Markdown files | Create the matching KB directories and templates |
| `tracker` | Configured tracker items | Create supporting summary/backlink directories when requested and generate tracker setup artifacts |
| `hybrid` | KB files until promotion, then tracker items | Create file directories plus promotion rules to create/link tracker items when the sharing boundary is crossed |

For GitHub-backed layers, setup should generate or guide creation of the GitHub governance profile: native issue types, issue forms, project/status guidance, labels that do not duplicate native metadata, pull request templates, governance CI, a path labeler, manual branch-protection/CODEOWNERS/project setup checklist, and a repo-local tracker workflow skill. For Jira-backed layers, setup should record project key/URL, issue type mapping, status mapping, query/JQL, link policy, and confirmation-gated write-back capabilities. Other trackers follow the same contract through adapter-specific fields under `connections.trackers[]`.

If a primitive family is omitted from `primitive-storage`, readers assume `files` for personal/private layers. In shared contributor layers, setup must render an explicit `primitive-storage` block: `github-issues` tracker ownership for shared process/operational families by default, or an explicit `files` fallback when the adopter cannot or does not want GitHub Issues to be canonical. Skills must refuse ambiguous writes when both a KB file and tracker item appear to be canonical for the same item.

### Product-management primitives

Roadmaps and journeys are the product-direction side of the same operating model that briefs, specs, releases, and incidents cover for delivery and operations.

| Primitive | Home | Primary question | Typical source inputs | Typical output |
|-----------|------|------------------|-----------------------|----------------|
| `journeys` | `_kb-journeys/` | What experience or process should exist for the target persona? | notes, research, briefs, support signals, existing docs | markdown journey specs, HTML journey maps, standalone mocks |
| `roadmaps` | `_kb-roadmaps/` | What should happen when, what is already true, and where does delivery drift from plan? | tracker exports, milestones, goals, journeys, git/release signals | MD + HTML + JSON roadmap/status artifacts |

Placement is an onboarding decision, not a fixed rule. A personal PM may own product-direction artifacts in their anchor layer; a team may place shared journeys and roadmaps in a team contributor layer; an org may own portfolio roll-ups in an org layer. The first setup path should keep ownership simple: one layer owns the roadmap scope and its cited journeys. Layered roadmaps/journeys are allowed by the graph, but cross-layer roll-ups and journey inheritance are deferred enhancement work until the single-layer ownership path is proven.

The roadmap artifact should stay legible as a product-management artifact, not just an engineering status report:

- make draft, proposed, agreed, and shipped status visible;
- use checkmarks only for implemented or already-true items;
- phrase roadmap item headlines as customer/user value, with implementation detail on the next line;
- aggregate dense source data into lanes and phases before rendering a presentation;
- preserve traceability to journeys, decisions, trackers, and delivery signals in the JSON/appendix.

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

Automation level contract:

- `level: 1` — manual only. No scheduled automation runs; rituals and digests happen only when the user invokes them.
- `level: 2` — scheduled read/review flows. Schedules may run rituals and digests, but `auto-promote.enabled` stays `false`.
- `level: 3` — scheduled flows plus guarded auto-promote. Auto-promote may run only when enabled, above the configured confidence threshold, and outside excluded workstreams.

Setup interview guidance for these three levels lives in [`plugins/kb/skills/kb-setup/references/automation-levels.md`](../plugins/kb/skills/kb-setup/references/automation-levels.md).

### `auto-promote.confidence-threshold` — what it is

`confidence-threshold` is the **integer 0–5 evaluation-gate score** an artifact must reach before it becomes eligible for auto-promote. It is the same scale as the gate score documented in §2 (one point per `yes` answer across the five questions), not a separate probability or learned metric. The field is named `confidence-threshold` rather than `gate-score-threshold` because adopters configuring it are conceptually saying "how confident must the agent be in this artifact before it ships upward without me looking".

Default: `4`. That is one notch above the "Finding + topic update + possibly a new decision or idea" line at score `3`, intentionally — at `3` material is filed but not yet promoted; at `4` the material has been corroborated against existing topics and is a candidate to leave the contributor scope.

Auto-promote algorithm at `level: 3`:

1. **Trigger:** scheduled `digest-parent` run (or an explicit `/kb sync`), not on every capture.
2. **Eligibility filter** (all conditions must hold per candidate artifact):
   - the artifact has a recorded gate score, and that score is `>= confidence-threshold`,
   - the artifact's workstream (if any) is not in `auto-promote.excluded-workstreams`,
   - the artifact has no `manual-review-required: true` frontmatter flag,
   - the artifact is in a state that allows promotion per its primitive's lifecycle (e.g. a decision must not be in `under-discussion`),
   - the user is not the only contributor at the source layer and the target layer has the same scope owner, OR the layer model is single-user (no staging needed).
3. **Promote target:** the layer named by the source layer's `parent` edge, per §1. If `parent` is `null`, no auto-promote happens — the artifact stays in place and is logged for the next manual review.
4. **Action:** for multi-user target layers, stage in the destination contributor scope and write a `_kb-log/auto-promote-staged.md` entry. For single-user targets, write the canonical record directly and apply the backlink contract in §1.
5. **Conflict / failure:** anything the algorithm cannot decide (title collision, divergent active record at the target, broken `canonical` link, missing parent layer) is **escalated** to `_kb-log/exceptions.md` and surfaced at the next `/kb status` triage scan. Nothing is silently overwritten.

Worked example: at the personal anchor layer, a finding with gate score 4, no `manual-review-required` flag, in workstream `caching` (not excluded), with `parent: team-observability` set — at the next `digest-parent` tick the agent stages it as `team-observability/.contributors/alice/_kb-references/findings/...` and logs the action. The contributor still reviews staged content during the next `/kb sync`; nothing is mass-published to layer truth without that step.

`auto-promote.confidence-threshold` is meaningless when `auto-promote.enabled: false` — the field stays in the schema so a future opt-in does not need a config migration.

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

Reference helper coverage: the repo ships neutral renderer helpers for roadmap and journey artifacts under `plugins/kb/skills/*/scripts/`. They cover local validation and artifact generation; apply-capable command paths stay behind the explicit confirmation gates defined in the roadmap and journey skill specs.

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

### Shared collaboration artifacts

For recurring software-engineering work, the KB should keep a reviewable markdown source behind the most common shared reports:

| Artifact | Source template | Canonical markdown source path | Relationship to roadmap and journeys |
|----------|-----------------|-------------------------------|--------------------------------------|
| Status report | `kb-management/templates/report-status.md` | `_kb-references/reports/sources/<scope>/status-<scope>-YYYY-MM-DD.md` | summarizes the current operating picture using roadmap scope, delivery reality, blockers, and decisions |
| Delivery report | `kb-management/templates/report-delivery.md` | `_kb-references/reports/sources/<scope>/delivery-<scope>-YYYY-MM-DD.md` | reconciles roadmap commitments against journey readiness and delivery signals |
| Roadmap change report | `kb-management/templates/report-roadmap-change.md` | `_kb-references/reports/sources/<scope>/roadmap-change-<scope>-YYYY-MM-DD.md` | records baseline changes, their reasons, and the required downstream updates |

Rules:

1. The markdown source is the canonical collaboration artifact. HTML is a rendering for consumption.
2. `<scope>` must match the roadmap or journey scope name when one exists, for example `growth`, `platform`, or `exec`.
3. Revisions append a new dated source file, they do not silently overwrite an older one.
4. Status and delivery reports belong beside roadmap and journey work, not inside those primitives. They link to roadmap and journey artifacts but do not replace them.

These are shared-memory artifacts, not just pretty HTML outputs. The markdown source is for collaboration, review, and traceability.

### Ritual triggers

| Ritual | Artifact |
|--------|----------|
| `/kb end-day` | Daily Digest HTML |
| `/kb end-week` | Weekly Status HTML |

### HTML artifact lifecycle (commit, host, merge)

HTML artifacts are **generated**, not authored. They are regenerated from KB state, can grow to multi-megabyte size for long-lived layers, and conflict trivially in git because every regeneration touches almost every line. The lifecycle below makes the commit/host/merge decision explicit so adopters do not have to invent one per layer.

#### Default commit policy

Anchor-layer live overviews are committable; everything else is generated locally by default.

| Artifact family | Filename pattern | Default `.gitignore` posture | Committable? | Why |
|-----------------|------------------|------------------------------|--------------|-----|
| Anchor-layer live overview | `index.html`, `dashboard.html` at the anchor-layer repo root | tracked | yes — the anchor layer's overview is the public/shared entry point | The anchor layer is the source of truth for the user's workspace; the overview belongs in version control so collaborators (and GitHub Pages) see it |
| Other-layer live overview | `index.html`, `dashboard.html` at a non-anchor layer | ignored | no by default; opt in per layer | Non-anchor layers usually have one contributor or one team viewing locally; committing every regeneration spam-bloats the layer repo |
| Historical artifacts | `<scope>/<slug>-v<X.Y>.html`, `reports/daily-YYYY-MM-DD.html`, `reports/weekly-YYYY-WW.html`, `_kb-journeys/html/`, `_kb-roadmaps/html/` | tracked | yes | These are dated/versioned and immutable, so they merge cleanly and form historical memory |
| Snapshot copies (cross-repo) | banner-tagged HTML imported from another repo | tracked | yes, with the snapshot banner from `html-artifacts.md` §"Snapshot artifacts" | They are point-in-time references; ignoring them would lose the snapshot |

Concrete default `.gitignore` entries scaffolded by `/kb setup` on a non-anchor layer:

```gitignore
# Generated live overviews — regenerated on every mutation
/index.html
/dashboard.html
```

The scaffold writes those lines only on non-anchor layers. On the anchor layer, `index.html` and `dashboard.html` are tracked.

#### Merge strategy

When live overviews are committed (anchor layer, or any layer that opted in), two contributors regenerating on the same hour will produce conflicting diffs in the HTML body. The conflict is mechanical, not semantic — the next regeneration always supersedes both branches. The recommended `.gitattributes` line:

```gitattributes
# Live overviews are regenerated artifacts — accept ours on merge,
# then regenerate from KB state to converge.
index.html       merge=ours
dashboard.html   merge=ours
```

`/kb setup` writes these `.gitattributes` lines on any layer where the live overviews are committed. After a merge that hits one of these, `/kb status --refresh-overviews` is the canonical recover step — it regenerates from current KB state, which is the actual source of truth.

Historical artifacts do **not** get `merge=ours` — they are dated and immutable, so two contributors should not be touching the same file. If they did, the conflict surfaces a real disagreement and needs human resolution.

#### Hosting modes

`/kb setup` Q9 asks how the user expects to view artifacts. Three modes are supported; the choice writes into `.kb-config/artifacts.yaml`:

| Mode | What it means | Setup writes |
|------|---------------|--------------|
| `local` (default) | Open `file://` paths in a browser; no hosting | `hosting.mode: local`; no Pages config |
| `github-pages` | The anchor layer publishes via GitHub Pages from the default branch root | `hosting.mode: github-pages`; ensures `.nojekyll` and tracks `index.html`, `dashboard.html` on the anchor layer |
| `external` | Some other static host pulls the anchor-layer repo | `hosting.mode: external`; tracks anchor-layer artifacts the same as `github-pages` but leaves deploy config to the adopter |

Hosting is a property of the anchor layer. Non-anchor layers stay `local` unless the adopter explicitly enables hosting on them; doing so just flips their live overviews from ignored to tracked (and adds the `merge=ours` lines).

#### Regeneration trigger

Regeneration of the affected layer's live overviews fires as part of the same mutation that triggered it — see [`plugins/kb/skills/kb-management/references/html-artifacts.md`](../plugins/kb/skills/kb-management/references/html-artifacts.md) "Auto-regeneration contract" for the full list of triggering operations. Adopters never need to run a separate "regenerate everything" command unless they hit a stale state (merge fallout, manual file edit, branch switch); `/kb status --refresh-overviews` is the repair path.

#### Size and bloat

Live overviews stay bounded because they index *current* state. Historical artifacts grow over time but are dated and small individually. For layers with thousands of historical artifacts, the `index.html` generator deduplicates versioned entries (see [`plugins/kb/skills/kb-management/references/html-artifacts.md`](../plugins/kb/skills/kb-management/references/html-artifacts.md) "Index rules"); the older versions stay on disk but do not load when the page renders. No spec-level pruning rule is required.

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

## 9. Adoption Stages

`agentic-kb` is designed to meet a team at one of three adoption stages and to make graduation between stages explicit instead of implicit. The stages are not marketing levels; they are the order in which the standard knowledge-ops failure modes (audit vacuum, knowledge drift, rubber-stamping, cascading agent errors) get addressed.

| Stage | Posture | Typical scaffold | Typical automation level |
|-------|---------|------------------|--------------------------|
| **1 — Capture discipline** | Humans author every artifact by hand into the directory contract; no `/kb` invocation in the loop. | One contributor anchor layer; `findings`, `topics`, `decisions`, `notes`, `tasks`, `foundation`; no roadmap/journey features unless explicitly needed; no `connections:` write-back. | 1 (manual only) |
| **2 — Agent-assisted triage** | The `/kb` evaluation gate fires on capture; agent proposes routing; humans confirm before persistence. | Stage 1 baseline plus `/kb` slash command and feature-keyword triggers wired into the harness; optional read-only `connections:` for tracker exports. | 1 (manual only); the agent is in the loop, but every persistence still waits on a human. |
| **3 — Bounded autonomous knowledge ops** | Scheduled rituals/digests; guarded auto-promote on confidence threshold; humans review only flagged exceptions. | Stage 2 baseline plus `auto-promote` config, declared exception channel, live-overview regeneration as part of every mutation. | 2 (scheduled rituals/digests) or 3 (scheduled flows plus guarded auto-promote). |

Stage and automation level are related but not identical. Adoption stage is the team's posture toward the agent; automation level is the configuration knob that enacts it. A Stage 1 team must not be configured at automation level 2 or 3 (no `/kb` invocation pattern for a schedule to fire from). A Stage 3 team should not be configured at automation level 1 (autonomous-loop benefits never materialize). `kb-setup` phase 3 enforces this consistency in the proposal it shows the user.

Graduation criteria between stages and the full operating contract live in [`plugins/kb/skills/kb-setup/references/adoption-stages.md`](../plugins/kb/skills/kb-setup/references/adoption-stages.md). They are normative for the wizard but informational for hand-edits — a team that wants to move stages without the wizard may, but the criteria name the failure modes that show up if the move is premature.

---

## 10. Relationship to Repo-as-OS Frameworks

`agentic-kb` is the **knowledge-ops layer** of an agentic enterprise. It owns Strategy, Design, and Learning artifacts: `foundation`, `briefs`, `specs`, `decisions`, `findings`, `topics`, `reports`. It does not own the work-flow side of the operating model (signals, missions, pull requests, releases as governance objects, policies as enforceable gates) — those are the domain of separate, complementary **repo-as-OS frameworks** that run an entire enterprise out of a git repository.

The two layers compose cleanly when both are present, and either side is usable without the other.

### Mapping (abstract)

| Knowledge-ops primitive (`agentic-kb`) | Work-flow primitive (typical repo-as-OS framework) | Relationship |
|----------------------------------------|----------------------------------------------------|--------------|
| `finding` | observation / signal | A finding is the durable evidence record; a signal is the work-flow trigger derived from it. The same content may appear as both. |
| `brief` | mission scope / charter | A brief frames the problem and intended outcome durably; a mission is the executable instance of that brief. |
| `spec` | implementation plan / RFC | A spec is the design contract; the framework typically references it from its mission or pull-request flow. |
| `decision` | decision record / ADR | These are usually the same artifact, with the framework defining where review and approval happen. |
| `release record` | release / ship event | A release record is the durable description; the framework typically owns the release execution and gate. |
| `incident record` | postmortem / production event | An incident record is the durable timeline; the framework typically owns the on-call routing. |
| `report progress` | status / readout | The progress report is composable across both surfaces. |
| `task` (knowledge-task) | engineering issue / tracker ticket | **Split ownership**, not the same artifact. See "Task ownership" below. |

This mapping is intentionally generic. `agentic-kb` does not depend on any specific repo-as-OS framework, is not packaged with one, and reviewers should reject any attempt to name a specific vendor framework as canonical. Adopters running such a framework get bridge defaults (`connections.product-repos[]` with watch globs and ticket patterns) when `kb-setup` phase 1 detects the structure; adopters who do not still get a fully usable knowledge-ops scaffold.

### Task ownership — KB vs. external tracker

This is the most common point where adopters drift: are tasks first-class in `_kb-tasks/` or in GitHub Issues / Jira / Linear?

**Canonical rule: split ownership.** KB tasks and tracker tasks are *different artifacts*, not two views of the same thing.

| Domain | Lives in | Examples |
|--------|----------|----------|
| **Knowledge work** | `_kb-tasks/` in the owning KB layer | "review the findings from yesterday's customer call", "decide between caching strategies A and B", "develop idea I-2026-05-15-foo", "draft the brief for the new pricing tier", "follow up on retro commitment X" |
| **Engineering work** | the external tracker (when one exists) | "implement endpoint /v2/users", "fix the deploy script", "land the cache invalidation refactor" |

The split has three rules:

1. **A knowledge-task never duplicates a tracker-task.** If an engineering issue exists in the tracker, the KB-side reference to it lives as a *link*, not a parallel task record. Use a `<!-- ref: <tracker-url> -->` line in the related decision/brief/spec, not a row in `_kb-tasks/backlog.md`.
2. **A tracker-task never duplicates a knowledge-task.** A retro commitment "decide caching strategy" does not become a GitHub Issue — it stays in the KB until it produces a decision artifact that can spawn engineering work.
3. **Status reconciliation does not exist** because there are no parallel records to reconcile. `/kb digest connections` may surface tracker movement that informs KB work (e.g. "the cache-invalidation ticket closed; is the related decision still relevant?"), but it does not flip KB-task state from tracker state, and the reverse.

`/kb task` lists KB tasks only. To see tracker tasks, the adopter uses the tracker's own UI; the tracker is the source of truth there. `/kb start-day` and `/kb start-week` may surface stale tracker links via `digest connections`, but the tracker remains canonical for its own domain.

If a workflow needs a single combined view (e.g. for a status report), `/kb report status [scope]` composes both surfaces — it cites KB tasks from `_kb-tasks/` and tracker tickets from `connections.product-repos[]` side by side, naming each source.

Adopters who *want* tracker write-back (so closing a tracker ticket auto-resolves a linked KB task) must wait for the reserved `writeback:` block to ship — see [`plugins/kb/skills/kb-management/references/connections-lifecycle.md`](../plugins/kb/skills/kb-management/references/connections-lifecycle.md) "Write-back (RESERVED)". Until then, the link is read-only and divergence is impossible by construction.

### Out of scope for `agentic-kb`

- enforcing approval policies on pull requests,
- packaging or releasing software,
- on-call routing,
- compliance posture self-assessment,
- multi-agent orchestration of work execution.

These belong to the surrounding framework (or to the team's existing toolchain) and are intentionally not modeled here.

---

## 11. Plugin / Marketplace Package Layout

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
- `dependencies` — other skills (by `name`) that must be installed for this one to work. Each entry is a `name` plus an optional SemVer range (`>=1.2, <2`). The installer refuses to install a skill whose declared dependencies are not satisfied in the target harness.

For skills that encode safety rules, policy checks, scoring, or routing logic, the marketplace repo should also ship deterministic regression fixtures under `tests/fixtures/` so prompt or model changes can be checked against known clean, violating, and ambiguous cases.

### Skill versioning, dependencies, and conflict resolution

A layer marketplace is multi-tenant by definition: it can host skills authored by different contributors across many adoption cycles. The fields below make publish, install, and upgrade decisions deterministic.

#### SemVer for skills

Every published skill MUST declare `version: <X>.<Y>.<Z>` in its frontmatter. The version follows the same SemVer contract as the framework itself:

| Bump | When |
|------|------|
| `PATCH` | Prose-only edits, fix-typo, documentation clarification |
| `MINOR` | New trigger phrases, new optional template fields, new reference docs — non-breaking additions |
| `MAJOR` | Renamed canonical command verb, removed trigger phrase, changed required template fields, changed safety-validation rules, or any change that would break an installer who pinned the previous major |

Installers default to `latest` within the same major. Adopters who want a fixed version pin the skill in their `.kb-config/layers.yaml` `marketplace:` block:

```yaml
marketplace:
  repo: ../team-skills
  install-mode: marketplace
  pin:
    kb-our-onboarding: ">=1.0, <2"
```

When a new major releases, the installer flags the pin and asks the adopter before upgrading — major upgrades are never silent.

#### Dependencies

`dependencies:` in skill frontmatter is a list of other skills this one needs:

```yaml
dependencies:
  - name: kb-management
    version: ">=6.0, <7"
  - name: kb-tracker-workflow
    version: ">=1.0"
```

Resolution rules:

1. The installer walks the dependency tree before writing any file. If a dependency is missing or out of range, the install is refused with a message naming the missing skill, the required range, and the marketplace it would come from.
2. Diamond dependencies (two skills require different ranges of the same third skill) resolve to the highest version that satisfies all ranges. If no such version exists, the install is refused.
3. A skill MAY declare `dependencies: []` (the default) to assert no cross-skill requirement.

`dependencies:` is independent of `incompatible_with:`. The first declares what MUST be installed; the second declares what MUST NOT be installed alongside.

#### Approval gating

Marketplace publishing has two modes, declared by the marketplace repo and surfaced in `layers.yaml`:

| Mode | Who can publish | Where the review happens |
|------|----------------|---------------------------|
| `install-mode: open` | Anyone with write access to the marketplace repo | None — publish lands on `main` directly |
| `install-mode: review-required` | Anyone with PR-open access; merges require maintainer approval per the marketplace repo's branch protection / CODEOWNERS | The marketplace PR is the review boundary |

`/kb publish` honors the configured mode:

- For `open`, the publish operation opens a branch and pushes a PR per the standard publish flow, then offers to fast-merge if the author has write rights.
- For `review-required`, the publish operation opens a PR and stops — the author waits for marketplace maintainer approval before the skill becomes installable.

Public layer marketplaces (a marketplace targeted at adopters the author does not personally know) MUST use `install-mode: review-required`. Private internal marketplaces (a single team's shared skills) MAY use `install-mode: open`. `/kb setup` proposes `review-required` whenever the configured marketplace repo's visibility is public.

#### Conflict resolution across marketplaces

A layer may reference multiple marketplaces (a team marketplace plus an org marketplace, say). If two marketplaces publish a skill with the same `name`, the installer resolves the conflict deterministically using the `priority:` field declared on the layer's marketplace block:

```yaml
marketplace:
  - repo: ../team-skills
    priority: 100
  - repo: ../org-skills
    priority: 50
```

Resolution rules:

1. **Higher `priority:` wins.** The skill from the higher-priority marketplace is installed; the lower-priority one is shadowed.
2. **Shadowed skills are visible to the adopter.** The installer emits a one-line warning naming the shadowed skill and its source marketplace; `/kb digest connections` includes a "shadowed skill" panel.
3. **No tie-breaker on equal priorities.** Equal `priority:` values across marketplaces are a configuration error and the installer refuses until the adopter resolves them.
4. **No `priority:` declared** defaults to `priority: 50`; the first marketplace listed wins on equal defaults only if it is the **only** marketplace declaring that skill.

Cross-marketplace upgrades respect the same dependency and version-pin rules as single-marketplace upgrades — a higher-priority marketplace cannot silently install a major upgrade past a declared pin.

---

## 12. Harness Support

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

Versioning rule: the marketplace-facing version in `.claude-plugin/marketplace.json`, `plugin.json`, and `plugins/kb/plugin.json` must match the repo release version declared in `VERSION` and the current release/changelog line. Marketplace versioning is release versioning, not a separate numbering scheme.

---

## Changelog

| Date | What changed |
|------|-------------|
| 2026-06-02 | Version aligned to 6.3.0 and §5 changed the shared process/operational primitive default from file-backed KB records to GitHub Issues via explicit `primitive-storage`, with file-backed defaults retained for personal/private layers. Source: issue #145 |
| 2026-05-24 | §1 capture-time layer routing now points reflection-driven routing at the strong/weak signal rubric in `capture-routing.md` and states that weak or ambiguous signals fall through to default. This removes the vague "clearly implies" trigger from the structural reference while keeping the detailed operational examples in the dedicated contract. Source: issue #126 |
| 2026-05-24 | Version aligned to 6.2.0 |
| 2026-05-23 | §1 added "Capture-time layer routing" subsection codifying the three routing modes (default / explicit / reflection-driven) and the mandatory human-confirmation gate for agent-inferred non-default capture targets. Direct cross-layer capture is now a named first-class flow parallel to `/kb promote`, not an implicit consequence of "context selects another contributor-capable layer". Full schema, audit rule K16, and response shapes live in `plugins/kb/skills/kb-management/references/capture-routing.md`. Closes the spec gap where artifacts could only flow private → shared via promote, and the agent had no codified obligation to confirm a self-chosen non-default destination |
| 2026-05-22 | Added pointer to `docs/concurrency.md` in the navigation preamble so adopters can find the parallel-promote / backlink-mutation / topic-merge resolution rules without grepping. No structural change in §1–§12. Closes audit finding #106 |
| 2026-05-22 | §4 added "Backlink (promoted-record stub)" subsection defining the concrete `status: promoted` + `canonical:` + `promoted-at` frontmatter and the standardized banner body that replaces a source-layer record when canonical ownership shifts upward; §4 retro variant added `status: open \| tracked \| closed` frontmatter plus a "Retro closure lifecycle" subsection covering transition triggers, the no-silent-close rule, and supersession; §6 added "HTML artifact lifecycle (commit, host, merge)" subsection covering default `.gitignore` posture per artifact family, `.gitattributes` `merge=ours` for committed live overviews, three hosting modes (`local` / `github-pages` / `external`), and the regeneration repair path; §11 added "Skill versioning, dependencies, and conflict resolution" subsection covering SemVer per skill, `dependencies:` resolution rules, `install-mode: open \| review-required` approval gating, and `priority:`-based conflict resolution across marketplaces. Closes audit findings #107, #111, #112, #113 |
| 2026-05-18 | §5 layers.yaml example annotated `writeback:` as RESERVED in v6.1.0 (no-op); §6 added the "`auto-promote.confidence-threshold` — what it is" subsection with the 0–5 gate-score definition, the auto-promote eligibility filter, the promote target rule, the conflict-escalation rule, and a worked example; §10 added the "Task ownership — KB vs. external tracker" subsection codifying split ownership (KB owns knowledge work, tracker owns engineering work, read-only links, no parallel status reconciliation) and added a corresponding row to the mapping table. Closes audit findings #102, #103, #105 |
| 2026-05-18 | §1 split "Contributor-scoped vs shared primitives" into two clearly orthogonal subsections — Axis 1 "Layer role" (`contributor` vs `consumer`, mutation rights) and Axis 2 "Artifact visibility" (`contributor-scoped` vs shared, per-primitive). Added a do-not-conflate callout. Closes the data-leak risk where multi-user team layers ship with everything shared by default because adopters never see the visibility axis. `kb-setup` phase 3 now must surface the default visibility per primitive in the proposed plan before scaffold. Updated the §10 repo-as-OS phrasing to match the kb-setup phase-1/phase-2 swap. Closes audit findings #98 and #104 |
| 2026-05-17 | Added `primitive-storage` to the layer config contract so onboarding can choose file-backed, tracker-backed, or hybrid ownership per primitive family and can generate generic GitHub/Jira tracker setup outcomes without duplicating canonical records; GitHub setup now points at a fuller governance profile with issue/project/PR rules, CI, labeler, checklist, and repo-local skill |
| 2026-05-15 | Release-readiness audit: removed active draft-feature wording for roadmap and journey flows, clarified stable helper coverage and apply-capable confirmation gates, trimmed unsupported harness rows from the public support matrix, and aligned the reference with the 6.1.0 release surface |
| 2026-05-14 | Added the retro variant to §4 Note formats (`type: retro` with cadence/facilitator/period frontmatter and a structured what-went-well / what-didn't / changed / will-change / open-questions / linked-artifacts section set) so sprint, project, post-launch, post-incident, and quarterly retros have a canonical shape. Retros stay inside the existing `notes` feature — no new directory or feature flag. Added a navigation pointer to the new role-handbook companion doc |
| 2026-05-10 | Version aligned to 6.0.0 after the v5 adoption-arc closeout. Updated the §4 brief, spec, release, and incident file formats so they match the templates the skill actually instantiates: brief gains "Why now", "Success signals", "Dependencies and handoffs", and an inline changelog and moves stakeholders into the frontmatter; spec gains "Requirements", "Proposed shape", "Rollout and migration", "Verification", "Open questions", and an inline changelog and links to the originating brief in the frontmatter; release gains "Audience" and "Linked spec" frontmatter and switches to the rollout/rollback/communications/follow-up section set; incident gains "Owners", "Services", and the precise "Opened" timestamp. The four artifacts are now the same shape across REFERENCE, templates, and the new `/kb brief`, `/kb spec`, `/kb release`, and `/kb incident` verbs in `command-reference.md` |
| 2026-05-10 | Added shared collaboration artifact guidance for status, delivery, and roadmap-change report sources |
| 2026-05-08 | Clarified the shipped role of the draft roadmap/journey helper scripts and bumped the reference patch version |
| 2026-05-06 | Version aligned to 5.6.0 after adding the decision/task promotion ownership rule: promoted decisions and tasks now have one canonical layer unless the source and target scopes genuinely differ |
| 2026-04-30 | Version aligned to 5.5.0 after promoting roadmap and journey work into the product-management operating surface: setup now derives their owning layer from role/goals and the reference names placement, visibility, and customer-value presentation rules |
| 2026-04-29 | Version aligned to 5.4.2 after the draft-skill discoverability fix. Structural contracts in this reference are unchanged; the dispatcher now routes `/kb roadmap` and `/kb journeys` through the kb-management surface that this reference describes |
| 2026-04-27 | Version aligned to 5.4.1 after the documentation-gap follow-up. Corrected the repo-as-OS bridge field name to `connections.product-repos[]` so the reference matches the live `layers.yaml` schema |
| 2026-04-27 | Added §9 "Adoption Stages" (capture discipline → agent-assisted triage → bounded autonomous, with mapping to automation levels) and §10 "Relationship to Repo-as-OS Frameworks" (abstract knowledge-ops ↔ work-flow primitive mapping; explicit out-of-scope list). Renumbered the previous §9 / §10 to §11 / §12 and updated the kb-operator cross-reference accordingly. Reference version aligned to 5.4.0 |
| 2026-04-26 | Added the operating-model pointer and the optional `delivery` / `operations` feature families, including standard file formats for briefs, specs, release records, and incident records |
| 2026-04-25 | v5.2.0 release alignment — version bumped to track the kb-management trigger expansion and the kb-setup goal-oriented question-flow rework; structural contracts in this reference are unchanged |
| 2026-04-25 | Clarified the onboarding entry points, separated layer role from contributor-scoped visibility, and documented the automation-level contract directly beside `.kb-config/automation.yaml` |
| 2026-04-25 | Concept-audit follow-up: the §10 harness matrix now records the "rules-only" and "not feasible" buckets the README lists, so the reference and glossary stay aligned |
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
