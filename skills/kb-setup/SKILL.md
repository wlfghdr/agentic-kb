---
name: kb-setup
description: Interactive onboarding wizard that scaffolds a complete agentic-kb workspace. Creates the personal KB (required), any optional team/org-unit KBs, configures IDE harnesses (VS Code Copilot, Claude Code, OpenCode), and generates all required templates, configuration files, and AGENTS.md/CLAUDE.md indexes. Triggered by `/kb setup` and onboarding phrases.
version: 2.2.0
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

## Scope boundary — install vs. init

This skill **initializes the user's KB workspace**. It does **not** distribute itself.

Two concerns, two tools:

| Concern | Who handles it | When |
|---------|---------------|------|
| Get `kb-management` + `kb-setup` + `kb-operator` into the harness (`.claude/`, `.opencode/`, `.github/`, or user-global equivalents) | Harness marketplace (`/plugin install kb@agentic-kb`) **or** `scripts/install.py` from a cloned marketplace repo | Before this skill runs — otherwise `/kb setup` wouldn't be callable |
| Scaffold the user's KB repos (`.kb-config.yaml`, foundation files, workstreams, topics, todos, log) | **This skill** | When the user types `/kb setup` |

Concrete consequence: by the time this skill runs, the skills are already present. Step 5/6 below do not re-install them — they only create the user's workspace-level configuration files (`.github/prompts/kb.prompt.md`, `AGENTS.md`, `.kb-config.yaml`, etc.) and invoke `scripts/install` **only** when the user picks an additional harness that isn't yet present.

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

### Step 1 — Prerequisites (MUST abort on missing required tools)

Required (setup cannot proceed without these):

| Tool | Check | Abort message if missing |
|------|-------|--------------------------|
| `git` | `git --version` exits 0 | macOS: `xcode-select --install` · Debian/Ubuntu: `sudo apt install git` · Fedora: `sudo dnf install git` · Windows: [git-scm.com/download/win](https://git-scm.com/download/win) |
| Harness CLI (at least one: `claude`, `code`, or `opencode`) | binary on PATH | Install the harness first; the skill can't install itself into an absent harness |

Recommended (warn, do not abort):

| Tool | Why | Install hint if missing |
|------|-----|------------------------|
| `gh` | GitHub-native PR/issue flows in `/kb promote`, `/kb publish` | [cli.github.com](https://cli.github.com/) |
| SSH key for the user's git host | Push without password prompts | Offer an `ssh-keygen -t ed25519 -C <email>` walkthrough |

On abort: print the missing tool, the OS-specific install command, and exit. Do **not** proceed partially and leave the workspace half-scaffolded.

### Step 2 — Create / clone repos
- Personal KB: `mkdir`, `git init`, remote setup.
- Team KB(s): clone OR create + contributor dir.
- Org-Unit KB: clone if configured.
- Marketplace: clone or register.

### Step 3 — Scaffold personal KB
Directories: `inputs/`, `inputs/digested/`, `references/{topics,findings,foundation,reports,legacy}/`, `ideas/`, `ideas/archive/`, `decisions/{active,archive}/`, `tasks/{,archive}/`, `log/`, `workstreams/`.

Files (from `templates/`):
- `AGENTS.md`, `README.md`, `.kb-config.yaml`, `.kb-automation.yaml`, `.kb-artifacts.yaml`.
- Initial `workstreams/<name>.md` per declared workstream.
- `references/foundation/{me,context,stakeholders,sources,naming}.md`.
- Initial `references/topics/<slug>.md` per declared theme (with empty changelog).
- `tasks/focus.md`, `tasks/backlog.md`.

### Step 4 — Scaffold team KB (if creating new)
- Contributor directory (`<your-name>/inputs/`, `<your-name>/outputs/{topics,findings}/`).
- `decisions/{active,archive}/`, `tasks/{focus,backlog}.md`, `log/`, `AGENTS.md`, `README.md`.

### Step 5 — Workspace-level configuration

Workspace-level *KB configuration* (distinct from harness-level *skill installation*):

- `AGENTS.md` at workspace root with a repo index + short-alias table + keyword lookup.
- `CLAUDE.md` → symlink to `AGENTS.md`.
- `.kb-config.yaml`, `.kb-automation.yaml`, `.kb-artifacts.yaml` at workspace root (not the KB root — these are workspace-scoped indexes of all configured layers).

The repo index and alias table are generated by scanning the workspace for git repos with an `AGENTS.md`, `CLAUDE.md`, or `README.md`. Short aliases are derived automatically (initials of hyphenated segments, or first 2–3 chars for single-word repos). Collisions are resolved by appending digits. Users can override aliases in `.kb-config.yaml` under `workspace.aliases`.

Optional workspace-level harness hooks (only written if the harness was **not** already configured by marketplace install or `scripts/install`):

- VS Code selected → write `.github/prompts/kb.prompt.md` and `.github/instructions/kb.instructions.md` from `templates/` **only if missing**.
- Claude Code / OpenCode selected → nothing to write at workspace level; plugin/install handles `.claude/` and `.opencode/`.

### Step 6 — Configure additional IDE targets

For any harness the user selected that is **not yet installed**, run the installer and record the outcome:

- **Claude Code**: recommend `/plugin marketplace add <repo-url>` + `/plugin install kb@agentic-kb` from inside Claude Code (preferred — handles updates). Fall back to `<marketplace>/scripts/install --target claude` for dev installs.
- **VS Code**: point the user at `chat.plugins.marketplaces` in `settings.json` for one-click install, or run `<marketplace>/scripts/install --target vscode` for direct workspace copy.
- **OpenCode**: no marketplace. Run `<marketplace>/scripts/install --target opencode` (workspace) or `--global`. OpenCode also reads `.claude/skills/`, so a Claude Code install in the same workspace is picked up automatically.

Never re-install into a harness that already has the skills — that causes symlink/file conflicts with `link_or_copy` falling back to "skip (exists)".

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

All templates are in `templates/`. The skill instantiates them with values from the interactive interview. Template keys are `{{DOUBLE_BRACE}}` placeholders.

### Placeholder → interview-answer mapping (MUST be substituted)

Every placeholder below has exactly one source — always from the interview answers collected in the 12 question blocks. If a source is missing, **ask the user again** before writing; never leave a literal `{{…}}` in an output file.

| Placeholder | Source (question block) |
|-------------|------------------------|
| `{{USER_NAME}}` | Q1 (your name) |
| `{{ROLE}}` | Q2 (role sentence) |
| `{{THEMES}}` | Q2 (theme keywords, rendered as a bullet list) |
| `{{KB_NAME}}` | Q4 (personal KB name; defaults to `<user-name>-kb` if the user accepts the default) |
| `{{KB_DESCRIPTION}}` | Q2 (one-sentence role statement) |
| `{{WORKSTREAMS}}` | Q8 (rendered as a bullet list: `- <name>: <themes>`) |
| `{{WORKSTREAM_N_NAME}}`, `{{WORKSTREAM_N_THEMES}}` | Q8 (per declared workstream) |
| `{{TEAM_NAME}}` | Q5 (per declared team, if any) |
| `{{ORG_UNIT_NAME}}` | Q6 (if an org-unit KB was onboarded) |
| `{{REPO_INDEX}}` | Computed — one bullet per configured KB layer with its path + role |
| `{{KEYWORD_LOOKUP}}` | Computed — `docs/glossary.md` summary injected verbatim |
| `{{RECENT_REPORTS}}` | Empty `<ul></ul>` on first run (will be filled by `/kb present` / `/kb report`) |
| `{{DATE}}` | Today's ISO-8601 date (`YYYY-MM-DD`) |
| `{{VERSION}}` | `1.0` on first scaffold; later artifacts bump their own version |

### Post-write check (MUST run before Step 8)

After all files are written and before the initial commit, scan the scaffolded workspace for any remaining `{{` sequence. If any match is found:

1. Stop — do not commit.
2. List the (file, line, placeholder) triples to the user.
3. Ask for the missing values.
4. Re-render, then re-scan.

Concrete grep the skill must run (or equivalent):

```
grep -rn '{{[A-Z_0-9]*}}' <workspace-root> || true
```

A zero-hit run is the gate for Step 8.
