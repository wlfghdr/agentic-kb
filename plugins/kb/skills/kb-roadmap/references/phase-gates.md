# Reference: phase gates for plan items

Plan items move through a generic pipeline. Phase markers are declared **inline in each plan item's markdown** (when the tracker exports to markdown) or computed from tracker status mapping (when the tracker is live).

## Generic phase pipeline

| Phase | Meaning | Typical gate criteria |
|---|---|---|
| `idea` | Captured, not yet shaped | Short title + problem statement |
| `defined` | Scope + success criteria written | Title, problem, success metric, rough size |
| `committed` | Approved for delivery, on the plan | Owner assigned, dependencies identified, in-quarter |
| `in-delivery` | Active work, has matching delivery signal | At least one tier-1/2 correlation match |
| `shipped` | Delivered, verified | Delivery signal reached main/release, acceptance met |
| `archived` | Closed without shipping | Explicit reason (superseded, dropped, deferred) |

These are **defaults**. Adopters override in `.kb-config/layers.yaml` with their own phase names and criteria.

## Status-to-phase mapping

The skill maps each tracker's native status into the generic phase pipeline via config:

```yaml
roadmap:
  phases:
    idea:        [Open, Backlog, New]
    defined:     [Ready, Refined, "To Do"]
    committed:   [Committed, Planned, "Sprint Ready"]
    in-delivery: [In Progress, "In Review", Blocked]
    shipped:     [Done, Closed, Released]
    archived:    ["Won't Do", Duplicate, Rejected]
```

When a tracker's raw status is unknown, the skill emits a warning and skips phase classification for that item (instead of guessing).

## Inline phase markers (markdown trackers only)

When the tracker adapter is markdown-based (`ticket-export-markdown`), the skill can optionally write phase transition timestamps into the plan item's markdown:

```markdown
<!-- phase: defined @ 2026-04-21T12:00:00Z -->
<!-- phase: committed @ 2026-04-28T09:15:00Z -->
```

Markers are append-only. The current phase is the newest marker. This lets any other tool (grep, CI, a different skill) read phase state without loading the skill.

## Gate criteria

Each phase declares required fields. Missing fields block the transition.

```yaml
roadmap:
  gate-criteria:
    defined:
      required-fields: [problem, success-metric, rough-size]
    committed:
      required-fields: [owner, in-period]
    in-delivery:
      required: [correlation-tier-1-or-2]
    shipped:
      required: [delivery-in-main, acceptance-met]
```

The skill checks criteria in `digest` mode and surfaces gate violations under section G. It never transitions a phase itself — adopters review and apply via `sync`.

## Roadmap view by phase

The forward-plan section (F) groups plan items by phase column instead of by priority or due date when `roadmap.forward-plan.group-by: phase` is set. This produces a pipeline-oriented kanban that mirrors delivery readiness rather than roadmap order.

## Why this is not VI-specific

The phase names are generic (`idea`, `defined`, `committed`, `in-delivery`, `shipped`, `archived`) and map onto any delivery pipeline — product increments, infrastructure changes, policy decisions, research items. Adopters with their own vocabulary rename phases in config without touching the skill.
