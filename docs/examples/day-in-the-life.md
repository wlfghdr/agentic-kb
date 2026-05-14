# Example: Day in the Life

> **Version:** 5.0.0 | **Last updated:** 2026-05-10

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

## Three other roles, same primitives

The same shapes serve very different days. These compact scenes show how a product manager, an engineering manager, and an on-call engineer use the same `/kb` surface that Alex used above.

### Product manager — Priya

```text
09:00  Priya: /kb start-day
       Agent: surfaces 2 open decisions waiting on her, 1 customer-feedback
              finding captured overnight, and a stale roadmap-change report
              from last week.

10:30  Priya: /kb https://transcript/customer-mid-market-call
       Agent: 4/5 — captured as finding, updated the onboarding journey's
              step 3 readiness from "ready" to "needs evidence", proposed
              a new brief on activation friction.

13:00  Priya: /kb brief activation-friction
       Agent: scaffolds _kb-delivery/briefs/2026-05-14-activation-friction.md
              with problem, why-now, scope, non-goals, and success signals;
              prompts for the outcome window.

16:00  Priya: /kb report roadmap-change platform
       Agent: opens roadmap-change source at
              _kb-references/reports/sources/platform/roadmap-change-platform-2026-05-14.md,
              renders the HTML, names the accountable roadmap owner for approval.
```

### Engineering manager — Eun-ji

```text
08:30  Eun-ji: /kb start-day
       Agent: 3 reports with open blockers, 1 decision overdue (D-2026-05-08
              missing RACI), incident I-2026-05-13-payment-latency resolved
              overnight with 2 follow-up tasks unowned.

11:00  Eun-ji: /kb decide hire-vs-internal-rotation
       Agent: opens the decision with explicit stakeholders, due date Friday,
              status gathering-evidence.

14:30  Eun-ji: /kb note meeting weekly-product-sync
       Agent: meeting note opens; attendees prompted; agent suggests linking
              to the active brief and the open decision.

15:30  Eun-ji: /kb report status engineering-org
       Agent: status source written under
              _kb-references/reports/sources/engineering-org/status-engineering-org-2026-05-14.md;
              flags 1 workstream with last-reviewed > 14 days as stale.

17:30  Eun-ji: /kb end-day
       Agent: 1 decision moved to under-discussion, 2 follow-up tasks
              archived after explicit confirmation, day summary committed.
```

### On-call SRE — Marek

```text
03:14  Pager fires.
       Marek: /kb incident payment-latency
       Agent: opens _kb-operations/incidents/2026/2026-05-13-payment-latency.md
              with severity prompt, owners, services. Marek picks sev-2,
              services=[payments, checkout].

03:18–05:42  Marek appends timeline entries as mitigations land.
             Agent keeps the record append-only after each update.

05:50  Marek: /kb incident resolve
       Agent: status moves to resolved; prompts for the post-incident retro
              window (recommended within 48 hours).

Next day:
14:00  Marek: /kb note retro payment-latency
       Agent: opens a retro note using the retro template;
              cadence=post-incident, period=2026-05-13 03:14–05:50;
              prompts to link the incident record.

14:45  Marek: /kb note end
       Agent: 3 action items in "What we will change" surfaced as proposed
              tasks; 1 promoted as a decision (vendor SLA escalation);
              no false-convergence flag since commitments are tracked.
```

The point of these three scenes is not that PMs, EMs, and SREs do the same things — they don't. The point is that the same primitives (`brief`, `decide`, `note meeting`, `note retro`, `incident`, `report status`, `report roadmap-change`) compose into very different daily shapes without forcing role-specific commands.

## Shared artifact rhythm behind the scenes

In a team using roadmap and journeys seriously, Alex would usually keep three recurring shared artifacts in motion:

- a **status report** such as `_kb-references/reports/sources/platform/status-platform-2026-04-18.md` for what matters now,
- a **delivery report** such as `_kb-references/reports/sources/platform/delivery-platform-2026-04-18.md` for roadmap-vs-reality,
- and a **roadmap change report** such as `_kb-references/reports/sources/platform/roadmap-change-platform-2026-04-18.md` whenever the baseline itself moves.

That keeps the daily chat, the roadmap, the journeys, and stakeholder updates from drifting apart.

## The Point

Alex never had to manually maintain a wiki hierarchy. The agent handled the bookkeeping while the human kept control over meaning, audience, and promotion.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-14 | Added compact PM, EM, and on-call SRE scenes so the example covers the three non-engineer roles the operating model names alongside engineers. Introduced the post-incident retro flow in the SRE scene to exercise the new `/kb note retro [topic]` variant | Daily-reality gap audit across software-company roles |
| 2026-05-10 | Added the shared artifact rhythm connecting status, delivery, and roadmap-change reports | Adoption-oriented engineering pass |
| 2026-04-25 | Reworked the example for 5.0.0: anchor layer, named team layers, year-based finding paths, and explicit cross-layer promotion replaced the old fixed-ladder example | v5.0.0 flexible layer model |
| 2026-04-18 | Initial version | Extracted from source spec §13 |
