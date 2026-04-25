---
name: kb-management
description: Lean, layered knowledge management driven by the `/kb` command. Operates on a flexible layer graph, applies the five-question evaluation gate, tracks findings, notes, decisions, ideas, and tasks as first-class artifacts, digests connected repos and trackers, and publishes reusable skills to per-layer marketplaces.
version: 5.1.0
triggers:
  - "/kb"
  - "knowledge base"
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
  - "note"
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

This skill implements the `agentic-kb` specification. It operates on the user's workspace as a **layer graph**: one anchor layer with `.kb-config/`, plus any number of additional contributor or consumer layers connected by `parent` edges.

## When to invoke

Invoke this skill whenever the user:

- Types `/kb` followed by text, a URL, a file path, or a subcommand.
- Describes work that implies capture, digestion, promotion, publication, decision-making, note-taking, or artifact generation.
- Needs a read-only triage summary across the current layer graph.

## The single command model

There is **one** user-facing command: `/kb`. Infer layer and action from context:

| Input | Action |
|---|---|
| URL or pasted text | Capture into the current layer via the evaluation gate |
| File path inside a known layer | Operate in that layer context |
| Explicit layer name | Route to the named target layer |
| Explicit subcommand (`review`, `promote`, `digest`, `task`, `note`, `report`, ...) | Run that flow |
| Bare `/kb` | Read-only triage scan |
| `.kb-config/layers.yaml` | Declares the layer graph, roles, parent edges, marketplaces, and connections |

Full command reference: `references/command-reference.md`.

## Core rules

1. **Run the evaluation gate before persistence.** Score material against the five gate questions. The score is the count of yes answers. Q4 + Q2 form the lighter note gate.
2. **Set and preserve maturity.** New findings and topics must carry `**Maturity**:`. `raw` means weak or single-signal, `emerging` means accepted and worth revisiting, `durable` means ready to promote or cite broadly.
3. **Respect the layer graph.** `promote` walks upward through `parent`; `digest` walks downward from parent or from `connections`. A `role: consumer` layer is read-down only: it may receive digests, but it is never a `promote` or `publish` target.
4. **Keep contributor-scoped and shared artifacts distinct.** Inputs, findings, ideas, and strategy digests stay contributor-scoped by default on multi-user layers. Decisions, tasks, workstreams, foundation files, reports, and meeting notes are shared unless the layer config says otherwise. This visibility rule is separate from the layer `role`.
5. **Log every operation.** Write to `.kb-log/YYYY-MM-DD.log` or `.kb-log/YYYY/YYYY-MM-DD.log` in the canonical `HH:MM:SSZ | operation | scope | target | details` format.
6. **Regenerate live overviews after mutation.** `dashboard.html` and the root `index.html` are part of the same mutation as capture, review, promote, publish, digest, decide, note-end, present, report, and ritual flows.
7. **Never mutate silently.** The response must make the action mode obvious: read-only analysis, proposed mutation, or applied mutation.
8. **Task creation and closure are explicit.** Propose task lines when material is actionable; do not add or archive them silently. External completion signals can reconcile tasks, but archival still needs confirmation.
9. **Next steps are mandatory.** End every response with 1–3 concrete follow-ups.
10. **Offer commit/push/PR after substantive change.** Respect branch protection and never force-push silently.

## Layer-aware flow primitives

| Flow | Command | What it does |
|------|---------|--------------|
| Capture | `/kb [input]` | Assess via gate; write finding or note; update topic/decision; route to workstream |
| Review | `/kb review` | Process all pending items in `_kb-inputs/` |
| Promote | `/kb promote [file] [layer]` | Promote to a named contributor-capable layer, or the next contributor-capable parent layer |
| Publish | `/kb publish [file] [layer]` | Package reusable knowledge as a skill and publish it to the target layer marketplace |
| Digest layer | `/kb digest [layer]` | Pull changes from a parent or adjacent layer |
| Digest connections | `/kb digest connections` | Pull deltas from configured product repos and trackers |
| Sync | `/kb sync [layer]` | Cross-reference contributor-scoped topics or findings |
| Diff | `/kb diff [layer]` | Show new material per contributor or connection |
| Migrate | `/kb migrate archives` / `/kb migrate layer-model` | Preview or apply legacy archive and layer-model migrations |
| Task | `/kb task` / `/kb task done [item]` | Manage focus/backlog |
| Note | `/kb note [text]` / `/kb note meeting [topic]` / `/kb note end` | Capture general or meeting notes and surface follow-on changes |
| Idea | `/kb idea [text]` | Create a seed idea |
| Develop | `/kb develop [idea]` | Spar on assumptions, contradictions, and convergence |
| Decide | `/kb decide [desc]` / `/kb decide resolve [D-id]` | Open or resolve a decision |
| Present | `/kb present [topic/file]` | Generate a versioned HTML presentation |
| Report | `/kb report [scope]` | Generate a layer or topic report |
| Progress report | `/kb report progress [scope]` | Generate the multi-source progress narrative |
| Rituals | `/kb start-day`, `/kb end-day`, `/kb start-week`, `/kb end-week` | Run composed briefings and summaries |
| Audit | `/kb audit` | Check contradictions, staleness, gaps, and layer-shape drift |
| Status | `/kb status` | Report pending work, connection drift, tasks, and recent activity |

## Output contract

Every response follows the same shape:

1. **What I did** — one short statement.
2. **Where it went** — relative paths inspected or written.
3. **Gate notes** — which gate signals matched, or n/a.
4. **Suggested next steps** — 1–3 concrete follow-ups.

Additional requirements:

- Make read-only vs proposed vs applied obvious.
- If external material was fetched, say so explicitly.
- If the action crossed layers, name source and destination.
- Surface uncertainty when the gate result is borderline or duplicative.

## Safety rules

- Never promote or publish content containing secrets.
- Never publish with PII to any layer marketplace.
- Never publish or promote to a `role: consumer` layer.
- Never auto-push to a protected branch.
- When a capture, report, presentation, or progress run needs external reads, show a preflight block first: declared source(s), filters/time window, read-only vs apply intent, and output path(s).
- Do not declare HTML artifact work complete until the generated artifact passes its QA sweep: theme toggle works, no unresolved placeholders remain, embedded assets resolve without network fetches, readability is acceptable in both themes, and keyboard affordances still work.

## Promote semantics

`/kb promote` is a composite applied mutation, not a mailbox drop. For multi-user contributor layers it stages the intake in the destination contributor scope before immediate review; single-user targets skip staging and write the reviewed result directly. Full contract: `references/promote-contract.md`.

When promoting to a locally available contributor-capable layer, the agent must:

1. run the promotion safety check,
2. stage the artifact into the target contributor scope when the target layer uses contributor-scoped inputs,
3. complete the destination-layer review immediately,
4. write the durable result into the destination references or shared primitive,
5. archive the staged intake under the year-based digested path, and
6. log both the intake and the reviewed result in the destination layer.

When the selected target is `role: consumer`, refuse and point to the next valid contributor layer.

## Templates

The templates this skill instantiates live in `templates/`:

- `finding.md`, `topic.md`, `decision.md`, `idea.md`, `note.md`, `workstream.md`
- `focus.md`, `backlog.md`
- `index.html`, `artifact-base.html`, `report.html`
- workspace and KB scaffolding templates supplied by `kb-setup`
- `.kb-config/layers.yaml`, `.kb-config/automation.yaml`, `.kb-config/artifacts.yaml`

## References (load on demand)

- `references/spec-summary.md` — condensed architecture and workspace layout.
- `references/command-reference.md` — full subcommand details.
- `references/promote-contract.md` — staged-review semantics for `/kb promote`.
- `references/rituals.md` — the four rituals in detail.
- `references/html-artifacts.md` — presentation/report generation contract.
- `references/evaluation-gate.md` — the five-question filter, in depth.
- `references/output-contract.md` — collaboration-safe wording and examples.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-25 | Clarified that consumer layers may receive digests but are never promote/publish targets, and added an explicit promote-contract reference for staged review semantics | Deep spec-audit follow-up |
| 2026-04-25 | Added the explicit 5.1 migration-helper surface (`/kb migrate archives`, `/kb migrate layer-model`) and aligned the declared skill version with the closeout release | v5.1.0 closeout release |
| 2026-04-25 | Reworked the behavioral spec for 5.0.0: `/kb` now operates on a flexible layer graph, notes became first-class, digests can read declared connections, and publish targets per-layer marketplaces instead of a fixed L4 | v5.0.0 flexible layer model |
| 2026-04-25 | Version aligned to 4.0.0 for the v4.0.0 framework release (composite `/kb promote` semantics + mandatory artifact preflight/QA contract) | v4.0.0 release alignment |
| 2026-04-25 | Added explicit preflight-fetch summaries for artifact-driving external reads and a mandatory post-generation HTML QA sweep; bumped declared skill version to 3.5.0 | Generic learnings extracted from live roadmap and presentation feature work |
