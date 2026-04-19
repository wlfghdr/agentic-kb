# Example: Day in the Life

> **Version:** 0.1 | **Last updated:** 2026-04-18

An illustrative walkthrough of a single day for a user named Alex, a principal engineer working on an observability platform. Alex has a personal KB, two team KBs, and consumes company strategy materials as they're published. The examples below are **not normative** — they show what the system feels like in practice.

## 07:55 — Workspace open

Alex opens the workspace folder in their editor. The `/kb` slash command is registered by the installed skill.

## 08:00 — Morning briefing

```
Alex: /kb start-day

Agent:
Good morning. Here's your briefing:

📋 Focus (from .tasks/focus.md):
  1. Finalize deployment-strategy position paper → promote to team
  2. Schedule architecture review with @alice
  3. Review platform backlog for sprint alignment

⚖️ Open Decisions (.decisions/active/):
  • D-2026-04-15: Progressive-delivery model (due Apr 30, status: under-discussion)
  • D-2026-04-18: Coordination model (due Apr 25, status: gathering-evidence)

🆕 New signals since yesterday:
  • Team KB (platform): @alice added architecture-v9-skeleton.md (3 new files)
  • Input pending: .inputs/2026-04-17-leadership-feedback.md (unprocessed)

📊 Workstreams:
  • reliability:   coordination paper needs evidence (D-2026-04-18)
  • platform:      progressive-delivery stalled — waiting on @bob's analysis
  • product-strategy: quiet — no new signals

💡 Suggested next steps:
  1. Digest @alice's v9 update — may have evidence for D-2026-04-18 (/kb digest team)
  2. Process leadership feedback (/kb review)
  3. Message @bob about the progressive-delivery analysis — decision due in 12 days

Shall I start with the team digest?
```

## 09:30 — A new input

Alex reads an interesting paper on coordination protocols, pastes the URL:

```
Alex: /kb https://example.org/papers/coordination-patterns — interesting paper on agent coordination

Agent: [reads paper, applies the evaluation gate]

Captured as finding: references/findings/2026-04-18-coordination-patterns.md
Workstream: reliability
Gate: 4/5 — strengthens deployment-strategy topic, informs D-2026-04-18, actionable, durable signal.
Decision impact: provides evidence for D-2026-04-18 (coordination model) — supports option (b).
Added to backlog: "Update deployment-strategy with coordination patterns"
TL;DR: Paper proposes a 3-phase coordination protocol for multi-agent systems...

💡 Next steps I can help with:
  1. Update the deployment-strategy topic with this evidence (/kb update-topic deployment-strategy)
  2. Advance decision D-2026-04-18 to "proposed" with this evidence
  3. Message @alice — this is relevant to their architecture work
  4. 🎤 Your backlog has "Present governance framework" — want me to draft a presentation?
```

## 11:15 — Process leadership feedback

```
Alex: /kb review

Agent: Found 1 unprocessed input: .inputs/2026-04-17-leadership-feedback.md

[applies the gate per item]

• 2026-04-17-leadership-feedback.md
  Gate: 3/5 — informs product-strategy topic + actionable.
  Finding: references/findings/2026-04-17-leadership-feedback-distilled.md
  Topic update: product-strategy.md (added "leadership wants Q3 focus on error budgets")
  TODOs added:
    - Respond to leadership with a one-pager by Thursday
    - Update Q3 product-strategy doc

💡 Next steps:
  1. Generate a one-pager? (/kb report product-strategy --for leadership --kind one-pager)
  2. Promote the product-strategy topic to the product-strategy team KB?
```

## 14:00 — Generate a presentation

Alex has the "Present governance framework" task on the backlog:

```
Alex: /kb present governance-framework

Agent: Generating presentation from references/topics/governance-framework.md...

Created: references/reports/governance-framework-v1.0.html
  - 7 slides: Problem → Pattern → Mechanism → Evidence → Proposal → Next Steps → Appendix
  - Intro slide: "Governance Framework — v1.0 · 2026-04-18" (subtle watermark)
  - Appendix: Changelog (v1.0: initial generation from topic file)
  - Sources: 3 findings, 1 decision outcome
  - Themes: light + dark embedded; toggle in top-right
  - CI-validated HTML: self-contained, accessibility AA passes.

💡 Next steps:
  1. Review and adjust the narrative — I can iterate if you paste notes back.
  2. Share with @alice before the architecture review.
  3. GitHub Pages is enabled — want me to publish it and update the index?
```

## 18:00 — Evening wrap

```
Alex: /kb end-day

Agent: Day summary:
  ✅ Captured 2 findings (coordination-patterns, leadership-feedback-distilled)
  ✅ Digested team KB (@alice v9, @bob pricing)
  ✅ Updated todo (2 done, 2 new in backlog)
  ✅ Generated governance-framework-v1.0.html presentation
  📝 Uncommitted changes: 7 files in personal KB

Committing: "2026-04-18: 2 findings, team digest, presentation v1.0, todo update"

Branch protection detected on main. Opening a PR instead:
  PR #42: https://github.com/<user>/<repo>/pull/42
  CI: pending — will ping when green.

💡 Next steps:
  1. Follow up with @alice once the PR is green (their turn on D-2026-04-18).
  2. Tomorrow's focus will start with: "Finalize deployment-strategy position paper."
```

## Friday 15:00 — Weekly summary

```
Agent (scheduled): /kb end-week

Weekly summary (2026-04-14 → 2026-04-18):

📊 Per-workstream progress:
  • reliability: 3 findings captured, D-2026-04-18 advanced to "proposed"
  • platform: 1 digest from team, progressive-delivery still blocked
  • product-strategy: 1 finding, topic refreshed

✅ Completed: 7 TODOs
📋 Open decisions: 2 active, 0 resolved this week
🎤 Presentations: 1 generated (governance-framework v1.0)

Promotion candidates:
  • findings/2026-04-18-coordination-patterns.md → team KB (high cross-reference potential)
  • topics/governance-framework.md → marketplace as kb-governance-framework skill (mature + generalizable)

Generated:
  • references/findings/2026-04-18-weekly-summary.md
  • references/reports/weekly-2026-W16.html (published to gh-pages)

💡 Next steps:
  1. Promote coordination-patterns to team? (/kb promote)
  2. Publish governance-framework as a marketplace skill? (/kb publish)
```

## The Point

Alex never opened a wiki, never drew a mind map, never categorized anything manually. The agent did the bookkeeping; Alex did the thinking. The KB stayed **small, current, decision-ready**.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §13 |
