---
mode: agent
description: KB operations — capture, digest, promote, decide, rituals, present, report
---

# /kb — Knowledge Base

The user invokes `/kb` from any harness. Route to the `kb-management` skill.

## Routing precedence

Evaluate in order and stop at the first match:

1. **No `.kb-config/layers.yaml` anywhere in the workspace** → hand off to the `kb-setup` skill (even if the user typed only `/kb` with no args). Announce: "No KB detected — running setup." Then run the onboarding interview.
2. **Explicit subcommand** after `/kb` (`review`, `promote`, `publish`, `digest`, `todo`, `task`, `idea`, `develop`, `decide`, `start-day`, `end-day`, `start-week`, `end-week`, `present`, `report`, `browse`, `install`, `audit`, `status`, `setup`) → route to that action per `references/command-reference.md`.
3. **URL or pasted text** → capture to L1. Apply the five-question evaluation gate.
4. **File path inside a known KB layer** → layer-appropriate operation (review/update-topic/decide) on that file.
5. **Bare `/kb` (no input)** → run the **triage scan** below and present the result.

## Triage scan (bare `/kb`)

When the user invokes `/kb` with no argument, scan the workspace and report a single consolidated status with concrete next-step suggestions. Check these signals in order:

| Signal | Check | Action hint |
|---|---|---|
| Setup complete? | `.kb-config/layers.yaml` exists and names at least the personal KB | If missing → `/kb setup` |
| Pending inputs | Files under `_kb-inputs/` not yet in `_kb-inputs/digested/` | Count + suggest `/kb review` |
| Open decisions | Files under `_kb-decisions/` with `status: proposed` in frontmatter | Count + suggest `/kb decide <key>` |
| Actionable todos | Files under `_kb-tasks/` with status `todo` or `doing` older than 7 days | Count + suggest `/kb todo review` |
| Rituals overdue | Today's `.kb-log/YYYY-MM-DD.log` missing a `start-day` entry; current week missing `start-week` | Suggest the missing ritual |
| Upstream digest drift | L2/L3 repos declared in `layers.yaml` whose HEAD commit differs from the watermark in `_kb-references/strategy-digests/.last-digest` (or equivalent per repo) | Suggest `/kb digest <layer>` |
| Promotions due | Findings/topics with `maturity: durable` in frontmatter not yet referenced in any L2/L3 KB | Suggest `/kb promote <file>` |
| Stale topics | Topics unchanged > 60 days and still referenced by recent findings | Suggest `/kb audit` |
| Artifact refresh due | Any state-mutating op since the last `present`/`report`/`end-day` (check `.kb-log/` vs. HTML mtimes) | Offer `/kb status --refresh-overviews` |

Output shape:

```
KB triage — <personal-kb-name>
  Setup: OK / MISSING
  Pending inputs: <N>         → /kb review
  Open decisions: <N>         → /kb decide <key>
  Overdue todos: <N>          → /kb todo review
  Rituals: start-day ✓ / ✗, start-week ✓ / ✗
  Upstream drift: <layers>    → /kb digest team
  Promotions due: <N>         → /kb promote <file>
  Stale topics: <N>           → /kb audit

Next: <top-3 concrete suggestions, most impactful first>
```

Always end with 1–3 suggested next steps. Never run a mutating operation inside a triage scan — only read.

## Execution rules (apply to every `/kb` invocation)

Follow the rules in the `kb-management` skill's SKILL.md. Always:

1. Apply the five-question evaluation gate before persisting anything.
2. Log the operation to `.kb-log/YYYY-MM-DD.log`.
3. Append an inline changelog entry on any topic / foundation file update.
4. End with 1–3 concrete next-step suggestions.
5. Offer to commit / push / open a PR after substantive changes (respect branch protection; no silent force-pushes).

