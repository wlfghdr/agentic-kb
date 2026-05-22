---
name: kb-setup
description: Interactive onboarding wizard that scaffolds an agentic-kb workspace around a flexible layer graph. Asks the user about their context, goals, audience, sources, and desired outputs first, derives a proposed layer graph and feature set including tracker-backed primitive ownership and product-management roadmap/journey placement when relevant, then creates or onboards layer repos, writes the anchor-layer config, configures documented harness workflows, and generates the required templates, indexes, tracker setup artifacts, and HTML style references.
version: 6.1.0
triggers:
  - "/kb setup"
  - "setup kb"
  - "init kb"
  - "init knowledge"
  - "onboard kb"
  - "bootstrap workspace"
  - "create kb"
  - "scaffold knowledge base"
  - "set up agentic-kb"
  - "start agentic-kb"
  - "first time using kb"
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

# Skill: KB Setup

This skill is the single entry point for bootstrapping an `agentic-kb` workspace. It is idempotent: reruns add missing pieces, propose graph extensions, and never overwrite existing material without confirmation.

## Scope boundary — install vs. init

This skill **initializes the user's KB workspace**. It does **not** distribute itself.

Two concerns, two tools:

| Concern | Who handles it | When |
|---------|---------------|------|
| Get `kb-management` + `kb-setup` + `kb-operator` into the harness | Marketplace install or `scripts/install.py` | Before this skill runs |
| Scaffold the user's layer repos, config, and workspace indexes | **This skill** | When the user types `/kb setup` |

## When to invoke

- The user types `/kb setup`.
- The user says they want to set up, bootstrap, or onboard a KB workspace.
- `kb-management` detects no `.kb-config/layers.yaml` in the current workspace and the user tries any `/kb` command.

## Interactive question flow

The interview is **goal-oriented, not feature-list-driven**. Phase 1 collects the minimum admin facts the wizard cannot infer (workspace root and harness — frontloaded so the user knows where files will land before they invest in long answers); phase 2 asks the user about their world in their own language; phase 3 shows a derived plan and lets the user adjust before anything is written.

Ask each block in order. Stop and wait after each block for the user's answer before proceeding. Never ask the user to enumerate layers, features, contributor-mode flags, or scopes in phase 2 — those are derived in phase 3 and only adjusted there.

### Phase 1 — Workspace and harness facts (short admin, frontloaded)

This phase runs first so the user always knows which directory the scaffold will land in and which harness will host `/kb` before they invest in open-ended answers. Wrong harness or wrong workspace root caught here is a one-line fix; caught after phase 2 it is sunk-cost frustration.

1. **Workspace root** — absolute path; default current directory. Confirm with the user before continuing if the current directory looks accidental (e.g. `~/Downloads`, a non-git directory the user did not expect).
2. **IDE targets** — multi-select from `claude-code`, `vscode`, `opencode`, `codex`, `gemini`, `kiro`. Used by `scripts/install.py` to decide where harness hooks are written (`.claude/commands/`, `.github/prompts/`, `.agents/skills/`, etc.). The right answer here prevents a silent "No KB detected" later.
3. **Discovery pass** — scan the workspace for existing KB repos, harness hooks, and likely layer candidates. Also probe for repo-as-OS structures (e.g. `work/signals/`, `work/missions/`, `org/<layer>/`, `CONFIG.yaml`, `CODEOWNERS` with policy directories). If a repo-as-OS structure is detected, surface it before phase 3 so the proposal can reuse existing repos and propose bridge defaults instead of inventing parallel structure.

### Phase 2 — Context and goals (open-ended)

Question count continues from phase 1 (Q4–Q11 global numbering, as listed in the placeholder mapping section below).

1. **Who you are** — name, role, and one sentence about the work you actually do day to day. Used for `foundation/me.md` and contributor directories.
2. **What you're trying to track or decide** — open prose. The wizard extracts themes (3–5 keywords) and workstream candidates from this answer; do not ask for keywords or workstream names directly.
3. **Why now** — what triggered this setup? "Too many directions to keep track of", "leadership keeps asking for status", "starting a new quarter", "team is drifting", etc. Used to bias which artifacts (briefings, weekly status, progress reports, roadmaps) the proposed plan emphasizes.
4. **Who else needs to see what** — describe the audience in plain words: "just me", "me and one team", "two teams plus an org-unit lead", "a whole company". Used to derive layer count, scopes, and role boundaries (which higher layers should be `consumer` rather than `contributor`).
5. **Where information feeds in** — describe the sources the user already reads from: product repos, issue trackers, dashboards, recurring meetings, stakeholder reports, exports. Also listen for whether any issue tracker is already the operational backbone for decisions, tasks, feature intake, roadmap items, or team commitments. Used to derive `connections:` and `primitive-storage:` per layer and to decide whether the lean export-backed roadmap path applies.
6. **What you want out** — describe the artifacts that would actually save time: morning briefing, weekly status to share with a boss, presentations, progress reports, roadmap reconciliation, journey specs, customer-value roadmaps, phase/lane plans, journey maps, or mock-backed flow specs. Used to derive enabled features (`reports`, `roadmaps`, `journeys`) and dashboard panels.
7. **How autonomous** — describe how hands-on or hands-off the user wants the agent: "I want to confirm everything", "process the obvious stuff and ask me on edge cases", "run on its own and tell me what changed". Mapped to automation levels 1 (manual only), 2 (scheduled rituals/digests), or 3 (scheduled flows plus guarded auto-promote); see `references/automation-levels.md` for the full contract. Note: `agentic-kb` does not ship a scheduler — at level 2/3 the user wires OS cron, CI, or their harness's native automation to invoke `/kb`.
8. **Operating context today, and target in 6 months** — pick one bucket for *today* and (optionally) one for *6 months out*: (a) **human-only / capture discipline first** — no agents in the workflow yet; goal is to get the artifact chain steady before adding any automation; (b) **repo-as-OS framework already in use** — the team already runs signals/missions/PRs or similar git-as-source-of-truth governance; agentic-kb slots in as the knowledge-ops layer; (c) **already running AI agents in daily work** — agents draft, triage, or act; goal is to ground them in shared context. This is mapped to **adoption stages 1 / 2 / 3** (see `references/adoption-stages.md`); answers steer the proposed scaffold scope and automation level so the user does not get a Stage-3 setup when they are starting at Stage 1, and does not get a Stage-1 setup when they are already past it.

### Phase 3 — Proposed plan (system shows, user adjusts)

The wizard presents a single concrete proposal derived from phase 1 + 2. The user reviews, adjusts inline if needed, and confirms. Do not ask the user to author the plan from scratch.

1. **Proposed layer graph and adoption stage** — show the derived layers as a single block: name, scope, role, parent, path, and enabled features per layer. Highlight which layer will be the anchor and label the proposed **adoption stage** (1 / 2 / 3) derived from Q11 + Q10 so the user can see at a glance whether the wizard is suggesting a capture-only scaffold, an agent-assisted scaffold, or a bounded-autonomous scaffold. Default for a new solo user starting at Stage 1: one contributor anchor layer (scope `personal`), no roadmap/journey features unless Q4/Q5/Q9 explicitly call for them, automation level 1, no `connections:` write-back. If Q4/Q5/Q9 mention product management, sequencing, customer journeys, launch planning, portfolio status, or stakeholder roadmap communication, propose `roadmaps` and/or `journeys` on the layer whose audience owns that work and label the placement as adjustable. Default for a team already on a repo-as-OS framework: one shared contributor layer plus a `connections.product-repos[]` entry pointing at the existing governance repo. Ask only one yes-or-adjust question on this block; route deeper edits through targeted follow-ups (rename, add/remove a layer, flip role, change parent, change stage, move roadmaps/journeys to another layer).
2. **Proposed connections, primitive storage, artifacts, and automation** — show the derived `connections:` per layer (sources from Q8, plus any repo-as-OS product-repo detected in Q3), the `primitive-storage:` decision for decisions/tasks/ideas/feature intake/roadmap items (`files`, `tracker`, or `hybrid`), the dashboard panels and report types that match Q9 outputs, the automation level from Q10 (1 / 2 / 3 per `references/automation-levels.md`), and any product-management feature blocks (`roadmaps`, `journeys`) that the requested artifacts imply. For each tracker-backed primitive, show the tracker provider, repo/project/key/query parameters known so far, the configured kind/type, the supporting KB summary directory, write-back mode, and the setup artifacts to generate. For each roadmap/journey block, show the chosen owning layer, source inputs, output directories, and whether the first proof path is export-backed or live-adapter-backed. For every multi-user layer, also surface the **default artifact visibility** per enabled primitive (e.g. "findings, ideas, topics → contributor-scoped; decisions, tasks, foundation, reports → shared") per `docs/REFERENCE.md` §1 "Two orthogonal axes", so the user can flip visibility before scaffold rather than discovering the default by surprise. Same single yes-or-adjust prompt; collect provider-specific missing values through targeted follow-ups instead of adding a new global interview phase.
3. **Proposed graduation criteria for the next stage** — name the 2–3 concrete things the user would need before safely advancing to the next adoption stage (e.g. "≥ 4 weeks of clean `.kb-log/` entries, one cross-layer promote completed, foundation/vmg.md confirmed by stakeholders" before turning on automation level 2). The user can accept, edit, or skip this block; it is informational and does not block scaffold.
4. **HTML artifact styling** — builtin, website-derived, or template-based corporate design. Default to `builtin` when Q3 does not mention external branding constraints.

### Phase 4 — Confirm and scaffold

1. **Final confirmation** — restate the chosen plan in one short summary: number of layers, anchor, audiences, adoption stage, automation level, IDE targets, which primitives are file-backed vs tracker-backed, where files will land, and which tracker setup package will be generated. Proceed to "What setup does after confirmation" only after explicit yes.

If the user wants to skip phase 2 entirely and author the plan directly, accept that and route to a compact expert path: ask the layer list with name/scope/role/parent/features/marketplace per layer, anchor, workstreams, automation, styling, IDE targets. Phase 1 (workspace root, IDE targets) is never skipped — the wizard needs both before it can write anything. Document this as the legacy entry point; the goal-oriented flow is the default.

## What setup does after confirmation

### Step 1 — Prerequisites

Required:

| Tool | Check | Abort message if missing |
|------|-------|--------------------------|
| `git` | `git --version` exits 0 | Install `git` first |
| At least one selected harness surface | binary or writable target path exists | Install the harness first or deselect it |

Recommended:

| Tool | Why |
|------|-----|
| `gh` | GitHub-native publish and issue flows |
| SSH key for the user's git host | Push without password prompts |

### Step 2 — Create or onboard repos

For each declared layer:

- create a new repo or onboard an existing one,
- initialize git when creating new repos,
- configure remotes only when the user asked for them,
- record the repo path in the anchor-layer `layers.yaml`.

### Step 3 — Scaffold each layer according to features

For every declared layer, create only the directories required by its enabled features.

Common files:

- `AGENTS.md`
- `README.md`
- `.kb-log/`
- `.nojekyll` when the layer will publish HTML
- `index.html` and `dashboard.html`

Feature directories:

- `inputs` → `_kb-inputs/` + `digested/YYYY/MM/`
- `findings` → `_kb-references/findings/YYYY/`
- `topics` → `_kb-references/topics/`
- `foundation` → `_kb-references/foundation/`
- `notes` → `_kb-notes/YYYY/`
- `delivery` → `_kb-delivery/briefs/` + `_kb-delivery/specs/`
- `operations` → `_kb-operations/releases/YYYY/` + `_kb-operations/incidents/YYYY/`
- `ideas` → `_kb-ideas/` + `archive/YYYY/`
- `decisions` → `_kb-decisions/` + `archive/YYYY/`
- `tasks` → `_kb-tasks/` + `archive/YYYY/`
- `workstreams` → `_kb-workstreams/`
- `reports` → `_kb-references/reports/`
- `roadmaps` → `_kb-roadmaps/`
- `journeys` → `_kb-journeys/`

When a primitive family is configured as `mode: tracker`, setup still creates the supporting KB directory only for summaries, reports, backlinks, or archived context. It must not seed a competing canonical backlog or decision list that would make the file and tracker both look authoritative.

For multi-user layers, shared primitives live at the repo root and contributor-scoped primitives are created under contributor or team directories.

### Step 4 — Write the anchor-layer config

Write `.kb-config/layers.yaml`, `.kb-config/automation.yaml`, and `.kb-config/artifacts.yaml` into the anchor layer.

The anchor config must include:

- `workspace.root`
- `workspace.user`
- `workspace.anchor-layer`
- `workspace.aliases`
- one `layers:` entry per declared layer
- optional `connections`, `marketplace`, `roadmap`, and `journeys` blocks per layer
- optional `primitive-storage` blocks per layer, mapping decisions, tasks, ideas, feature intake, and roadmap items to `files`, `tracker`, or `hybrid` ownership

When Q4/Q5/Q9 indicate product-management work, setup should propose these blocks rather than waiting for the user to know the feature names. The user still confirms placement. The conservative default is to co-locate a roadmap scope with the journeys it cites in the same contributor-capable layer. Layered roadmaps and journeys are allowed by the layer graph, but setup should mark cross-layer roll-ups/inheritance as a later enhancement unless the user explicitly asks for an expert configuration.

When Q5 or discovery indicates an existing tracker backbone, setup should propose `primitive-storage` instead of assuming file-backed decisions and tasks. Conservative defaults:

- personal or private layers: `files` for decisions, tasks, and ideas,
- shared layers without an existing tracker process: `files`, with a note that tracker backing can be added later,
- shared layers with an existing tracker process: `tracker` for tasks and feature intake, `tracker` or `hybrid` for decisions and ideas depending on whether the user wants early deliberation in files,
- roadmap items: `tracker` only when the roadmap source is already tracker-scoped; otherwise keep roadmap artifacts file-backed and read tracker data as evidence.

### Step 4b — Configure tracker backbone setup artifacts

If any `primitive-storage` entry uses `mode: tracker` or `mode: hybrid`, setup must generate or guide the selected tracker setup package.

For GitHub-backed trackers, setup writes or proposes the GitHub governance profile described in `references/github-governance-profile.md`:

- `.github/ISSUE_TEMPLATE/config.yml`,
- one issue form per configured kind/type,
- `.github/PULL_REQUEST_TEMPLATE.md`,
- `.github/labeler.yml`,
- `.github/workflows/kb-github-governance.yml`,
- a repo-local `agent-skills/kb-tracker-workflow/SKILL.md` (or the harness-equivalent skill location),
- `GITHUB_GOVERNANCE_SETUP.md` with the manual checklist for native issue types, project/status fields, milestones, labels, branch protection, CODEOWNERS, parent/sub-issues, and required checks that cannot be represented fully as files.

For Jira-backed trackers, setup writes or proposes:

- the `connections.trackers[]` project/query/type/status mapping,
- the `primitive-storage` mapping,
- a repo-local tracker workflow skill,
- a manual checklist for project fields, workflow states, issue types, and link policy.

For any tracker provider, setup refuses to perform write-back unless `writeback.enabled` and the provider capabilities are explicitly confirmed. Missing CLI authentication should downgrade to file generation plus manual setup instructions, not a half-configured tracker.

### Step 5 — Configure harnesses

Write only the harness hooks needed for the selected surfaces:

- VS Code → `.github/prompts/kb.prompt.md` and `.github/instructions/kb.instructions.md`
- Claude Code → `.claude/commands/kb.md`
- OpenCode → `.opencode/commands/kb.md`
- Codex → `.agents/skills/kb/SKILL.md`
- Gemini → `.gemini/commands/kb.toml`
- Kiro → `.kiro/skills/kb/SKILL.md`

Never reinstall into a surface that is already up to date unless the user asked for `--force` behavior.

### Step 6 — Verify

Minimum verification sequence:

1. scan for unresolved placeholders,
2. generate `index.html` and `dashboard.html` for every layer,
3. run `/kb status` in the anchor layer,
4. run `/kb start-day` in the anchor layer,
5. if a team or org layer exists, prove one promote or digest path,
6. if `roadmaps` or `journeys` are enabled, render their dry-run outputs,
7. if any tracker-backed primitive is configured, validate that each `primitive-storage.*.tracker` points to a declared tracker, that required issue forms or type-mapping instructions exist for GitHub/Jira selections, and that no write-back capability is enabled without the matching confirmation gate.

### Step 7 — First win + next-steps shortlist

Verification proves the scaffold is correct. It does not prove the workspace *does anything yet*. Step 7 closes that gap so the user leaves setup with a visible artifact and a curated 3–5 command shortlist, not with a read-only "Setup: OK" message and a 33-command flatlist.

**7a — Optional bootstrap capture (default yes).** Ask one question:

> *"Want to capture a first piece of material right now? Paste a URL, a file path, or short text. Skip with `no` if you'd rather start clean."*

If the user answers with content, route it through the full `kb-management` flow (evaluation gate → finding under `_kb-references/findings/YYYY/` or skip with logged reason → topic update if score ≥ 3 → `.kb-log/` entry → regenerate `index.html` and `dashboard.html`). Emit the resulting artifact path back to the user explicitly:

> *"Wrote `alice-personal/_kb-references/findings/2026-05-18-caches-and-invalidation.md` (gate score 3/5). `alice-personal/index.html` updated. Open it in your browser to see your first KB artifact live."*

If the user answers `no` or skips, write a `_kb-log/setup-skipped-bootstrap.md` line and continue. The capture is optional, not required for setup to count as complete.

**7b — Curated next-steps shortlist.** Emit a priorized 3–5 command list, derived from the chosen adoption stage (Q11) and audience (Q7). Do not paste the full 33-command surface; pick what this user should actually try first. Suggested patterns:

| Stage × audience | Shortlist (in this order) |
|------------------|---------------------------|
| Stage 1, solo | `/kb capture <text-or-URL>` · `/kb note meeting <topic>` · `/kb review` · `/kb start-day` |
| Stage 1, multi-user | `/kb capture …` · `/kb note meeting …` · `/kb decide …` · `/kb promote <file> <layer>` · `/kb end-week` |
| Stage 2, solo | `/kb capture …` · `/kb review` · `/kb decide …` · `/kb digest <layer>` · `/kb start-day` |
| Stage 2, multi-user | `/kb capture …` · `/kb review` · `/kb promote …` · `/kb digest …` · `/kb end-week` |
| Stage 3 (any) | `/kb status` · `/kb digest <layer>` · `/kb audit` · `/kb end-week` (the user owns the scheduler trigger that fires the rest, per `automation-levels.md`) |

Adjust if Q9 ("what you want out") names roadmaps or journeys — insert `/kb roadmap` and/or `/kb journeys` after capture. Adjust if Q9 names release/incident artifacts — insert `/kb release` and/or `/kb incident`.

The shortlist is informational, not blocking. The user can always invoke any of the 33 commands; the full surface is documented in [`plugins/kb/commands/kb.md`](../../commands/kb.md) and [`plugins/kb/skills/kb-management/references/command-reference.md`](../kb-management/references/command-reference.md).

**7c — Closing message.** Emit one short summary, in plain language, naming exactly what was produced and what the user should do next. Example for Stage 1 solo with a bootstrap capture:

> *"Setup complete. `alice-personal` is your anchor layer; `team-observability` is the contributor target for promotions. You wrote your first finding (`_kb-references/findings/2026-05-18-...md`), and `index.html` reflects it. Try these next: `/kb capture <text>` to file more material, `/kb start-day` for a morning briefing, `/kb note meeting <topic>` before your next sync. Run `/kb status` any time to see where you stand."*

Adapt the wording to the actual scaffold, but keep three properties: (a) one short paragraph, not a wall of text; (b) name the actual artifact paths the user can open; (c) name 3 commands max in the closing, even if the full shortlist is longer.

**7d — Ritual cadence reminder (level 1 only).** If automation level is `1`, append a second short paragraph naming the rituals that the user must trigger themselves and the recommended cadence. `agentic-kb` does not ship a scheduler (see `references/automation-levels.md` "Scheduler ownership") — at level 1 there is no scheduler at all, so the user is the only thing that pulls the trigger.

The closing message includes:

> *"Rituals are manual at level 1. Suggested cadence: `/kb start-day` each morning, `/kb end-day` before you stop, `/kb end-week` on Friday afternoon. `/kb status` is safe to run any time. If a ritual gets forgotten, the next `/kb start-day` reconciles missing days from `.kb-log/` and git diff — but the more consistent you are early on, the cleaner the daily/weekly summaries get."*

Setup also offers two optional artifacts to make the cadence stick:

1. **Calendar reminder snippet** — on user opt-in, write `_kb-references/rituals.ics` with `start-day`, `end-day` (M–F), and `end-week` (Fri 15:00) events the user can drop into their calendar.
2. **Repeat hint in `/kb status`** — `kb-management` already surfaces "missing today's `start-day`" under the "Rituals" triage signal (see [`plugins/kb/skills/kb-management/references/command-reference.md`](../../skills/kb-management/references/command-reference.md) "Triage scan"). At level 1, the closing message points the user at `/kb status` as the explicit nudge channel.

When automation level is `2` or `3`, this block is replaced by the scheduler-ownership reminder (already covered in `references/automation-levels.md` "Scheduler ownership"): the user owns the cron/CI/harness-native trigger that fires the scheduled rituals.

## Migration mode

If the user points setup at an older fixed-ladder KB:

1. analyze the current layout,
2. run `/kb migrate layer-model` in dry-run mode to preview the new layer graph,
3. map old L1/L2/L3/L4/L5 references to named `layers:` entries,
4. run `/kb migrate archives` in dry-run mode to preview the year-based archive moves,
5. apply only after explicit confirmation.

## Idempotency

Running `/kb setup` again:

- detects existing repos and layer declarations,
- proposes only missing or changed pieces,
- offers to add a new layer without disturbing the current graph,
- never rewrites an existing file without confirmation.

## Safety

- Never overwrite existing files without explicit confirmation.
- Never create a remote repo without asking.
- Never push to a remote without asking.
- Never force personal-layer assumptions onto a team-only workspace.

## Placeholder mapping

Question references in this table use the global numbering: phase 1 covers Q1–Q3 (workspace root, IDE targets, discovery pass), phase 2 covers Q4–Q11 (the open-ended context block), phase 3 covers Q12–Q15 (proposal blocks the user adjusts or accepts), phase 4 covers Q16 (final yes).

The layer-graph scaffold uses double-curly setup placeholders for these token names:

| Token name | Source |
|------------|--------|
| `USER_NAME` | Q4 |
| `ROLE` | Q4 (role sentence extracted from the same answer) |
| `THEMES` | extracted from Q4/Q5 (3–5 keywords); rendered as a bullet list into `foundation/me.md` |
| `KB_NAME` | anchor-layer name (derived and confirmed in phase 3 question 1, i.e. Q12) |
| `WORKSPACE_ROOT` | Q1 |
| `WORKSTREAM_1_NAME`, `WORKSTREAM_1_THEMES` | extracted from Q5 (themes) and confirmed in phase 3 question 1 (Q12) |
| `WORKSTREAMS` | rendered list of all confirmed workstreams, including repeated workstream token groups, for `personal-kb-AGENTS.md` |
| `ADOPTION_STAGE` | derived from Q11 (today bucket); used in `automation.yaml` and the scaffolded `foundation/me.md` so the chosen stage is durable, not implicit |
| `AUTOMATION_LEVEL` | derived from Q10 + Q11 (1, 2, or 3 per `references/automation-levels.md`); written into `automation.yaml` |
| `TEAM_NAME`, `ORG_UNIT_NAME` | layer name from phase 3 question 1 (Q12) when the proposal includes a shared contributor or synthesis layer; used by the `team-kb-*` and `org-kb-*` templates |
| `REPO_INDEX`, `ALIAS_INDEX`, `KEYWORD_LOOKUP` | rendered from the discovered + confirmed repo set (Q3 + phase 3 question 1, Q12); used by `workspace-AGENTS.md` |
| `VMG_VISION`, `VMG_MISSION`, `VMG_GOALS` | populated by the VMG sourcing step (URL fetch, file read, or direct text per `references/setup-flow.md`); placeholders survive only if the user opts to fill VMG later, in which case a backlog item is created |
| `DATE` | today |
| `VERSION` | `1.0` on first scaffold |

Layer-specific repeated content beyond the anchor layer is rendered from the interview answers rather than from hard-coded placeholder names.

Substitution examples:

```yaml
# before substitution
workspace:
  anchor-layer: <KB_NAME placeholder>

# after confirmation
workspace:
  anchor-layer: alice-personal

# if the user deliberately defers VMG text
vision: "<VMG_VISION placeholder>"  # follow-up task required before setup is complete
```

The `notes` feature always includes general notes, meeting notes, and retros. Setup does not ask for those variants separately; it only decides whether the layer gets the `notes` feature at all. `/kb note retro [topic]` then uses the same `_kb-notes/YYYY/` directory as the other note variants.

## Post-write placeholder check

After writing the scaffold, scan the workspace for any remaining double-curly placeholder sequences outside the deliberate presentation-template placeholders. If any remain:

1. stop,
2. list the file and placeholder,
3. ask for the missing value,
4. re-render and rescan.

## References

- `references/setup-flow.md` — full step-by-step walkthrough with example output, including VMG sourcing and update guidance.
- `references/github-governance-profile.md` — generic GitHub issue/project/PR governance profile generated when GitHub is the tracker or repo workflow backbone.
- `references/automation-levels.md` — meaning of setup levels 1/2/3 and how they map into `automation.yaml`.
- `references/adoption-stages.md` — the human → agentic curve: Stage 1 (capture discipline) → Stage 2 (agent-assisted triage) → Stage 3 (bounded autonomous). Names what each stage scaffolds, the graduation criteria between stages, and how adoption stage and automation level relate.
- `references/migration-guide.md` — how to migrate an existing KB.
- `references/troubleshooting.md` — common setup issues.
- `../../../docs/examples/first-hour.md` — narrative onboarding walkthrough for new adopters (the user-facing companion to this skill).
- `../../../docs/first-run-acceptance.md` — deterministic acceptance baseline used by maintainers and team leads to verify rollout quality. **Not** the doc adopters read after first install — see `first-hour.md` for that.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-22 | Added Step 7d "Ritual cadence reminder (level 1 only)" — when automation level is `1`, the closing message names the manual ritual cadence (`/kb start-day` each morning, `/kb end-day` before stop, `/kb end-week` Friday afternoon) explicitly, points at `/kb status` as the in-tool nudge channel, and offers an optional `_kb-references/rituals.ics` calendar snippet. At level 2/3 the existing scheduler-ownership reminder fires instead. Closes audit finding #108 | Concept/spec gap audit |
| 2026-05-18 | Added Step 7 "First win + next-steps shortlist" — closing step after verification. Optional bootstrap capture (default yes) writes a first finding through the full evaluation gate and surfaces the artifact path back to the user; curated 3–5 command shortlist derived from adoption stage + audience replaces the implicit "you have 33 commands, gl hf" feeling at setup end. References section now names `docs/examples/first-hour.md` as the user-facing companion and reframes `docs/first-run-acceptance.md` as the maintainer/QA baseline. Closes audit findings #99, #100, #101 | Concept/onboarding/process audit |
| 2026-05-18 | Phase order swap: phase 1 is now "Workspace and harness facts" (Q1–Q3 — workspace root, IDE targets, discovery pass), phase 2 is now "Context and goals" (Q4–Q11). Frontloads the admin block so the user knows where files will land and which harness will host `/kb` before investing in long answers. All cross-references and the placeholder-mapping table renumbered. Q10 ("How autonomous") now states explicitly that `agentic-kb` does not ship a scheduler. Phase 3 block 2 must now surface default artifact visibility per primitive per `docs/REFERENCE.md` §1 "Two orthogonal axes". Closes audit findings #98 and #104 | Concept/onboarding/process audit |
| 2026-05-17 | Extended onboarding to decide per-layer primitive storage (`files`, `tracker`, `hybrid`) for decisions, tasks, ideas, feature intake, and roadmap items; setup now treats generic GitHub/Jira type mapping, issue templates, governance CI, labeler/PR templates, manual branch-protection/project setup, and repo-local tracker workflow skills as first-class outcomes when a tracker backbone is selected | Tracker-backed onboarding design |
| 2026-05-15 | Removed literal double-curly placeholder examples from the published setup skill so GitHub Pages can build the released docs while preserving the setup-token contract for agents | Pages release fix |
| 2026-05-15 | Skill version aligned to 6.1.0. Setup now documents that notes include general, meeting, and retro variants under one feature; delivery/operations scaffold directories are explicit; roadmap/journey blocks are stable setup-proposed features instead of draft-feature blocks; and placeholder substitution examples show confirmed and deliberately deferred values | Release-readiness audit |
| 2026-05-10 | Skill version aligned to 6.0.0 for the v5 adoption-arc closeout. No behavioral changes to the four-phase interview, scaffold output, or migration flow. The setup output contract picks up the new `/kb brief`, `/kb spec`, `/kb release`, and `/kb incident` verbs because the kb-management plugin it composes ships them as canonical flows; the templated `kb.prompt.md` was patched in lock-step to enumerate those subcommands and to drop the retired `SKILL.md rule #10c` cross-reference in favor of rule 8 | v6.0.0 adoption + daily-usage gap audit |
| 2026-05-05 | v5.5.1: closed the placeholder-mapping gap that had been silently broken since the goal-oriented + adoption-stage extensions. Documented the global Q-numbering convention, listed the previously-undocumented token names the templates emit (`THEMES`, `WORKSTREAMS`, `TEAM_NAME`, `ORG_UNIT_NAME`, `REPO_INDEX`, `ALIAS_INDEX`, `KEYWORD_LOOKUP`, `VMG_VISION`, `VMG_MISSION`, `VMG_GOALS`, `AUTOMATION_LEVEL`), and replaced the stale "Q12" wording with phase-3-question-1 wording so the table no longer reads as off-by-one | Onboarding consistency review |
| 2026-04-30 | Version aligned to 5.5.0 after making roadmap and journey work a setup-proposed product-management surface. Setup now derives roadmap/journey features from role/goals/outputs, asks which layer owns them, and writes matching config only after confirmation | Product-management surface integration |
| 2026-04-29 | Skill version aligned to 5.4.2 after the draft-skill discoverability fix. The packaged `kb.prompt.md` template now routes `/kb roadmap` and `/kb journeys` to the matching draft skills with a config-block check; this skill's setup-flow contract is unchanged | v5.4.2 draft-skill discoverability fix |
| 2026-04-27 | Skill version aligned to 5.4.1 after the documentation-gap follow-up. Clarified the repo-as-OS bridge field name to `connections.product-repos[]` and linked the setup-flow VMG sourcing/update guidance | 5.4.1 patch release |
| 2026-04-27 | Clarified the repo-as-OS bridge wording so the proposal names the current schema field `connections.product-repos[]`, and pointed the setup-flow reference description at the new VMG sourcing/update guidance | Documentation gap follow-up |
| 2026-04-27 | v5.4.0: added Q8 ("operating context today, and target in 6 months") to phase 1 so the wizard can bias the proposal to the team's adoption stage (1, 2, or 3) instead of forcing a Stage-3 scaffold on a Stage-1 team or vice versa; phase 2 discovery pass now also probes for repo-as-OS structures so the proposal can offer bridge defaults; phase 3 question 12 now labels the proposed scaffold with its adoption stage; phase 3 question 14 surfaces graduation criteria for the next stage. Added `references/adoption-stages.md` as the normative contract; subsequent question numbers renumbered. Skill version aligned to 5.4.0 | Soft-transition extension |
| 2026-04-25 | v5.2.0: replaced the feature-list-driven 12-block interview with a four-phase, goal-oriented flow. Phase 1 asks the user about their identity, what they track, why now, audience, sources, desired outputs, and autonomy preference in their own language; phase 2 collects only the workspace and harness facts that cannot be inferred; phase 3 presents one derived plan (layer graph, connections, artifacts, automation, styling) for inline adjust-or-confirm; phase 4 takes a single yes. The legacy "author the plan directly" path stays available as a compact expert mode. Q7 wording carries the automation-level contract added in #76 forward into the new flow | Goal-oriented onboarding |
| 2026-04-25 | Documented what automation levels 1/2/3 mean during setup and linked the interview step to a dedicated reference so adopters do not have to infer the contract from `automation.yaml` alone | Deep spec-audit follow-up |
| 2026-04-25 | Added the explicit 5.1 migration-helper handoff so setup now points legacy adopters at `/kb migrate layer-model` and `/kb migrate archives` instead of leaving those follow-ups implicit | v5.1.0 closeout release |
| 2026-04-25 | Reworked setup for 5.0.0: onboarding now discovers and scaffolds a flexible layer graph, supports team-only or multi-org adoption, writes per-layer marketplaces and connections, and scaffolds year-based archives plus notes | v5.0.0 flexible layer model |
| 2026-04-25 | Version aligned to 4.0.0 for the v4.0.0 framework release | v4.0.0 release alignment |
| 2026-04-22 | Added Codex CLI acceptance guidance and clarified the difference between first-class supported harnesses and compatible CLI workflows | Compatibility expansion |
