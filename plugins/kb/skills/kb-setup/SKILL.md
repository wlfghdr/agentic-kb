---
name: kb-setup
description: Interactive onboarding wizard that scaffolds an agentic-kb workspace around a flexible layer graph. Creates or onboards layer repos, writes the anchor-layer config, configures documented harness workflows, and generates the required templates, indexes, and HTML style references.
version: 5.0.0
triggers:
  - "/kb setup"
  - "setup kb"
  - "init kb"
  - "init knowledge"
  - "onboard kb"
  - "bootstrap workspace"
  - "create kb"
  - "scaffold knowledge base"
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

Ask each block in order. Stop and wait after each block for the user's answer before proceeding.

1. **Your name** — used for contributor directories and defaults.
2. **Your role and themes** — one sentence plus 3–5 theme keywords.
3. **Workspace root** — absolute path; default current directory.
4. **Discovery pass** — scan the workspace for existing KB repos, harness hooks, and likely layer candidates. Present what was found before asking for mutations.
5. **Layer declarations** — repeat this block for every layer the user wants:
   - create new or onboard existing,
   - layer name,
   - scope,
   - role (`contributor` or `consumer`),
   - parent layer,
   - path,
   - enabled features,
   - contributor-mode overrides for `topics` or `notes`,
   - optional marketplace repo.
   Default suggestion when nothing exists: one contributor anchor layer plus one team layer.
6. **Anchor layer** — choose which contributor-capable layer holds `.kb-config/` and acts as the user's home base.
7. **Workstreams** — 1–5 workstreams for the anchor layer.
8. **IDE targets** — multi-select from `claude-code`, `vscode`, `opencode`, `codex`, `gemini`, `kiro`.
9. **Connections and integrations** — linked product repos, tracker exports or live trackers, reference mode, write-back policy.
10. **Draft features** — if any layer enables `roadmaps` or `journeys`, collect the additional per-layer config needed for those features.
11. **Automation level** — 1, 2, or 3.
12. **HTML artifact styling** — builtin, website-derived, or template-based corporate design.

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
2. propose the new layer graph,
3. map old L1/L2/L3/L4/L5 references to named `layers:` entries,
4. move archives into year-based directories with `git mv`,
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
| `{{ROLE}}` | Q2 |
| `{{KB_NAME}}` | anchor-layer name |
| `{{WORKSPACE_ROOT}}` | Q3 |
| `{{WORKSTREAM_1_NAME}}`, `{{WORKSTREAM_1_THEMES}}` | Q7 |
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

- `references/setup-flow.md` — full step-by-step walkthrough with example output.
- `references/migration-guide.md` — how to migrate an existing KB.
- `references/troubleshooting.md` — common setup issues.
- `../../../docs/first-run-acceptance.md` — deterministic onboarding acceptance path.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-25 | Reworked setup for 5.0.0: onboarding now discovers and scaffolds a flexible layer graph, supports team-only or multi-org adoption, writes per-layer marketplaces and connections, and scaffolds year-based archives plus notes | v5.0.0 flexible layer model |
| 2026-04-25 | Version aligned to 4.0.0 for the v4.0.0 framework release | v4.0.0 release alignment |
| 2026-04-22 | Added Codex CLI acceptance guidance and clarified the difference between first-class supported harnesses and compatible CLI workflows | Compatibility expansion |
