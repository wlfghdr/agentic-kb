# Changelog

All notable changes to the **agentic-kb** specification are documented here.

This file follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) convention.
The spec uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html): `MAJOR.MINOR.PATCH`.

## Versioning Conventions

| Bump | When to use |
|------|-------------|
| **PATCH** | Prose edits, typos, clarifications that don't change meaning or structure |
| **MINOR** | New sections, new spec rules, new commands — non-breaking additions |
| **MAJOR** | Breaking changes to the directory layout, command surface, or file formats that invalidate existing implementations |

**Versioning**: the root-level `VERSION` file and this `CHANGELOG.md` track the aggregate framework version. The behavioral spec lives in `plugins/kb/skills/*/SKILL.md` and `plugins/kb/agents/*.md`; the structural reference is `docs/REFERENCE.md`.

---

## [Unreleased]

### Changed

- **`/kb promote` for local team KBs** — promotion is now a composite operation: stage the intake in the target contributor `_kb-inputs/`, run the L2 review immediately in team context, archive the staged input under `_kb-inputs/digested/YYYY-MM/`, and leave the reviewed result in `_kb-references/`. Updated `kb-management`, its command/output docs, the team-scaffold template, and collaboration guidance so promote no longer teaches a mandatory second manual `/kb review` after every L1 promotion.

### Fixed

- **`docs/examples/first-hour.md` setup-flow drift** — the first-hour walkthrough now matches the current `kb-setup` interview order: 13 core question blocks, VMG explicitly documented as Q3, and the remaining onboarding answers renumbered through Q13. Fixes #27.
- **Phantom Family-1 live overviews dropped** — `kb-management` SKILL rule 9, `command-reference.md` `--refresh-overviews`, `html-artifacts.md` §Family 1, `docs/REFERENCE.md` §HTML artifacts, `kb-operator.md` §Always-current overviews, and `docs/examples/first-hour.md` all stop claiming that `inventory.html`, `open-decisions.html`, and `open-tasks.html` get regenerated after every mutation. No generator ever existed for those three files; their equivalent signals already live in `dashboard.html` panels. The orphan cards pointing to them in `kb-management/templates/index.html` are replaced with a dashboard card. Fixes #18.
- **`docs/REFERENCE.md` workspace-root prompt contract** — the required-files row no longer treats `.github/prompts/kb.prompt.md` as universal. `REFERENCE.md` now mirrors the established harness-specific setup contract: VS Code uses `.github/prompts/` + `.github/instructions/`, Claude Code and OpenCode do not require workspace prompt files, and compatible CLI workflows reuse whatever prompt/instruction files are already present in the initialized workspace. Fixes #28.
- **`kb-setup` version alignment** — bumped `plugins/kb/skills/kb-setup/SKILL.md` from `3.4.0` to `3.4.1` so the shipped placeholder-gate behavior fix is versioned under the current framework patch release.
- **Setup post-write placeholder gate blocked on shipped template** — `kb-setup` Step 8 scanned every file in the scaffolded workspace for residual `{{…}}` markers and refused to commit when it found any. The shipped `presentation-template.html` (and its branded sibling) intentionally keep seven `{{…}}` fields because they are filled per-artifact by `/kb present`, so the gate failed on every first run. The post-write check + `docs/examples/first-hour.md` + `docs/first-run-acceptance.md` now exempt those filenames. Fixes #17.
- **Idea lifecycle field canonicalized to `**Stage**:`** — `generate-dashboard.py` now reads the `**Stage**:` bold-bullet field on idea files (matching `docs/REFERENCE.md` and the `idea.md` template) and accepts a legacy `**Status**:` fallback so pre-3.5 idea files keep rendering. Audit K5 + cross-primitive rule X3 updated to the canonical field. `test_generate_dashboard.py` gains a regression case covering both forms. Fixes #35.
- **`command-reference.md` triage table completeness** — the bare-`/kb` signal list now includes `Top task` and `External completions`, matching the generated `kb.prompt.md` contract and the task-handling rules already defined in `kb-management`. Follow-up within PR #49.
- **`command-reference.md` drift** — the task verb is now declared canonical as `/kb task` (with `/kb todo` and `/kb tasks` as accepted aliases), a new Ideas section documents `/kb idea` and `/kb develop`, and the stale-task triage rule is split into `focus-overdue-days` (7) and `backlog-stale-days` (14) matching the canonical bullet-in-file data model used by `kb.prompt.md` and SKILL rule 11g. Fixes #24, #25, #26.
- **`scripts/install.py` drift detection** — existing installs now compare source and installed front-matter `version:` values for skills and agents before skipping. Re-runs report `up-to-date` when versions match, `stale (old -> new)` when a copied install is behind, and the generic `skip (exists)` path now tells adopters to rerun with `--force` to reinstall/update. Fixes #29.
- **Evaluation gate Q5 polarity and scoring examples** — `kb-management` now frames Q5 as "materially new compared to existing topics", defines the numeric score as the count of yes answers across Q1-Q5, removes the obsolete VMG `+1` bonus from the normative summaries, and fixes the worked examples/log wording. Fixes #30.
- **`**Maturity**:` never written on findings/topics** — added the field to `finding.md` and `topic.md` templates, wired the capture flow in `kb-management/SKILL.md` to set it from the gate outcome, and aligned the triage signal (`kb.prompt.md`, `command-reference.md`) and audit rule K1 (`audit.md`) to read the same bold-bullet form. Fixes the broken `capture → promote` surfacing loop (#14, #31).
- **Open-decisions triage signal never fires** — aligned the `/kb` triage rule and audit K4 to read the decision template's `**Status**:` bold-bullet form instead of a non-existent `status: proposed` YAML frontmatter. Triage now counts open decisions as files under `_kb-decisions/` whose status is not `resolved` / `superseded` / `dropped`. Fixes #15.
- **Dashboard focus/backlog parser bugs** (`scripts/generate-dashboard.py`) — the parser now respects `##` section boundaries (no more `(none)` under `## Waiting` counted as a focus task), strips HTML comments from bullet titles so metadata like `<!-- workstream: … -->` no longer leaks into the rendered UI, and skips placeholder bullets (`(none)`, `(empty)`, `—`, `-`). Added `scripts/test_generate_dashboard.py` with CI coverage. Fixes #23.
- **Missing `idea.md` scaffold template** — restored `plugins/kb/skills/kb-management/templates/idea.md` so `/kb idea` has a canonical file source again, matching the behavioral spec and REFERENCE docs.
- **`/kb setup` scaffold source ambiguity** — clarified in `plugins/kb/skills/kb-setup/SKILL.md` which personal-KB scaffold files come from `kb-setup/templates/` versus `kb-management/templates/`, so implementers no longer have to guess across two directories.
- **Residual vendor-neutrality cleanup** — removed the last internal-specific residue from the public spec by replacing an internal example label in `kb-roadmap` adapter docs and generalizing a changelog note that still exposed a vendor-prefixed token pattern.
- **Vendor-neutrality sweep** — removed all vendor-specific terms from scripts, templates, and plugin skill docs:
  - `generate-dashboard.py` / `generate-index.py`: removed vendor logo SVG and vendor-prefixed CSS variable mappings; only generic token names remain.
  - `kb-setup/templates/artifacts.yaml`: removed vendor logo option; built-in choices are now `hexagon | none` plus custom `logo-file`.
  - `kb-journeys/SKILL.md`: removed internal-repo path reference from mock-extraction script description.
  - `kb-roadmap` references and script: replaced vendor-specific hierarchy terms with generic equivalents (Theme, Initiative, Epic) throughout `adapters.md`, `html-template.md`, and `kb_roadmap.py`.
- **`CONTRIBUTING.md` stale reference** — replaced `make check` (no Makefile exists) with "Local checks pass".
- **Version alignment** — `kb-management` SKILL.md, `kb-setup` SKILL.md, and `kb-operator` agent.md now all declare `version: 3.2.0`, matching the framework version.
- **`spec-summary.md` layout discrepancy** — decisions directory now shows active decisions at root (matching REFERENCE.md and SKILL.md), not under an `active/` subdirectory. Added missing `_kb-ideas/`, `index.html`, and `dashboard.html` entries.
- **`command-reference.md` stale path** — promote command now references `_kb-inputs/` (not old `inputs/`). Section renamed to "Decisions & Tasks" for glossary consistency.
- **`rituals.md` rule number drift** — task-reconciliation references updated from `#10c` to `#11c` (matching current SKILL.md rule numbering).
- **`setup-flow.md` broken links** — fixed relative path depth for `docs/first-run-acceptance.md` cross-references (4 levels → 5 levels).
- **`REFERENCE.md` markdown-lint violations** — removed leading whitespace on heading and list items in the draft-skill config section; fixed extra table column in the changelog.
- **`generate-index.py` self-containment** — removed the external Google Fonts import so generated root artifact indexes stay fully self-contained and comply with the HTML artifact contract.
- **Stale manual-refresh guidance** (`docs/examples/first-hour.md`, `plugins/kb/skills/kb-management/references/command-reference.md`, `docs/roadmap.md`) — walkthroughs, triage rules, and roadmap status now match the shipped always-current overview behavior.
- **Manifest version drift** (`plugin.json`, `plugins/kb/plugin.json`, `.claude-plugin/marketplace.json`) — root and per-plugin marketplace metadata now match the current framework version (`3.2.0`) and describe the shipped draft extensions accurately.
- **`kb-roadmap` config-path drift** (`plugins/kb/skills/kb-roadmap/scripts/kb_roadmap.py`) — the pilot now reads `.kb-config/layers.yaml` and `.kb-config/artifacts.yaml`, with legacy fallback to the retired flat config files.

### Added

- **Simulated-workspace regression coverage for `generate-index.py`** (`scripts/test_generate_index.py`, `.github/workflows/validate.yml`) — CI now generates a root artifact index inside a temporary KB and verifies pinned-category ordering, version-family deduplication, referenced-subpage hiding, and dual-theme output.
- **Automatic live-overview regeneration contract** (`plugins/kb/skills/kb-management/SKILL.md`, `plugins/kb/skills/kb-management/references/html-artifacts.md`, `plugins/kb/agents/kb-operator.md`, `plugins/kb/skills/kb-setup/templates/kb.prompt.md`) — overviews are now regenerated as part of every state-mutating `/kb` operation instead of being treated as a later optional refresh.
- **Top-level coverage for draft primitives** (`README.md`, `docs/REFERENCE.md`, `docs/glossary.md`, `AGENTS.md`, `CONTRIBUTING.md`) — the public spec now explicitly documents the optional `kb-roadmap` and `kb-journeys` skills, their `_kb-roadmaps/` and `_kb-journeys/` directories, and the current `plugins/kb/` source layout.

### Tooling

- **`check_consistency.py` forbidden-term scanning** — extended to cover all text file types and removed the `plugins/` exclusion so skill/agent docs are also checked.

## [3.4.0] — 2026-04-22

### Added

- **Codex CLI compatibility model** (`README.md`, `docs/REFERENCE.md`, `docs/first-run-acceptance.md`, `docs/examples/first-hour.md`, `plugins/kb/skills/kb-setup/SKILL.md`, `plugins/kb/skills/kb-setup/references/setup-flow.md`, `docs/glossary.md`) — documented Codex CLI as a compatible repo-local workflow, distinguished first-class supported harnesses from partial/manual paths, and updated onboarding plus harness-support guidance to leave room for additional CLIs and IDEs under the same model.

### Version bumps

- Root `VERSION`: 3.3.0 → 3.4.0.
- `plugin.json`: 3.3.0 → 3.4.0.
- `plugins/kb/plugin.json`: 3.3.0 → 3.4.0.
- `.claude-plugin/marketplace.json`: 3.3.0 → 3.4.0.
- `plugins/kb/skills/kb-setup/SKILL.md`: 3.3.0 → 3.4.0.
- `plugins/kb/skills/kb-management/SKILL.md`: 3.3.0 → 3.4.0.
- `plugins/kb/agents/kb-operator.md`: 3.3.0 → 3.4.0.

## [3.1.0] — 2026-04-20

### Added

- **Generic presentation template** (`plugins/kb/skills/kb-setup/templates/presentation-template.html`) — vendor-neutral reveal-style deck that adopters get via `/kb setup` Q13. Left-aligned section-title slides with a gradient underline, closing slide before an appendix divider, and a mandatory Changelog slide as the final slide.
- **Vendor-neutrality pre-push hook** (`scripts/hooks/pre-push` + `scripts/install-hooks.sh`) — runs `check_consistency.py`, `check_plugin_structure.py`, and `check_html_artifacts.py` before every push so forbidden terms, broken structure, and drift never reach the remote. Emergency bypass documented (`git push --no-verify`).
- **Blocklist guidance in CONTRIBUTING.md** — describes the optional `.forbidden-terms.txt` layered-vocabulary mechanism and how to install the pre-push hook locally.

### Fixed

- **Duplicate commands in VS Code** (`kb-management` + `kb:kb-management`): root `plugin.json` now declares only a `plugins` array pointing to `plugins/kb/` instead of listing skills/agents directly. Moved `plugins/kb/.claude-plugin/plugin.json` → `plugins/kb/plugin.json` (flat marketplace convention, matching common agent-plugin layouts). Added `x-skills` and `x-agents` to plugin manifest.
- **Physical consolidation under `plugins/kb/`**: skills and the agent are no longer duplicated between top-level `skills/`, `agents/` and symlinks inside `plugins/kb/`. The real directories now live at `plugins/kb/skills/kb-management/`, `plugins/kb/skills/kb-setup/`, `plugins/kb/agents/kb-operator.md`. Top-level `skills/` and `agents/` directories are removed. This prevents VS Code Agent Plugins from registering each skill twice (once as a root-plugin skill, once as a `kb:` sub-plugin skill).
- **`install.py`**: resolves skills/agents from per-plugin manifests (`x-skills`/`x-agents` in `plugins/<name>/plugin.json`) instead of from root `plugin.json` `skills`/`agents` keys (removed). Falls back to disk enumeration. Discovers skill/agent source paths by walking `plugins/<name>/skills/` and `plugins/<name>/agents/`.
- **`generate_plugins.py`**: no longer materialises symlinks — plugin dirs are the canonical source. Now only regenerates the per-plugin `plugin.json` manifest with `x-skills`/`x-agents` derived from the real directory contents. Still idempotent.
- **`check_plugin_structure.py`**: iterates `plugins/<name>/skills/` and `plugins/<name>/agents/` instead of the removed top-level dirs.
- **`.claude-plugin/marketplace.json`**: version bumped 2.0.0 → 3.0.0.
- **Remaining bare KB paths**: `rituals.md`, `spec-summary.md`, `migration-guide.md`, `troubleshooting.md` updated to use `_kb-` prefix convention consistently (`_kb-tasks/`, `_kb-decisions/`, `_kb-inputs/`, `_kb-references/`, `.kb-log/`).

### Changed

- **Configuration consolidated into `.kb-config/` directory**: flat `.kb-config.yaml`, `.kb-automation.yaml`, `.kb-artifacts.yaml` replaced by `.kb-config/layers.yaml`, `.kb-config/automation.yaml`, `.kb-config/artifacts.yaml`. All config lives inside the personal KB — workspace root no longer hosts config YAMLs. L2/L3 repos do not need config — the personal KB's `layers.yaml` is the single source of truth for layer topology. Updated: REFERENCE.md, both SKILL.md files, all templates, spec-summary, html-artifacts, glossary, first-hour, setup-flow, migration-guide, troubleshooting, kb-operator agent.

### Documentation additions

- **Built-in tools in SKILL frontmatter**: both `kb-management` and `kb-setup` now declare 13 built-in tools (`run_in_terminal`, `read_file`, `create_file`, `replace_string_in_file`, `multi_replace_string_in_file`, `list_dir`, `file_search`, `grep_search`, `semantic_search`, `manage_todo_list`, `vscode_askQuestions`, `fetch_webpage`, `memory`) so the chat session has all needed tools selected by default.
- **Setup questionnaire explanations**: each of the 13 interview questions now includes a brief `→` note explaining how the answer affects the resulting setup.
- **`docs/collaboration.md`**: added a dedicated human collaboration guide for shared KB workspaces, including layer responsibilities, review points, action-mode clarity, and failure recovery norms.
- **`docs/first-run-acceptance.md`**: added a deterministic onboarding acceptance path with explicit install-vs-init boundaries, expected first outputs, scaffold checks, and a team-lead rollout checklist.
- **Collaboration-safe output contract**: added `plugins/kb/skills/kb-management/references/output-contract.md`, tightened output semantics in `kb-management`, and updated examples so read-only, proposed, and applied actions are auditable for humans.

---

## [3.0.0] — 2026-04-19

### Breaking — Directory renames

All KB-managed folders use a `_kb-` prefix to clearly separate them from user files and non-KB directories:

| Old | New | Reason |
|-----|-----|--------|
| `inputs/` | `_kb-inputs/` | `_kb-` prefix — visible, sorted to top, unambiguously KB-managed |
| `ideas/` | `_kb-ideas/` | Same |
| `decisions/` | `_kb-decisions/` | Same |
| `tasks/` | `_kb-tasks/` | Same |
| `references/` | `_kb-references/` | Same |
| `workstreams/` | `_kb-workstreams/` | Same |
| `log/` | `.kb-log/` | Dot prefix — truly hidden infra you never browse |
| *(new)* | `.kb-scripts/` | Same — hidden infra |

Convention: `_kb-*` = visible KB structure (you browse these, KB agents manage them), `.kb-*` = hidden infrastructure.

Team KB contributor folders now **mirror personal KB structure** — `_kb-inputs/` + `_kb-references/` instead of the old `inputs/` + `outputs/` pattern.

**Migration**: `git mv inputs _kb-inputs && git mv ideas _kb-ideas && git mv decisions _kb-decisions && git mv tasks _kb-tasks && git mv references _kb-references && git mv workstreams _kb-workstreams && git mv log .kb-log`.

### Changed

- `docs/REFERENCE.md` — all L1/L2/L3 layout diagrams, required-files table, file format headings, and the five-layer ASCII overview updated to new directory names. Version bumped to 3.0.
- `docs/glossary.md` — Focus, Idea, Task paths updated.
- `docs/examples/day-in-the-life.md` — all path references updated.
- `docs/examples/first-hour.md` — all path references updated.
- `skills/kb-management/SKILL.md` — directory contract, log rule, flow primitives updated.
- `skills/kb-management/references/` — command-reference, evaluation-gate, html-artifacts, rituals, spec-summary updated.
- `skills/kb-setup/SKILL.md` — Step 3 (personal KB scaffold) and Step 4 (team KB scaffold) directory lists updated.
- `skills/kb-setup/references/` — setup-flow, migration-guide updated.
- `skills/kb-setup/templates/` — personal-kb-README, personal-kb-AGENTS, team-kb-README, team-kb-AGENTS, org-kb-README, kb.prompt, kb.instructions updated.
- `agents/kb-operator.md` — `_kb-inputs/` in capture loop.

### Version bumps

- Root `VERSION`: 2.2.0 → 3.0.0.
- `plugin.json`: 2.2.0 → 3.0.0.
- `docs/REFERENCE.md`: 1.0 → 3.0.
- `skills/kb-setup/SKILL.md`: 2.2.0 → 3.0.0.
- `skills/kb-management/SKILL.md`: 2.2.0 → 3.0.0.
- `agents/kb-operator.md`: 2.2.0 → 3.0.0.

---

## [2.2.0] — 2026-04-19

### Removed

- **`docs/concept/` (12 files) and `docs/spec/` (11 files)** — consolidated into a single `docs/REFERENCE.md`. The behavioral spec is the skill/agent files themselves; the reference doc retains only implementation-critical structure (architecture, layout, formats, HTML contract, security, marketplace).

### Changed

- `docs/REFERENCE.md` — new single-file reference replacing 23 concept/spec docs.
- All cross-references (`README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `agents/kb-operator.md`, `docs/roadmap.md`, `scripts/check_html_artifacts.py`, `skills/kb-management/references/spec-summary.md`) updated to point to `docs/REFERENCE.md`.
- `README.md` — replaced `<org>` placeholders with actual repo URL (`wlfghdr/agentic-kb`). Restructured install section as "Getting started": marketplace-first flow (connect → `/kb setup`), cross-harness install script as optional secondary path.
- `README.md` — rewrote problem section as direct questions ("Does this sound familiar?"), renamed "The solution" → "How it works".
- `index.html` — intro now leads with the same user-facing questions; problem section renamed to "Why existing approaches fail".
- `docs/concept/02-architecture.md` — L3 now has team-isolated directories (mirroring L2's person-directories). L5 clarified as reference-only (no bottom-up input). Added contributor-unit / cross-analysis summary to the ASCII diagram.
- `docs/spec/workspace-layout.md` — L3 directory layout updated with per-team `_kb-inputs/` + `_kb-references/` structure. Required-files table updated.

### Added

- `docs/concept/11-ideas.md` — Ideas as first-class incubation objects with lifecycle (`seed → growing → ready → shipped | archived`), `/kb develop` sparring flow, pattern detection (3+ signal convergence), annotations, freshness tracking.
- `docs/concept/12-vision-mission-goals.md` — VMG strategic steering model across all layers. Vision (years), Mission (quarters), Goals (weeks–quarters). Evaluation gate enhancement, task prioritization, cross-layer coherence checks, ritual integration.
- `/kb idea [text]`, `/kb develop [idea]` commands.
- `ideas/` directory in workspace layout (L1, L2, L3).
- `idea.md` template added to kb-management skill.
- `idea-create`, `idea-develop`, `idea-ship` log operations.
- Idea lifecycle management in kb-operator agent (Section 4).
- VMG-aligned evaluation gate scoring, goal status in rituals.
- `skills/kb-management/templates/report.html` — comprehensive slide-deck template with 12 slide types (Cover, Metrics, Progress, Decisions, Blocked, Ideas, Kanban, Daily Digest, Stakeholder Map, Pitch, Comparison, Closing), dark/light theme, slide engine with keyboard navigation, and sample data.
- Slide composition spec in `html-artifacts.md` — defines per-report-type slide recipes (Weekly Status, Daily Digest, Pitch, Roadmap Status, Topic Presentation) and ritual triggers for report generation.
- Stakeholder auto-update rule in `07-stakeholders.md` — agent detects relevance changes during processing and suggests updates to `stakeholders.md`.
- `stakeholder-update` log operation added to `logging.md`.

### Changed (continued)

- **Renamed `todo/` → `tasks/`** across entire spec. "todo" remains a recognized command synonym. Affects: `05-tasks.md` (renamed from `05-todos.md`), workspace-layout, commands, rituals, logging, glossary, skills, agent.
- `open-todos.html` → `open-tasks.html` in all artifact references.
- Evaluation gate (08) now offers idea creation at 1–2/5 when novelty detected, and checks VMG strategic alignment.
- Memory model (03) expanded from three to four types (added Incubation).
- Overview (01) renumbered principles 1–9, added Ideas (#4) and VMG (#5).
- Skills bumped to v2.2.0, agent bumped to v2.2.0.

### Version bumps

- Root `VERSION`: 2.1.0 → 2.2.0.
- `plugin.json`: 2.0.0 → 2.2.0.
- `skills/kb-setup/SKILL.md`: 2.1.0 → 2.2.0.
- `skills/kb-management/SKILL.md`: 2.2.0 (already bumped).
- `agents/kb-operator.md`: 2.2.0 (already bumped).

---

## [2.1.0] — 2026-04-18

### Added

- `docs/examples/first-hour.md` — zero-to-first-briefing walkthrough. Covers Stage 1 (marketplace install or `scripts/install`), Stage 2 (`/kb setup` wizard with suggested answers), Stage 3 (`/kb start-day`, `/kb <URL>`, `/kb end-day`), plus a failure-mode table pointing adopters back to the right doc/skill when any stage breaks.
- `skills/kb-setup/SKILL.md` — explicit "Scope boundary — install vs. init" section separating harness-level skill distribution (marketplace or `scripts/install`) from workspace-level KB scaffolding (this skill's job).
- `skills/kb-setup/SKILL.md` — "Placeholder → interview-answer mapping" table and a mandatory post-write `grep '{{[A-Z_0-9]*}}'` gate before the initial commit. A zero-hit scan is required; otherwise the skill halts and asks for the missing values.
- `docs/spec/setup.md` — mirror scope-boundary table; Step 5/6 rewritten to stop re-doing the installer's job.
- `docs/spec/ide-support.md` capability matrix — new row for the `kb-operator` Level-3 autonomous loop: native on Claude Code + OpenCode, not natively available in VS Code Copilot (cron fallback required). Linked from `agents/kb-operator.md` §Autonomous loop.
- `docs/roadmap.md` §Near-Term — "Auto-regeneration of always-current overviews" explicitly scheduled for v2.1, with Level-1/2/3 behavior and CI-diffable fixture as acceptance criteria.

### Changed

- `skills/kb-setup/SKILL.md` Step 1 prerequisites now **abort** when required tools (`git`, at least one harness CLI) are missing, with per-OS install commands. `gh` and SSH keys stay as warnings. No more "guide install if missing" half-measure.
- `docs/spec/html-artifacts.md` §Family 1 — clarified that automatic regeneration after every state-mutating `/kb` operation ships in v2.1. In v2.0 the reference implementation regenerates overviews on explicit invocation (`/kb present`, `/kb report`, `/kb end-day`, `/kb end-week`, `/kb status --refresh-overviews`). The Family 1 refresh-trigger column is now an aspirational contract until v2.1.
- `skills/kb-management/SKILL.md` — scope note matching the html-artifacts.md change. After a mutating operation, the skill **offers** the refresh instead of running it silently.
- `agents/kb-operator.md` §Artifact generation + §Autonomous loop — same scope split (v2.0 manual, v2.1 automatic); Level-3 loop no longer claims silent overview regeneration.

### Fixed

- CI: `markdown-lint` now passes on `main`. Disabled cosmetic `MD060`/`MD040`; added blank lines around headings and lists in `AGENTS.md`; escaped `|` inside table cells in `docs/glossary.md` and `docs/spec/workspace-layout.md`; removed the duplicate empty `[0.1.0]` heading in this file.
- CI: `consistency-and-versions` now passes on `main`. Added an `[Unreleased]` section as required by `scripts/check_consistency.py`.

### Version bumps

- Root `VERSION`: 2.0.0 → 2.1.0.
- `skills/kb-setup/SKILL.md`: 2.0.0 → 2.1.0.
- `skills/kb-management/SKILL.md`: 2.0.0 → 2.1.0.
- `agents/kb-operator.md`: 2.0.0 → 2.1.0.
- `docs/spec/setup.md`: 0.1 → 0.2.
- `docs/spec/html-artifacts.md`: 0.2 → 0.3.
- `docs/spec/ide-support.md`: 0.2 → 0.3.
- `docs/roadmap.md`: 2.0 → 2.1.

---

## [2.0.0] — 2026-04-18

### Changed

- Moved `examples/html/overview.html` to `index.html` at repo root — serves as GitHub Pages landing page and is easy to find/open locally.
- Added `index.html` template to kb-management skill — every generated KB gets a root index linking to reports, decisions, and todos.
- Updated all internal references and relative links accordingly.
- Version bump to 2.0.0 for initial public release.

---

## [0.2.0] — 2026-04-18

### Added

- **Always-current HTML overviews** regenerated after every state-mutating `/kb` operation: `inventory.html` (configured layers + external sources + workstreams + marketplace), `open-decisions.html`, `open-todos.html`, `index.html`. Watermark: `latest · YYYY-MM-DD HH:MM`. Spec: `docs/spec/html-artifacts.md` §"Family 1".
- **Daily summary** as a historical finding — generated by `/kb end-day`: `_kb-references/findings/YYYY-MM-DD-daily-summary.md` + rendered `_kb-references/reports/daily-YYYY-MM-DD.html`. Back-filled from the log if end-day was skipped.
- **Weekly summary** rendered artifact — paired with the existing weekly-summary finding: `_kb-references/reports/weekly-YYYY-WW.html`.
- `docs/overview.html` moved to `index.html` at repo root — self-contained one-page visual overview with SVG diagrams (five-layer architecture, memory model, multi-harness distribution), light + dark themes, watermark, changelog appendix.

### Changed

- **Harness compliance refactor** after verifying current docs for Claude Code, VS Code Copilot Chat, and OpenCode:
  - Moved marketplace manifest to `.claude-plugin/marketplace.json` at repo root (Claude Code spec).
  - Per-plugin manifest is now `<plugin>/.claude-plugin/plugin.json` with `name` / `version` / `description`.
  - Dropped `.opencode-plugin/` (not an OpenCode path) — real OpenCode layout is `.opencode/{skills,agents,commands}/`.
  - Agent files renamed from `<name>.agent.md` to `<name>.md` (cross-agent compatible; VS Code installer renames on copy).
  - Installer `scripts/install.py` rewritten: correct per-harness paths (`.claude/`, `.opencode/`, `.github/`), fallback global paths (`~/.claude/`, `~/.config/opencode/`, `~/.copilot/`), explicit `--target` options.
  - Added top-level `plugin.json` for VS Code Agent Plugin install via `chat.plugins.marketplaces`.
- Docs rewritten for reality: `docs/spec/marketplace-and-skills.md` v0.2, `docs/spec/ide-support.md` v0.2.
- Every ritual and every state-mutating command now regenerates live overviews as its last step.
- `docs/spec/commands.md` + `docs/spec/rituals.md` updated to reflect daily-summary generation in `end-day` and overview regeneration.
- `docs/concept/03-memory-model.md` updated: daily + weekly summaries are first-class historical findings.
- `scripts/check_consistency.py` forbidden-term list externalized to optional `.forbidden-terms.txt` (gitignored) — the spec itself no longer lists organization-specific terms.
- `README.md` trimmed and restructured around Problem → Solution → Install.

### Fixed

- Removed the one remaining internal-vocabulary reference ("Lane 2") from `docs/concept/06-workstreams.md`.
- `scripts/check_html_artifacts.py` theme-marker regex loosened to accept `[data-theme="light"]` / `[data-theme="dark"]` CSS selectors (the common idiomatic form).

---

## [0.1.0] — 2026-04-18

### Added

- Initial concept docs (`docs/concept/`): overview, architecture (5 layers), memory model, decisions, todos, workstreams, stakeholders, evaluation gate, flows, external links.
- Initial spec docs (`docs/spec/`): workspace layout, commands, rituals, automation levels, setup, marketplace + skills (multi-harness), IDE support, HTML artifacts (presentations + reports), file formats, security/privacy, logging.
- OSS scaffolding: `LICENSE` (Apache-2.0), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `AGENTS.md`, `CODEOWNERS`, issue/PR templates, dependabot config.
- Lean CI (`.github/workflows/validate.yml`): markdown lint, dead-link check, consistency + version sync check, HTML validation hook.
- Reference implementation: `skills/kb-management`, `skills/kb-setup`, `agents/kb-operator.md`; generator at `scripts/generate_plugins.py`; cross-harness installer at `scripts/install`.
