---
name: kb-setup
description: Interactive onboarding wizard that scaffolds a complete agentic-kb workspace. Creates the personal KB (required), any optional team/org-unit KBs, configures documented harness workflows (VS Code Copilot, Claude Code, OpenCode, plus compatible CLI guidance such as Codex CLI), and generates all required templates, configuration files, and AGENTS.md/CLAUDE.md indexes. Triggered by `/kb setup` and onboarding phrases.
version: 3.4.1
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

This skill is the single entry point for bootstrapping an `agentic-kb` workspace. It runs once per user; subsequent invocations are **idempotent** (add missing pieces, never overwrite).

## Scope boundary — install vs. init

This skill **initializes the user's KB workspace**. It does **not** distribute itself.

Two concerns, two tools:

| Concern | Who handles it | When |
|---------|---------------|------|
| Get `kb-management` + `kb-setup` + `kb-operator` into the harness (`.claude/`, `.opencode/`, `.github/`, or user-global equivalents) | Harness marketplace (`/plugin install kb@agentic-kb`) **or** `scripts/install.py` from a cloned marketplace repo | Before this skill runs — otherwise `/kb setup` wouldn't be callable |
| Scaffold the user's KB repos (`.kb-config/`, foundation files, workstreams, topics, todos, log) | **This skill** | When the user types `/kb setup` |

Concrete consequence: by the time this skill runs, the skills are already present. Step 5/6 below do not re-install them — they only create the user's workspace-level configuration files (`.github/prompts/kb.prompt.md`, `AGENTS.md`, etc.) and invoke `scripts/install` **only** when the user picks an additional harness that isn't yet present.

## When to invoke

- The user types `/kb setup`.
- The user says *"set me up with a KB"*, *"onboard me"*, *"bootstrap my workspace"*, or equivalent.
- `kb-management` detects no `.kb-config/layers.yaml` in the current directory and the user tries to run any `/kb` command — offer to run setup first.

## Interactive question flow

Ask each block in order. Stop and wait after each block for the user's answer before proceeding. Each question includes a brief explanation of how the answer shapes the setup.

1. **Your name** (used for contributor directories): `your-name`.
   *→ Sets your contributor directory name in team/org KBs, and the default KB repo name (`<name>-kb`).*
2. **Your role and themes**: one sentence + 3–5 theme keywords (these become initial workstreams).
   *→ Seeds your `me.md` foundation file, creates initial topic stubs under `_kb-references/topics/`, and pre-populates workstream files.*
3. **Vision, mission & goals (VMG)**: provide any of:
   - A URL to a strategy doc, OKR page, or team charter.
   - A file path to an existing document.
   - A short text description (vision in one sentence, mission in one sentence, 1–5 goals).
   - "Skip" — creates the file with placeholder sections.
   *→ Pre-fills `_kb-references/foundation/vmg.md`. If a URL or file is provided, the agent extracts vision/mission/goals and structures them. During `/kb digest team` and `/kb digest org`, upstream VMG from higher layers gets merged into this file automatically.*
4. **Workspace root**: absolute path. Default: current directory.
   *→ All repos, config files (`AGENTS.md`, `.kb-config/`), and harness hooks are created relative to this path.*
5. **Personal KB (L1)** — required:
   - Create new? → ask for name, initialize git, choose remote.
   - Onboard existing? → ask for path.
   *→ Your single source of truth. All `/kb` commands operate on this repo. "Onboard existing" runs migration analysis instead of scaffolding from scratch.*
6. **Team KBs (L2)** — optional, multiple:
   - Create new / onboard existing / skip.
   *→ Shared decision logs and cross-contributor references. Creates your contributor directory (`<name>/_kb-inputs/`, `<name>/_kb-references/`) and team-level `_kb-decisions/`, `_kb-tasks/`.*
7. **Org-Unit KB (L3)** — optional:
   - Onboard existing / skip.
   *→ Links your workspace to the org-wide aggregation layer. Enables `/kb promote` to push mature content upstream and, for local team KBs, complete the team-layer intake review in the same operation.*
8. **Marketplace (L4)** — optional:
   - Install from marketplace (recommended for users).
   - Clone for contributing (for skill authors).
   - Skip.
   *→ "Install" adds skills/agents to your IDE for immediate use. "Clone" gives you the source repo for authoring or modifying skills.*
9. **Personal workstreams**: 1–5 parallel workstreams with theme keywords.
   *→ Creates `_kb-workstreams/<name>.md` files and links them to your topic stubs. The daily/weekly rituals use these to scope briefings and reviews.*
10. **IDE targets**: multi-select from `vscode`, `claude-code`, `opencode`, `codex-cli`.
    *→ Determines which harness configuration files are written (`.github/prompts/`, `.claude/skills/`, `.opencode/`) and whether the setup summary must explain a compatible CLI workflow. Multiple selections create cross-harness compatibility.*
11. **Integrations**: marketplace-available MCP servers / APIs to wire up.
    *→ Configures external tool access (e.g., Jira, Confluence, GitHub) in `.kb-config/layers.yaml`. Each integration is validated for connectivity before persisting.*

11b. **Roadmap trackers** (only if `kb-roadmap` is installed or selected in Q8):
    For each workstream declared in Q9, ask:
    - *"Where do plans live for `<workstream>`?"* — options: GitHub issues, Jira, Linear, markdown export (jira-sync, etc.), skip.
    - *"Where does delivery happen for `<workstream>`?"* — option: one or more git repo paths.
    - *"What search parameters identify items in scope?"* — free-text for JQL / GitHub issue filter / label set / component, with examples per tracker.
    - *"Should the skill be allowed to write back (comments, status transitions, links)?"* — default no; if yes, which capabilities (`write-comments`, `write-status`, `write-link`, `write-item`) and which env var holds the auth token.
    - *"Opt in to continuous config tuning?"* — default yes. Skill produces a post-run digest of zero-match filters, low-match filters, and suspected noise; user walks them via `/kb roadmap tune`.

    *→ Writes `.kb-config/layers.yaml roadmap.issue-trackers[]` + `roadmap.scopes.<workstream>.trackers[]` with the declared search params. Also writes `roadmap.tune.enabled: true|false`. These values are the starting point; the tune command refines them over time.*

11c. **Import / export tools** (general, not scoped to a single primitive):
    - *"Which tools should the agent use to export content out of your trackers for offline processing?"* — options: native API (needs auth env var), CLI tool already on PATH (e.g. a sync CLI), pre-generated markdown dump, custom script. Multi-select.
    - *"Which tools can the agent call to reference a ticket from inside a KB file?"* — options: link only (URL), link + fetch summary on demand (requires read capability), deep-embed (mirror ticket body into the KB file; refresh on demand).
    - *"Ticket-reference pattern"* — free-text regex for matching ticket keys in prose (e.g. `[A-Z]+-\d+` for Jira, `#\d+` for GitHub issues, `<slug>-\d+` for Linear). Default: detect from Q11b tracker selections.
    - *"Branch / commit trailer convention"* — does your team encode ticket keys in branch names (`feat/<KEY>`, `feat/#<n>`) or commit trailers (`Refs: <KEY>`)? Both? Neither? Drives the correlation ladder's tier-2 heuristic.
    *→ Writes `.kb-config/layers.yaml integrations.tools[]` + `integrations.reference-patterns[]` + `integrations.correlation-hints.branch-patterns`. Applies to roadmap + journeys + any future primitive needing tracker correlation.*

11d. **Journeys** (only if `kb-journeys` is installed or selected in Q8):
    - *"Do you want to author user/customer/product journeys in this KB?"* — yes/no.
    - If yes:
      - *"Where should journey source markdown live?"* — options: inside this KB under `_kb-journeys/`, or in an external repo path (agent reads, writes HTML back into KB).
      - *"Tier taxonomy"* — default `Tier 1 / Tier 2 / Tier 3` or custom list of (key, label) pairs.
      - *"Readiness chip taxonomy"* — default `Green / Amber / Red`, or custom.
      - *"Actor vocabulary"* — default `CLI, WEB UI, AGENT, SYSTEM, PERSONA`, or custom list.
      - *"Link journeys to a roadmap scope?"* — if `kb-roadmap` is also enabled, offer to bind journeys to one of the declared roadmap scopes for bidirectional traceability.
    *→ Writes `.kb-config/layers.yaml journeys:` block with `source-dir`, `output-dir`, `tiers`, `readiness-levels`, `actors`, optional `roadmap-link.scope`. Scaffolds `_kb-journeys/` folder with a starter `overview.md` and an empty `html/` target. Binds journey HTML generation to the same brand tokens as presentations (Q13) — no separate brand choice.*
12. **Automation level**: 1 (manual), 2 (semi-auto), 3 (full-auto).
    *→Surfaces affected by this single choice** (the token file is reused across every HTML artifact — never re-pick per surface):

    | Surface | Template bound | Config key |
    |---------|---------------|-----------|
    | KB root index + reports | `_kb-references/templates/<brand>-presentation.html` | `styling.reference-file` |
    | Presentations | same | same |
    | Roadmap HTML (`kb-roadmap`) | `kb-roadmap/templates/roadmap.html.hbs` + adopter's tokens CSS | `html-template.base` + `html-template.tokens` in `.kb-config/artifacts.yaml` |
    | Journey HTML + mocks (`kb-journeys`, if enabled in Q11d) | `kb-journeys/templates/journey.html.hbs` + `kb-journeys/templates/shared.css.hbs` + adopter's tokens CSS | `journeys-template.base` + `journeys-template.tokens` in `.kb-config/artifacts.yaml` |

    For (b) website and (c) template paths, the skill extracts the adopter's `:root` / `[data-theme="dark"]` / `[data-theme="light"]` token blocks into a **single brand tokens CSS file** (default location `_kb-references/templates/brand/tokens.css`) and points **all four** surface configs at it. This ensures presentations, reports, roadmaps, and journeys share one source of brand truth.

    ** Controls `.kb-config/automation.yaml`: Level 1 = agent always asks before committing/pushing. Level 2 = auto-commit locally, ask before push. Level 3 = auto-commit and push (requires CI safety net).*
13. **HTML artifact styling** — corporate design is mandatory, not optional:
    - *"For generated presentations and reports, which corporate design should the agent use?"*
    - (a) **Default built-in template** — vendor-neutral accessible tokens shipped with agentic-kb.
    - (b) **Derive from a website** — point to a corporate web page; agent fetches, extracts colors/typography/spacing, writes a token file.
    - (c) **Point to a corporate template file** — the preferred path for adopters with an existing brand HTML. Agent copies the file to `_kb-references/templates/<brand>-presentation.html` and anchors all artifacts to it.
    - Always generate both light and dark themes with an in-page toggle.
    *→ This question configures the single source of truth for all HTML artifacts (root index, presentations, reports). Every `/kb present`, `/kb report`, and `/kb-report` run reads `.kb-config/artifacts.yaml → styling.reference-file` and reuses its CSS variables — they never improvise a fresh palette.*

    **Customization contract (what the skill must do per choice):**

    | Choice | Required setup actions |
    |--------|----------------------|
    | (a) builtin | Copy `templates/presentation-template.html` → `_kb-references/templates/presentation-template.html` **unchanged**. Write `styling.source: builtin` and `styling.reference-file: _kb-references/templates/presentation-template.html` to `.kb-config/artifacts.yaml`. Index/reports use the vendor-neutral default theme in `.kb-scripts/generate-index`. |
    | (b) website | Copy `templates/presentation-template.html` → `_kb-references/templates/<brand>-presentation.html`. Fetch the URL, extract primary/secondary/surface/text colors + heading/body font. Rewrite only the `:root`/`[data-theme="dark"]`/`[data-theme="light"]` token blocks and the `--font-family` variable in that file — keep all layout, slide types, and scripts intact. Also offer to fetch the site's favicon/signet and inline it into the `.brand-logo` and `.bg-brand` `<svg>` slots. Set `styling.source: template`, `styling.reference-file: _kb-references/templates/<brand>-presentation.html`, `styling.reference-url: <the-url>`. |
    | (c) template | Copy the provided file to `_kb-references/templates/<brand>-presentation.html` (preserve the original source path in a comment header). If the file is missing any of: dark theme token block, light theme token block, `.brand-logo` slot, `.bg-brand` slot, theme toggle, or timestamp meta-line on the cover — offer to merge the missing pieces from `templates/presentation-template.html` (the skill's generic baseline). Set `styling.source: template`, `styling.reference-file: _kb-references/templates/<brand>-presentation.html`. |

    **The generic `templates/presentation-template.html`** is structured so that only five areas need brand customization (every customization point is marked with `CUSTOMIZE:` comments):
    1. Dark-theme token block (`:root`, `[data-theme="dark"]`)
    2. Light-theme token block (`[data-theme="light"]`)
    3. `--font-family`
    5. **If journeys are enabled (Q11d)**: render the starter `_kb-journeys/overview.md` via `kb-journeys render --dry-run`; confirm the generated `shared.css` `:root` block contains the same primary brand hex as the presentation template. If not, the token extraction missed a surface — abort Step 3 and rerun.
    6. **If roadmap is enabled (Q11b)**: render a no-op `/kb roadmap <default-scope>` to verify the roadmap HTML uses the same tokens. Zero hex drift across the three surfaces is the exit criterion.
    4. `.brand-logo` inline `<svg>` — the small signet in the header
    5. `.bg-brand` inline `<svg>` — the large visible brand mark on the cover slide

    Everything else (slide types, cards, callouts, badges, tables, nav, theme toggle, keyboard shortcuts, print CSS, changelog appendix, cover timestamp) is reusable as-is.

    **Post-customization verification (MUST pass before Step 8 commit):**

    1. Run `python3 .kb-scripts/generate-index . --title "<KB_NAME>"` and confirm the generated `index.html` contains the adopter's accent color hex value (not the neutral default unless the adopter's brand IS that color).
    2. Open the reference template and confirm it defines both `:root`/`[data-theme="dark"]` and `[data-theme="light"]` token blocks. If the adopter's file is single-theme, the skill MUST extend it with a light-theme counterpart derived from the dark tokens (or vice versa).
    3. Grep the generated `index.html` for the adopter's primary brand color — if zero hits, token extraction failed; report the mismatch and ask the user to fix the template or switch to builtin.
    4. Confirm the brand template still renders a non-placeholder `.brand-logo` and `.bg-brand` SVG. If the placeholders are still there, prompt the user for the brand signet SVG and inline it before proceeding.

## What setup does (after confirmation)

### Step 1 — Prerequisites (MUST abort on missing required tools)

Required (setup cannot proceed without these):

| Tool | Check | Abort message if missing |
|------|-------|--------------------------|
| `git` | `git --version` exits 0 | macOS: `xcode-select --install` · Debian/Ubuntu: `sudo apt install git` · Fedora: `sudo dnf install git` · Windows: [git-scm.com/download/win](https://git-scm.com/download/win) |
| Harness CLI (at least one first-class target: `claude`, `code`, or `opencode`) | binary on PATH | Install the harness first; the skill can't install itself into an absent harness |
| Optional compatible CLI: `codex` | binary on PATH when Codex workflow is selected | Not required for bootstrap. If present, include Codex-specific repo-local workflow notes in the final setup summary. |

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
Directories: `_kb-inputs/`, `_kb-inputs/digested/`, `_kb-references/{topics,findings,foundation,reports,legacy}/`, `_kb-ideas/`, `_kb-ideas/archive/`, `_kb-decisions/`, `_kb-decisions/archive/`, `_kb-tasks/{,archive}/`, `.kb-log/`, `.kb-scripts/`, `_kb-workstreams/`.

Files (from the scaffold template set):
- `AGENTS.md`, `README.md`, `.kb-config/layers.yaml`, `.kb-config/automation.yaml`, `.kb-config/artifacts.yaml` from `kb-setup/templates/`.
- Initial `_kb-workstreams/<name>.md` per declared workstream from `kb-management/templates/workstream.md`.
  - If the referenced template file is missing, stop and report the missing path instead of improvising a substitute scaffold.
- `_kb-references/foundation/{me,context,vmg,stakeholders,sources,naming}.md` from `kb-setup/templates/`.
  - `vmg.md` is pre-filled from Q3: if the user provided a URL, fetch and extract vision/mission/goals into structured sections. If a file path, read and extract. If short text, structure directly. If skipped, write placeholder sections.
- Initial `_kb-references/topics/<slug>.md` per declared theme (with empty changelog) from `kb-management/templates/topic.md`.
  - If the referenced template file is missing, stop and report the missing path instead of improvising a substitute scaffold.
- `_kb-references/templates/presentation-template.html` — copied verbatim from `kb-setup/templates/presentation-template.html` (vendor-neutral baseline: design tokens, dark/light themes, slide nav, brand-mark slot, cover timestamp, appendix/changelog). Q13 rewrites this file in place when the adopter picks template/website; the copy is also the fallback for `source: builtin`.
- `_kb-tasks/focus.md`, `_kb-tasks/backlog.md` from `kb-management/templates/{focus,backlog}.md`.
  - If the referenced template file is missing, stop and report the missing path instead of improvising a substitute scaffold.
- `.kb-scripts/generate-index` — artifact index generator (from `scripts/generate-index.py`).
- `.nojekyll` — **required** empty marker file at the repo root. GitHub Pages runs Jekyll by default, which silently drops directories whose names start with `_` (e.g. `_kb-references/`, `_kb-inputs/`). Without `.nojekyll`, every artifact under an underscore-prefixed directory returns 404 on Pages. The file must be present on whichever branch Pages serves from (typically `main` or `gh-pages`).
- `index.html` — initial root artifact index (generated by running the script).

### Step 4 — Scaffold team KB (if creating new)
- Contributor directory (`<your-name>/_kb-inputs/`, `<your-name>/_kb-references/{topics,findings}/`).
- `_kb-decisions/`, `_kb-decisions/archive/`, `_kb-tasks/{focus,backlog}.md`, `_kb-tasks/archive/`, `.kb-log/`, `AGENTS.md`, `README.md`.
- `.kb-scripts/generate-index` — artifact index generator (same script as personal KB).
- `.nojekyll` — empty marker at repo root (same reason as personal KB: Pages would otherwise 404 every `_`-prefixed path).
- `index.html` — initial root artifact index.

### Step 5 — Workspace-level configuration

Workspace-level *KB configuration* (distinct from harness-level *skill installation*):

- `AGENTS.md` at workspace root with a repo index + short-alias table + keyword lookup.
- `CLAUDE.md` → symlink to `AGENTS.md`.

Note: all configuration YAMLs live inside the personal KB under `.kb-config/` — not at workspace root. The workspace root only holds `AGENTS.md`, `CLAUDE.md`, and `.github/` harness hooks.

The repo index and alias table are generated by scanning the workspace for git repos with an `AGENTS.md`, `CLAUDE.md`, or `README.md`. Short aliases are derived automatically (initials of hyphenated segments, or first 2–3 chars for single-word repos). Collisions are resolved by appending digits. Users can override aliases in `.kb-config/layers.yaml` under `workspace.aliases`.

Optional workspace-level harness hooks (only written if the harness was **not** already configured by marketplace install or `scripts/install`):

- VS Code selected → write `.github/prompts/kb.prompt.md` and `.github/instructions/kb.instructions.md` from `templates/` **only if missing**.
- Claude Code / OpenCode selected → nothing to write at workspace level; plugin/install handles `.claude/` and `.opencode/`.
- Codex CLI selected → do not claim native install support. Reuse the workspace-level `AGENTS.md`, `CLAUDE.md`, and any generated prompt/instruction files as the documented operating contract.

### Step 6 — Configure additional IDE targets

For any harness the user selected that is **not yet installed**, run the installer and record the outcome:

- **Claude Code**: recommend `/plugin marketplace add <repo-url>` + `/plugin install kb@agentic-kb` from inside Claude Code (preferred — handles updates). Fall back to `<marketplace>/scripts/install --target claude` for dev installs.
- **VS Code**: point the user at `chat.plugins.marketplaces` in `settings.json` for one-click install, or run `<marketplace>/scripts/install --target vscode` for direct workspace copy.
- **OpenCode**: no marketplace. Run `<marketplace>/scripts/install --target opencode` (workspace) or `--global`. OpenCode also reads `.claude/skills/`, so a Claude Code install in the same workspace is picked up automatically.
- **Codex CLI**: no native marketplace/install target yet. Mark it as a compatible CLI workflow, explain that `/kb setup` bootstrap should happen through a first-class supported harness (or a repo-local manual setup path), and point Codex users at the generated workspace files as the runtime contract.

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
5. Move material that doesn't fit into `_kb-references/legacy/` with a note — **never delete**.

## Idempotency

Running `/kb setup` a second time:

- Detects existing structure.
- Offers to add only missing pieces.
- Prompts if a file with the same path but different content is detected.

## Safety

- Never overwrites existing files without explicit confirmation.
- Never creates a remote repo without asking.
- Never pushes to a remote without asking.

## Promote handoff expectation

Scaffolded team KBs must teach the same promote contract as `kb-management`:

- L1 → L2 promotion is not mailbox-only.
- If the destination team KB is available locally, `/kb promote` stages the
   artifact in `<contributor>/_kb-inputs/`, performs the contributor-local team
   review immediately, archives the staged intake under `digested/YYYY-MM/`, and
   leaves the durable result in `<contributor>/_kb-references/`.
- Team READMEs and prompts must describe `/kb review` as the command for
   material created directly inside the team repo, not as a mandatory second step
   after every L1 promotion.

## References (load on demand)

- `references/setup-flow.md` — full step-by-step walkthrough with example output.
- `../../../docs/first-run-acceptance.md` — deterministic onboarding acceptance path and rollout verification baseline.
- `references/migration-guide.md` — how to migrate an existing KB.
- `references/troubleshooting.md` — common setup issues.

## Templates

All templates are in `templates/`. The skill instantiates them with values from the interactive interview. Template keys are `{{DOUBLE_BRACE}}` placeholders.

### Placeholder → interview-answer mapping (MUST be substituted)

Every placeholder below has exactly one source — always from the interview answers collected in the 13 question blocks. If a source is missing, **ask the user again** before writing; never leave a literal `{{…}}` in an output file.

| Placeholder | Source (question block) |
|-------------|------------------------|
| `{{USER_NAME}}` | Q1 (your name) |
| `{{ROLE}}` | Q2 (role sentence) |
| `{{THEMES}}` | Q2 (theme keywords, rendered as a bullet list) |
| `{{KB_NAME}}` | Q5 (personal KB name; defaults to `<user-name>-kb` if the user accepts the default) |
| `{{KB_DESCRIPTION}}` | Q2 (one-sentence role statement) |
| `{{VMG_VISION}}` | Q3 (extracted vision statement — from URL fetch, file read, or direct text; placeholder if skipped) |
| `{{VMG_MISSION}}` | Q3 (extracted mission statement — same sources as vision) |
| `{{VMG_GOALS}}` | Q3 (extracted goals as table rows `| G-YYYY-Qn-N | description | horizon | active |`; placeholder row if skipped) |
| `{{WORKSTREAMS}}` | Q9 (rendered as a bullet list: `- <name>: <themes>`) |
| `{{WORKSTREAM_N_NAME}}`, `{{WORKSTREAM_N_THEMES}}` | Q9 (per declared workstream) |
| `{{TEAM_NAME}}` | Q6 (per declared team, if any) |
| `{{ORG_UNIT_NAME}}` | Q7 (if an org-unit KB was onboarded) |
| `{{REPO_INDEX}}` | Computed — one bullet per configured KB layer with its path + role |
| `{{KEYWORD_LOOKUP}}` | Computed — `docs/glossary.md` summary injected verbatim |
| `{{RECENT_REPORTS}}` | Empty `<ul></ul>` on first run (will be filled by `/kb present` / `/kb report`) |
| `{{DATE}}` | Today's ISO-8601 date (`YYYY-MM-DD`) |
| `{{MATURITY}}` | `raw` for the initial topic-stub scaffold (empty positions). Findings written later by `/kb` capture set it from the gate outcome — see `kb-management/SKILL.md` rule 1. |
| `{{VERSION}}` | `1.0` on first scaffold; later artifacts bump their own version |
| `{{BRAND_NAME}}` | Q13 — adopter brand display name (defaults to `{{KB_NAME}}` when not set) |
| `{{CONFIDENTIAL_LABEL}}` | Q13 — e.g. `Confidential`, `Internal`, or empty string to hide |
| `{{PRESENTATION_TITLE}}` | Left as-is in `presentation-template.html`; filled by `/kb present` |
| `{{SUBTITLE}}`, `{{COVER_BADGE}}`, `{{CONTACT}}` | Left as-is in the template; filled per-artifact by `/kb present` |
| `{{CREATED_ISO}}`, `{{CREATED_DATE}}`, `{{CREATED_TIME}}` | Filled at artifact render time with exact creation timestamp (ISO-8601, `YYYY-MM-DD`, `HH:MM TZ`) |

### Post-write check (MUST run before Step 8)

After all files are written and before the initial commit, scan the scaffolded workspace for any remaining `{{` sequence **outside** the deliberate deferred-placeholder set. If any match is found:

1. Stop — do not commit.
2. List the (file, line, placeholder) triples to the user.
3. Ask for the missing values.
4. Re-render, then re-scan.

Deferred-placeholder exemption: the presentation template (`_kb-references/templates/presentation-template.html` — or `<brand>-presentation.html` when Q13 branded it) intentionally keeps its placeholders unfilled because they are per-artifact fields filled at presentation time by `/kb present`. Exempt this file from the gate. The exempted placeholders are `{{PRESENTATION_TITLE}}`, `{{SUBTITLE}}`, `{{COVER_BADGE}}`, `{{CONTACT}}`, `{{CREATED_ISO}}`, `{{CREATED_DATE}}`, `{{CREATED_TIME}}` (see §Templates).

Concrete grep the skill must run (or equivalent):

```
grep -rn --exclude-dir=node_modules \
     --exclude '*-presentation.html' --exclude 'presentation-template.html' \
     '{{[A-Z_0-9]*}}' <workspace-root> || true
```

A zero-hit run is the gate for Step 8.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-22 | Bumped declared skill version to 3.4.1 so the placeholder-gate behavior change ships under the current framework patch version | Version alignment |
| 2026-04-22 | Post-write placeholder gate now exempts `presentation-template.html` (and its branded sibling) because its `{{…}}` markers are deliberately deferred for `/kb present` — setup Step 8 no longer blocks on the shipped template | Fixes #17 |
| 2026-04-22 | Clarified which personal-KB scaffold files come from `kb-setup` templates versus `kb-management` templates and required setup to stop explicitly if a referenced template file is missing | Scaffold source contract |
| 2026-04-22 | Clarified which personal-KB scaffold files come from `kb-setup` templates versus `kb-management` templates so `/kb setup` is implementable without guesswork | System test follow-up |
| 2026-04-22 | Added Codex CLI as a documented compatible workflow and clarified that first-class install support still belongs to Claude Code, VS Code, and OpenCode; version bumped to 3.4.0 | Compatibility expansion |
| 2026-04-22 | Team-KB scaffolding now explains that `/kb promote` completes local team intake review during the same operation; version bumped to 3.3.0 | Team promote flow fix |
| 2026-04-22 | Version aligned to 3.2.0 | Spec review |
