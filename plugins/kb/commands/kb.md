---
mode: agent
description: KB operations — capture, digest, promote, decide, rituals, present, report, roadmap, journeys
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
2. **Explicit subcommand** after `/kb` (`review`, `promote`, `publish`, `digest`, `todo`, `task`, `idea`, `develop`, `decide`, `note`, `brief`, `spec`, `release`, `incident`, `migrate`, `sync`, `diff`, `start-day`, `end-day`, `start-week`, `end-week`, `present`, `report`, `audit`, `status`, `setup`) → route to that action per `references/command-reference.md`.
3. **Product-management subcommand** after `/kb` — `roadmap` (or `roadmaps`) hands off to the `kb-roadmap` skill; `journeys` (or `journey`) hands off to the `kb-journeys` skill. If the active layer has not declared the matching `roadmap:` / `journeys:` config block in `.kb-config/layers.yaml`, refuse with a clear message that names the missing block, points the user at the skill's `references/config-schema.md`, and offers `/kb setup` as the normal path for deciding which layer should own the artifact.
4. **URL or pasted text** → capture into the active layer (the anchor unless context selects another contributor-capable layer). Apply the five-question evaluation gate.
5. **File path inside a known KB layer** → layer-appropriate operation (review/update-topic/decide) on that file.
6. **Bare `/kb` (no input)** → run the **triage scan** below and present the result.

## Triage scan (bare `/kb`)

When the user invokes `/kb` with no argument, scan the workspace and report a single consolidated status with concrete next-step suggestions. Check these signals in order:

| Signal | Check | Action hint |
|---|---|---|
| Setup complete? | `.kb-config/layers.yaml` exists and names an anchor layer | If missing → `/kb setup` |
| **Top task** | First item in `_kb-tasks/focus.md` (if any) | Always include as `Next up: …` |
| **External completions** | Open focus/backlog tasks with evidence of closure (merged PR / closed tracker ticket / commit referencing the task slug / same slug already in a shared `_kb-tasks/archive/`). See SKILL.md rule 8 (Task creation and closure are explicit). | Propose archiving — never auto-close |
| Pending inputs | Files under `_kb-inputs/` not yet in `_kb-inputs/digested/` | Count + suggest `/kb review` |
| Open decisions | Files under `_kb-decisions/` (not in `archive/`) whose `**Status**:` is not `resolved` / `superseded` / `dropped` | Count + suggest `/kb decide <key>` |
| Stale tasks | `_kb-tasks/backlog.md` items untouched > 14 days | Annotate `stale: true`; list but don't remove |
| Overdue focus | `_kb-tasks/focus.md` items with status `doing` > 7 days | Surface so user can re-plan |
| Rituals overdue | Today's `.kb-log/YYYY-MM-DD.log` missing a `start-day` entry; current week missing `start-week` | Suggest the missing ritual |
| Upstream digest drift | Parent layers declared in `.kb-config/layers.yaml` whose HEAD commit differs from the watermark in `_kb-references/strategy-digests/.last-digest` (or per-source watermark file) | Suggest `/kb digest <layer>` |
| Connection drift | Declared `connections:` sources changed since the last connection digest watermark | Suggest `/kb digest connections` |
| Promotions due | Findings/topics declaring `**Maturity**: durable` not yet referenced in any contributor-capable parent layer | Suggest `/kb promote <file>` |
| Stale topics | Topics unchanged > 60 days and still referenced by recent findings | Suggest `/kb audit` |

Output shape:

```
KB triage — <personal-kb-name>
  Setup: OK / MISSING
  Next up: <focus[0]>                       ← always, if focus.md not empty
  Reconciled completions: <N>               → archive? (confirm)
  Pending inputs: <N>                       → /kb review
  Open decisions: <N>                       → /kb decide <key>
  Stale tasks: <N> (annotated, not removed)
  Overdue focus items: <N>
  Rituals: start-day ✓ / ✗, start-week ✓ / ✗
  Upstream drift: <layers>                  → /kb digest team
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

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-22 | Removed two dead verbs (`browse`, `install`) from the explicit-subcommand routing list. They had no implementation, no documentation, and no description anywhere — caught by the new command-list drift guard in `scripts/check_consistency.py`. Closes audit finding #109 | Audit-tracker closeout |
| 2026-05-15 | Reframed the `/kb roadmap` and `/kb journeys` routing row as stable product-management subcommands gated by explicit owning-layer config, removing the old draft-skill wording from the active command-generation surface | Release-readiness audit |
| 2026-05-10 | v6.0.0: removed residual fixed-ladder vocabulary (`L1` capture target in routing precedence, `L2/L3 repos` and `L2/L3 KB` in the triage signal table), replaced with the layer-graph terms (active layer, parent layers, contributor-capable parent layer). Added the canonical delivery/operations subcommands (`brief`, `spec`, `release`, `incident`) plus `note`, `migrate`, `sync`, `diff` to the explicit-subcommand list so the routing precedence matches `command-reference.md`. Added a connection-drift signal to the triage scan. Updated the rule-cross-reference for external completions to point at SKILL.md rule 8 (Task creation and closure are explicit) instead of the retired sub-letter `rule #10c`. First changelog row in this file | v6.0.0 adoption + daily-usage gap audit |
