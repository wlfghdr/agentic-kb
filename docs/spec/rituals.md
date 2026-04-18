# Rituals

> **Version:** 0.1 | **Last updated:** 2026-04-18

Rituals are composed commands — they string together several primitive operations into a single, user-facing flow. They exist because knowledge work has rhythm: mornings, evenings, weekly closes.

## The Four Rituals

| Ritual | Command | When | Purpose |
|--------|---------|------|---------|
| Start day | `/kb start-day` | Morning | Briefing: what to focus on |
| End day | `/kb end-day` | End of workday | Wrap: commit, archive done, prep for tomorrow |
| Start week | `/kb start-week` | Monday | Planning: digest everything, set priorities |
| End week | `/kb end-week` | Friday 15:00 | Summary: promotion candidates, presentation prep |

Each ritual is fully specified in [commands.md](commands.md). This document specifies the **invariants** and **automation hooks**.

## Invariants

Every ritual MUST:

1. **Start with `/kb status`** — the ritual always reports the current state before acting.
2. **Read the log** — today's and yesterday's `log/` entries are always loaded.
3. **Respect the evaluation gate** — rituals don't bypass the gate. They just amortize the work.
4. **End with suggested next steps** — no ritual leaves the user with no path forward.
5. **Log the ritual invocation** — one log line per ritual with a summary.
6. **Regenerate live overviews** — `inventory.html`, `open-decisions.html`, `open-todos.html`, `index.html` are rebuilt at ritual end so the user's dashboard reflects the new state.

## Scheduling

Rituals can be scheduled via the harness's background automation (see [automation.md](automation.md)). Recommended defaults:

```yaml
# .kb-automation.yaml
schedules:
  start-day: daily 08:00
  end-day: daily 18:00
  start-week: monday 08:00
  end-week: friday 15:00
```

`end-week` at 15:00 on Friday is a deliberate choice: early enough to leave slack for the user to act on the output before the weekend.

## Friday 15:00 — Why Specifically

- **Weekly summary** generated into `references/findings/YYYY-MM-DD-weekly-summary.md`.
- **Promotion candidates** surfaced — the set of mature findings or topics that could go to team or marketplace.
- **Presentation suggestions** — any meetings scheduled for next week that look presentation-worthy.
- **Commit + push** offered (with branch-protection handling — see [commands.md](commands.md)).

If the user is not available at 15:00, the ritual queues its output as an `inputs/` item to be reviewed at the start of the next session.

## Ritual Composition

Rituals are composed from primitives:

```
start-day  = status + read-log + review-inputs + decisions-status + workstream-signals + briefing
end-day    = uncommitted-summary + archive-done + pull-next + log-append + offer-commit + suggestions
start-week = digest-team + workstream-review + audit-decisions + audit-backlog + marketplace-check + briefing
end-week   = weekly-summary + todo-cleanup + promotion-candidates + presentation-candidates + offer-commit
```

Primitives are internal — they are not separate user-visible commands. This keeps the surface small.

## Running Rituals on Demand

Even when scheduled, rituals can be invoked manually: `/kb start-day` mid-morning or `/kb end-week` on any weekday. They are idempotent within the same day/week (re-running doesn't duplicate findings or log entries).

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | v0.2 — end-day produces a daily summary finding + HTML; every ritual regenerates live overviews | html-artifacts.md v0.2 |
| 2026-04-18 | v0.1 — initial version | Extracted from source spec §6 |
