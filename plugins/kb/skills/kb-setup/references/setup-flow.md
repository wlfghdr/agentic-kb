# Setup Flow — step by step

Full walkthrough the skill follows on `/kb setup`.

For the deterministic acceptance baseline used to verify real onboarding and team rollout quality, see [`docs/first-run-acceptance.md`](../../../../../docs/first-run-acceptance.md).

## Prerequisites

- `git` installed → fail loudly if not.
- `gh` (or equivalent remote CLI) → guide install if not.
- IDE CLI(s) the user selected → guide install if not.
- SSH key for remotes → offer `ssh-keygen` walkthrough if missing.

## Interview

Run the 12-question interview (see SKILL.md). Validate each answer before proceeding to the next block.

## Repo creation / onboarding

For each repo (personal / team / org-unit / marketplace), offer:

- `create` — `mkdir` + `git init` + remote setup + initial commit.
- `onboard` — ask for path; verify it's a git repo.
- `skip` (except personal, which is required).

## Scaffold — personal KB

Create these directories (idempotent):

```
_kb-inputs/
_kb-inputs/digested/
_kb-references/topics/
_kb-references/findings/
_kb-references/foundation/
_kb-references/reports/
_kb-references/legacy/
_kb-decisions/
_kb-decisions/archive/
_kb-tasks/
_kb-tasks/archive/
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
- `_kb-references/foundation/vmg.md` ← `foundation-vmg.md` (pre-filled from Q3: URL fetch, file read, or direct text)
- `_kb-references/foundation/stakeholders.md` ← `foundation-stakeholders.md`
- `_kb-references/foundation/sources.md` ← `foundation-sources.md`
- `_kb-references/foundation/naming.md` ← `foundation-naming.md`
- `_kb-tasks/focus.md` ← `focus.md`
- `_kb-tasks/backlog.md` ← `backlog.md`
- Per workstream: `_kb-workstreams/<name>.md` ← `workstream.md`
- Per theme: `_kb-references/topics/<theme-slug>.md` ← `topic.md` (empty changelog)

## Scaffold — team KB (if creating new)

```
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

## Scaffold — org-unit KB

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

## Initial commits

Per repo:

```
git add -A
git commit -m "Initial agentic-kb scaffold (via /kb setup)"
git push <remote> <branch>   # if remote configured and user confirms
```

Respect branch protection — open a PR if the default branch is protected.

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
