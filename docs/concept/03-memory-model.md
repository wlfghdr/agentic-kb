# Memory Model — Findings, Topics, Foundation

> **Version:** 0.1 | **Last updated:** 2026-04-18

Every personal and team KB has three kinds of memory, each with a distinct purpose and context-cost profile. Understanding which is which is the single most important thing about navigating the KB.

## Three Memory Types

| Type | Purpose | Lifecycle | Context cost |
|------|---------|-----------|--------------|
| **Historical** (`references/findings/`) | "What did I learn and when?" Evidence trail. | Created once, **never edited** | LOW — only recent ones loaded |
| **Topic** (`references/topics/`) | "What is my current position on X?" | **Updated in place**, carries inline changelog | MEDIUM — loaded when relevant |
| **Foundation** (`references/foundation/`) | Identity: who you are, what you care about | Rarely changes, carries inline changelog | LOW — loaded always |

## Historical Memory — `references/findings/`

Dated snapshots. Each finding is a single event: a paper you read, a meeting outcome, a distilled conclusion from one or more inputs.

```
findings/
  2026-04-18-coordination-patterns.md
  2026-04-17-feedback-from-leadership.md
  2026-04-15-initial-thesis.md
```

- **Format**: `YYYY-MM-DD-slug.md`.
- **Rule**: once written, a finding is **immutable**. Corrections go in a new finding that references the old one.
- **Purpose**: audit trail. Answers "what did I know when?"
- **Used by**: topic updates cite findings as sources; digests summarize recent findings; the agent searches findings when re-deriving a position.

### Daily and weekly summaries are findings too

Two special kinds of finding are generated automatically by the rituals:

- **Daily summary** — created by `/kb end-day` as `references/findings/YYYY-MM-DD-daily-summary.md`. Captures the day's activity: findings, decisions, TODOs, promotions, skipped items, per-workstream progress.
- **Weekly summary** — created by `/kb end-week` (Friday 15:00 default) as `references/findings/YYYY-MM-DD-weekly-summary.md`. Aggregates the week's dailies + promotion and presentation candidates + staleness flags.

Both have a rendered HTML companion in `references/reports/` (see [../spec/html-artifacts.md](../spec/html-artifacts.md)). The markdown file is the source; the HTML is a presentation layer.

Because they follow the `YYYY-MM-DD-slug.md` finding format, they participate in all normal finding behavior — immutable, referenced by topics, surfaced by digests.

## Topic Memory — `references/topics/`

Living documents. One file per theme. Updated whenever a finding changes the position.

```
topics/
  service-reliability.md       ← current position on SLOs, error budgets, incident patterns
  deployment-strategy.md       ← current position on rollout risk, canary, progressive delivery
  knowledge-management-system.md
```

- **Format**: `topic-slug.md` — no date, always current.
- **Rule**: **one file per topic**. Never duplicate. If a theme emerges that doesn't fit, create a new topic.
- **Inline changelog required** (see below).
- **Used by**: the agent reads topics when processing related inputs; topics ground the "current position" for reports and presentations.

### When does a topic get its own file?

- **At setup**: the onboarding interview captures 3–5 initial themes; each becomes an initial topic file.
- **Organically**: when a finding doesn't fit any existing topic and ≥3 related findings have accumulated, the agent suggests creating a new topic.
- **On pruning**: if a topic hasn't been referenced or updated in ≥60 days, `/kb audit` flags it for archival to `references/legacy/`.

Rule of thumb: *if you'd need to explain your position to a colleague, it deserves a topic file. If it's a one-time observation, it's a finding.*

## Foundation Memory — `references/foundation/`

Rarely-changing identity files.

```
foundation/
  me.md            ← your identity, role, style preferences
  context.md       ← current working context, active priorities
  sources.md       ← index of durable references
  stakeholders.md  ← people map: who cares about what
  naming.md        ← optional: naming conventions you follow
```

- **Purpose**: gives the agent permanent context without re-explaining yourself.
- **Inline changelog required**. Because these files define your working identity, tracking *why* they changed matters more than when.
- **Used by**: loaded on every agent invocation. Keep it short.

## Inline Changelogs

Long-lived files (topics, foundation, and team output topics) carry a **changelog at the bottom** — under a final `---` separator, newest entry first:

```markdown
# Topic: Deployment Strategy

[... main content ...]

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Added progressive-delivery evidence | findings/2026-04-18-canary-study.md |
| 2026-04-10 | Revised rollback thresholds after incident | findings/2026-04-10-incident-retro.md |
| 2026-03-28 | Initial position — extracted from core-topics.md | — |
```

### Why inline, not just git log?

Git history shows *that* a file changed, but not *why* or *what triggered it*. The inline changelog links each revision to its source finding, making the reasoning chain traceable without leaving the file.

### Rules

- The changelog is always the **last section** (after a `---`).
- Newest entry first.
- Each entry: date, one-line description, source (link to a finding, team input, or a short note).
- The agent appends automatically on every update.
- When the agent only needs the current position, it reads up to the final `---` and skips the changelog to save tokens.

## How the Agent Keeps Context Small

| What it loads | When | Size |
|---|---|---|
| `foundation/me.md` + `context.md` | Always | ~200 lines |
| `todo/focus.md` | Always | ~10 lines |
| `decisions/active/*.md` (titles only) | On start-day | ~10 lines |
| Relevant `topics/*.md` | When processing related input | 1–2 files |
| Recent `findings/` | When digesting or auditing | Last 5–10 |
| `workstreams/<relevant>.md` | When routing workstream content | 1 file |
| `todo/backlog.md` | On explicit todo review | ~30 lines |
| `todo/archive/*` | Never (unless searching history) | 0 lines |
| `inputs/digested/*` | Never (unless re-processing) | 0 lines |
| Full decision file | When processing related input | 1 file |
| `decisions/archive/` | Only when referencing past decisions | 0 lines |
| `log/` (current + yesterday) | On start-day, status | 2 files |
| Older `log/` | Never (unless searching history) | 0 lines |

The structural rule is: **split by access pattern, not by topic**. Hot data (focus.md, foundation, current topics) stays tiny. Cold data (archives, old logs, old findings) stays on disk but out of context.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | v0.2 — added "Daily and weekly summaries are findings too" section | html-artifacts.md v0.2 |
| 2026-04-18 | v0.1 — initial version | Extracted from source spec §3b/3c |
