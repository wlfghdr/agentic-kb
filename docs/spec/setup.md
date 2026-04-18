# Setup — The Onboarding Flow

> **Version:** 0.1 | **Last updated:** 2026-04-18

`/kb setup` is the interactive wizard that bootstraps a complete workspace. It runs once. It is the only user-facing command that creates directories and repos from scratch.

## What It Asks

1. **Your name** (for contributor directories): `your-name`.
2. **Your role and themes**: a short sentence describing what you do and 3–5 theme keywords (these become initial workstreams).
3. **Workspace root**: absolute path. Defaults to the current directory.
4. **Personal KB (L1)** — required:
   - Create new? → name, init git, choose remote.
   - Onboard existing? → path to existing repo.
5. **Team KB(s) (L2)** — optional, multiple allowed:
   - Create new? → name, init git, invite collaborators.
   - Onboard existing? → clone URL(s).
   - Skip (solo mode).
6. **Org-Unit KB (L3)** — optional:
   - Onboard existing? → clone URL.
   - Skip.
7. **Marketplace (L4)** — optional:
   - Install from marketplace? (recommended for users).
   - Clone for contributing? (for skill authors).
   - Skip.
8. **Personal workstreams**: define 1–5 parallel workstreams with theme keywords.
9. **IDE targets**: multi-select from `vscode`, `claude-code`, `opencode`.
10. **Integrations**: any MCP servers / external tools to wire up (marketplace-available only).
11. **Automation level**: 1 (manual), 2 (semi-auto), 3 (full-auto).
12. **HTML artifact styling** (see below).

### HTML Artifact Styling

Because `/kb present` and `/kb report` generate HTML artifacts (see [html-artifacts.md](html-artifacts.md)), the setup asks:

> *"For generated presentations and reports, what styling should the agent use?"*
>
> 1. **Default built-in** — a plain, accessible, minimal HTML/CSS template shipped with the skill.
> 2. **Point me to a website** — give a URL; the agent will read the page's visual language (colors, typography, spacing) and derive a matching theme.
> 3. **Point me to a template file** — give a path to an existing HTML template (e.g. one your organization has standardized on).
>
> *In all cases, the agent produces both a light and a dark theme with an in-page toggle.*

The selection is stored in `.kb-artifacts.yaml`:

```yaml
styling:
  source: website                   # builtin | website | template
  reference-url: https://example.org/brand
  reference-file: ../styling/my-template.html   # if source=template
  themes: [light, dark]             # always both
  default-theme: auto               # auto | light | dark
  watermark:
    enabled: true
    position: intro-slide
    format: "v{version} · {date}"
```

## What Setup Does

```
Step 1 — Prerequisites
  - git installed?
  - IDE CLI tools available? (gh, or equivalent — guide install if not)
  - SSH keys configured? (guide setup if not)

Step 2 — Create/clone repos
  - Personal KB: mkdir + git init + remote setup
  - Team KB(s): clone or create + contributor dir
  - Org-Unit KB: clone (if configured)
  - Marketplace: clone or install

Step 3 — Scaffold personal KB
  - Directories from workspace-layout.md §Personal KB
  - Files from file-formats.md templates
  - .kb-config.yaml, .kb-automation.yaml, .kb-artifacts.yaml
  - Initial topic files from declared themes (with empty changelog)
  - foundation/{me,context,stakeholders,sources}.md

Step 4 — Scaffold team KB (if creating new)
  - Contributor directory structure
  - decisions/active/, decisions/archive/
  - todo/ with focus.md, backlog.md
  - AGENTS.md, README.md, log/

Step 5 — Scaffold workspace-level config
  - .github/prompts/kb.prompt.md
  - .github/instructions/kb.instructions.md
  - AGENTS.md at workspace root with repo index
  - CLAUDE.md symlink → AGENTS.md
  - .claude/, .opencode/, and .github/skills|agents|prompts|instructions/ populated via scripts/install for the selected harness(es)

Step 6 — Configure IDE targets
  - VS Code: update settings.json, register marketplace
  - Claude Code: add marketplace + install kb plugin (preferred) or run scripts/install --target claude
  - OpenCode: run scripts/install --target opencode (workspace) or --global; .claude/skills/ is also read natively

Step 7 — Configure integrations
  - For each integration the user opted in to: validate access; fall back to skip if unavailable.

Step 8 — Initial commits
  - Commit personal KB scaffold.
  - Commit workspace config.
  - Push if remotes are configured.

Step 9 — Verify
  - Run /kb status → clean state expected.
  - Run /kb start-day → produce first briefing.
  - Print quickstart card.
```

## Migration from Existing KBs

If the user has an existing knowledge base in another layout, `/kb setup` offers a migration mode. The migration:

1. Analyzes the existing layout against this spec.
2. Proposes a diff (files to create, rename, restructure).
3. Applies the diff only after user confirmation.
4. Preserves all git history via `git mv`.
5. Never deletes — material that doesn't fit is moved to `references/legacy/` with a note.

## Idempotency

`/kb setup` is **idempotent** by design. Running it a second time:

- Detects existing structure.
- Offers to add missing pieces.
- Never overwrites existing files (prompts if a file with the same path but different content is detected).

## Verification Checklist (Post-Setup)

- [ ] Personal KB structure matches [workspace-layout.md](workspace-layout.md).
- [ ] `.kb-config.yaml` validates (see [file-formats.md](file-formats.md)).
- [ ] `/kb status` runs cleanly.
- [ ] `/kb start-day` produces a non-empty briefing (or explicitly reports *"no pending work"*).
- [ ] At least one commit per created repo.
- [ ] Harness sanity test: the `/kb` slash command is available from the selected IDE(s).

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §10, plus onboarding questions for HTML styling |
