# Command Reference — kb-management

## Capture & Process

| Subcommand | Action |
|-----------|--------|
| `/kb [text/URL/path]` | Capture: assess + persist via the gate; route to workstream |
| `/kb review` | Process all pending items in `_kb-inputs/` |
| `/kb promote [file]` | L1 → team KB's contributor `inputs/` (ask which team if multiple) |
| `/kb promote org [file]` | L2 → org-unit KB |
| `/kb publish [file]` | L1/L2/L3 → marketplace skill (PR) |

## Decisions & TODOs

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
└── Bare `/kb` → show status
```

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

Keep it terse.
