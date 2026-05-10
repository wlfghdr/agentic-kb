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
| `/kb todo` | Show `focus.md` |
| `/kb todo done [item]` | Complete item → archive, pull next from backlog |
| `/kb decide [description]` | Create new `_kb-decisions/D-YYYY-MM-DD-slug.md` |
| `/kb decide resolve [D-id]` | Archive decision + update topics + close related TODOs |

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
| `/kb status --refresh-overviews` | Manually rebuild `inventory.html`, `open-decisions.html`, `open-tasks.html`, and the root artifact `index.html` when you need a repair/rebuild pass |
| `/kb present [topic/file]` | Generate HTML presentation from topic/finding |
| `/kb report [scope]` | Generate HTML report (personal / team / org / weekly / topic) |
| `/kb report status [scope]` | Generate a shared status report for leads, product, and stakeholders |
| `/kb report delivery [scope]` | Generate a delivery report grounded in roadmap + journeys + delivery signals |
| `/kb report roadmap-change [scope]` | Generate a roadmap change report that explains baseline updates and downstream impact |
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
| Pending inputs | `_kb-inputs/` not yet in `_kb-inputs/digested/` |
| Open decisions | `_kb-decisions/*.md` with `status: proposed` |
| Overdue todos | `_kb-tasks/*.md` with status `todo`/`doing` > 7 days |
| Rituals | Today's `.kb-log/YYYY-MM-DD.log` missing `start-day`; current week missing `start-week` |
| Upstream digest drift | L2/L3 HEAD differs from `_kb-references/strategy-digests/.last-digest` (or per-repo watermark) |
| Promotions due | `maturity: durable` findings/topics not yet referenced in L2/L3 |
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
| 2026-05-10 | Added explicit shared report variants for status, delivery, and roadmap-change collaboration flows | Adoption-oriented engineering pass |
| 2026-04-22 | Reframed `/kb promote` as a composite local-team operation: intake plus immediate team review and archival, not a pure inbox copy | Team promote flow fix |
| 2026-04-22 | Fixed stale `inputs/` path in promote command; renamed section from "Decisions & TODOs" to "Decisions & Tasks" | Spec review |
| 2026-04-20 | Documented `/kb status --refresh-overviews` as the explicit manual repair and rebuild path, and aligned triage guidance with always-current overviews | v3.2.0 live-overview refresh |
