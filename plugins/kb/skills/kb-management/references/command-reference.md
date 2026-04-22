# Command Reference — kb-management

## Capture & Process

| Subcommand | Action |
|-----------|--------|
| `/kb [text/URL/path]` | Capture: assess + persist via the gate; route to workstream |
| `/kb review` | Process all pending items in `_kb-inputs/` |
| `/kb promote [file]` | L1 → local team KB intake + immediate L2 review: stage in the contributor `_kb-inputs/`, process in team context, archive to `_kb-inputs/digested/YYYY-MM/`, and write the reviewed result to `_kb-references/` (ask which team if multiple) |
| `/kb promote org [file]` | L2 → org-unit KB |
| `/kb publish [file]` | L1/L2/L3 → marketplace skill (PR) |

## Decisions & Tasks

| Subcommand | Action |
|-----------|--------|
| `/kb task` | Show `focus.md` (top item is "Next up") |
| `/kb task done [item]` | Complete item → archive, pull next from backlog |
| `/kb decide [description]` | Create new `_kb-decisions/D-YYYY-MM-DD-slug.md` |
| `/kb decide resolve [D-id]` | Archive decision + update topics + close related tasks |

`/kb todo` and `/kb tasks` are accepted aliases of `/kb task` (and mirror in subcommands — `/kb todo done [item]` ≡ `/kb task done [item]`). The canonical verb in the spec is `task`; it matches the `_kb-tasks/` directory and avoids confusion with in-code TODO comments.

## Ideas

| Subcommand | Action |
|-----------|--------|
| `/kb idea [text]` | Create `_kb-ideas/I-YYYY-MM-DD-slug.md` (`**Stage**: seed`) |
| `/kb develop [idea]` | Sparring session: probe assumptions, contradictions, gaps, convergence; append an entry to the idea's Development Log |

Ideas progress through `seed` → `growing` → `ready` → `shipped` → `archived` (see `docs/REFERENCE.md` §Idea). `/kb develop` is the sparring pass that moves an idea forward; a mature idea is either cited by a decision, converted into a finding/topic, or shipped into a roadmap item. Edit the `**Stage**:` line directly when the idea reaches a new stage.

## Rituals

| Subcommand | Action |
|-----------|--------|
| `/kb start-day` | Briefing: focus + decisions + new signals grouped by workstream |
| `/kb end-day` | Wrap: summary, archive done, offer commit |
| `/kb start-week` | Weekly planning: all-layer digest + priorities |
| `/kb end-week` | Friday 15:00 summary: promotion candidates, presentation suggestions |

## Team & Org (L2/L3)

| Subcommand | Action |
|-----------|--------|
| `/kb digest team` | Pull team changes → new `findings/YYYY-MM-DD-<team>-contrib-digest.md` |
| `/kb digest org` | Pull org-unit changes |
| `/kb sync team` | Cross-reference contributor topics |
| `/kb diff team` | Show what's new per contributor |

## Marketplace (L4)

| Subcommand | Action |
|-----------|--------|
| `/kb publish [file]` | Package knowledge as skill → PR to marketplace |
| `/kb browse` | List marketplace skills |
| `/kb install [skill]` | Install a skill into the current harness |

## Meta

| Subcommand | Action |
|-----------|--------|
| `/kb audit` | Check contradictions, gaps, staleness |
| `/kb status` | Pending inputs, recent activity, todo counts, workstream summary |
| `/kb status --refresh-overviews` | Manually rebuild `dashboard.html` and the root artifact `index.html` when you need a repair/rebuild pass |
| `/kb present [topic/file]` | Generate HTML presentation from topic/finding |
| `/kb report [scope]` | Generate HTML report (personal / team / org / weekly / topic) |
| `/kb setup` | Hand off to `kb-setup` skill |

## Publish flow (detail)

1. Take source file (finding, topic, or team output).
2. Extract generalizable pattern — strip personal context, add trigger description.
3. Format as `SKILL.md` with YAML frontmatter (`name`, `description`, `version`, `triggers`, `tools`, `requires`, `license`).
4. Safety validation:
   - No PII
   - No credentials / tokens / API keys
   - No hardcoded external URLs (use `sources.md` aliases)
   - No destructive shell commands
5. Only reference tools available via the marketplace.
6. Scaffold `skills/<name>/` with `SKILL.md`, `references/`, and `scripts/` as needed.
7. Open a PR against the marketplace repo.

Not every piece of knowledge becomes a skill. Skills are for **reusable instructions** that help an agent do a specific job.

## Capture decision tree

```
input?
├── URL → fetch if user confirms; treat content as text
├── File path inside a KB → run gate on file content
├── Pasted text → run gate on text directly
└── Bare `/kb` → run triage scan (see below)
```

## Triage scan (bare `/kb`)

When `/kb` is invoked with no argument, report a read-only consolidated status. Canonical signal list (also defined in `kb.prompt.md`):

| Signal | Where to look |
|---|---|
| Setup complete? | `.kb-config/layers.yaml` exists |
| Top task | First item in `_kb-tasks/focus.md` (if any) — always surface as `Next up: ...` |
| External completions | Open focus/backlog tasks with evidence of closure (merged PR / closed ticket / commit reference / same slug already archived upstream) — propose archiving only; never auto-close in triage |
| Pending inputs | `_kb-inputs/` not yet in `_kb-inputs/digested/` |
| Open decisions | `_kb-decisions/*.md` (not in `archive/`) whose `**Status**:` is not `resolved` / `superseded` / `dropped` |
| Overdue focus | Bullets in `_kb-tasks/focus.md` with `status: doing` held > 7 days (`focus-overdue-days`) |
| Stale backlog | Bullets in `_kb-tasks/backlog.md` untouched > 14 days (`backlog-stale-days`) — annotated `stale: true`, never removed |
| Rituals | Today's `.kb-log/YYYY-MM-DD.log` missing `start-day`; current week missing `start-week` |
| Upstream digest drift | L2/L3 HEAD differs from `_kb-references/strategy-digests/.last-digest` (or per-repo watermark) |
| Promotions due | `**Maturity**: durable` findings/topics not yet referenced in L2/L3 |
| Stale topics | Topics unchanged > 60 days but still cited by recent findings |

Triage is read-only — no mutations, no commits. Output ends with 1–3 concrete next steps.

## Gate scoring

| Matches | Action | Log op |
|---------|--------|--------|
| 0 / 5 | Discard | `skipped` |
| 1–2 / 5 | Finding only | `capture` |
| 3+ / 5 | Finding + topic update + possibly decision | `capture` + `update-topic` + (optional) `decide` |

## Output shape

```
1. What I did       (one sentence)
2. Where it went    (relative paths)
3. Gate notes       (which Q matched, optional)
4. Suggested next steps (1-3 concrete follow-ups)
```

Collaboration-safe interpretation:

- `What I did` must make the action mode obvious: read-only, proposed, or applied.
- `Where it went` must distinguish inspected paths from written paths.
- `Gate notes` must expose external fetches, duplication, and low-confidence judgments when relevant.
- `Suggested next steps` must stay clearly separate from changes that already happened.

See `output-contract.md` for the full wording contract and examples.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-22 | Added the missing `Top task` and `External completions` triage signals so the bare-`/kb` status table fully matches `kb.prompt.md` and the task-handling rules | PR #49 follow-up |
| 2026-04-22 | `/kb task` named as the canonical task verb (with `todo` / `tasks` as accepted aliases); new Ideas section covering `/kb idea` + `/kb develop`; triage stale-task rule split into `focus-overdue-days` (7) and `backlog-stale-days` (14) matching `kb.prompt.md` and SKILL rule 11g | Fixes #24, #25, #26 |
| 2026-04-22 | Reframed `/kb promote` as a composite local-team operation: intake plus immediate team review and archival, not a pure inbox copy | Team promote flow fix |
| 2026-04-22 | Fixed stale `inputs/` path in promote command; renamed section from "Decisions & TODOs" to "Decisions & Tasks" | Spec review |
| 2026-04-20 | Documented `/kb status --refresh-overviews` as the explicit manual repair and rebuild path, and aligned triage guidance with always-current overviews | v3.2.0 live-overview refresh |
