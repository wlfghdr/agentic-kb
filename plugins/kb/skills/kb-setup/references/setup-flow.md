# Setup Flow — step by step

Full walkthrough the skill follows on `/kb setup`.

For the deterministic acceptance baseline used to verify real onboarding and team rollout quality, see [`docs/first-run-acceptance.md`](../../../../../docs/first-run-acceptance.md).

## Prerequisites

- `git` installed → fail loudly if not.
- `gh` (or equivalent remote CLI) → guide install if not.
- IDE CLI(s) the user selected → guide install if not.
- SSH key for remotes → offer `ssh-keygen` walkthrough if missing.

## Interview

Run the four-phase, goal-oriented interview defined in `SKILL.md` ("Interactive question flow"):

1. **Phase 1 — Context and goals**: identity, what the user tracks/decides, why now, audience, sources, desired outputs, autonomy preference, and operating context. All open-ended; never asks the user to enumerate features, scopes, or layer counts.
2. **Phase 2 — Workspace and harness facts**: workspace root, IDE targets, discovery pass against existing KB material.
3. **Phase 3 — Proposed plan**: the wizard derives a layer graph, connections, artifacts, automation level, product-management roadmap/journey placement, and HTML styling from phases 1 + 2 and presents them as one block. The user adjusts inline or confirms; deeper edits are routed through targeted follow-ups (rename, add/remove a layer, flip role, change parent, move roadmap/journey ownership).
4. **Phase 4 — Final confirmation**: one summary, one yes.

Validate each answer block before advancing. Never derive layer features from a feature list dictated to the user; always derive them from the user's own answers and let the user adjust the proposal in phase 3. A compact expert path (the legacy "author the plan directly" mode) is available on request for users who already know the framework.

## Repo creation / onboarding

For each declared layer or marketplace repo, offer:

- `create` — `mkdir` + `git init` + remote setup + initial commit.
- `onboard` — ask for path; verify it's a git repo.
- `skip` (except that at least one contributor-capable layer is required).

## Scaffold — anchor contributor layer

Create these directories (idempotent):

```
_kb-inputs/
_kb-inputs/digested/YYYY/MM/
_kb-references/topics/
_kb-references/findings/YYYY/
_kb-references/foundation/
_kb-references/reports/
_kb-references/legacy/
_kb-notes/YYYY/
_kb-decisions/
_kb-decisions/archive/YYYY/
_kb-tasks/
_kb-tasks/archive/YYYY/
.kb-log/
_kb-workstreams/
```

If the derived feature set includes product-management artifacts, also create only the enabled directories:

```
_kb-roadmaps/
_kb-journeys/
```

Instantiate these files from `templates/`:

- `AGENTS.md` ← `personal-kb-AGENTS.md`
- `README.md` ← `personal-kb-README.md`
- `.kb-config/layers.yaml` ← `layers.yaml`
- `.kb-config/automation.yaml` ← `automation.yaml`
- `.kb-config/artifacts.yaml` ← `artifacts.yaml`
- `_kb-references/foundation/me.md` ← `foundation-me.md`
- `_kb-references/foundation/context.md` ← `foundation-context.md`
- `_kb-references/foundation/vmg.md` ← `foundation-vmg.md` (pre-filled from the best available strategic source: URL fetch, file read, or direct text)
- `_kb-references/foundation/stakeholders.md` ← `foundation-stakeholders.md`
- `_kb-references/foundation/sources.md` ← `foundation-sources.md`
- `_kb-references/foundation/naming.md` ← `foundation-naming.md`
- `_kb-tasks/focus.md` ← `focus.md`
- `_kb-tasks/backlog.md` ← `backlog.md`
- Per workstream: `_kb-workstreams/<name>.md` ← `workstream.md`
- Per theme: `_kb-references/topics/<theme-slug>.md` ← `topic.md` (empty changelog)
- `index.html`, `dashboard.html`, `.nojekyll`

When `roadmaps` or `journeys` are enabled, render their config blocks into `.kb-config/layers.yaml` under the owning layer and their template blocks into `.kb-config/artifacts.yaml`. The first-run default is one owning layer for both artifacts unless the user explicitly selects different owners.

## Scaffold — additional shared contributor layer

```
_kb-notes/
_kb-decisions/
_kb-decisions/archive/
_kb-tasks/archive/
.kb-log/
<contributor>/_kb-inputs/digested/
<contributor>/_kb-references/topics/
<contributor>/_kb-references/findings/
```

- `AGENTS.md` ← `team-kb-AGENTS.md`
- `README.md` ← `team-kb-README.md`
- `_kb-tasks/focus.md`, `_kb-tasks/backlog.md`
- `index.html`, `dashboard.html`, `.nojekyll`

## Scaffold — synthesis or consumer layer

```
_kb-decisions/
_kb-decisions/archive/
_kb-tasks/archive/
_kb-workstreams/
.kb-log/
```

- `AGENTS.md` ← `org-kb-AGENTS.md`
- `README.md` ← `org-kb-README.md`
- `_kb-tasks/focus.md`, `_kb-tasks/backlog.md`
- `index.html`, `dashboard.html`, `.nojekyll`

## Scaffold — workspace root

```
.github/prompts/
.github/instructions/
```

And (if selected):

```
.claude/
.opencode/
```

- `AGENTS.md` ← `workspace-AGENTS.md`
- `CLAUDE.md` → symlink to `AGENTS.md` (copy on Windows)
- `.github/prompts/kb.prompt.md` ← `kb.prompt.md`
- `.github/instructions/kb.instructions.md` ← `kb.instructions.md`

### Repo index and short aliases

The generated `AGENTS.md` includes:

1. **Repo index table** — every repo in the workspace with its path, instruction file, and one-line description.
2. **Short alias table** — auto-generated abbreviations for fast navigation:

```markdown
| Alias | Repo | Path |
|-------|------|------|
| `ba` | backend-api | backend-api/ |
| `psb` | product-strategy-brainstorming | product-strategy-brainstorming/ |
| `akb` | agentic-kb | agentic-kb/ |
| `pkb` | personal-kb | personal-kb/ |
```

Alias generation rules:

- Use initials of hyphenated segments (e.g., `product-strategy-brainstorming` → `psb`).
- Single-word repos get first 2–3 letters (e.g., `backend-api` → `ba`, or `frontend` → `fe`).
- On collision, append a digit or use a longer prefix.
- The user can override aliases in `.kb-config/layers.yaml` under `workspace.aliases`.

1. **Keyword lookup** — concept → file map, also resolving aliases.

## IDE configuration

Per selected IDE:

- **VS Code**: merge into `.vscode/settings.json` → `chat.plugins.marketplaces`.
- **Claude Code**: preferred path — inside Claude Code run `/plugin marketplace add <repo-url>` + `/plugin install kb@agentic-kb`. Alternative: `<marketplace>/scripts/install --target claude`.
- **OpenCode**: no official marketplace. Run `<marketplace>/scripts/install --target opencode` (workspace) or `--global` (user). OpenCode also reads `.claude/skills/` for cross-agent compatibility.
- **Codex CLI**: run `<marketplace>/scripts/install --target codex` (workspace) or `--global`. Codex reads `AGENTS.md` plus `.agents/skills/kb/SKILL.md`; invoke the workflow through the skill picker or `$kb`, not a custom `/kb` slash command.

## Initial commits

Per repo:

```
git add -A
git commit -m "Initial agentic-kb scaffold (via /kb setup)"
git push <remote> <branch>   # if remote configured and user confirms
```

Respect branch protection — open a PR if the default branch is protected.

## VMG sourcing and updates

`_kb-references/foundation/vmg.md` is the strategic steering model for the layer. Setup should make its initial source explicit instead of leaving the file as an unexplained template.

### Initial population during setup

The wizard does not assume a VMG document already exists. During scaffold, it offers three sourcing modes:

| Method | When to use | How |
|--------|-------------|-----|
| **URL fetch** | A public or accessible strategy page, OKR page, roadmap page, or planning doc already exists | Fetch the URL, extract the vision, mission, and goal statements, then draft them into `vmg.md` for review |
| **File read** | The user already has a strategy document on disk | Read the file, extract the relevant sections, then draft them into `vmg.md` |
| **Direct text** | No existing source exists, or the user wants to dictate it inline | Fill the template from the user's wording and confirm before writing |

After population by any method, always:

1. show the draft `vmg.md` to the user for review,
2. ask for edits before writing,
3. note missing fields, placeholders, or unresolved goals as explicit follow-up tasks instead of pretending the steering model is complete.

If no VMG content is available at setup time, write the template with placeholders intact and add a backlog item to complete it later.

### Updates after setup

VMG updates happen in two common ways.

**1. Triggered by a parent-layer digest.**

When `/kb digest <layer>` pulls changes from a parent layer that includes `foundation/vmg.md`, the skill should:

1. compare the upstream VMG with the current layer's `vmg.md`,
2. surface the changed or new goal lines,
3. propose appending new goals, updating changed goals, or marking retired goals as `dropped`,
4. wait for explicit confirmation before writing,
5. log the update clearly as a VMG change.

The current layer's VMG is the merged local view. Upstream updates should never overwrite local context silently.

**2. Manual update by the user.**

When the user edits `vmg.md` directly or asks to update their VMG, the skill should:

1. propose the change inline,
2. append a row to the file's `## Changelog` section,
3. offer a commit if the change is substantive.

### Conflict handling

If an upstream goal contradicts the current layer's goal, flag the conflict as an explicit decision candidate rather than silently choosing one version. The durable fix is a decision record plus an intentional VMG update.

## Verification

Run:

- `/kb status` → expect clean state.
- `/kb start-day` → expect a non-empty briefing or explicit *"no pending work"*.
- If `roadmaps` or `journeys` are enabled, run their dry-run render/audit path and expect the output to name the configured owning layer, source directories, and missing-source gaps without writing to trackers.

Print a quickstart card:

```
You're set up. Try:
  /kb                    → status
  /kb [paste text/URL]   → capture
  /kb start-day          → morning briefing
  /kb review             → process inputs
  /kb end-day            → commit + wrap
  /kb roadmap            → roadmap status (if enabled)
  /kb journeys           → journey status (if enabled)
```

After the quickstart, validate the deterministic rollout baseline against [`docs/first-run-acceptance.md`](../../../../../docs/first-run-acceptance.md).

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-30 | Added setup guidance for deriving, placing, scaffolding, and verifying roadmap/journey product-management artifacts from role/goals instead of requiring users to know feature names upfront | Product-management surface integration |
| 2026-04-27 | Added explicit VMG sourcing and update guidance for setup, including URL/file/direct-text population modes, parent-digest updates, manual edits, and conflict handling. Also removed the stale question-number reference from the `vmg.md` scaffold bullet | Documentation gap follow-up |
