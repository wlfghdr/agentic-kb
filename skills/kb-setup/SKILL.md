---
name: kb-setup
description: Interactive onboarding wizard that scaffolds a complete agentic-kb workspace. Creates the personal KB (required), any optional team/org-unit KBs, configures IDE harnesses (VS Code Copilot, Claude Code, OpenCode), and generates all required templates, configuration files, and AGENTS.md/CLAUDE.md indexes. Triggered by `/kb setup` and onboarding phrases.
version: 2.0.0
triggers:
  - "/kb setup"
  - "setup kb"
  - "init kb"
  - "init knowledge"
  - "onboard kb"
  - "bootstrap workspace"
  - "create kb"
  - "scaffold knowledge base"
tools: []
requires: []
author: agentic-kb contributors
homepage: https://github.com/wlfghdr/agentic-kb
license: Apache-2.0
---

# Skill: KB Setup

This skill is the single entry point for bootstrapping an `agentic-kb` workspace. It runs once per user; subsequent invocations are **idempotent** (add missing pieces, never overwrite).

## When to invoke

- The user types `/kb setup`.
- The user says *"set me up with a KB"*, *"onboard me"*, *"bootstrap my workspace"*, or equivalent.
- `kb-management` detects no `.kb-config.yaml` in the current directory and the user tries to run any `/kb` command — offer to run setup first.

## Interactive question flow

Ask each block in order. Stop and wait after each block for the user's answer before proceeding.

1. **Your name** (used for contributor directories): `your-name`.
2. **Your role and themes**: one sentence + 3–5 theme keywords (these become initial workstreams).
3. **Workspace root**: absolute path. Default: current directory.
4. **Personal KB (L1)** — required:
   - Create new? → ask for name, initialize git, choose remote.
   - Onboard existing? → ask for path.
5. **Team KBs (L2)** — optional, multiple:
   - Create new / onboard existing / skip.
6. **Org-Unit KB (L3)** — optional:
   - Onboard existing / skip.
7. **Marketplace (L4)** — optional:
   - Install from marketplace (recommended for users).
   - Clone for contributing (for skill authors).
   - Skip.
8. **Personal workstreams**: 1–5 parallel workstreams with theme keywords.
9. **IDE targets**: multi-select from `vscode`, `claude-code`, `opencode`.
10. **Integrations**: marketplace-available MCP servers / APIs to wire up.
11. **Automation level**: 1 (manual), 2 (semi-auto), 3 (full-auto).
12. **HTML artifact styling**:
    - *"For generated presentations and reports, what styling should the agent use?"*
    - (a) Default built-in template.
    - (b) Point to a website — agent derives a matching theme from the page.
    - (c) Point to a template file.
    - Always generate both light and dark themes with an in-page toggle.

## What setup does (after confirmation)

### Step 1 — Prerequisites
- Check `git`, `gh` (or equivalent), IDE CLIs are installed. Guide install if missing.
- SSH key check (offer `ssh-keygen` walkthrough if missing).

### Step 2 — Create / clone repos
- Personal KB: `mkdir`, `git init`, remote setup.
- Team KB(s): clone OR create + contributor dir.
- Org-Unit KB: clone if configured.
- Marketplace: clone or register.

### Step 3 — Scaffold personal KB
Directories: `inputs/`, `inputs/digested/`, `references/{topics,findings,foundation,reports,legacy}/`, `decisions/{active,archive}/`, `todo/{,archive}/`, `log/`, `workstreams/`.

Files (from `templates/`):
- `AGENTS.md`, `README.md`, `.kb-config.yaml`, `.kb-automation.yaml`, `.kb-artifacts.yaml`.
- Initial `workstreams/<name>.md` per declared workstream.
- `references/foundation/{me,context,stakeholders,sources,naming}.md`.
- Initial `references/topics/<slug>.md` per declared theme (with empty changelog).
- `todo/focus.md`, `todo/backlog.md`.

### Step 4 — Scaffold team KB (if creating new)
- Contributor directory (`<your-name>/inputs/`, `<your-name>/outputs/{topics,findings}/`).
- `decisions/{active,archive}/`, `todo/{focus,backlog}.md`, `log/`, `AGENTS.md`, `README.md`.

### Step 5 — Workspace-level configuration
- `.github/prompts/kb.prompt.md` (the slash-command entry).
- `.github/instructions/kb.instructions.md` (routing rules).
- `AGENTS.md` at workspace root with a repo index.
- `CLAUDE.md` → symlink to `AGENTS.md`.
- `.claude/` and `.opencode/` if those harnesses were selected.

### Step 6 — Configure IDE targets
- **VS Code**: update `settings.json` with the marketplace entry.
- **Claude Code**: preferred — inside Claude Code run `/plugin marketplace add <repo-url>` then `/plugin install kb@agentic-kb`. For dev installs: `<marketplace>/scripts/install --target claude`.
- **OpenCode**: no official marketplace. Run `<marketplace>/scripts/install --target opencode` (workspace) or `--global`. OpenCode also reads `.claude/skills/` so a Claude Code install in the same workspace is picked up.

### Step 7 — Configure integrations
- For each opted-in integration: validate access; skip with a warning if unreachable.

### Step 8 — Initial commits
- Commit personal KB scaffold.
- Commit workspace config.
- Push if remotes are configured.

### Step 9 — Verify
- Run `/kb status` — expect clean state.
- Run `/kb start-day` — expect a non-empty briefing or explicit *"no pending work"*.
- Print a quickstart card.

## Migration mode

If the user points at an existing knowledge base in another layout:

1. Analyze the existing layout against this spec.
2. Propose a diff (files to create, rename, restructure).
3. Apply **only after explicit confirmation**.
4. Use `git mv` to preserve history.
5. Move material that doesn't fit into `references/legacy/` with a note — **never delete**.

## Idempotency

Running `/kb setup` a second time:

- Detects existing structure.
- Offers to add only missing pieces.
- Prompts if a file with the same path but different content is detected.

## Safety

- Never overwrites existing files without explicit confirmation.
- Never creates a remote repo without asking.
- Never pushes to a remote without asking.

## References (load on demand)

- `references/setup-flow.md` — full step-by-step walkthrough with example output.
- `references/migration-guide.md` — how to migrate an existing KB.
- `references/troubleshooting.md` — common setup issues.

## Templates

All templates are in `templates/`. The skill instantiates them with values from the interactive interview. Template keys are `{{double-brace}}` placeholders.
