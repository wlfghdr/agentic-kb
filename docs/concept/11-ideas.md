# Ideas — Incubation & Development

> **Version:** 0.1 | **Last updated:** 2026-04-18

Ideas are the bridge between raw signal (findings) and curated positions (topics). A finding that has novelty value or opens new possibilities but isn't yet ready to shape a topic becomes an **idea** — a first-class object with its own lifecycle, tracked and developed over time.

## Why Ideas Exist

The evaluation gate answers "should we keep this?" but not "should we develop this further?" Findings are immutable snapshots. Topics are settled positions. Between them is a gap: observations with potential that need sparring, evidence gathering, and deliberate development before they can inform a position.

Ideas fill this gap. They are the KB's incubation layer.

## Lifecycle

```
seed  →  growing  →  ready  →  shipped | archived
```

| Status | Meaning |
|--------|---------|
| `seed` | Captured — raw potential, no development yet |
| `growing` | Under active development — evidence gathering, sparring, refinement |
| `ready` | Mature — ready to inform a topic update, a decision, or a promotion |
| `shipped` | Acted on — absorbed into a topic, promoted, or published |
| `archived` | Parked — not relevant now, preserved for future reference |

## File Layout

```
ideas/
├── I-2026-04-18-agent-memory-patterns.md     # active idea
├── I-2026-04-15-cross-team-digest-model.md   # active idea
└── archive/                                   # shipped + archived ideas
    └── I-2026-03-28-deprecated-approach.md
```

- **Format**: `I-YYYY-MM-DD-slug.md` — prefixed with `I-` to distinguish from findings (`YYYY-MM-DD-slug.md`) and decisions (`D-YYYY-MM-DD-slug.md`).
- **Location**: `ideas/` at KB root (same level as `decisions/`, `tasks/`).
- **Team/org ideas**: in team/org KBs, ideas live inside the contributor or team directory (`<name>/ideas/`).

## Idea File Format

```markdown
---
id: I-2026-04-18-agent-memory-patterns
status: growing
themes: [knowledge-management, agent-architecture]
sparked-by: findings/2026-04-18-memory-research.md
---

# Idea: Agent Memory Patterns for KB Operations

## The Idea

One to three sentences capturing the core assertion.

## Why This Matters

What changes if this idea is right? What's at stake?

## Evidence & Signals

- finding/2026-04-18-memory-research.md — initial research
- finding/2026-04-20-competitor-analysis.md — competitive landscape

## Assumptions (to test)

- Assumption A — not yet validated
- Assumption B — partially validated by [evidence]

## Open Questions

- Question 1?
- Question 2?

## Development Log

| Date | What happened |
|------|--------------|
| 2026-04-20 | Added competitor analysis evidence |
| 2026-04-18 | Sparked from memory research finding |
```

## Annotations on Ideas

Follow-up observations are added as **blockquote annotations** — the original idea text is never edited except for status transitions and the development log:

```markdown
> **2026-04-20**: The competitor analysis strengthens assumption A.
> This shifts the idea from "interesting" to "we should prototype."
```

This preserves the reasoning chain. The development log tracks milestones; annotations capture the thinking between milestones.

## How Ideas Interact with Other Objects

| Object | Relationship |
|--------|-------------|
| **Findings** | Spark ideas (via `sparked-by`). New findings can strengthen or weaken an idea. |
| **Topics** | When an idea reaches `ready`, it informs a topic update. The idea's `shipped` status links to the topic changelog entry. |
| **Decisions** | An idea at `ready` may trigger a new decision ("should we adopt this approach?"). |
| **Tasks** | Development steps become tasks in `tasks/backlog.md` linked to the idea. |
| **Workstreams** | Ideas are routed to workstreams via their `themes`. |

## `/kb develop` — The Sparring Flow

When the user invokes `/kb develop [idea]`, the agent plays **sparring partner**:

1. **Build internal model** (before saying anything):
   - Core assertion — what is this idea really claiming?
   - Assumptions — what must be true for this to work?
   - Contradictions — what existing topics/decisions does this challenge?
   - Failure modes — how could this go wrong?
   - Gaps — what evidence is missing?

2. **Socratic questioning** — ask the user to defend the weakest assumption.

3. **Devil's advocate** — present the strongest counter-argument.

4. **Convergence** — when the user is satisfied, summarize:
   - Updated assertion (may have shifted)
   - Validated/invalidated assumptions
   - Concrete next steps (evidence to gather, people to consult)
   - Status recommendation (stay `growing`, move to `ready`, or `archive`)

5. **Record** — append to the development log and add annotations.

## When Does an Idea Get Created?

- **Explicitly**: `/kb idea [text]` — creates a seed idea.
- **From capture**: when the evaluation gate scores 1–2 but detects novelty potential ("this doesn't strengthen an existing position, but it opens a new direction"), the agent offers to create an idea instead of (or in addition to) a finding.
- **From audit**: `/kb audit` may detect a cluster of findings that suggest an unformalized idea.

## Pattern Detection

When ≥3 findings converge on a theme that has no corresponding topic or idea, the agent flags a **pattern alert** and offers to create an idea. This is the "3+ signal convergence" heuristic — borrowed from signal processing: isolated observations are noise, but clustered observations indicate something worth developing.

## Freshness

- Ideas in `seed` status for >14 days without development → flagged in `/kb audit`.
- Ideas in `growing` status for >30 days without a development log entry → flagged.
- The agent surfaces stale ideas in `start-week`.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version — Ideas as first-class incubation objects | Research: ai-opm-workspace, agentic-enterprise signal lifecycle |
