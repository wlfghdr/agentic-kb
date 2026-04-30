---
name: kb-roadmap
description: Reconcile planning-truth sources against delivery reality. Ingests ≥1 plan source (ticket export, milestone markdown, OKRs) and ≥1 delivery source (git repository, ADR set, release log), runs a five-tier correlation ladder, detects mismatches, and emits a living roadmap artifact in Markdown, HTML, and JSON. Triggered by `/kb roadmap` and roadmap-reconciliation phrases.
version: 0.2.0
status: draft
triggers:
  - "/kb roadmap"
  - "roadmap synthesis"
  - "product roadmap"
  - "phase roadmap"
  - "now next later"
  - "roadmap presentation"
  - "customer-value roadmap"
  - "plan vs delivery"
  - "plan delivery reconciliation"
  - "deviation digest"
  - "roadmap digest"
tools: []
requires:
  - kb-management
author: agentic-kb contributors
homepage: https://github.com/wlfghdr/agentic-kb
license: Apache-2.0
---

# Skill: KB Roadmap

Organizations always have **at least two sources of planning truth** — tickets and the repository, milestones and delivery, OKRs and commits. They drift. Manual reconciliation is expensive and always stale. This skill closes the loop: it ingests plan + delivery, correlates them across a five-tier ladder, and produces a roadmap artifact that says what is planned, what is delivered, and where the two disagree.

This skill is **vendor-neutral**. All vocabulary specific to a particular tracker, repository host, or organization lives in the adopter's `.kb-config/layers.yaml` and `.kb-config/artifacts.yaml`, never in this skill.

The roadmap is a **product-management artifact**, not just a tracker report. Its job is to make planned customer/user value, confidence, delivery reality, and source traceability visible in one place.

At 5.1, the skill resolves its `roadmap:` block from the **active layer** entry in `.kb-config/layers.yaml` and can normalize read-only tracker inputs from that layer's `connections.trackers[]` declarations when legacy `roadmap.issue-trackers[]` entries are absent.

## When to invoke

Invoke whenever the user:

- Types `/kb roadmap` (optionally followed by `--since`, `--scope`, `--workstream`, `digest`, `sync`).
- Asks for a roadmap, status, or deviation report that spans both a planning tool and a repository.
- Asks *"what shipped vs. what was planned?"*, *"where does my roadmap drift from reality?"*, or *"which tickets have no code?"*

## The single command model

One entry point — `/kb roadmap` — with context-driven subcommands:

| Input | Action |
|---|---|
| `/kb roadmap` | Generate artifact with default scope + timeframe |
| `/kb roadmap --since YYYY-MM-DD` | Custom baseline |
| `/kb roadmap --scope <name>` | Scope to a workstream declared in `.kb-config/layers.yaml` |
| `/kb roadmap digest` | Pull latest plan + delivery state; compute delta; do not render |
| `/kb roadmap sync` | Propose plan-source updates based on delivery reality (dry-run default) |

Full reference: `references/command-reference.md`.

## Core rules (always apply)

1. **Every run writes three artifacts** — Markdown, HTML, JSON — with the same base name and timestamp. The JSON is authoritative; MD + HTML render from it.
2. **Correlation ladder has five tiers.** Stop at the first match; classify every matched pair by tier. Unmatched items on both sides become mismatch findings.
3. **Never silently drop an unmatched item.** It is either a delivery-without-plan, a plan-without-delivery, or a traceability gap — all three are first-class artifact entries.
4. **Deep-investigation matches (tier 4) are proposed, never final.** Emit them as `proposed, pending review`; the user confirms before downgrading to tier 1–3.
5. **Graceful degradation.** Artifact must be useful even when correlation rate is 0% — in that case, plan + delivery render side-by-side with an explicit "no matches found" banner.
6. **Read-only by default.** `digest` and plain `roadmap` never write to plan sources. `sync` emits a dry-run plan unless `--apply` is passed, and `--apply` requires a confirmation prompt. Tracker writes (comments, status, links) require the same `--apply` gate.
7. **Resume routing is deterministic.** When invoked with no work to do, run the conformance check + state assessment + ordered resume rules from `references/state-machine.md`. LLM judgment is not used to pick the next action.
8. **`/discuss` mode is write-free.** When the user message contains `/discuss`, do not regenerate artifacts, apply tuning, or write to trackers. Explain, propose, preview — see `references/discuss-mode.md`.
9. **Continuous config tuning is opt-in.** After each run, emit a tuning digest (zero-match filters, low-match filters, unreachable items, suspected noise). Apply only via `/kb roadmap tune` with explicit per-proposal confirmation. See `references/issue-trackers.md`.
10. **Log every run** to the adopter's `.kb-log/YYYY-MM-DD.log`.
11. **Zero vendor strings in skill code.** Tracker adapters, ticket-key patterns, phase names, status mappings, correlation rules, and styling all come from config.
12. **Journeys are ground truth when declared.** If the scope has `journey-refs`, every **non-infrastructural / non-foundational** item is cross-checked against its cited journey step(s): items with broken citations, uncovered steps, and reality-vs-readiness drift all surface as first-class findings. Infrastructure, build, security-hardening, platform, and foundational work satisfy the rule via an explicit escape hatch (label, trailer, or ADR link — see `references/audit.md` R1). Authoring commands (`ideate`/`discuss`/`review`/`refine`) treat the journey as the third party in every critique. The journey is never silently updated by roadmap runs — drift findings offer a transition into `/kb journeys review` instead. See `references/journey-grounding.md`.
13. **The audit is the consistency gate.** `/kb roadmap audit` runs all 15 rules (mappings · timeline · scope · structural) and emits a triple-artifact report with an actionable correction per violation. It is the single sanctioned path to reconcile gaps across issues ↔ roadmap items ↔ journey steps. See `references/audit.md`.
14. **No roadmap artifact without timeline + status board.** The HTML must always include a quarter-axis timeline (section 02) and a phase-columned kanban status board (section 03), in that order. When data is thin, both sections degrade gracefully (empty quarters, empty columns) — they never disappear. See `references/html-template.md` for the full template contract.
15. **Presentation roadmap view is value-first.** When rendering a phase/lane roadmap for humans, aggregate noisy source inputs into lanes and phases, keep each lane to a small number of items per phase, and phrase each item as a customer/user value headline plus a second-line implementation detail. Do not use checkmarks for proposed work; checkmarks mean implemented or already true.
16. **Commitment status is explicit.** Roadmap items distinguish `draft`, `proposed`, `agreed`, `committed`, `in-delivery`, and `shipped` (or the adopter's mapped equivalents). The rendered artifact must make the confidence/commitment level visible so a draft alignment board is not mistaken for an approved plan.

## The correlation ladder

Apply in order. Stop at the first tier that matches. See `references/correlation-ladder.md` for details.

| Tier | Signal | Example |
|------|--------|---------|
| 1 | Direct key match | Ticket key in commit message, PR title, branch name, or PR body |
| 2 | Cross-reference graph | Ticket remote-links point at PR; PR body references ticket; git trailer asserts ticket |
| 3 | Temporal + textual heuristic | Ticket status change and commits overlap in time window, by same author, with title-token overlap above threshold |
| 4 | Deep investigation (LLM-assisted) | For still-unmatched items on both sides, produce a ranked candidate-match list with rationale; flag `proposed, pending review` |
| 5 | Mismatch finding | Remaining unmatched items classified into `delivered-unplanned`, `planned-undelivered`, `traceability-gap` |

## Directory contract (adopter's KB)

The skill writes into a **dedicated** `_kb-roadmaps/` folder at the adopter's KB root — a peer of `_kb-references/`, `_kb-decisions/`, `_kb-ideas/`, `_kb-tasks/`, not a subdirectory of reports. Roadmaps are a distinct primitive.

```
my-kb/
├── .kb-config/
│   ├── layers.yaml              # active layer declares roadmap: and optional connections:
│   └── artifacts.yaml           # declares html-template + brand assets
├── _kb-roadmaps/                # dedicated root (configurable via roadmap.output-dir)
│   ├── <workstream>/           # per-workstream detail view
│   │   ├── roadmap-YYYY-MM-DD.{md,html,json}
│   │   └── status-YYYY-MM-DD.{md,html,json}
│   ├── exec/                   # cross-workstream roll-up (C-level)
│   │   └── roadmap-exec-YYYY-MM-DD.{md,html,json}
│   ├── index.html              # auto-generated; links to latest per scope
│   └── archive/                # older than retention-days
├── _kb-references/findings/      # mismatch findings land here (opt-in)
└── .kb-log/YYYY-MM-DD.log
```

## Two views

**Detail view** (per workstream): full sections A–G — ticket + commit detail, correlation audit. Audience: the team driving the workstream.

**Roll-up view** (exec / C-level): sections X1–X7 — portfolio state, momentum, risks, shifts, scope changes, decisions needed, next-period focus. No commit-level detail. Audience: leadership.

Declare scopes in the active layer's `.kb-config/layers.yaml` entry under `roadmap.scopes`. Default: every workstream gets a detail scope; adopters add one `kind: roll-up` scope per leadership rhythm.

See `references/folder-layout.md` for the full contract.

## Roadmap communication contract

When `/kb roadmap` renders a presentation-oriented roadmap view, it applies these generic communication rules:

| Rule | Contract |
|------|----------|
| Phase clarity | Use adopter-configured phases, but provide a concise legend that separates past truth, active work, proposed scope, later follow-up, and strategic direction. |
| Lane aggregation | Group source items into a small set of product or workstream lanes. Dense ticket lists stay in the appendix / JSON, not in the board. |
| Value headline | The first line answers: what does a user, customer, operator, or stakeholder get that they did not get before? |
| Detail line | The second line explains what/how: tracker cluster, implementation mechanism, dependency, or source basis. |
| Draft callout | If the run is synthesis-only, mark the artifact as draft / not agreed and name what would make it agreed. |
| Implemented marker | Use checkmarks only for implemented or already-true capabilities verified by delivery sources or accepted docs. |
| Traceability | Every visible roadmap item keeps source refs in JSON and appendix even when the board text is deliberately short. |

The default phase labels are generic and may be renamed in config: `done`, `now`, `next`, `later`, `future`. The renderer may expose a `now / next / later` presentation mode, but the JSON sidecar keeps the canonical phase and commitment fields.

## Configuration contract

See `references/config-schema.md`. Minimum adopter config in the active layer entry of `.kb-config/layers.yaml`:

```yaml
layers:
  - name: alice-personal
    path: .
    connections:
      trackers:
        - name: jira-export
          kind: jira
          export-dir: ../exports/jira
    roadmap:
      default-scope: <workstream-name>
      default-timeframe: week          # week | month | quarter | since:DATE | range:A..B
      output-dir: _kb-roadmaps
      scopes:
        <workstream-name>:
          kind: detail
      correlation:
        ticket-key-pattern: "[A-Z]+-\\d+"
        branch-prefixes: [feature/, fix/, chore/]
        trailer-keys: [Ticket, Issue, Jira]
        deep-investigation: true
      mismatch-findings:
        route-to: _kb-references/findings
        min-loc-threshold: 20
        stalled-after-days: 14
```

Brand + styling live in `.kb-config/artifacts.yaml`:

```yaml
html-template:
  base: kb-roadmap/templates/roadmap.html
  tokens: neutral            # or a path to a tokens file
  logo:                       # optional SVG in header, respects theme
    light: ""
    dark: ""
  themes: [light, dark, auto]
```

## Artifact sections (MD and HTML mirror each other)

All sections are **mandatory**. Empty sections render with an explicit "no items" note.

| Section | Content |
|---------|---------|
| **A. Plan baseline** | All plan items in scope, grouped by the configured `hierarchy` |
| **B. Delivery baseline** | All delivery signals in scope (commits, PRs, tags, ADRs) |
| **C. Correlation matrix** | Matched pairs grouped by ladder tier; counts per tier |
| **D. Delta since baseline** | Items newly opened, changed, merged, or shipped since `--since` |
| **E. Mismatch findings** | `delivered-unplanned` · `planned-undelivered` · `traceability-gap` · `journey-uncovered` · `journey-citation-broken` · `journey-reality-mismatch` |
| **F. Forward plan** | Plan items in status `next`/`in-progress`, kanban view, plus highest-impact uncovered journey steps as candidate-next-work |
| **G. Decisions needed** | Cross-reference to `_kb-decisions/` + suggested new decisions from gaps, including journey-drift decisions |

## Output contract

Every response:

1. **What I did** — one short statement.
2. **Where it went** — paths to the three emitted artifacts.
3. **Correlation summary** — items matched per tier + mismatch counts.
4. **Suggested next steps** — 1–3 concrete follow-ups (confirm tier-4 matches, open decisions for gaps, adjust plan-source).

## Safety rules

- **Never push to plan sources without explicit `--apply`.** Even then, require confirmation.
- **Never include raw credentials or tokens** in artifact output — scrub before render.
- **Never fetch external URLs** beyond declared source paths without informing the user.
- **Never block on missing data** — degrade and surface the gap in the artifact itself.

## Adapter contract

Source adapters are declared by name in config. The skill ships with a minimum neutral set; adopters add more by dropping a Python module under `scripts/adapters/` that exports a `load(config) -> list[Item]` function.

Shipped adapters:

| Name | Kind | Reads |
|------|------|-------|
| `ticket-export-markdown` | plan | a directory of markdown files with YAML frontmatter (Program/Package/Item hierarchy) |
| `milestone-markdown` | plan | `*.md` files with a `## Milestones` heading |
| `git-repo` | delivery | a git checkout — commits, PRs via GitHub CLI, tags, ADR glob |
| `release-log` | delivery | a `CHANGELOG.md` or `RELEASES.md` |

See `references/adapters.md`.

## References (load on demand)

- `references/correlation-ladder.md` — the five tiers, in depth
- `references/adapters.md` — source adapter contract and shipped set
- `references/issue-trackers.md` — **bidirectional tracker model** (read + write + continuous tuning)
- `references/phase-gates.md` — generic phase pipeline for plan items (`idea` → `defined` → `committed` → `in-delivery` → `shipped`)
- `references/state-machine.md` — inline state markers + deterministic resume routing
- `references/discuss-mode.md` — `/discuss` contract (no writes, propose-only)
- `references/authoring-commands.md` — `ideate` (creative), `discuss` (devil's advocate), `review` (challenge + create), `refine` (implementation plan)
- `references/mismatch-findings.md` — classification rules, noise filters, routing
- `references/journey-grounding.md` — journeys as reference + review lens + consistency check for every roadmap run
- `references/audit.md` — `/kb roadmap audit`: 15 rules across mappings / timeline / scope / structural, with offered corrections
- `references/html-template.md` — generated HTML contract: required sections (timeline + kanban are mandatory), derivation rules, adopter customization points
- `references/config-schema.md` — full `.kb-config/layers.yaml` `roadmap:` block
- `references/artifact-contract.md` — MD/HTML/JSON output specs
- `references/folder-layout.md` — `_kb-roadmaps/` layout + detail/roll-up views
- `references/command-reference.md` — full subcommand details

## Templates

- `templates/roadmap.md.hbs` — markdown report template
- `templates/roadmap.html.hbs` — HTML report template (neutral palette, dark/light toggle, optional logo slot, WCAG AA, print fallback)
- `templates/roadmap.json.schema.json` — JSON sidecar schema

## Status

This skill is **draft (v0.2.0)**. It is setup-proposed when the user's role, goals, sources, or desired outputs imply product-management roadmap work; adopters confirm the owning layer by declaring a `roadmap:` block on that layer in `.kb-config/layers.yaml`. Breaking changes are expected before v1.0.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-30 | Promoted roadmap work into the product-management surface: added value-first presentation rules, draft/agreed/shipped commitment visibility, setup-proposed status, and broader natural-language triggers | Product-management surface integration |
| 2026-04-25 | Aligned the draft roadmap contract with the shipped 5.1 behavior: the active layer owns the `roadmap:` block, `connections.trackers[]` can seed read-only tracker inputs, and the examples no longer imply the retired top-level shape | v5.1.0 closeout release |
