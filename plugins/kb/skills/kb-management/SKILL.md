---
name: kb-management
description: Lean, layered knowledge management driven by the `/kb` command. Captures material into a personal KB, routes to workstreams, applies a five-question evaluation gate, tracks decisions and ideas as first-class objects, manages tasks, generates versioned HTML artifacts, and promotes content across layers (personal, team, org-unit, marketplace). Triggered by `/kb` and knowledge-related phrases.
version: 3.4.1
triggers:
  - "/kb"
  - "knowledge base"
  - "personal kb"
  - "team kb"
  - "capture"
  - "digest"
  - "promote"
  - "publish"
  - "start day"
  - "end day"
  - "start week"
  - "end week"
  - "todo"
  - "task"
  - "decide"
  - "idea"
  - "develop"
  - "goal"
  - "knowledge management"
  - "present"
  - "report"
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
requires: []
author: agentic-kb contributors
homepage: https://github.com/wlfghdr/agentic-kb
license: Apache-2.0
---

# Skill: KB Management

This skill implements the `agentic-kb` specification. It operates on the user's workspace — a directory containing one required **personal KB** and any number of optional **team**, **org-unit**, **marketplace**, and **company** layers. See `references/spec-summary.md` for the condensed architecture.

## When to invoke

Invoke this skill whenever the user:

- Types `/kb` followed by text, a URL, a file path, or a subcommand (`review`, `promote`, `publish`, `digest team`, `task`, `todo`, `idea`, `develop`, `decide`, `start-day`, `end-day`, `start-week`, `end-week`, `present`, `report`, `browse`, `install`, `audit`, `status`).
- Describes work that implies capture (*"I just read this paper…"*), decision (*"we need to decide…"*), idea development (*"I've been thinking about…"*), or promotion (*"this should go to the team"*) — offer to run the corresponding `/kb` action first.

## The single command model

There is **one** user-facing command: `/kb`. Infer layer and action from context:

| Input | Action |
|---|---|
| URL / pasted text | Capture to L1 |
| Path inside `my-kb/` | L1 operation |
| Path inside a team repo | Team operation |
| Explicit keyword (`team`, `org`, `publish`) | Disambiguates |
| `.kb-config/layers.yaml` | Declares which dirs are which layer |

Full command reference: `references/command-reference.md`.

## Core rules (always apply)

1. **Run the evaluation gate** before persisting anything. Five questions:
   1. Does this strengthen a position?
   2. Does this inform a decision?
   3. Would the user reference this again?
   4. Is this actionable?
   5. Is this materially new compared to existing topics?
   Score = count of "yes" answers across Q1-Q5. Score 0 → discard + log `skipped` with rationale. Score 1–2 → finding only (offer idea creation if novelty detected). Score 3+ → finding + topic update + possibly new decision or idea.

   **Set `**Maturity**:` from the gate outcome** when writing the finding/topic: score 1–2 → `raw`; score 3+ → `emerging`. Only promote to `durable` on explicit user confirmation ("this is ready to share") or when a second corroborating capture lands. The `Promotions due` triage signal and audit rule K1 read this field — never leave it blank.

1b. **Check strategic alignment** when VMG is declared in `_kb-references/foundation/vmg.md`. VMG alignment does not change the numeric gate score; use it to prioritize accepted material. Material contradicting a goal is captured + flagged for decision review.

2. **Always suggest next steps.** Every operation output ends with 1–3 concrete follow-ups (promote, notify, update topic, generate presentation).

3. **Route to workstreams.** Analyze content against the workstream themes in `.kb-config/layers.yaml`. If cross-workstream, flag the connection.

4. **Log every operation** to `.kb-log/YYYY-MM-DD.log` in the format `HH:MM:SSZ | op | scope | target | details`.

5. **Append inline changelog** entries on topic and foundation file updates (newest first, under a `---` separator).

6. **Never silent failures.** If an operation fails, surface it — never mask.

7. **Offer commit/push/PR** after substantive changes. Respect branch protection (open a PR instead of pushing to a protected branch). Never force-push silently. Keep CI green.

8. **Presentation-worthy detection.** When a TODO contains *present, pitch, demo, share, slide, meeting prep*, add 🎤 and offer `/kb present`.

9. **Auto-regenerate live overviews after every mutation.** After any state-mutating operation (`capture`, `review`, `promote`, `publish`, `digest`, `decide`, `decide-resolve`, `task-add`, `task-done`, `update-topic`, `audit`, `present`, `report`, `end-day`, `end-week`, and automation-loop writes), regenerate `dashboard.html` and the root artifact `index.html` before the response/commit completes. Treat these two files as part of the same mutation, not as a later optional step.

10. **Regenerate root `index.html` and `dashboard.html`** whenever a mutation creates or modifies KB state, including the live overview refresh above. Run `python3 scripts/generate-index.py REPO_ROOT --title "..." --description "..."` and `python3 scripts/generate-dashboard.py REPO_ROOT --title "..." --description "..."` (or the `.kb-scripts/` copies). `/kb status --refresh-overviews` remains available as a manual repair/rebuild trigger, but freshness no longer depends on it. `index.html` serves as the GitHub Pages landing page (artifact inventory); `dashboard.html` is the owner-facing command center (focus, ideas, decisions, inputs, recent findings/digests/reports, workstreams, opt-in GitHub/Jira).

11. **Task handling discipline — apply on every `/kb` invocation, not only `/kb task`.** Tasks are first-class and the user's most fragile surface. Rules:

    a. **Surface the top task.** Every response that isn't a pure status/read query ends its next-step suggestions with the current top item from `_kb-tasks/focus.md` if one exists. Format: `Next up: <focus item>` (single line, no commentary).

    b. **Never create a task silently.** When the evaluation gate marks captured material as actionable (Q4 = yes), do **not** auto-append to `focus.md` or `backlog.md`. Propose the exact task line (title, workstream, optional RACI) and ask for confirmation. On confirm, add to `backlog.md` by default — only add to `focus.md` if the user says "focus" or explicitly picks it.

    c. **Detect external completion.** Before `start-day`, `end-day`, `start-week`, `end-week`, `status`, or any triage scan, run this reconciliation pass:
        - For every open task in `focus.md` / `backlog.md`, look for completion signals since the task's last mtime:
          - closed Jira ticket referenced in the task body (via `jira-sync` if wired up)
          - merged PR referenced in the task body (via `gh` if wired up)
          - commits in any declared layer whose message or trailer references the task's slug / ID
          - a shared team/org task file with the same slug now in `_kb-tasks/archive/`
        - If found, mark the task `status: done` with a `completed-by: <source>` trailer and a `completed-at: <ISO>` timestamp, but **do not archive silently** — list the reconciled items and ask "Archive these N completed tasks?". On confirm, move to `_kb-tasks/archive/YYYY-MM.md` in one batch commit.

    d. **Never delete a task.** Only move to `_kb-tasks/archive/YYYY-MM.md` with a `status:` trailer (`done`, `dropped`, `superseded-by: <id>`). Deletion requires `/kb task purge <id>` and confirmation.

    e. **Shared-task safety.** Tasks in team/org KBs with a RACI **may only be closed by R or A**, or with confirmation from someone named in the RACI, or when an explicit external signal (merged PR, closed ticket) is found. In all other cases, propose the close and wait for user confirmation — never auto-close a shared task.

    f. **No destructive reorder without diff.** When `end-day` / `end-week` reshuffles `focus.md` / `backlog.md`, show the diff and ask before writing.

    g. **Stale signal, not stale deletion.** Backlog items untouched > 14 days get a `stale: true` annotation on the ritual pass. Annotation only — no removal.

    h. **Preserve provenance.** Every task gets created with `source:` (the finding / decision / input that spawned it) and `created: <ISO>`. Retain across moves (backlog → focus → archive).

## Directory contract (personal KB)

```
my-kb/
├── .kb-config/               # all KB config lives here
│   ├── layers.yaml           # layer declaration, workspace aliases, VMG
│   ├── automation.yaml       # automation level + schedules
│   └── artifacts.yaml        # HTML artifact styling
├── _kb-inputs/                  # the inbox; digested/YYYY-MM/ archive
├── _kb-references/
│   ├── topics/              # living; inline changelog required
│   ├── findings/            # YYYY-MM-DD-slug.md; immutable
│   ├── foundation/          # me, context, vmg, stakeholders, sources, naming
│   ├── legacy/              # archived topics after audit
│   └── reports/             # generated HTML artifacts
├── _kb-ideas/
│   ├── I-YYYY-MM-DD-slug.md # active ideas (seed/growing/ready)
│   └── archive/             # shipped + archived
├── _kb-decisions/
│   ├── D-YYYY-MM-DD-slug.md # active decisions at root
│   └── archive/
├── _kb-tasks/
│   ├── focus.md             # max 6 items
│   ├── backlog.md
│   └── archive/YYYY-MM.md
├── .kb-log/YYYY-MM-DD.log
├── .kb-scripts/                    # optional utility scripts
├── _kb-workstreams/<name>.md
└── index.html                      # auto-generated artifact index (GitHub Pages root)
```

See `references/spec-summary.md` §Workspace for team and org-unit KB shape.

## Flow primitives

| Flow | Command | What it does |
|------|---------|--------------|
| Capture | `/kb [input]` | Assess via gate; write finding; update topic/decision; archive input; route to workstream; offer idea if novelty detected |
| Review | `/kb review` | Process all pending items in `_kb-inputs/` |
| Promote | `/kb promote [file]` | L1 → L2 intake + immediate L2 review for local team KBs: stage in the contributor `_kb-inputs/`, process in team context, archive under `_kb-inputs/digested/YYYY-MM/`, and leave the reviewed result in `_kb-references/` |
| Promote org | `/kb promote org [file]` | L2 → L3 |
| Publish | `/kb publish [file]` | L1/L2/L3 → L4 marketplace; packages as SKILL.md; opens PR |
| Digest team | `/kb digest team` | Pull team changes since watermark; distill new findings; incorporate team VMG updates into personal `vmg.md` |
| Digest org | `/kb digest org` | L3 → L1 equivalent; incorporate org VMG updates into personal `vmg.md` |
| Sync team | `/kb sync team` | Cross-reference contributor topics; flag conflicts |
| Diff team | `/kb diff team` | Show new items per contributor |
| Task | `/kb task` / `/kb task done [item]` | Manage focus/backlog (aliases: todo, tasks) |
| Idea | `/kb idea [text]` | Create a new idea (`**Stage**: seed`) |
| Develop | `/kb develop [idea]` | Sparring: assumptions, contradictions, gaps, convergence |
| Decide | `/kb decide [desc]` / `/kb decide resolve [D-id]` | Open/resolve a decision; update affected topics |
| Start-day / End-day / Start-week / End-week | rituals | See `references/rituals.md` |
| Present | `/kb present [topic/file]` | HTML presentation — see `references/html-artifacts.md` |
| Report | `/kb report [scope]` | HTML report (personal / team / org) |
| Browse / Install | `/kb browse` / `/kb install [skill]` | Marketplace queries |
| Audit | `/kb audit` | Contradictions, gaps, staleness. Runs KB-wide checks and delegates scope-specific audits to `kb-roadmap` (mappings · timeline · scope · structural) and `kb-journeys` (structure · citations · coverage) when those skills are installed. See `references/audit.md`. |
| Status | `/kb status` | Pending inputs, recent activity, task counts, goal status |

## Output contract

Every response follows the same shape:

1. **What I did** — one short statement.
2. **Where it went** — relative file paths.
3. **Gate notes** — which of the five questions matched (if relevant).
4. **Suggested next steps** — 1–3 concrete follow-ups.

Additional collaboration-safe requirements:

- Make the action mode obvious: **read-only analysis**, **proposed mutation**, or **applied mutation**.
- If external material was fetched, say so explicitly.
- If the action crossed layers (`promote`, `digest`, `publish`), show source and destination clearly.
- Make uncertainty visible when the gate result is borderline, low-confidence, or partially duplicative.
- Never blur an already-applied mutation into a mere suggestion, or a suggestion into an applied change.

Keep output terse. The user reads it in a terminal/editor pane, not a full document.

## Safety rules

- **Never promote content containing secrets** (API keys, tokens, credentials). Refuse with an explanation.
- **Never publish with PII** to the marketplace. Check before packaging.
- **Never auto-push to a protected branch.** Open a PR.
- **Never force-push or rebase** without explicit confirmation.
- **Always inform before fetching external URLs.**

## Promote semantics

`/kb promote` is a composite applied mutation, not a mailbox drop.

When promoting from L1 to a team KB that exists in the current workspace, the
agent must:

1. run the promotion safety check (team relevance, secrets/PII, audience fit),
2. copy the source artifact into the target contributor `_kb-inputs/`,
3. immediately switch to the destination team context and apply the L2 review
  gate there,
4. write the reviewed result to the contributor `_kb-references/` area,
5. archive the staged intake under `_kb-inputs/digested/YYYY-MM/`, and
6. log both the cross-layer intake and the review result in the team KB's
  `.kb-log/`.

Only stop after step 2 when the destination layer is unavailable locally,
explicitly remote-only, or blocked by a concrete error. In those cases, say that
the promote completed as an intake-only fallback and name the missing review
step.

## Templates

The templates this skill instantiates live in `templates/`:

- `finding.md`, `topic.md`, `decision.md`, `idea.md`, `workstream.md`
- `focus.md`, `backlog.md`
- `index.html` — KB root landing page linking to dashboards, reports, topics, findings
- `artifact-base.html`
- `personal-kb-AGENTS.md`, `personal-kb-README.md`
- `team-kb-AGENTS.md`, `team-kb-README.md`, `org-kb-AGENTS.md`, `org-kb-README.md`
- `workspace-AGENTS.md`, `kb.prompt.md`, `kb.instructions.md`
- `.kb-config/layers.yaml`, `.kb-config/automation.yaml`, `.kb-config/artifacts.yaml`

## References (load on demand)

- `references/spec-summary.md` — condensed architecture and workspace layout.
- `references/command-reference.md` — full subcommand details.
- `references/rituals.md` — the four rituals in detail.
- `references/html-artifacts.md` — presentation/report generation contract.
- `references/evaluation-gate.md` — the five-question filter, in depth.
- `references/output-contract.md` — collaboration-safe wording and examples for read-only, proposed, and applied operations.

These files are loaded **only when the specific behavior is invoked**. The skill's top-level instructions are sufficient for most operations.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-22 | Simplified rule 9 to regenerate only `dashboard.html` and the root `index.html` after every mutation — dropped the three phantom overviews (`inventory.html`, `open-decisions.html`, `open-tasks.html`) that had no shipped generator; their signals live in dashboard panels | Fixes #18 |
| 2026-04-22 | Canonicalized the idea lifecycle field as `**Stage**:` across audit K5 and the command-reference blurb so dashboard and audit agree with the REFERENCE and template | Fixes #35 |
| 2026-04-22 | `command-reference.md` now declares `/kb task` canonical (with `todo` / `tasks` aliases), documents `/kb idea` + `/kb develop` in a new Ideas section, and splits the stale-task triage rule into `focus-overdue-days` (7) and `backlog-stale-days` (14) matching the bullet-in-file data model | Fixes #24 + #25 + #26 |
| 2026-04-22 | Reframed evaluation-gate Q5 as positive novelty (`materially new compared to existing topics`) and removed the obsolete VMG `+1` bonus from the core rule so the score is always the count of yes answers | Fixes #30 |
| 2026-04-22 | Wired `**Maturity**:` into the capture flow so bare `/kb` triage and audit K1 can read the field they were designed for | Fixes #14 + #31 |
| 2026-04-22 | Aligned open-decisions triage + audit K4 to read the template's `**Status**:` bold-bullet form so `/kb` triage finally counts open decisions | Fixes #15 |
| 2026-04-22 | Restored the missing `idea.md` scaffold template so `/kb idea` has a canonical file source again | System test follow-up |
| 2026-04-22 | Version aligned to 3.4.0 after documenting Codex CLI compatibility in the public setup/onboarding contract | Compatibility expansion |
| 2026-04-22 | `/kb promote` now performs destination-layer review for local team KBs instead of stopping at the team inbox; version bumped to 3.3.0 | Team promote flow fix |
| 2026-04-22 | Version aligned to 3.2.0 | Spec review |
| 2026-04-20 | Made overview regeneration part of every state-mutating `/kb` operation and retained `/kb status --refresh-overviews` as a manual repair/rebuild trigger | v3.2.0 live-overview refresh |
