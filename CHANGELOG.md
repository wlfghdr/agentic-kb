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

**Document-level versioning**: each spec document (`docs/spec/*.md`, `docs/concept/*.md`) carries its own `Version` field in its frontmatter or first heading, plus a `## Changelog` section at the bottom. The root-level `VERSION` file and this `CHANGELOG.md` track the aggregate framework version.

---

## [Unreleased]

### Changed

- `README.md` — replaced `<org>` placeholders with actual repo URL (`wlfghdr/agentic-kb`). Restructured install section as "Getting started": marketplace-first flow (connect → `/kb setup`), cross-harness install script as optional secondary path.
- `README.md` — rewrote problem section as direct questions ("Does this sound familiar?"), renamed "The solution" → "How it works".
- `index.html` — intro now leads with the same user-facing questions; problem section renamed to "Why existing approaches fail".
- `docs/concept/02-architecture.md` — L3 now has team-isolated directories (mirroring L2's person-directories). L5 clarified as reference-only (no bottom-up input). Added contributor-unit / cross-analysis summary to the ASCII diagram.
- `docs/spec/workspace-layout.md` — L3 directory layout updated with per-team `inputs/` + `outputs/` structure. Required-files table updated.

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
- **Daily summary** as a historical finding — generated by `/kb end-day`: `references/findings/YYYY-MM-DD-daily-summary.md` + rendered `references/reports/daily-YYYY-MM-DD.html`. Back-filled from the log if end-day was skipped.
- **Weekly summary** rendered artifact — paired with the existing weekly-summary finding: `references/reports/weekly-YYYY-WW.html`.
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
