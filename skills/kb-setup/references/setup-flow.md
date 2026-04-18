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
inputs/
inputs/digested/
references/topics/
references/findings/
references/foundation/
references/reports/
references/legacy/
decisions/active/
decisions/archive/
tasks/
tasks/archive/
log/
workstreams/
```

Instantiate these files from `templates/`:

- `AGENTS.md` ← `personal-kb-AGENTS.md`
- `README.md` ← `personal-kb-README.md`
- `.kb-config.yaml` ← `.kb-config.yaml`
- `.kb-automation.yaml` ← `.kb-automation.yaml`
- `.kb-artifacts.yaml` ← `.kb-artifacts.yaml`
- `references/foundation/me.md` ← `foundation-me.md`
- `references/foundation/context.md` ← `foundation-context.md`
- `references/foundation/stakeholders.md` ← `foundation-stakeholders.md`
- `references/foundation/sources.md` ← `foundation-sources.md`
- `references/foundation/naming.md` ← `foundation-naming.md`
- `tasks/focus.md` ← `focus.md`
- `tasks/backlog.md` ← `backlog.md`
- Per workstream: `workstreams/<name>.md` ← `workstream.md`
- Per theme: `references/topics/<theme-slug>.md` ← `topic.md` (empty changelog)

## Scaffold — team KB (if creating new)

```
decisions/active/
decisions/archive/
tasks/archive/
log/
<contributor>/inputs/digested/
<contributor>/outputs/topics/
<contributor>/outputs/findings/
```

- `AGENTS.md` ← `team-kb-AGENTS.md`
- `README.md` ← `team-kb-README.md`
- `tasks/focus.md`, `tasks/backlog.md`

## Scaffold — org-unit KB

```
decisions/active/
decisions/archive/
tasks/archive/
workstreams/
log/
```

- `AGENTS.md` ← `org-kb-AGENTS.md`
- `README.md` ← `org-kb-README.md`
- `tasks/focus.md`, `tasks/backlog.md`

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
