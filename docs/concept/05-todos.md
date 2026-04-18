# TODOs

> **Version:** 0.1 | **Last updated:** 2026-04-18

A lean, focused task tracker. Designed for:

- **Small context windows** — active items are separated from history.
- **Machine-readable** — the agent can parse and update it.
- **Human-scannable** — plain Markdown, no special tooling.
- **Auto-fed** — KB processing, digests, and inputs create tasks automatically.

## File Structure: `todo/`

```
todo/
├── focus.md             # what you're doing NOW (max 3 items) — always in context
├── backlog.md           # what's queued up — moderate size
└── archive/             # done items — never loaded unless searching
    ├── 2026-04.md       # monthly archive files
    ├── 2026-03.md
    └── ...
```

**Why split it?** A single `todo.md` with all states grows unbounded. Completed items from three months ago waste context tokens every time the agent reads your tasks. Separating `focus.md` (~10 lines) from `archive/` (unlimited) keeps the agent fast and focused.

## `focus.md` — Always in Context

```markdown
# Focus

- [ ] Finalize deployment-strategy position paper → promote to team
- [ ] Schedule architecture review with @alice
- [ ] Review platform backlog for sprint alignment

## Waiting

- [ ] @alice: architecture v9 review
- [ ] @carol: positioning draft
```

**Rules**:

- Max **3** focus items.
- `Waiting` items track external blockers.
- When a focus item is done, the agent moves it to `archive/YYYY-MM.md` and pulls the next item from `backlog.md`.

## `backlog.md` — Next Up

```markdown
# Backlog

- [ ] Digest @bob's latest pricing analysis
- [ ] Update deployment-strategy topic with new evidence
- [ ] Respond to leadership feedback (inputs/2026-04-17-feedback.md)
- [ ] 🎤 Present governance framework at architecture review ← presentation trigger
```

**Rules**:

- Unordered.
- Items auto-added from KB processing.
- No limit.
- Only loaded when reviewing tasks or during `start-day`.

## `archive/YYYY-MM.md` — History

```markdown
# 2026-04 — Completed

- [x] 2026-04-17: Promoted coordination finding to team KB
- [x] 2026-04-16: Digested team KB contributions
- [x] 2026-04-15: Updated workstream digests
```

**Rules**:

- One file per month.
- Never loaded into context unless explicitly searching history.
- Auto-populated when items complete.

## TODOs in Team and Org-Unit KBs

Team (L2) and org-unit (L3) KBs have their own `todo/` with the same structure, but **with RACIs**:

```markdown
# Focus (Team)

- [ ] **R**: @alice | **A**: @bob | Finalize API versioning proposal
- [ ] **R**: @carol | **A**: @dave | Review pricing counter-analysis
```

RACI rules (required outside personal KB):

| Letter | Role |
|--------|------|
| **R** — Responsible | Who does the work |
| **A** — Accountable | Who approves / owns the outcome |
| **C** — Consulted | Who provides input (optional, listed in decision file) |
| **I** — Informed | Who needs to know when done (optional) |

The agent cross-references team/org TODOs with personal focus items when you're the R or A.

## Auto-Feed Sources

| Trigger | Creates in | Example |
|---------|-----------|---------|
| New unprocessed input in `inputs/` | `backlog.md` | "Review: feedback.md" |
| Team digest action items | `backlog.md` | "Respond to @alice's proposal" |
| Stale topic (>30 days untouched) | `backlog.md` | "Refresh: deployment-strategy.md" |
| `/kb` capture with action implied | `backlog.md` | "Integrate finding into [topic]" |
| Open decision needs evidence | `backlog.md` | "Gather evidence for D-2026-04-18" |
| Open decision needs stakeholder input | `backlog.md` | "Schedule meeting: @alice re: trust model" |
| Decision resolved | `archive/` | Related TODOs auto-completed |
| Presentation-worthy TODO detected | suggestion | "Generate presentation for upcoming pitch?" |

**Never auto-delete**: only the user or an explicit `/kb todo done` marks items complete.

## Presentation-Worthy TODO Detection

When a backlog or focus item contains keywords like *"present"*, *"pitch"*, *"demo"*, *"share"*, *"slide"*, *"meeting prep"*, the agent adds a 🎤 marker and suggests generating an HTML artifact. See [../spec/html-artifacts.md](../spec/html-artifacts.md).

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §4 |
