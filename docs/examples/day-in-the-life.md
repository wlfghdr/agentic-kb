# Example: Day in the Life

> **Version:** 5.0.0 | **Last updated:** 2026-04-25

An illustrative walkthrough of a single day for a user named Alex, a principal engineer working on an observability platform. Alex has one anchor layer, two shared team layers, and consumes company guidance from a consumer layer. The examples below are not normative; they show what the system feels like in practice.

## 08:00 — Morning briefing

```text
Alex: /kb start-day

Agent:
What I did: Checked Alex's anchor layer and prepared a read-only morning briefing.
Where it went: read _kb-tasks/focus.md, _kb-decisions/, declared layer pointers, and today's .kb-log.
Gate notes: n/a — briefing, not capture.
Suggested next steps:
  1. Digest team-observability — may have evidence for D-2026-04-18 (/kb digest team-observability)
  2. Process leadership feedback (/kb review)
  3. Message @bob about the progressive-delivery analysis
```

## 09:30 — A new signal

```text
Alex: /kb https://example.org/papers/coordination-patterns

Agent:
What I did: Captured the paper as an anchor-layer finding after fetching the external URL.
Where it went: wrote _kb-references/findings/2026/2026-04-18-coordination-patterns.md, updated the reliability topic, and refreshed index.html + dashboard.html.
Gate notes: 4/5 — externally fetched, informs D-2026-04-18, actionable, durable signal.
Suggested next steps:
  1. Promote this finding to team-observability
  2. Advance D-2026-04-18 with this evidence
  3. Start a meeting note before the architecture review
```

## 11:15 — Review local input

```text
Alex: /kb review

Agent:
What I did: Captured and distilled one local input, applied mutation.
Where it went: wrote _kb-references/findings/2026/2026-04-17-leadership-feedback-distilled.md, updated product-strategy.md, refreshed index.html + dashboard.html.
Gate notes: 3/5 — local-only source, actionable, informs a workstream topic.
Suggested next steps:
  1. Generate a one-pager with /kb report progress product-strategy
  2. Promote the topic to the product-strategy layer if the team needs it
```

## 14:00 — Team promotion

```text
Alex: /kb promote _kb-references/findings/2026/2026-04-18-coordination-patterns.md team-observability

Agent:
What I did: Promoted one anchor-layer finding to team-observability and completed the destination review.
Where it went: staged team-observability/alex/_kb-inputs/2026-04-18-coordination-patterns.md, wrote team-observability/alex/_kb-references/findings/2026-04-18-coordination-patterns.md, archived team-observability/alex/_kb-inputs/digested/2026/04/2026-04-18-coordination-patterns.md, refreshed team-observability/index.html + dashboard.html.
Gate notes: source gate 4/5, destination review confirmed team relevance and no secret or PII indicators.
Suggested next steps:
  1. Open a shared decision if the architecture review needs alignment
  2. Digest product-strategy if this affects roadmap framing
```

## 18:00 — Evening wrap

```text
Alex: /kb end-day

Agent:
Day summary:
  ✅ Captured 2 findings
  ✅ Promoted 1 finding to team-observability
  ✅ Updated 1 topic and 1 decision
  ✅ Refreshed dashboard.html and index.html in affected layers

Suggested next steps:
  1. Review the promoted finding with @alice tomorrow
  2. Use /kb report progress team-observability before the weekly sync
```

## The Point

Alex never had to manually maintain a wiki hierarchy. The agent handled the bookkeeping while the human kept control over meaning, audience, and promotion.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-25 | Reworked the example for 5.0.0: anchor layer, named team layers, year-based finding paths, and explicit cross-layer promotion replaced the old fixed-ladder example | v5.0.0 flexible layer model |
| 2026-04-18 | Initial version | Extracted from source spec §13 |
