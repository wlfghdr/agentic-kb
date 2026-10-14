# Command Reference — kb-management

## Capture & Process

| Subcommand | Action |
|-----------|--------|
| `/kb [text/URL/path]` | Capture: assess + persist via the gate; routes per the three capture-routing modes (default → active layer; explicit → user-named target or `capture-routing:` rule match; reflection-driven → propose target + wait for human confirmation). See [`capture-routing.md`](./capture-routing.md) |
| `/kb <layer> [text/URL/path]` | Explicit-mode capture: route directly to the named contributor-capable layer (skips the default active-layer destination; no extra confirmation since routing was user-declared) |
| `/kb review` | Process all pending items in `_kb-inputs/` for the current layer or contributor scope |
| `/kb promote [file] [layer]` | Promote to the named target layer, or to the next contributor-capable parent layer if omitted |
| `/kb publish [file] [layer]` | Package knowledge as a skill and publish it to the marketplace attached to the target layer |

## Notes

| Subcommand | Action |
|-----------|--------|
| `/kb note [text]` | Create a general note under `_kb-notes/YYYY/MM-DD-slug.md` |
| `/kb note meeting [topic]` | Start a meeting note and prompt for attendees |
| `/kb note retro [topic]` | Start a retrospective note using `templates/retro.md`; prompts for cadence (sprint / project / post-launch / post-incident / quarterly), facilitator, attendees, the period under review, and linked artifacts (incidents, releases, briefs, specs) |
| `/kb note end` | Close the current note, propose decisions/tasks/topic updates, and log the result |

Notes use a lighter gate than findings. They are cheap capture surfaces that feed decisions, tasks, roadmap updates, and later findings without pretending to be immutable evidence.

Retro variants have one additional contract: `/kb note end` on a retro must surface every action item from *What we will change* as a proposed task on the layer's `_kb-tasks/backlog.md`, or as a new decision if the item is a fork rather than a commitment. A retro that closes without any tracked commitments is flagged in the response under Gate notes as a likely "false convergence" (see [`docs/collaboration.md`](../../../../../docs/collaboration.md)); the agent does not silently fix this — the user is asked to confirm whether the retro really had no follow-ups.

Retros also carry an explicit closure lifecycle (`status: open | tracked | closed` in the frontmatter — see `docs/REFERENCE.md` §4 "Retro closure lifecycle"). `/kb note end` on a retro moves it to `status: tracked` when every *What we will change* item is linked to a backlog task or decision; otherwise the retro stays `open` and the false-convergence Gate note fires. `/kb audit` rule K12 reports `open` retros older than 7 days and `tracked` retros eligible for `closed`. `/kb start-week` surfaces unfinished retro commitments (any retro at `status: tracked` whose linked tasks/decisions are still open).

## Decisions & Tasks

| Subcommand | Action |
|-----------|--------|
| `/kb task` | Show `focus.md` (top item is `Next up`) |
| `/kb task done [item]` | Mark a task done and offer archival to `_kb-tasks/archive/YYYY/MM.md` |
| `/kb decide [description]` | Create new `_kb-decisions/D-YYYY-MM-DD-slug.md` |
| `/kb decide resolve [D-id]` | Archive decision + update topics + close related tasks |

`/kb todo` and `/kb tasks` are accepted aliases of `/kb task`. The canonical verb in the spec is `task`.

Tasks follow the same canonical-ownership rule as decisions: if a team, org, or company layer owns the same work item and accountable owner, keep the task there and close/archive the source-layer duplicate. A contributor-owned layer may keep a separate task only for a narrower personal sub-task or owner-specific slice that links back to the canonical shared task.

If the active layer declares `primitive-storage` with `mode: tracker` for `decisions` or `tasks`, these commands create a proposed tracker mutation instead of a canonical KB file mutation. The agent must show the issue/ticket body, type/kind, target tracker, links, and action, then evaluate the capability boundary in [`tracker-backed-primitives.md`](./tracker-backed-primitives.md): declared adapter capability, available authentication/tooling, and explicit confirmation are all required to apply it. Missing capability or authentication returns the same proposal with exact manual steps; the user supplies the resulting tracker identifier for the backlink. KB files in the supporting summary directory may be written only as backlinks, reports, or archived context. The reserved connection-digest `writeback` switch does not govern these commands.

## Ideas

| Subcommand | Action |
|-----------|--------|
| `/kb idea [text]` | Create `_kb-ideas/I-YYYY-MM-DD-slug.md` (`**Stage**: seed`) |
| `/kb develop [idea]` | Sparring session: probe assumptions, contradictions, gaps, convergence; append to the idea's Development Log |

## Delivery & Operations

| Subcommand | Action |
|-----------|--------|
| `/kb brief [title]` | Open a delivery-intent artifact under `_kb-delivery/briefs/YYYY-MM-DD-slug.md` from the brief template; prompts for missing problem, scope, success signals, and dependency fields |
| `/kb spec [title]` | Open a design-contract artifact under `_kb-delivery/specs/YYYY-MM-DD-slug.md` from the spec template; prompts for missing context, requirements, proposed shape, verification, and open-questions fields, and offers to link an existing brief |
| `/kb release [title]` | Open a release record under `_kb-operations/releases/YYYY/YYYY-MM-DD-slug.md` from the release template; prompts for audience, scope, rollout plan, verification, and rollback before the change ships |
| `/kb incident [title]` | Open an incident record under `_kb-operations/incidents/YYYY/YYYY-MM-DD-slug.md` from the incident template; opened timestamp, severity, owners, services, impact, detection, and timeline are required and append-only once mitigated |

These four verbs require the layer to declare the matching feature in `.kb-config/layers.yaml`: `delivery` for `brief` and `spec`, `operations` for `release` and `incident`. If the feature is not enabled, the skill refuses with a clear message and points at the layer config. Brief and spec link upward into decisions and findings; release and incident link downward into follow-up tasks and findings.

## Digests & Layer Flow

| Subcommand | Action |
|-----------|--------|
| `/kb digest [layer]` | Pull changes from a named parent or adjacent layer into the current layer |
| `/kb digest connections` | Walk the current layer's declared `connections:` and capture deltas since the last watermark |
| `/kb sync [layer]` | Cross-reference contributor-scoped topics or findings when the layer uses contributor-scoped primitives; reconcile promote conflicts, diverged backlinks, and unresolved topic author-sections per [`docs/concurrency.md`](../../../../../docs/concurrency.md) |
| `/kb diff [layer]` | Show what's new per contributor or per connected source |

If the target layer is `role: consumer`, `promote` and `publish` must refuse and point to the next valid contributor layer.
For the staged-review contract behind `/kb promote`, see [`promote-contract.md`](./promote-contract.md).
When promoting decisions or tasks, keep one canonical path for the owning scope; close or archive the source as `superseded` unless it still has a genuinely different scope, accountable owner, or sub-task responsibility.
For connection declaration, watermarks, drift checks, and write-back, see [`connections-lifecycle.md`](./connections-lifecycle.md).
For tracker-backed primitive ownership, see [`tracker-backed-primitives.md`](./tracker-backed-primitives.md).

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
| `/kb report status [scope]` | Generate a shared status report for leads, product, and stakeholders |
| `/kb report delivery [scope]` | Generate a delivery report grounded in roadmap, journeys, and delivery signals |
| `/kb report roadmap-change [scope]` | Generate a roadmap change report that explains baseline updates and downstream impact |
| `/kb report progress [scope]` | Generate the named progress report for a layer, workstream, or time window |
| `/kb setup` | Hand off to `kb-setup` skill |

## `/kb report` guidance for shared artifacts

Use `/kb report` as a family, not a single vague output. For recurring software-engineering collaboration, prefer these specific report intents:

| Report kind | Purpose | Should pull from |
|-------------|---------|------------------|
| `status` | shared operating picture | active decisions, blockers, latest delivery report, roadmap scope |
| `delivery` | commitments vs reality | roadmap artifact, journey coverage, tracker / PR / shipped signals |
| `roadmap-change` | explain baseline changes | roadmap diff, affected journeys, stakeholder impact, required follow-up |
| `weekly` | time-boxed memory | week dailies, completed tasks, promotion candidates |
| `topic` | narrative explanation | findings, topics, decisions, proposals |

When one of these report kinds exists, the agent should say so explicitly in `What I did` and should link the upstream shared artifacts it relied on.

Canonical shared-report contract:

- `status` source: `_kb-references/reports/sources/<scope>/status-<scope>-YYYY-MM-DD.md`
- `delivery` source: `_kb-references/reports/sources/<scope>/delivery-<scope>-YYYY-MM-DD.md`
- `roadmap-change` source: `_kb-references/reports/sources/<scope>/roadmap-change-<scope>-YYYY-MM-DD.md`
- `status` may be initiated by the report owner or ritual owner and approved by the named `Owner`.
- `delivery` may be initiated by engineering or delivery owners and approved by the named engineering or delivery owner.
- `roadmap-change` may be opened automatically when roadmap scope, sequencing, dates, ownership, or committed phase changes, but it is only approved by the accountable roadmap owner or PM.
- In other words, roadmap-change may be opened automatically, but never auto-approved.

## Product-management subcommands

The plugin ships two product-management skills that own their own subcommand surface. `/kb` routes to them after the core subcommands above, and only when setup has proposed or the user has manually declared the matching config block on the confirmed owning layer.

| Subcommand | Skill | Activated by |
|-----------|-------|--------------|
| `/kb roadmap [...]` | [`kb-roadmap`](../../kb-roadmap/SKILL.md) | `roadmap:` block on the active layer in `.kb-config/layers.yaml` (+ `html-template:` in `.kb-config/artifacts.yaml`) |
| `/kb journeys [...]` (alias `/kb journey`) | [`kb-journeys`](../../kb-journeys/SKILL.md) | `journeys:` block on the active layer in `.kb-config/layers.yaml` (+ `journeys-template:` in `.kb-config/artifacts.yaml`) |

When a user invokes `/kb roadmap` or `/kb journeys` and the matching block is missing, refuse with a message that names the missing block and points at the skill's `references/config-schema.md`. Also offer `/kb setup` as the normal path for deciding which layer should own roadmap and journey artifacts. Never silently scaffold the config — the placement decision is the point. Full subcommand surface for each skill lives in its own `references/command-reference.md`.

## Publish flow (detail)

1. Take source file (finding, topic, note, or shared layer output).
2. Extract the generalizable pattern and strip local-only context.
3. Format as `SKILL.md` with YAML frontmatter (`name`, `description`, `version`, `triggers`, `tools`, `requires`, `license`).
4. Safety validation:
   - No PII
   - No credentials / tokens / API keys
   - No hardcoded external URLs (use `sources.md` aliases or `connections` config)
   - No destructive shell commands
5. Only reference tools available via the target marketplace.
6. Scaffold `plugins/<plugin>/skills/<name>/` with `SKILL.md`, `references/`, `templates/`, and `scripts/` as needed.
7. Open a PR against the marketplace repo configured for the target layer.

For the full publish contract, including the generalizability gate and response expectations, see [`publish-contract.md`](./publish-contract.md).

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
| Rituals | Today's `.kb-log/YYYY-MM-DD.log` or `.kb-log/YYYY/YYYY-MM-DD.log` missing `start-day`; current week missing `start-week`. At automation level 1 (manual only), surface a nudge — *"No `start-day` today. Run `/kb start-day`?"* — because nothing else fires the ritual; at levels 2/3 the scheduler is the source of truth and this signal only warns when the scheduler itself appears stuck (no log entry past the configured cadence + 1 hour) |
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
