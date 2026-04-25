# Command Reference — kb-management

## Capture & Process

| Subcommand | Action |
|-----------|--------|
| `/kb [text/URL/path]` | Capture: assess + persist via the gate; route to the active layer and workstream |
| `/kb review` | Process all pending items in `_kb-inputs/` for the current layer or contributor scope |
| `/kb promote [file] [layer]` | Promote to the named target layer, or to the next contributor-capable parent layer if omitted |
| `/kb publish [file] [layer]` | Package knowledge as a skill and publish it to the marketplace attached to the target layer |

## Notes

| Subcommand | Action |
|-----------|--------|
| `/kb note [text]` | Create a general note under `_kb-notes/YYYY/MM-DD-slug.md` |
| `/kb note meeting [topic]` | Start a meeting note and prompt for attendees |
| `/kb note end` | Close the current note, propose decisions/tasks/topic updates, and log the result |

Notes use a lighter gate than findings. They are cheap capture surfaces that feed decisions, tasks, roadmap updates, and later findings without pretending to be immutable evidence.

## Decisions & Tasks

| Subcommand | Action |
|-----------|--------|
| `/kb task` | Show `focus.md` (top item is `Next up`) |
| `/kb task done [item]` | Mark a task done and offer archival to `_kb-tasks/archive/YYYY/MM.md` |
| `/kb decide [description]` | Create new `_kb-decisions/D-YYYY-MM-DD-slug.md` |
| `/kb decide resolve [D-id]` | Archive decision + update topics + close related tasks |

`/kb todo` and `/kb tasks` are accepted aliases of `/kb task`. The canonical verb in the spec is `task`.

## Ideas

| Subcommand | Action |
|-----------|--------|
| `/kb idea [text]` | Create `_kb-ideas/I-YYYY-MM-DD-slug.md` (`**Stage**: seed`) |
| `/kb develop [idea]` | Sparring session: probe assumptions, contradictions, gaps, convergence; append to the idea's Development Log |

## Digests & Layer Flow

| Subcommand | Action |
|-----------|--------|
| `/kb digest [layer]` | Pull changes from a named parent or adjacent layer into the current layer |
| `/kb digest connections` | Walk the current layer's declared `connections:` and capture deltas since the last watermark |
| `/kb sync [layer]` | Cross-reference contributor-scoped topics or findings when the layer uses contributor-scoped primitives |
| `/kb diff [layer]` | Show what's new per contributor or per connected source |

If the target layer is `role: consumer`, `promote` and `publish` must refuse and point to the next valid contributor layer.
For the staged-review contract behind `/kb promote`, see [`promote-contract.md`](./promote-contract.md).
For the publish contract (generalizability gate, safety validation, SKILL.md frontmatter), see [`publish-contract.md`](./publish-contract.md).
For connection setup, digest lifecycle, watermark format, and write-back, see [`connections-lifecycle.md`](./connections-lifecycle.md).

## Migration

| Subcommand | Action |
|-----------|--------|
| `/kb migrate archives` | Preview or apply the year-based archive moves for digests, tasks, findings, decisions, ideas, notes, strategy digests, and optional daily logs |
| `/kb migrate layer-model` | Preview or apply the conversion from the retired fixed-layer schema to the list-based layer graph |

Both helpers are dry-run first. The shipped helper scripts live under `plugins/kb/skills/kb-management/scripts/` and apply only after explicit confirmation.

## Rituals

| Subcommand | Action |
|-----------|--------|
| `/kb start-day` | Briefing: focus + decisions + connection deltas grouped by workstream |
| `/kb end-day` | Wrap: summary, archive done items, offer commit |
| `/kb start-week` | Weekly planning: all-layer digest + priorities |
| `/kb end-week` | Weekly summary: promotion candidates, progress deltas, presentation suggestions |

## Meta

| Subcommand | Action |
|-----------|--------|
| `/kb audit` | Check contradictions, gaps, staleness, and layer-shape mismatches |
| `/kb status` | Pending inputs, recent activity, task counts, connection drift, and workstream summary |
| `/kb status --refresh-overviews` | Manually rebuild `dashboard.html` and the root artifact `index.html` |
| `/kb present [topic/file]` | Generate HTML presentation from topic, finding, note, or report source |
| `/kb report [scope]` | Generate HTML report for a topic, layer, or ritual summary |
| `/kb report progress [scope]` | Generate the named progress report for a layer, workstream, or time window |
| `/kb setup` | Hand off to `kb-setup` skill |

## Publish flow (detail)

For the full publish contract — generalizability gate, safety validation, SKILL.md frontmatter, staging behavior, and response expectations — see [`publish-contract.md`](./publish-contract.md).

Summary steps:

1. Take source file (finding, topic, note, or shared layer output).
2. Extract the generalizable pattern and strip local-only context.
3. Format as `SKILL.md` with YAML frontmatter (`name`, `description`, `version`, `triggers`, `tools`, `requires`, `license`).
4. Safety validation:
   - No PII
   - No credentials / tokens / API keys
   - No hardcoded external URLs (use `sources.md` aliases or `connections` config)
   - No destructive shell commands
5. Only reference tools available via the target marketplace.
6. Scaffold `skills/<name>/` with `SKILL.md`, `references/`, and `scripts/` as needed.
7. Open a PR against the marketplace repo configured for the target layer.

## Capture decision tree

```text
input?
├── URL → fetch if user confirms; treat content as text
├── File path inside a known layer → run gate on file content
├── Pasted text → run gate on text directly
└── Bare `/kb` → run triage scan (see below)
```

## Triage scan (bare `/kb`)

When `/kb` is invoked with no argument, report a read-only consolidated status. Canonical signal list:

| Signal | Where to look |
|---|---|
| Setup complete? | `.kb-config/layers.yaml` exists and names an anchor layer |
| Top task | First item in `_kb-tasks/focus.md` (if any) — always surface as `Next up: ...` |
| External completions | Open focus/backlog tasks with evidence of closure (merged PR / closed ticket / commit reference / same slug already archived upstream) — propose archiving only; never auto-close in triage |
| Pending inputs | `_kb-inputs/` not yet in `_kb-inputs/digested/` |
| Open decisions | `_kb-decisions/*.md` (not in `archive/`) whose `**Status**:` is not `resolved` / `superseded` / `dropped` |
| Overdue focus | Bullets in `_kb-tasks/focus.md` with `status: doing` held > 7 days (`focus-overdue-days`) |
| Stale backlog | Bullets in `_kb-tasks/backlog.md` untouched > 14 days (`backlog-stale-days`) — annotated `stale: true`, never removed |
| Rituals | Today's `.kb-log/YYYY-MM-DD.log` or `.kb-log/YYYY/YYYY-MM-DD.log` missing `start-day`; current week missing `start-week` |
| Upstream digest drift | Declared parent layers whose HEAD commit differs from the latest strategy-digest watermark |
| Connection drift | `connections` sources changed since the last connection digest watermark |
| Promotions due | Findings/topics declaring `**Maturity**: durable` not yet referenced in a higher contributor layer |
| Stale topics | Topics unchanged > 60 days and still referenced by recent findings |

Triage is read-only — no mutations, no commits. Output ends with 1–3 concrete next steps.

## Gate scoring

| Matches | Action | Log op |
|---------|--------|--------|
| 0 / 5 | Discard | `skipped` |
| 1–2 / 5 | Finding only | `capture` |
| 3+ / 5 | Finding + topic update + possibly decision | `capture` + `update-topic` + (optional) `decide` |

## Output shape

```text
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
| 2026-04-25 | Added pointers to publish-contract.md and connections-lifecycle.md so adopters can follow the full depth of /kb publish and /kb digest connections from the command surface | Deep spec-audit follow-up |
| 2026-04-25 | Added an explicit pointer from the command reference to the staged-review promote contract so adopters can see when staging happens and when it does not | Deep spec-audit follow-up |
| 2026-04-25 | Added the explicit migration helper commands so the command surface now includes the 5.1 closeout path for old archive layouts and fixed-layer configs | v5.1.0 closeout release |
| 2026-04-25 | Reworked the command surface for the 5.0 layer graph: promote/publish now target named layers, notes became a first-class primitive, `digest connections` and `report progress` were added, and triage now checks anchor-layer setup plus connection drift | v5.0.0 flexible layer model |
| 2026-04-22 | Clarified that `--refresh-overviews` is the manual repair path for rebuilding `dashboard.html` and the root artifact `index.html`, replacing the prior always-current/phantom-overview wording | PR #53 fix |
| 2026-04-22 | Added the missing `Top task` and `External completions` triage signals so the bare-`/kb` status table fully matches `kb.prompt.md` and the task-handling rules | PR #49 follow-up |
| 2026-04-22 | `/kb task` named as the canonical task verb (with `todo` / `tasks` as accepted aliases); new Ideas section covering `/kb idea` + `/kb develop`; triage stale-task rule split into `focus-overdue-days` (7) and `backlog-stale-days` (14) matching `kb.prompt.md` and SKILL rule 11g | Fixes #24, #25, #26 |
| 2026-04-22 | Reframed `/kb promote` as a composite local-team operation: intake plus immediate team review and archival, not a pure inbox copy | Team promote flow fix |
