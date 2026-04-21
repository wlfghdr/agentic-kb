# Reference: the five-tier correlation ladder

The correlation engine matches plan items (tickets, milestones) to delivery signals (commits, PRs, tags, ADRs). It applies tiers in order and stops at the first match. Every matched pair records its tier for later auditing; every unmatched item flows to tier 5 (mismatch finding).

## Tier 1 — Direct key match

Signal: a stable identifier for a plan item appears verbatim in a delivery signal.

- Ticket key (config: `correlation.ticket-key-pattern`) appears in:
  - commit message (title or body)
  - PR title or body
  - branch name
  - tag name or release note
- GitHub issue/PR number appears in a ticket's description, comments, or remote-links field
- Milestone name appears in a tag or release title

Confidence: **high**. No human review required.

## Tier 2 — Cross-reference graph

Signal: plan and delivery items already link to each other, one hop away.

- Ticket has a remote-link (or field) pointing at a PR URL
- PR body contains `Fixes <ticket>` / `Closes <ticket>` / `Part of <ticket>`
- Commit trailer asserts a ticket via `correlation.trailer-keys`
- A tracker-native link from ticket to epic/milestone and the milestone maps to a repo tag

The engine walks this one-hop graph. For example: ticket A → PR B → commits C..D propagates A ↔ C..D.

Confidence: **high**. No human review required.

## Tier 3 — Temporal + textual heuristic

Signal: inferred correlation when neither key nor cross-reference exists.

Applied when all of the following are true for a candidate `(plan-item, delivery-item)` pair:

1. Delivery item's author appears in plan item's assignee/owner field at any point in the window
2. Plan item's status changed (or delivery item landed) within a configurable temporal window (default: 7 days)
3. Title-token overlap between plan item and delivery item exceeds threshold (default: Jaccard ≥ 0.35 on lowercased non-stopword tokens)

Confidence: **medium**. Record with tier marker; no mandatory review, but flagged for audit.

## Tier 4 — Deep investigation (LLM-assisted)

Signal: an LLM pass over still-unmatched items produces ranked candidate matches with rationale.

The pass runs only on items not matched by tiers 1–3. Inputs per candidate: plan item summary + description, delivery item title + first 500 chars of body, author, timestamps. The model returns a ranked list of candidate matches with a rationale sentence.

Outputs are written as `proposed, pending review`. They do **not** count toward the "matched" total until confirmed by a human in a review pass (`/kb roadmap --review-tier-4`).

Confidence: **speculative**. Never auto-final.

## Tier 5 — Mismatch finding

Any item unmatched after tier 4 is classified:

| Class | Definition | Action |
|---|---|---|
| `delivered-unplanned` | Delivery item with no matching plan item | Render in section E; optionally route to `_kb-references/findings/` |
| `planned-undelivered` | Plan item with no matching delivery item and status ≠ closed | Render in section E; flag for plan-source review |
| `traceability-gap` | A plan item and a delivery item likely related (per tier-3 signals just below threshold) but never explicitly linked | Render in section E; suggest adding a cross-reference |
| `stalled-in-progress` | Plan item in `in-progress` state for > `stalled-after-days` with no matching delivery activity | Render in section E as risk |

## Noise filters (config)

To keep section E readable, the engine applies filters before routing to mismatch findings:

- `mismatch-findings.min-loc-threshold`: delivered-unplanned commits smaller than this LoC count are suppressed (default: 20)
- `mismatch-findings.ignore-paths`: glob patterns; commits touching only ignored paths (e.g. docs, tests, deps) are suppressed (default: includes common lockfiles and CHANGELOG patterns)
- `mismatch-findings.min-ticket-priority`: planned-undelivered items below this priority are suppressed

## Audit trail

Each match records:

```json
{
  "plan_id": "...",
  "delivery_id": "...",
  "tier": 2,
  "signal": "pr-body-fixes-ticket",
  "confidence": "high",
  "proposed": false,
  "reviewed_by": null,
  "timestamp": "2026-04-21T14:30:00Z"
}
```

The JSON sidecar preserves the full ladder output so future runs can diff correlation quality over time.
