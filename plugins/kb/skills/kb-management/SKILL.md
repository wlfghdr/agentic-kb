---
name: kb-management
description: Lean, layered knowledge management driven by the `/kb` command. Operates on a flexible layer graph, applies the five-question evaluation gate, tracks findings, notes, decisions, ideas, tasks, briefs, specs, releases, and incidents as first-class artifacts, digests connected repos and trackers, and publishes reusable skills to per-layer marketplaces.
version: 5.6.0
triggers:
  # Command surface
  - "/kb"
  - "kb status"
  - "knowledge base"
  - "kb-config"
  - "layer graph"
  - "anchor layer"
  # Capture / triage flows
  - "capture"
  - "review inputs"
  - "process inputs"
  - "inbox review"
  - "evaluation gate"
  # Cross-layer flows
  - "digest"
  - "promote"
  - "promote to"
  - "publish"
  - "publish to"
  - "migrate kb"
  - "kb migrate"
  - "migrate layer-model"
  - "migrate archives"
  # First-class artifacts (multi-word to limit false positives)
  - "brief"
  - "spec"
  - "release"
  - "incident"
  - "finding"
  - "findings"
  - "decision"
  - "decisions"
  - "open decision"
  - "workstream"
  - "workstreams"
  - "vmg"
  - "vision mission goals"
  - "stakeholder map"
  - "foundation file"
  # Note / idea / task verbs
  - "note"
  - "meeting note"
  - "idea"
  - "develop idea"
  - "sparring session"
  - "decide"
  - "todo"
  - "task"
  # Rituals
  - "start day"
  - "end day"
  - "start week"
  - "end week"
  - "morning briefing"
  - "daily digest"
  - "daily summary"
  - "weekly status"
  - "weekly summary"
  # Artifacts
  - "present"
  - "report"
  - "progress report"
  # Draft-skill handoff (route to kb-roadmap / kb-journeys)
  - "roadmap"
  - "roadmaps"
  - "product roadmap"
  - "phase roadmap"
  - "now next later"
  - "roadmap presentation"
  - "roadmap status"
  - "journey"
  - "journeys"
  - "user journey"
  - "customer journey"
  - "product journey"
  - "journey map"
  - "user flow"
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
- Mentions any feature keyword from the `triggers:` list above, even **without** the `/kb` prefix — e.g. "let me capture this", "promote that finding to the team layer", "start my day", "open a decision on caching", "weekly status please". The harness fires the skill on those phrases; the skill is responsible for routing them to the right `/kb` flow and confirming the proposed action before mutating state.
- Describes work that implies capture, digestion, promotion, publication, decision-making, note-taking, or artifact generation, even when no listed keyword appears verbatim.
- Needs a read-only triage summary across the current layer graph.

When the user invokes the skill via a feature keyword rather than `/kb`, the response MUST: name the inferred `/kb …` flow, restate the inferred target layer, and ask for confirmation before any mutation. Read-only flows (`status`, triage scans) may proceed immediately.

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
4. **Keep contributor-scoped and shared artifacts distinct.** Inputs, findings, ideas, and strategy digests stay contributor-scoped by default on multi-user layers. Decisions, tasks, workstreams, foundation files, reports, delivery artifacts, operations artifacts, and meeting notes are shared unless the layer config says otherwise. This visibility rule is separate from the layer `role`.
5. **Keep decisions and tasks canonical to one owning layer.** When promoting a decision or task, determine whether the target layer now owns the same scope and accountable decider/owner. If yes, close, archive, or replace the source item with a backlink; keep two active records only when their scopes, recommendations, accountable owners, or sub-task responsibilities differ.
6. **Log every operation.** Write to `.kb-log/YYYY-MM-DD.log` or `.kb-log/YYYY/YYYY-MM-DD.log` in the canonical `HH:MM:SSZ | operation | scope | target | details` format.
7. **Regenerate live overviews after mutation.** `dashboard.html` and the root `index.html` are part of the same mutation as capture, review, promote, publish, digest, decide, note-end, present, report, and ritual flows.
8. **Never mutate silently.** The response must make the action mode obvious: read-only analysis, proposed mutation, or applied mutation.
9. **Task creation and closure are explicit.** Propose task lines when material is actionable; do not add or archive them silently. External completion signals can reconcile tasks, but archival still needs confirmation.
10. **Next steps are mandatory.** End every response with 1–3 concrete follow-ups.
11. **Offer commit/push/PR after substantive change.** Respect branch protection and never force-push silently.

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
| Roadmap (draft) | `/kb roadmap [...]` | Hand off to `kb-roadmap` for plan-vs-delivery reconciliation; refuse if the active layer has no `roadmap:` block |
| Journeys (draft) | `/kb journeys [...]` (alias `/kb journey`) | Hand off to `kb-journeys` for journey authoring + render; refuse if the active layer has no `journeys:` block |

Roadmaps and journeys are product-management primitives, but they stay layer-owned. If a user asks for roadmap or journey work and the current layer has no matching block, route them to `/kb setup` or the expert config path so they can choose whether the artifact belongs in a personal, team, org, or other contributor layer. Do not silently choose a layer for them.

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
3. determine whether any promoted decision or task becomes canonical in the target layer or remains a distinct source-layer item,
4. complete the destination-layer review immediately,
5. write the durable result into the destination references or shared primitive,
6. archive the staged intake under the year-based digested path,
7. close or archive superseded source-layer decisions/tasks when the target layer owns the same scope, and
8. log both the intake and the reviewed result in the destination layer.

When the selected target is `role: consumer`, refuse and point to the next valid contributor layer.

## Templates

The templates this skill instantiates live in `templates/`:

- `finding.md`, `topic.md`, `decision.md`, `idea.md`, `note.md`, `workstream.md`
- `brief.md`, `spec.md`, `release.md`, `incident.md`
- `focus.md`, `backlog.md`
- `index.html`, `artifact-base.html`, `report.html`
- workspace and KB scaffolding templates supplied by `kb-setup`
- `.kb-config/layers.yaml`, `.kb-config/automation.yaml`, `.kb-config/artifacts.yaml`

## References (load on demand)

- `references/spec-summary.md` — condensed architecture and workspace layout.
- `references/command-reference.md` — full subcommand details.
- `references/connections-lifecycle.md` — connection declaration, watermarks, drift checks, and write-back.
- `references/promote-contract.md` — staged-review semantics for `/kb promote`.
- `references/publish-contract.md` — marketplace packaging, safety validation, and publish response contract.
- `references/rituals.md` — the four rituals in detail.
- `references/html-artifacts.md` — presentation/report generation contract.
- `references/evaluation-gate.md` — the five-question filter, in depth.
- `references/output-contract.md` — collaboration-safe wording and examples.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-06 | Version aligned to 5.6.0 after adding the decision/task promotion ownership rule: promoted decisions and tasks now get one canonical owning layer, and source-layer records are closed or archived unless their scope genuinely differs | Decision/task ownership follow-up |
| 2026-04-30 | Version aligned to 5.5.0 after making roadmap and journey work a setup-proposed product-management surface. Added natural-language product roadmap/journey triggers and clarified that missing config should route to setup/placement rather than silent scaffolding | Product-management surface integration |
| 2026-04-29 | Closed the draft-skill discoverability gap: added `roadmap`/`roadmaps`/`journey`/`journeys` to the trigger surface and a flow-primitive row that names the `/kb roadmap` and `/kb journeys` handoffs to the kb-roadmap and kb-journeys draft skills. Skill version aligned to 5.4.2 | v5.4.2 draft-skill discoverability fix |
| 2026-04-27 | Skill version aligned to 5.4.1 after the documentation-gap follow-up. Behavioral surface unchanged; new connection lifecycle and publish contract details live in dedicated references | 5.4.1 patch release |
| 2026-04-27 | Added load-on-demand references for connection lifecycle and publish contract details so the behavioral spec can stay concise while the edge-case and packaging rules live in dedicated docs | Documentation gap follow-up |
| 2026-04-27 | Skill version aligned to 5.4.0 for the soft-transition extension. No behavioral changes here — adoption-stage logic lives in `kb-setup`; this skill just continues to honor the "When to invoke" + Stage-2 confirmation rule it already declares | Soft-transition extension |
| 2026-04-26 | Added delivery/operations artifact coverage to the behavioral surface: `brief`, `spec`, `release`, and `incident` now count as feature keywords, and the template list now includes their standard markdown shapes | Software-engineering operating-model gap closure |
| 2026-04-25 | v5.2.0: expanded the `triggers:` list to cover every first-class feature keyword (findings, decisions, workstreams, vmg, meeting notes, sparring, briefings, daily/weekly summaries, progress reports, migrations) so harnesses fire the skill on natural-language feature mentions, not only on the literal `/kb` command. Added an explicit "When to invoke" rule that requires the response to name the inferred `/kb …` flow and ask for confirmation before any mutation when the user did not type `/kb` directly | Trigger surface expansion |
| 2026-04-25 | Clarified that consumer layers may receive digests but are never promote/publish targets, and added an explicit promote-contract reference for staged review semantics | Deep spec-audit follow-up |
| 2026-04-25 | Added the explicit 5.1 migration-helper surface (`/kb migrate archives`, `/kb migrate layer-model`) and aligned the declared skill version with the closeout release | v5.1.0 closeout release |
| 2026-04-25 | Reworked the behavioral spec for 5.0.0: `/kb` now operates on a flexible layer graph, notes became first-class, digests can read declared connections, and publish targets per-layer marketplaces instead of a fixed L4 | v5.0.0 flexible layer model |
| 2026-04-25 | Version aligned to 4.0.0 for the v4.0.0 framework release (composite `/kb promote` semantics + mandatory artifact preflight/QA contract) | v4.0.0 release alignment |
| 2026-04-25 | Added explicit preflight-fetch summaries for artifact-driving external reads and a mandatory post-generation HTML QA sweep; bumped declared skill version to 3.5.0 | Generic learnings extracted from live roadmap and presentation feature work |
