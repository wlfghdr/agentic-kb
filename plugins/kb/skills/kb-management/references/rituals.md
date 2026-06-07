# Rituals — kb-management

> **Version:** 6.3.0 | **Last updated:** 2026-06-02

## Invariants for every ritual

1. Start with `/kb status` mental check.
2. Read today's and yesterday's `.kb-log/`.
3. Respect the evaluation gate — rituals do not bypass it.
4. End with suggested next steps.
5. Log the invocation as `ritual-<name>`.

## `/kb start-day`

1. Read `_kb-tasks/focus.md`.
2. **Run task reconciliation** under SKILL.md rule 8 (Task creation and closure are explicit) — detect external completions from declared `connections:` (commits, merged PRs, closed tracker tickets) or from a shared archive. Propose closures; do not auto-archive.
3. Scan `_kb-decisions/` — any due soon or blocked?
4. Read today's and yesterday's `.kb-log/`.
5. `git diff` in the anchor layer since last activity.
6. `git diff` in parent or connected layers since last digest.
7. Scan `_kb-inputs/` — anything unprocessed?
8. Check workstreams for cross-workstream connections.
9. **Output**: briefing grouped by workstream. Top of briefing: `Next up: <focus[0]>` + any reconciled completions awaiting archive confirmation.
10. **Suggest**: digest a parent layer, digest connections, process inputs, message @stakeholder, etc.

## `/kb end-day`

1. Review uncommitted changes; summarize the day.
2. **Run task reconciliation** under SKILL.md rule 8 for anything closed during the day.
3. Propose moving confirmed-done focus items → `_kb-tasks/archive/YYYY/MM.md`. **Do not move silently** — show the diff, ask once.
4. Update decisions if any state changed.
5. Propose pulling next items from `backlog.md` → `focus.md` (if space). Show diff, ask.
6. Append to today's `.kb-log/` entry.
7. Offer to stage, commit, push (PR if branch protection).
8. **Suggest**: promotion candidates, overdue decisions.

## `/kb start-week`

1. Full parent-layer or shared-layer digest.
2. Review all workstream files for movement.
3. Audit `_kb-decisions/` — overdue? new evidence?
4. **Run task reconciliation** under SKILL.md rule 8 across `focus.md` and `backlog.md`; annotate items untouched > 14 days with `stale: true` (annotation only — no removal).
5. Check marketplace for new skills matching themes.
6. **Output**: weekly briefing grouped by workstream. Include reconciled completions + stale-annotated items.
7. **Suggest**.

## `/kb end-week` — Friday 15:00

1. Generate `_kb-references/findings/YYYY/YYYY-MM-DD-weekly-summary.md`.
2. Task cleanup pass — propose archive for all reconciled-done items; propose drop for stale items the user confirms are obsolete. **Every move is confirmed, never silent.**
3. Identify promotion candidates for parent contributor layers and publish candidates for layer marketplaces.
4. Identify presentation-worthy items for next week.
5. Per-workstream progress summary.
6. Offer to commit + push.
7. **Output**: week-in-review + promotion candidates + presentation suggestions + `Next up:` hint for Monday.

## Idempotency

Rituals are idempotent within a day / week — running twice doesn't duplicate log entries or findings.

## Friday 15:00 scheduling

- Deliberately early — leaves slack for the user to act before the weekend.
- If user is unavailable at 15:00, queue output as an `_kb-inputs/` item for next session.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-06-02 | Added required version/changelog metadata so plugin specs and references are covered by the consistency check | Issue #144 |
| 2026-05-10 | First changelog row in this file (closes the AGENTS rule 3 gap), plus three drift fixes the v6 audit surfaced: replaced the retired `SKILL.md rule #11c` cross-references with pointers to the current rule 8 (Task creation and closure are explicit); corrected the task-archive path from `_kb-tasks/archive/YYYY-MM.md` to the canonical `_kb-tasks/archive/YYYY/MM.md` declared in `docs/REFERENCE.md` §3 so end-of-day archival writes to the right place; corrected the weekly-summary finding path to the year-nested `_kb-references/findings/YYYY/YYYY-MM-DD-weekly-summary.md` shape used everywhere else in the spec | v6.0.0 adoption + daily-usage gap audit |
