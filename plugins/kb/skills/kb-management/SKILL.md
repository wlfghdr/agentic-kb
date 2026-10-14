---
name: kb-management
description: Lean, layered knowledge management driven by the `/kb` command. Operates on a flexible layer graph, applies the five-question evaluation gate, tracks findings, notes (including retros), decisions, ideas, tasks, briefs, specs, releases, and incidents as first-class artifacts, digests connected repos and trackers, and publishes reusable skills to per-layer marketplaces.
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
  - "retro"
  - "retrospective"
  - "post-mortem"
  - "postmortem"
  - "sprint retro"
  - "post-incident retro"
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
  # Product-management handoff (route to kb-roadmap / kb-journeys)
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

Concurrency contract: [`docs/concurrency.md`](../../../../docs/concurrency.md) defines the promote-collision, diverged-backlink, topic-merge, and append-only log cases that `/kb sync` and `/kb audit` reconcile.

## Core rules

1. **Run the evaluation gate before persistence.** Score material against the five gate questions. The score is the count of yes answers. Q4 + Q2 form the lighter note gate.
2. **Set and preserve maturity.** New findings and topics must carry `**Maturity**:`. `raw` means weak or single-signal, `emerging` means accepted and worth revisiting, `durable` means ready to promote or cite broadly.
3. **Respect the layer graph.** `promote` walks upward through `parent`; `digest` walks downward from parent or from `connections`. A `role: consumer` layer is read-down only: it may receive digests, but it is never a `promote` or `publish` target.
4. **Keep contributor-scoped and shared artifacts distinct.** Inputs, findings, ideas, and strategy digests stay contributor-scoped by default on multi-user layers. Decisions, tasks, workstreams, foundation files, reports, delivery artifacts, operations artifacts, and meeting notes are shared unless the layer config says otherwise. This visibility rule is separate from the layer `role`.
5. **Keep decisions and tasks canonical to one owning layer and one storage backbone.** When promoting a decision or task, determine whether the target layer now owns the same scope and accountable decider/owner. If yes, close, archive, or replace the source item with a backlink; keep two active records only when their scopes, recommendations, accountable owners, or sub-task responsibilities differ. When the target layer declares `primitive-storage` with `mode: tracker`, propose or update the configured tracker item instead of creating a competing canonical KB file.
6. **Log every operation.** Write to `.kb-log/YYYY-MM-DD.log` or `.kb-log/YYYY/YYYY-MM-DD.log` in the canonical `HH:MM:SSZ | operation | scope | target | details` format.
7. **Regenerate live overviews after mutation.** `dashboard.html` and the root `index.html` are part of the same mutation as capture, review, promote, publish, digest, decide, note-end, present, report, and ritual flows.
8. **Never mutate silently.** The response must make the action mode obvious: read-only analysis, proposed mutation, or applied mutation.
9. **Task creation and closure are explicit.** Propose task lines when material is actionable; do not add or archive them silently. External completion signals can reconcile tasks, but archival still needs confirmation.
10. **Next steps are mandatory.** End every response with 1–3 concrete follow-ups.
11. **Offer commit/push/PR after substantive change.** Respect branch protection and never force-push silently.
12. **Capture target is the active layer unless explicit or confirmed.** Every `/kb [text/URL/path]` invocation picks one of three routing modes: (a) **default** — capture into the active layer (the anchor unless context already selected a different contributor-capable layer); (b) **explicit** — the user named a target layer in the invocation, or a `capture-routing:` rule in `.kb-config/layers.yaml` matches the input; (c) **reflection-driven** — the input's content/source/context matches the strong-signal rubric in `references/capture-routing.md` for a non-default contributor-capable layer. Mode (c) requires explicit human confirmation **before** the mutation; no soft-write to a staging area as a fallback. Weak or ambiguous signals fall through to default. A previous confirmation does not give the agent standing permission for future captures — the supported way to make a target sticky is a `capture-routing:` rule, not implicit memory. The response must name the routing mode and, for mode (c), present the proposed target with a one-line reason and offer the default as a fallback. Direct routing is parallel to `/kb promote`, not a substitute: promote moves material that matured upward; direct capture skips a private→shared hop when the destination was clear from the start. Full contract: `references/capture-routing.md`.

## Layer-aware flow primitives

| Flow | Command | What it does |
|------|---------|--------------|
| Capture | `/kb [input]` | Assess via gate; write finding or note; update topic/decision; route to workstream. Destination follows rule 12: default = active layer; explicit when the user names a target or a `capture-routing:` rule matches; reflection-driven targets require human confirmation before mutation |
| Review | `/kb review` | Process all pending items in `_kb-inputs/` |
| Promote | `/kb promote [file] [layer]` | Promote to a named contributor-capable layer, or the next contributor-capable parent layer |
| Publish | `/kb publish [file] [layer]` | Package reusable knowledge as a skill and publish it to the target layer marketplace |
| Digest layer | `/kb digest [layer]` | Pull changes from a parent or adjacent layer |
| Digest connections | `/kb digest connections` | Pull deltas from configured product repos and trackers |
| Sync | `/kb sync [layer]` | Cross-reference contributor-scoped topics or findings; reconcile promote conflicts, diverged backlinks, and unresolved topic author-sections per [`docs/concurrency.md`](../../../../docs/concurrency.md) |
| Diff | `/kb diff [layer]` | Show new material per contributor or connection |
| Migrate | `/kb migrate archives` / `/kb migrate layer-model` | Preview or apply legacy archive and layer-model migrations |
| Task | `/kb task` / `/kb task done [item]` | Manage focus/backlog |
| Note | `/kb note [text]` / `/kb note meeting [topic]` / `/kb note retro [topic]` / `/kb note end` | Capture general, meeting, or retro notes and surface follow-on changes. The retro variant uses the structured what-went-well / what-didn't / changed / will-change / open-questions / linked-artifacts shape and must produce tracked commitments (tasks or decisions) before it is considered closed |
| Idea | `/kb idea [text]` | Create a seed idea |
| Develop | `/kb develop [idea]` | Spar on assumptions, contradictions, and convergence |
| Decide | `/kb decide [desc]` / `/kb decide resolve [D-id]` | Open or resolve a decision |
| Brief | `/kb brief [title]` | Open a delivery-intent artifact under `_kb-delivery/briefs/`; requires `delivery` feature on the layer |
| Spec | `/kb spec [title]` | Open a design-contract artifact under `_kb-delivery/specs/`; requires `delivery` feature on the layer |
| Release | `/kb release [title]` | Open a release record under `_kb-operations/releases/YYYY/`; requires `operations` feature on the layer |
| Incident | `/kb incident [title]` | Open an incident record under `_kb-operations/incidents/YYYY/`; requires `operations` feature on the layer |
| Present | `/kb present [topic/file]` | Generate a versioned HTML presentation |
| Report | `/kb report [scope]` | Generate a layer or topic report |
| Progress report | `/kb report progress [scope]` | Generate the multi-source progress narrative |
| Rituals | `/kb start-day`, `/kb end-day`, `/kb start-week`, `/kb end-week` | Run composed briefings and summaries |
| Audit | `/kb audit` | Check contradictions, staleness, gaps, and layer-shape drift |
| Status | `/kb status` | Report pending work, connection drift, tasks, and recent activity |
| Roadmap | `/kb roadmap [...]` | Hand off to `kb-roadmap` for plan-vs-delivery reconciliation; refuse if the active layer has no `roadmap:` block |
| Journeys | `/kb journeys [...]` (alias `/kb journey`) | Hand off to `kb-journeys` for journey authoring + render; refuse if the active layer has no `journeys:` block |

Roadmaps and journeys are product-management primitives, but they stay layer-owned. If a user asks for roadmap or journey work and the current layer has no matching block, route them to `/kb setup` or the expert config path so they can choose whether the artifact belongs in a personal, team, org, or other contributor layer. Do not silently choose a layer for them.

When a flow creates or updates a primitive covered by `primitive-storage`, resolve the storage mode before writing:

- `files`: write the normal KB artifact or task file.
- `tracker`: propose a tracker item/comment/link/status update using the configured tracker kind/type; after confirmation, write only summaries, backlinks, reports, or archive context to the KB.
- `hybrid`: write the early KB artifact first, then offer promotion to the configured tracker when the item crosses the layer's sharing boundary.

If the config is ambiguous or both a KB file and tracker item claim canonical ownership, stop and propose an audit/cleanup step before mutation.

For `tracker` operations, apply the capability precedence from `references/tracker-backed-primitives.md`: `primitive-storage` selects canonical ownership; the named tracker must declare the operation in `capabilities`; authentication/tooling must be available through canonical `auth-env` or documented ambient authentication; and the user must confirm that exact mutation. For a pre-7.0 unambiguous live adapter whose capability field is absent, apply the reference's temporary normalization and surface its migration warning; explicit empty lists plus generic/export-backed/custom adapters remain read-only. `connections.writeback` governs only reserved connection-digest write-back and cannot enable canonical CRUD. Ownership failure follows the configured canonical home without proposing a noncanonical tracker mutation. After ownership succeeds, missing capability or authentication produces a complete manual proposal and waits for the resulting tracker identifier; no path creates a competing canonical KB record.

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

- `finding.md`, `topic.md`, `decision.md`, `idea.md`, `note.md`, `retro.md`, `workstream.md`
- `brief.md`, `spec.md`, `release.md`, `incident.md`
- `focus.md`, `backlog.md`
- `index.html`, `artifact-base.html`, `report.html`
- workspace and KB scaffolding templates supplied by `kb-setup`
- `.kb-config/layers.yaml`, `.kb-config/automation.yaml`, `.kb-config/artifacts.yaml`

## References (load on demand)

- `references/spec-summary.md` — condensed architecture and workspace layout.
- `references/command-reference.md` — full subcommand details.
- `references/connections-lifecycle.md` — connection declaration, watermarks, drift checks, and write-back.
- `references/tracker-backed-primitives.md` — generic tracker-backed decisions, tasks, ideas, feedback, intake, routing, and audit pattern.
- `references/capture-routing.md` — destination-layer routing modes for `/kb` capture: default / explicit / reflection-driven, the human-confirmation gate, and the `capture-routing:` config schema.
- [`docs/concurrency.md`](../../../../docs/concurrency.md) — shared-layer concurrency contract for promote collisions, backlink divergence, topic merges, and append-only logs.
- `references/promote-contract.md` — staged-review semantics for `/kb promote`.
- `references/publish-contract.md` — marketplace packaging, safety validation, and publish response contract.
- `references/rituals.md` — the four rituals in detail.
- `references/html-artifacts.md` — presentation/report generation contract.
- `references/evaluation-gate.md` — the five-question filter, in depth.
- `references/output-contract.md` — collaboration-safe wording and examples.
