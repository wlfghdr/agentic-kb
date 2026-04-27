---
name: kb-setup
description: Interactive onboarding wizard that scaffolds an agentic-kb workspace around a flexible layer graph. Asks the user about their context, goals, audience, sources, and desired outputs first, derives a proposed layer graph and feature set, then creates or onboards layer repos, writes the anchor-layer config, configures documented harness workflows, and generates the required templates, indexes, and HTML style references.
version: 5.4.1
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

The interview is **goal-oriented, not feature-list-driven**. Phase 1 asks the user about their world in their own language; phase 2 collects the minimum admin facts the wizard cannot infer; phase 3 shows a derived plan and lets the user adjust before anything is written.

Ask each block in order. Stop and wait after each block for the user's answer before proceeding. Never ask the user to enumerate layers, features, contributor-mode flags, or scopes in phase 1 — those are derived in phase 3 and only adjusted there.

### Phase 1 — Context and goals (open-ended)

1. **Who you are** — name, role, and one sentence about the work you actually do day to day. Used for `foundation/me.md` and contributor directories.
2. **What you're trying to track or decide** — open prose. The wizard extracts themes (3–5 keywords) and workstream candidates from this answer; do not ask for keywords or workstream names directly.
3. **Why now** — what triggered this setup? "Too many directions to keep track of", "leadership keeps asking for status", "starting a new quarter", "team is drifting", etc. Used to bias which artifacts (briefings, weekly status, progress reports, roadmaps) the proposed plan emphasizes.
4. **Who else needs to see what** — describe the audience in plain words: "just me", "me and one team", "two teams plus an org-unit lead", "a whole company". Used to derive layer count, scopes, and role boundaries (which higher layers should be `consumer` rather than `contributor`).
5. **Where information feeds in** — describe the sources the user already reads from: product repos, issue trackers, dashboards, recurring meetings, stakeholder reports, exports. Used to derive `connections:` per layer and to decide whether the lean export-backed roadmap path applies.
6. **What you want out** — describe the artifacts that would actually save time: morning briefing, weekly status to share with a boss, presentations, progress reports, roadmap reconciliation, journey specs. Used to derive enabled features (`reports`, `roadmaps`, `journeys`) and dashboard panels.
7. **How autonomous** — describe how hands-on or hands-off the user wants the agent: "I want to confirm everything", "process the obvious stuff and ask me on edge cases", "run on its own and tell me what changed". Mapped to automation levels 1 (manual only), 2 (scheduled rituals/digests), or 3 (scheduled flows plus guarded auto-promote); see `references/automation-levels.md` for the full contract.
8. **Operating context today, and target in 6 months** — pick one bucket for *today* and (optionally) one for *6 months out*: (a) **human-only / capture discipline first** — no agents in the workflow yet; goal is to get the artifact chain steady before adding any automation; (b) **repo-as-OS framework already in use** — the team already runs signals/missions/PRs or similar git-as-source-of-truth governance; agentic-kb slots in as the knowledge-ops layer; (c) **already running AI agents in daily work** — agents draft, triage, or act; goal is to ground them in shared context. This is mapped to **adoption stages 1 / 2 / 3** (see `references/adoption-stages.md`); answers steer the proposed scaffold scope and automation level so the user does not get a Stage-3 setup when they are starting at Stage 1, and does not get a Stage-1 setup when they are already past it.

### Phase 2 — Workspace and harness facts (short admin)

1. **Workspace root** — absolute path; default current directory.
2. **IDE targets** — multi-select from `claude-code`, `vscode`, `opencode`, `codex`, `gemini`, `kiro`.
3. **Discovery pass** — scan the workspace for existing KB repos, harness hooks, and likely layer candidates. Also probe for repo-as-OS structures (e.g. `work/signals/`, `work/missions/`, `org/<layer>/`, `CONFIG.yaml`, `CODEOWNERS` with policy directories). If a repo-as-OS structure is detected, surface it before phase 3 so the proposal can reuse existing repos and propose bridge defaults instead of inventing parallel structure.

### Phase 3 — Proposed plan (system shows, user adjusts)

The wizard presents a single concrete proposal derived from phase 1 + 2. The user reviews, adjusts inline if needed, and confirms. Do not ask the user to author the plan from scratch.

1. **Proposed layer graph and adoption stage** — show the derived layers as a single block: name, scope, role, parent, path, and enabled features per layer. Highlight which layer will be the anchor and label the proposed **adoption stage** (1 / 2 / 3) derived from Q8 + Q7 so the user can see at a glance whether the wizard is suggesting a capture-only scaffold, an agent-assisted scaffold, or a bounded-autonomous scaffold. Default for a new solo user starting at Stage 1: one contributor anchor layer (scope `personal`), no draft features, automation level 1, no `connections:` write-back. Default for a team already on a repo-as-OS framework: one shared contributor layer plus a `connections.product-repos[]` entry pointing at the existing governance repo. Ask only one yes-or-adjust question on this block; route deeper edits through targeted follow-ups (rename, add/remove a layer, flip role, change parent, change stage).
2. **Proposed connections, artifacts, and automation** — show the derived `connections:` per layer (sources from Q5, plus any repo-as-OS product-repo detected in Q11), the dashboard panels and report types that match Q6 outputs, the automation level from Q7 (1 / 2 / 3 per `references/automation-levels.md`), and any draft-feature blocks (`roadmaps`, `journeys`) that the requested artifacts imply. Same single yes-or-adjust prompt.
3. **Proposed graduation criteria for the next stage** — name the 2–3 concrete things the user would need before safely advancing to the next adoption stage (e.g. "≥ 4 weeks of clean `.kb-log/` entries, one cross-layer promote completed, foundation/vmg.md confirmed by stakeholders" before turning on automation level 2). The user can accept, edit, or skip this block; it is informational and does not block scaffold.
4. **HTML artifact styling** — builtin, website-derived, or template-based corporate design. Default to `builtin` when Q3 does not mention external branding constraints.

### Phase 4 — Confirm and scaffold

1. **Final confirmation** — restate the chosen plan in one short summary: number of layers, anchor, audiences, adoption stage, automation level, IDE targets, where files will land. Proceed to "What setup does after confirmation" only after explicit yes.

If the user wants to skip phase 1 entirely and author the plan directly, accept that and route to a compact expert path: ask the layer list with name/scope/role/parent/features/marketplace per layer, anchor, workstreams, automation, styling, IDE targets. Document this as the legacy entry point; the goal-oriented flow is the default.

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
- `ideas` → `_kb-ideas/` + `archive/YYYY/`
- `decisions` → `_kb-decisions/` + `archive/YYYY/`
- `tasks` → `_kb-tasks/` + `archive/YYYY/`
- `workstreams` → `_kb-workstreams/`
- `reports` → `_kb-references/reports/`
- `roadmaps` → `_kb-roadmaps/`
- `journeys` → `_kb-journeys/`

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
6. if `roadmaps` or `journeys` are enabled, render their dry-run outputs.

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

The layer-graph scaffold uses these placeholders directly:

| Placeholder | Source |
|-------------|--------|
| `{{USER_NAME}}` | Q1 |
| `{{ROLE}}` | Q1 (role sentence extracted from the same answer) |
| `{{KB_NAME}}` | anchor-layer name (derived in Q12) |
| `{{WORKSPACE_ROOT}}` | Q9 |
| `{{WORKSTREAM_1_NAME}}`, `{{WORKSTREAM_1_THEMES}}` | extracted from Q2 (themes) and confirmed in Q12 |
| `{{ADOPTION_STAGE}}` | derived from Q8 (today bucket); used in `automation.yaml` and the scaffolded `foundation/me.md` so the chosen stage is durable, not implicit |
| `{{DATE}}` | today |
| `{{VERSION}}` | `1.0` on first scaffold |

Layer-specific repeated content beyond the anchor layer is rendered from the interview answers rather than from hard-coded placeholder names.

## Post-write placeholder check

After writing the scaffold, scan the workspace for any remaining `{{...}}` sequences outside the deliberate presentation-template placeholders. If any remain:

1. stop,
2. list the file and placeholder,
3. ask for the missing value,
4. re-render and rescan.

## References

- `references/setup-flow.md` — full step-by-step walkthrough with example output, including VMG sourcing and update guidance.
- `references/automation-levels.md` — meaning of setup levels 1/2/3 and how they map into `automation.yaml`.
- `references/adoption-stages.md` — the human → agentic curve: Stage 1 (capture discipline) → Stage 2 (agent-assisted triage) → Stage 3 (bounded autonomous). Names what each stage scaffolds, the graduation criteria between stages, and how adoption stage and automation level relate.
- `references/migration-guide.md` — how to migrate an existing KB.
- `references/troubleshooting.md` — common setup issues.
- `../../../docs/first-run-acceptance.md` — deterministic onboarding acceptance path.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-27 | Skill version aligned to 5.4.1 after the documentation-gap follow-up. Clarified the repo-as-OS bridge field name to `connections.product-repos[]` and linked the setup-flow VMG sourcing/update guidance | 5.4.1 patch release |
| 2026-04-27 | Clarified the repo-as-OS bridge wording so the proposal names the current schema field `connections.product-repos[]`, and pointed the setup-flow reference description at the new VMG sourcing/update guidance | Documentation gap follow-up |
| 2026-04-27 | v5.4.0: added Q8 ("operating context today, and target in 6 months") to phase 1 so the wizard can bias the proposal to the team's adoption stage (1, 2, or 3) instead of forcing a Stage-3 scaffold on a Stage-1 team or vice versa; phase 2 discovery pass now also probes for repo-as-OS structures so the proposal can offer bridge defaults; phase 3 question 12 now labels the proposed scaffold with its adoption stage; phase 3 question 14 surfaces graduation criteria for the next stage. Added `references/adoption-stages.md` as the normative contract; subsequent question numbers renumbered. Skill version aligned to 5.4.0 | Soft-transition extension |
| 2026-04-25 | v5.2.0: replaced the feature-list-driven 12-block interview with a four-phase, goal-oriented flow. Phase 1 asks the user about their identity, what they track, why now, audience, sources, desired outputs, and autonomy preference in their own language; phase 2 collects only the workspace and harness facts that cannot be inferred; phase 3 presents one derived plan (layer graph, connections, artifacts, automation, styling) for inline adjust-or-confirm; phase 4 takes a single yes. The legacy "author the plan directly" path stays available as a compact expert mode. Q7 wording carries the automation-level contract added in #76 forward into the new flow | Goal-oriented onboarding |
| 2026-04-25 | Documented what automation levels 1/2/3 mean during setup and linked the interview step to a dedicated reference so adopters do not have to infer the contract from `automation.yaml` alone | Deep spec-audit follow-up |
| 2026-04-25 | Added the explicit 5.1 migration-helper handoff so setup now points legacy adopters at `/kb migrate layer-model` and `/kb migrate archives` instead of leaving those follow-ups implicit | v5.1.0 closeout release |
| 2026-04-25 | Reworked setup for 5.0.0: onboarding now discovers and scaffolds a flexible layer graph, supports team-only or multi-org adoption, writes per-layer marketplaces and connections, and scaffolds year-based archives plus notes | v5.0.0 flexible layer model |
| 2026-04-25 | Version aligned to 4.0.0 for the v4.0.0 framework release | v4.0.0 release alignment |
| 2026-04-22 | Added Codex CLI acceptance guidance and clarified the difference between first-class supported harnesses and compatible CLI workflows | Compatibility expansion |
