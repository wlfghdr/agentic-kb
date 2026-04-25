---
mode: agent
description: KB operations — capture, digest, promote, decide, rituals, present, report
tools:
  - run_in_terminal
  - read_file
  - create_file
  - replace_string_in_file
  - multi_replace_string_in_file
  - list_dir
  - file_search
  - grep_search
  - semantic_search
  - manage_todo_list
  - vscode_askQuestions
  - fetch_webpage
  - memory
---

# /kb — Knowledge Base

The user invokes `/kb` from any harness. Route to the `kb-management` skill.

> **Tool requirement.** This prompt needs file + terminal tools (declared in the frontmatter `tools:` list) to run file scaffolding, ritual scans, and git operations. On recent VS Code builds they are auto-selected from the frontmatter. If the chat session reports "no tools available" when this prompt runs, open the Chat view → gear/Configure Chat → Tools, enable the 13 built-in tools listed in the frontmatter above, and rerun `/kb`. This is a one-time per-session action.

## Routing precedence

Evaluate in order and stop at the first match:

1. **No `.kb-config/layers.yaml` anywhere in the workspace** → hand off to the `kb-setup` skill (even if the user typed only `/kb` with no args). Announce: "No KB detected — running setup." Then run the onboarding interview.
2. **Explicit subcommand** after `/kb` (`review`, `promote`, `publish`, `digest`, `todo`, `task`, `idea`, `develop`, `decide`, `start-day`, `end-day`, `start-week`, `end-week`, `present`, `report`, `browse`, `install`, `audit`, `status`, `setup`) → route to that action per `references/command-reference.md`.
3. **URL or pasted text** → capture to the anchor layer. Apply the five-question evaluation gate.
4. **File path inside a known KB layer** → layer-appropriate operation (review/update-topic/decide) on that file.
5. **Bare `/kb` (no input)** → run the **triage scan** below and present the result.

## Triage scan (bare `/kb`)

When the user invokes `/kb` with no argument, scan the workspace and report a single consolidated status with concrete next-step suggestions. Check these signals in order:

| Signal | Check | Action hint |
|---|---|---|
| Setup complete? | `.kb-config/layers.yaml` exists and names at least one contributor-capable layer | If missing → `/kb setup` |
| **Top task** | First item in `_kb-tasks/focus.md` (if any) | Always include as `Next up: …` |
| **External completions** | Open focus/backlog tasks with evidence of closure (merged PR / closed Jira ticket / commit referencing the task slug / same slug already in a shared `_kb-tasks/archive/`). See SKILL.md rule #10c. | Propose archiving — never auto-close |
| Pending inputs | Files under `_kb-inputs/` not yet in `_kb-inputs/digested/` | Count + suggest `/kb review` |
| Open decisions | Files under `_kb-decisions/` (not in `archive/`) whose `**Status**:` is not `resolved` / `superseded` / `dropped` | Count + suggest `/kb decide <key>` |
| Stale tasks | `_kb-tasks/backlog.md` items untouched > 14 days | Annotate `stale: true`; list but don't remove |
| Overdue focus | `_kb-tasks/focus.md` items with status `doing` > 7 days | Surface so user can re-plan |
| Rituals overdue | Today's `.kb-log/YYYY-MM-DD.log` missing a `start-day` entry; current week missing `start-week` | Suggest the missing ritual |
| Upstream digest drift | Parent or connected repos declared in `layers.yaml` whose HEAD commit differs from the local digest watermark | Suggest `/kb digest <layer>` or `/kb digest connections` |
| Promotions due | Findings/topics declaring `**Maturity**: durable` not yet referenced in any declared parent contributor layer | Suggest `/kb promote <file> <layer>` |
| Stale topics | Topics unchanged > 60 days and still referenced by recent findings | Suggest `/kb audit` |

Output shape:

```
KB triage — <anchor-layer-name>
  Setup: OK / MISSING
  Next up: <focus[0]>                       ← always, if focus.md not empty
  Reconciled completions: <N>               → archive? (confirm)
  Pending inputs: <N>                       → /kb review
  Open decisions: <N>                       → /kb decide <key>
  Stale tasks: <N> (annotated, not removed)
  Overdue focus items: <N>
  Rituals: start-day ✓ / ✗, start-week ✓ / ✗
  Upstream drift: <layers>                  → /kb digest <layer>
  Promotions due: <N>                       → /kb promote <file>
  Stale topics: <N>                         → /kb audit

Next: <top-3 concrete suggestions, most impactful first>
```

Always end with 1–3 suggested next steps. **Triage is read-only** — the external-completion check surfaces candidates, it never writes or archives. Archival requires explicit confirmation via a subsequent `/kb task done <id>` or a ritual that prompts for it.

## Execution rules (apply to every `/kb` invocation)

Follow the rules in the `kb-management` skill's SKILL.md. Always:

1. Apply the five-question evaluation gate before persisting anything.
2. Log the operation to `.kb-log/YYYY-MM-DD.log`.
3. Append an inline changelog entry on any topic / foundation file update.
4. End with 1–3 concrete next-step suggestions.
5. Offer to commit / push / open a PR after substantive changes (respect branch protection; no silent force-pushes).
