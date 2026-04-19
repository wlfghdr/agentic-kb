---
name: kb-management
description: Lean, layered knowledge management driven by the `/kb` command. Captures material into a personal KB, routes to workstreams, applies a five-question evaluation gate, tracks decisions and ideas as first-class objects, manages tasks, generates versioned HTML artifacts, and promotes content across layers (personal, team, org-unit, marketplace). Triggered by `/kb` and knowledge-related phrases.
version: 3.0.0
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

> **v2.0 scope note.** HTML overviews (`inventory.html`, `open-decisions.html`, `open-tasks.html`, `index.html`) are regenerated **on explicit invocation** — `/kb present`, `/kb report`, `/kb end-day`, `/kb end-week`, or `/kb status --refresh-overviews`. Automatic regeneration after every state-mutating operation is planned for v2.1 (see `docs/roadmap.md`). Until then, after a mutating operation the skill **offers** the refresh but does not run it silently.

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
   5. Does this already exist?
   Score 0 → discard + log `skipped` with rationale. Score 1–2 → finding only (offer idea creation if novelty detected). Score 3+ → finding + topic update + possibly new decision or idea.

1b. **Check strategic alignment** when VMG is declared. Material aligned with active goals gets +1. Material contradicting a goal is captured + flagged for decision review.

2. **Always suggest next steps.** Every operation output ends with 1–3 concrete follow-ups (promote, notify, update topic, generate presentation).

3. **Route to workstreams.** Analyze content against the workstream themes in `.kb-config/layers.yaml`. If cross-workstream, flag the connection.

4. **Log every operation** to `.kb-log/YYYY-MM-DD.log` in the format `HH:MM:SSZ | op | scope | target | details`.

5. **Append inline changelog** entries on topic and foundation file updates (newest first, under a `---` separator).

6. **Never silent failures.** If an operation fails, surface it — never mask.

7. **Offer commit/push/PR** after substantive changes. Respect branch protection (open a PR instead of pushing to a protected branch). Never force-push silently. Keep CI green.

8. **Presentation-worthy detection.** When a TODO contains *present, pitch, demo, share, slide, meeting prep*, add 🎤 and offer `/kb present`.

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
│   ├── foundation/          # me, context, stakeholders, sources, naming
│   ├── legacy/              # archived topics after audit
│   └── reports/             # generated HTML artifacts
├── _kb-ideas/
│   ├── I-YYYY-MM-DD-slug.md # active ideas (seed/growing/ready)
│   └── archive/             # shipped + archived
├── _kb-decisions/
│   ├── D-YYYY-MM-DD-slug.md # active decisions at root
│   └── archive/
├── _kb-tasks/
│   ├── focus.md             # max 3 items
│   ├── backlog.md
│   └── archive/YYYY-MM.md
├── .kb-log/YYYY-MM-DD.log
├── .kb-scripts/                    # optional utility scripts
└── _kb-workstreams/<name>.md
```

See `references/spec-summary.md` §Workspace for team and org-unit KB shape.

## Flow primitives

| Flow | Command | What it does |
|------|---------|--------------|
| Capture | `/kb [input]` | Assess via gate; write finding; update topic/decision; archive input; route to workstream; offer idea if novelty detected |
| Review | `/kb review` | Process all pending items in `_kb-inputs/` |
| Promote | `/kb promote [file]` | L1 → L2 (team KB's contributor `_kb-inputs/`) with safety pre-check |
| Promote org | `/kb promote org [file]` | L2 → L3 |
| Publish | `/kb publish [file]` | L1/L2/L3 → L4 marketplace; packages as SKILL.md; opens PR |
| Digest team | `/kb digest team` | Pull team changes since watermark; distill new findings |
| Digest org | `/kb digest org` | L3 → L1 equivalent |
| Sync team | `/kb sync team` | Cross-reference contributor topics; flag conflicts |
| Diff team | `/kb diff team` | Show new items per contributor |
| Task | `/kb task` / `/kb task done [item]` | Manage focus/backlog (aliases: todo, tasks) |
| Idea | `/kb idea [text]` | Create a new idea (seed status) |
| Develop | `/kb develop [idea]` | Sparring: assumptions, contradictions, gaps, convergence |
| Decide | `/kb decide [desc]` / `/kb decide resolve [D-id]` | Open/resolve a decision; update affected topics |
| Start-day / End-day / Start-week / End-week | rituals | See `references/rituals.md` |
| Present | `/kb present [topic/file]` | HTML presentation — see `references/html-artifacts.md` |
| Report | `/kb report [scope]` | HTML report (personal / team / org) |
| Browse / Install | `/kb browse` / `/kb install [skill]` | Marketplace queries |
| Audit | `/kb audit` | Contradictions, gaps, staleness |
| Status | `/kb status` | Pending inputs, recent activity, task counts, goal status |

## Output contract

Every response follows the same shape:

1. **What I did** — one short statement.
2. **Where it went** — relative file paths.
3. **Gate notes** — which of the five questions matched (if relevant).
4. **Suggested next steps** — 1–3 concrete follow-ups.

Keep output terse. The user reads it in a terminal/editor pane, not a full document.

## Safety rules

- **Never promote content containing secrets** (API keys, tokens, credentials). Refuse with an explanation.
- **Never publish with PII** to the marketplace. Check before packaging.
- **Never auto-push to a protected branch.** Open a PR.
- **Never force-push or rebase** without explicit confirmation.
- **Always inform before fetching external URLs.**

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

These files are loaded **only when the specific behavior is invoked**. The skill's top-level instructions are sufficient for most operations.
