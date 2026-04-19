# Setup Flow — step by step

Full walkthrough the skill follows on `/kb setup`.

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
__inputs/
__inputs/digested/
_references/topics/
_references/findings/
_references/foundation/
_references/reports/
_references/legacy/
_decisions/active/
_decisions/archive/
_tasks/
_tasks/archive/
.kb-log/
_workstreams/
```

Instantiate these files from `templates/`:

- `AGENTS.md` ← `personal-kb-AGENTS.md`
- `README.md` ← `personal-kb-README.md`
- `.kb-config.yaml` ← `.kb-config.yaml`
- `.kb-automation.yaml` ← `.kb-automation.yaml`
- `.kb-artifacts.yaml` ← `.kb-artifacts.yaml`
- `_references/foundation/me.md` ← `foundation-me.md`
- `_references/foundation/context.md` ← `foundation-context.md`
- `_references/foundation/stakeholders.md` ← `foundation-stakeholders.md`
- `_references/foundation/sources.md` ← `foundation-sources.md`
- `_references/foundation/naming.md` ← `foundation-naming.md`
- `_tasks/focus.md` ← `focus.md`
- `_tasks/backlog.md` ← `backlog.md`
- Per workstream: `_workstreams/<name>.md` ← `workstream.md`
- Per theme: `_references/topics/<theme-slug>.md` ← `topic.md` (empty changelog)

## Scaffold — team KB (if creating new)

```
_decisions/active/
_decisions/archive/
_tasks/archive/
.kb-log/
<contributor>/_inputs/digested/
<contributor>/outputs/topics/
<contributor>/outputs/findings/
```

- `AGENTS.md` ← `team-kb-AGENTS.md`
- `README.md` ← `team-kb-README.md`
- `_tasks/focus.md`, `_tasks/backlog.md`

## Scaffold — org-unit KB

```
_decisions/active/
_decisions/archive/
_tasks/archive/
_workstreams/
.kb-log/
```

- `AGENTS.md` ← `org-kb-AGENTS.md`
- `README.md` ← `org-kb-README.md`
- `_tasks/focus.md`, `_tasks/backlog.md`

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
| `bb` | bluebox | bluebox/ |
| `psb` | product-strategy-brainstorming | product-strategy-brainstorming/ |
| `akb` | agentic-kb | agentic-kb/ |
| `whkb` | wh-kb | wh-kb/ |
```

Alias generation rules:
- Use initials of hyphenated segments (e.g., `product-strategy-brainstorming` → `psb`).
- Single-word repos get first 2–3 letters (e.g., `bluebox` → `bb`).
- On collision, append a digit or use a longer prefix.
- The user can override aliases in `.kb-config.yaml` under `workspace.aliases`.

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
