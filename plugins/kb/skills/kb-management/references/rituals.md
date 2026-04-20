# Rituals — kb-management

## Invariants for every ritual

1. Start with `/kb status` mental check.
2. Read today's and yesterday's `.kb-log/`.
3. Respect the evaluation gate — rituals do not bypass it.
4. End with suggested next steps.
5. Log the invocation as `ritual-<name>`.

## `/kb start-day`

1. Read `_kb-tasks/focus.md`.
2. **Run task reconciliation** (see SKILL.md rule #10c) — detect external completions from Jira / GitHub / commits / shared archives. Propose closures; do not auto-archive.
3. Scan `_kb-decisions/` — any due soon or blocked?
4. Read today's and yesterday's `.kb-log/`.
5. `git diff` in personal KB since last activity.
6. `git diff` in team KB(s) since last digest.
7. Scan `_kb-inputs/` — anything unprocessed?
8. Check workstreams for cross-workstream connections.
9. **Output**: briefing grouped by workstream. Top of briefing: `Next up: <focus[0]>` + any reconciled completions awaiting archive confirmation.
10. **Suggest**: digest team, process inputs, message @stakeholder, etc.

## `/kb end-day`

1. Review uncommitted changes; summarize the day.
2. **Run task reconciliation** (SKILL.md rule #10c) for anything closed during the day.
3. Propose moving confirmed-done focus items → `_kb-tasks/archive/YYYY-MM.md`. **Do not move silently** — show the diff, ask once.
4. Update decisions if any state changed.
5. Propose pulling next items from `backlog.md` → `focus.md` (if space). Show diff, ask.
6. Append to today's `log/`.
7. Offer to stage, commit, push (PR if branch protection).
8. **Suggest**: promotion candidates, overdue decisions.

## `/kb start-week`

1. Full team KB digest.
2. Review all workstream files for movement.
3. Audit `_kb-decisions/` — overdue? new evidence?
4. **Run task reconciliation** (SKILL.md rule #10c) across `focus.md` and `backlog.md`; annotate items untouched > 14 days with `stale: true` (annotation only — no removal).
5. Check marketplace for new skills matching themes.
6. **Output**: weekly briefing grouped by workstream. Include reconciled completions + stale-annotated items.
7. **Suggest**.

## `/kb end-week` — Friday 15:00

1. Generate `_kb-references/findings/YYYY-MM-DD-weekly-summary.md`.
2. Task cleanup pass — propose archive for all reconciled-done items; propose drop for stale items the user confirms are obsolete. **Every move is confirmed, never silent.**
3. Identify promotion candidates (L1 → L2 / L4).
4. Identify presentation-worthy items for next week.
5. Per-workstream progress summary.
6. Offer to commit + push.
7. **Output**: week-in-review + promotion candidates + presentation suggestions + `Next up:` hint for Monday.

## Idempotency

Rituals are idempotent within a day / week — running twice doesn't duplicate log entries or findings.

## Friday 15:00 scheduling

- Deliberately early — leaves slack for the user to act before the weekend.
- If user is unavailable at 15:00, queue output as an `_kb-inputs/` item for next session.
