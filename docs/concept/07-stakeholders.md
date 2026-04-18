# Stakeholders

> **Version:** 0.1 | **Last updated:** 2026-04-18

A lightweight people map in `references/foundation/stakeholders.md`. **Not a CRM** — just enough information for the agent to suggest who to involve when a decision or a topic update touches specific people.

## Format

```markdown
# Stakeholders

| Person | Role | Cares about | Reach via |
|--------|------|-------------|-----------|
| @alice | Architect | Backend architecture, trust model, API design | Slack, team KB |
| @bob | Researcher | Incident agents, pricing, user research | Slack, team KB |
| @carol | Marketing | Positioning, website, go-to-market | Slack, team KB |
| @dave | Leadership | Strategic direction, OKRs | Email, 1:1 meetings |
```

## Rules

- Keep it to people you **actively interact with on KB topics** — not an org chart.
- Updated during onboarding and when new collaborators appear in team/org KBs.
- The `Reach via` column can be any channel identifier: Slack, email, meeting, issue comment, chat thread.

## How the Agent Uses It

| When | Agent behavior |
|------|----------------|
| A decision involves unresolved stakeholder input | Suggests *"Set up meeting with @alice"* or *"Message @alice about decision D-…"* |
| A topic update might interest specific people | Suggests *"Notify @alice?"* |
| `/kb start-day` detects `Waiting` items | Shows who to follow up with and how |
| `/kb digest team` finds a new contributor | Offers to add them to `stakeholders.md` |

## Context Cost

~30 lines. Loaded only when decisions or TODOs reference people. Never a bottleneck.

## In Team and Org-Unit KBs

Team and org-unit KBs do **not** maintain a central stakeholders file — RACIs on decisions and TODOs already capture who's involved for each piece of work. The personal KB's `stakeholders.md` is the canonical place for the user's own mental model of their network.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §3g |
