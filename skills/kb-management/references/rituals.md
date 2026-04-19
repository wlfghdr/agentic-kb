# Rituals — kb-management

## Invariants for every ritual

1. Start with `/kb status` mental check.
2. Read today's and yesterday's `log/`.
3. Respect the evaluation gate — rituals do not bypass it.
4. End with suggested next steps.
5. Log the invocation as `ritual-<name>`.

## `/kb start-day`

1. Read `tasks/focus.md`.
2. Scan `decisions/active/` — any due soon or blocked?
3. Read today's and yesterday's `log/`.
4. `git diff` in personal KB since last activity.
5. `git diff` in team KB(s) since last digest.
6. Scan `inputs/` — anything unprocessed?
7. Check workstreams for cross-workstream connections.
8. **Output**: briefing grouped by workstream.
9. **Suggest**: digest team, process inputs, message @stakeholder, etc.

## `/kb end-day`

1. Review uncommitted changes; summarize the day.
2. Move completed focus items → `tasks/archive/YYYY-MM.md`.
3. Update decisions if any state changed.
4. Pull next items from `backlog.md` → `focus.md` (if space).
5. Append to today's `log/`.
6. Offer to stage, commit, push (PR if branch protection).
7. **Suggest**: promotion candidates, overdue decisions.

## `/kb start-week`

1. Full team KB digest.
2. Review all workstream files for movement.
3. Audit `.decisions/active/` — overdue? new evidence?
4. Audit `.tasks/backlog.md` for stale items (>14 days untouched).
5. Check marketplace for new skills matching themes.
6. **Output**: weekly briefing grouped by workstream.
7. **Suggest**.

## `/kb end-week` — Friday 15:00

1. Generate `references/findings/YYYY-MM-DD-weekly-summary.md`.
2. Full TODO cleanup (archive done, prune stale backlog).
3. Identify promotion candidates (L1 → L2 / L4).
4. Identify presentation-worthy items for next week.
5. Per-workstream progress summary.
6. Offer to commit + push.
7. **Output**: week-in-review + promotion candidates + presentation suggestions.

## Idempotency

Rituals are idempotent within a day / week — running twice doesn't duplicate log entries or findings.

## Friday 15:00 scheduling

- Deliberately early — leaves slack for the user to act before the weekend.
- If user is unavailable at 15:00, queue output as an `.inputs/` item for next session.
