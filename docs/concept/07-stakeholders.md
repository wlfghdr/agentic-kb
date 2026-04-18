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

## Auto-Update Rule

The stakeholder map is a **living document**. The agent updates it whenever processing reveals evidence of relevance changes:

| Signal detected during processing | Agent action |
|------------------------------------|-------------|
| New person mentioned 3+ times in findings (within 14 days) | Suggest adding to `stakeholders.md` with inferred role |
| Existing stakeholder mentioned in a new team/org-unit context | Suggest updating their "Cares about" column |
| Stakeholder not mentioned for 60+ days | Flag as potentially stale in `end-week` |
| Team restructure signal (new org unit, team rename, role change) | Suggest updating role + org affiliation |
| New blocker or decision involving an unknown person | Suggest adding immediately with "Reach via" TBD |
| Digest from L2/L3 reveals new RACI assignments on the user | Suggest adding the accountable person |

Rules:
- **Never silently update** — always show the proposed change and ask for confirmation.
- Updates are logged as `stakeholder-update` operations in the daily log.
- The stakeholder map is included in the weekly report's Stakeholder Map slide if any changes occurred that week.
- At team/org-unit level, stakeholder changes propagate as suggestions to personal KBs (not forced).

## Context Cost

~30 lines. Loaded only when decisions or tasks reference people. Never a bottleneck.

## In Team and Org-Unit KBs

Team and org-unit KBs do **not** maintain a central stakeholders file — RACIs on decisions and tasks already capture who's involved for each piece of work. The personal KB's `stakeholders.md` is the canonical place for the user's own mental model of their network.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §3g |
