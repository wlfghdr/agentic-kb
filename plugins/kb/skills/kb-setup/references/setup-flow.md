# Setup Flow — step by step

Full walkthrough the skill follows on `/kb setup`.

For the deterministic acceptance baseline used to verify real onboarding and team rollout quality, see [`docs/first-run-acceptance.md`](../../../../../docs/first-run-acceptance.md).

## Prerequisites

- `git` installed → fail loudly if not.
- `gh` (or equivalent remote CLI) → guide install if not.
- IDE CLI(s) the user selected → guide install if not.
- SSH key for remotes → offer `ssh-keygen` walkthrough if missing.

## Interview

Run the 12-block interview (see SKILL.md). Validate each answer before proceeding to the next block.

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

Instantiate these files from `templates/`:

- `AGENTS.md` ← `personal-kb-AGENTS.md`
- `README.md` ← `personal-kb-README.md`
- `.kb-config/layers.yaml` ← `layers.yaml`
- `.kb-config/automation.yaml` ← `automation.yaml`
- `.kb-config/artifacts.yaml` ← `artifacts.yaml`
- `_kb-references/foundation/me.md` ← `foundation-me.md`
- `_kb-references/foundation/context.md` ← `foundation-context.md`
- `_kb-references/foundation/vmg.md` ← `foundation-vmg.md` (pre-filled from Q3 — see [VMG sourcing](#vmg-sourcing-and-updates) below)
- `_kb-references/foundation/stakeholders.md` ← `foundation-stakeholders.md`
- `_kb-references/foundation/sources.md` ← `foundation-sources.md`
- `_kb-references/foundation/naming.md` ← `foundation-naming.md`
- `_kb-tasks/focus.md` ← `focus.md`
- `_kb-tasks/backlog.md` ← `backlog.md`
- Per workstream: `_kb-workstreams/<name>.md` ← `workstream.md`
- Per theme: `_kb-references/topics/<theme-slug>.md` ← `topic.md` (empty changelog)
- `index.html`, `dashboard.html`, `.nojekyll`

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

3. **Keyword lookup** — concept → file map, also resolving aliases.

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

`_kb-references/foundation/vmg.md` is the strategic steering model for the KB layer. Every capture, digest, and ritual checks it.

### Initial population during setup

During setup (interview block 2 collects role/themes; the VMG content is sourced in the scaffold step). The skill offers three methods:

| Method | When to use | How |
|--------|-------------|-----|
| **URL fetch** | Company or team OKR page, strategy doc, or public roadmap page is accessible | Agent fetches the URL, extracts the vision, mission, and goal statements, and drafts them into `vmg.md` for user review and edit |
| **File read** | The user has an existing strategy doc on disk | Agent reads the file, extracts the relevant sections, and drafts them into `vmg.md` |
| **Direct text** | No existing document; user dictates the VMG inline | Agent fills the template with the user's input verbatim and confirms |

After population by any method, always:

1. show the draft `vmg.md` to the user for review,
2. ask for any edits before writing,
3. note any missing fields (e.g., goals table not yet filled) as open tasks in `_kb-tasks/backlog.md`.

If no VMG content is available at setup time, write the template with all placeholders intact and add a `backlog.md` item: `Fill in vmg.md vision, mission, and goals`.

### Updates after setup

VMG updates happen in two ways:

**1. Triggered by a parent-layer digest (`/kb digest <layer>`).**

When a digest pulls changes from a parent layer that includes a `foundation/vmg.md`, the skill:

1. compares the upstream VMG with the current layer's `vmg.md`,
2. surfaces a diff of changed or new goal lines,
3. proposes appending new goals, updating existing ones with changed priority, and marking retired goals `dropped`,
4. waits for explicit confirmation before writing any change,
5. logs `update-topic | personal | vmg.md | VMG updated from <parent-layer> digest`.

The current layer's VMG is always the merged view. New or updated goals from upstream are appended, not silently overwritten.

**2. Manual update by the user.**

The user edits `vmg.md` directly or says "update my VMG". The skill:

1. proposes the change inline,
2. appends a changelog row to the file's `## Changelog` section (the template ships with one),
3. offers to commit.

### Conflict handling

If an upstream goal contradicts the current layer's goal (e.g., different priority horizon, conflicting direction), the skill flags the conflict as a candidate for a new decision (`_kb-decisions/D-YYYY-MM-DD-vmg-conflict.md`) rather than silently choosing one version. The user resolves the conflict via `/kb decide resolve` before the VMG update is finalized.

## Verification

Run:

- `/kb status` → expect clean state.
- `/kb start-day` → expect a non-empty briefing or explicit *"no pending work"*.

Print a quickstart card:

```
You're set up. Try:
  /kb                    → status
  /kb [paste text/URL]   → capture
  /kb start-day          → morning briefing
  /kb review             → process inputs
  /kb end-day            → commit + wrap
```

After the quickstart, validate the deterministic rollout baseline against [`docs/first-run-acceptance.md`](../../../../../docs/first-run-acceptance.md).

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-25 | Added VMG sourcing section covering the three initial-population methods (URL fetch, file read, direct text), post-setup update triggers (parent-layer digest and manual), and conflict handling | Deep spec-audit follow-up |
