# Command Reference

> **Version:** 0.1 | **Last updated:** 2026-04-18

There is one user-facing command: **`/kb`**. The agent infers the layer and the action from input context (content, file path, keywords, and `.kb-config.yaml`).

Explicit subcommands are provided for disambiguation but are never required for the common path.

## Summary

```
/kb                        → status (if bare) or auto-detect from context
/kb [text/URL/path]        → capture and assess material
/kb review                 → process all pending items in inputs/

/kb promote [file]         → push to team KB (asks which if multiple)
/kb promote org [file]     → push to org-unit KB
/kb publish [file]         → package as skill → PR to marketplace

/kb digest team            → pull team KB changes into personal findings
/kb digest org             → pull org-unit changes into personal findings
/kb sync team              → cross-reference all team contributors
/kb diff team              → show what's new from other team contributors

/kb todo                   → show focus items
/kb todo done [item]       → complete an item

/kb decide [description]   → create a new decision
/kb decide resolve [D-id]  → resolve a decision (archive + update topics + close TODOs)

/kb start-day              → morning briefing
/kb end-day                → evening wrap
/kb start-week             → weekly planning
/kb end-week               → weekly summary (Friday 15:00)

/kb audit                  → check for contradictions, gaps, staleness
/kb status                 → pending inputs, recent activity, todo counts, workstream summary

/kb present [topic/file]   → generate HTML presentation
/kb report [topic/file]    → generate HTML report (personal, team, or org-unit scope)

/kb browse                 → list available marketplace skills
/kb install [skill]        → install a skill from marketplace

/kb setup                  → full interactive onboarding wizard
```

## How the Agent Infers Context

| Input | Inferred action |
|-------|-----------------|
| A URL or pasted text | Capture to L1 |
| A path inside `my-kb/` | Operation on L1 |
| A path inside a team KB | Team-layer operation |
| The keyword `team` / `org` / `publish` | Disambiguates the layer |
| `.kb-config.yaml` declarations | Which repos correspond to which layers |

## `/kb start-day` — Morning Briefing

1. Read `todo/focus.md`.
2. Scan `decisions/active/` — any due soon or blocked?
3. Read today's and yesterday's `log/`.
4. `git diff` in personal KB since last activity.
5. `git diff` in team KB(s) since last digest.
6. Scan `inputs/` — anything unprocessed? (add to `backlog.md` if so).
7. Check workstreams for cross-workstream connections.
8. **Output**: briefing grouped by workstream.
9. **Suggest next steps**.

## `/kb end-day` — Evening Wrap

1. Review uncommitted changes; summarize the day.
2. Move completed focus items → `todo/archive/YYYY-MM.md`.
3. Update decisions if any state changed.
4. Pull next items from `backlog.md` → `focus.md` (if space).
5. Append to today's `log/`.
6. **Generate the daily summary**: `references/findings/YYYY-MM-DD-daily-summary.md` + rendered `references/reports/daily-YYYY-MM-DD.html`. See [html-artifacts.md](html-artifacts.md).
7. **Regenerate live overviews**: `inventory.html`, `open-decisions.html`, `open-todos.html`, `index.html`.
8. Offer to stage, commit, push (and open a PR if branch protection requires).
9. **Suggest next steps** (promotion candidates, overdue decisions).

If `end-day` is skipped for a given date, the next `start-day` generates the missing day's summary from the log + git diff before producing its briefing.

## `/kb start-week` — Weekly Planning

1. Full team KB digest.
2. Review all workstream files for movement.
3. Audit `decisions/active/` — overdue? new evidence?
4. Audit `todo/backlog.md` for stale items (>14 days untouched).
5. Check marketplace for new skills matching themes.
6. **Output**: weekly briefing grouped by workstream.
7. **Suggest next steps**.

## `/kb end-week` — Friday 15:00

1. Generate the weekly summary finding → `references/findings/YYYY-MM-DD-weekly-summary.md` + rendered `references/reports/weekly-YYYY-WW.html`.
2. Full TODO cleanup (archive done, prune stale backlog).
3. Identify candidates for promotion (L1 → L2 or → L4).
4. Identify presentation-worthy items for the upcoming week.
5. Per-workstream progress summary.
6. **Regenerate live overviews**: `inventory.html`, `open-decisions.html`, `open-todos.html`, `index.html`.
7. Offer to commit + push.
8. **Output**: week-in-review + promotion candidates + presentation suggestions.

## `/kb present` — Generate Presentation

Generates an HTML presentation from a topic or finding. Output goes to `references/reports/` (personal) or the equivalent in team/org KBs. The template is described in [html-artifacts.md](html-artifacts.md). Intro slide carries `vX.Y — YYYY-MM-DD` as a subtle watermark; appendix carries a changelog of presentation versions.

## `/kb report` — Generate Report

Like `/kb present` but for report layouts: work summaries, topic-change digests, cross-team overviews. The agent chooses the right template based on scope (personal / team / org-unit). See [html-artifacts.md](html-artifacts.md).

## `/kb publish` — Become a Skill

1. Take a source file (finding, topic, or team output).
2. Extract the generalizable pattern (strip personal context, add trigger description).
3. Format as `SKILL.md` with the required frontmatter (see [marketplace-and-skills.md](marketplace-and-skills.md)).
4. Run safety validation (no PII, no credentials, no external URLs in skill body, no dangerous shell commands).
5. Ensure only marketplace-available tools are referenced.
6. Scaffold `skills/<name>/` structure.
7. Open a PR against the marketplace repo.

**Not every piece of knowledge becomes a skill.** Skills are for reusable instructions. A meeting outcome is not a skill. A diagnostic workflow is.

## Commit/Push/PR Offer

After any substantive edit to a KB, the agent offers to commit and push. Rules:

- **Never push a red CI** — if the workspace has CI and the agent detects expected failure, it runs the checks locally first.
- **Branch protection** — if the target branch is protected, the agent creates a topic branch and opens a PR instead of pushing to the protected branch.
- **Ask before force-push or rebase** — never silent.
- The user can set a default policy in `.kb-automation.yaml` (see [automation.md](automation.md)).

## Live Overview Regeneration — Every Mutation

After **any** state-mutating command (`capture`, `review`, `promote`, `publish`, `digest`, `decide`, `decide-resolve`, `todo-add`, `todo-done`, `update-topic`, `audit`, any ritual), the agent regenerates the four live overview HTML files:

- `references/reports/inventory.html`
- `references/reports/open-decisions.html`
- `references/reports/open-todos.html`
- `references/reports/index.html`

Rules:

- Regeneration is **deterministic** (same state → byte-identical output).
- Regeneration runs as the **last step** of each operation, so the dashboard always reflects the new state.
- At **Level 1** automation, the agent asks before regenerating (with a one-press accept).
- At **Level 2/3**, regeneration is silent.
- Regenerated files are bundled with the same commit as the data change that triggered them.

Full contract: [html-artifacts.md](html-artifacts.md).

## Command Input/Output Contract

Every command follows the same output shape:

1. **What I did** — a short statement of the action performed.
2. **Where it went** — file paths (relative, clickable in IDE).
3. **Gate notes** — if any of the five gate questions matter, what matched.
4. **Suggested next steps** — 1–3 concrete follow-ups.

Implementations MUST preserve this shape. It is what makes the agent trustworthy.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | v0.2 — end-day/end-week generate daily/weekly summary + HTML; every mutation regenerates live overviews | html-artifacts.md v0.2 |
| 2026-04-18 | v0.1 — initial version | Extracted from source spec §6, §12 |
