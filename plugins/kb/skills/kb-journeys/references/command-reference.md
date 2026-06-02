# Reference: `/kb journeys` command reference

> **Version:** 6.3.0 | **Last updated:** 2026-06-02

## Base command

```
/kb journeys
```

The behavioral spec below describes the intended `/kb journeys` surface. The shipped helper scripts in this repo currently cover `render` and `extract-mocks`, with no-extra-dependency fallback paths; the broader state-machine, authoring, and rename flows remain draft-spec behavior.

No-argument invocation. Runs the state machine: scan `journeys.source-dir`, compare against `journeys.output-dir`, report:

- Journeys unrendered (source newer than HTML)
- Mocks with missing standalone pages
- Audit failures since last run
- Steps without readiness chips
- Orphan mocks (standalone page exists but source envelope removed)

Picks the single highest-value next action and surfaces it.

## Subcommands

### `new [slug]`

```
/kb journeys new [--slug SLUG] [--tier TIER] [--phase PHASE]
```

Scaffolds a new journey markdown file from `templates/journey.md.hbs` under `journeys.source-dir/<slug>.md`. If the journey is tier-1 with multiple phases declared, scaffolds the directory form instead. Interactively prompts for persona, entry conditions, exit conditions, and initial step outline.

### `render`

```
/kb journeys render [--journey SLUG] [--dry-run]
```

Generates HTML set + mocks. Without `--journey`, renders all journeys. With `--dry-run`, prints what would be written without writing.

Steps:

1. Read `.kb-config/artifacts.yaml` `journeys-template.tokens`, emit `shared.css`.
2. Render each discovered journey markdown file (single-file roots plus directory `README.md` journeys) via `templates/journey.html.hbs`.
3. Render `overview.md` plus the discovered journey set into `index.html`.
4. Run mock extractor to refresh standalone mock pages and source-page backlinks.

If `python-markdown` or `beautifulsoup4` are absent, the shipped helper falls back to its built-in local renderer/extractor path instead of failing hard.

### `extract-mocks`

```
/kb journeys extract-mocks [--journey SLUG]
```

Runs the extractor only. Useful when only mock envelopes changed and the surrounding journey prose is stable.

### `audit`

```
/kb journeys audit [--journey SLUG] [--resolve VIOLATION-ID --action ACTION] [--apply]
```

Runs the canonical J1-J19 audit defined in [`references/audit.md`](./audit.md). Without `--resolve`, it scans journey sources, generated mocks, overview metadata, roadmap citations, ownership metadata, and configured actors, then emits the triple artifact:

- `_kb-journeys/audit-<YYYY-MM-DD>.md`
- `_kb-journeys/audit-<YYYY-MM-DD>.html`
- `_kb-journeys/audit-<YYYY-MM-DD>.json`

The audit covers:

- J1/J2 — metadata and required section integrity
- J3/J4/J5 — step id format, collisions, and rename safety
- J6/J7/J8 — readiness and configured actor coverage
- J9/J10/J11/J12 — mock envelope and standalone mock integrity
- J13/J14 — interface and cross-reference resolution
- J15/J16 — roadmap citation and coverage checks when roadmap links are configured
- J17/J18/J19 — overview drift, ownership metadata, and unused configured actors

Resolution mode applies one offered correction from the last audit report. Source edits, config edits, tracker writes, and id rewrites keep their normal safety gates; `rename-id` and tracker writes require `--apply`.

Policy knobs live under `journeys.audit` in `.kb-config/layers.yaml`: `readiness-required`, `interface-resolution`, `orphan-mocks`, `max-violations-per-class`, and `severity-gate`.

Exit codes:

| Code | Meaning |
|---|---|
| 0 | No violations, or only warnings below `severity-gate` |
| 1 | Config error or unreadable journey source |
| 2 | Violations exceed `severity-gate` |
| 3 | User deferred one or more resolutions without completing |

### `ideate | discuss | review | refine`

Shared authoring arc. See `references/authoring.md` for journey-specific stance rules; shared contract in `kb-roadmap/references/authoring-commands.md`.

```
/kb journeys ideate [--from SEED] [--persona NAME]
/kb journeys discuss <journey-slug-or-step-id> [--write]
/kb journeys review <journey-slug> [--discuss-only]
/kb journeys refine <journey-slug> [--force]
```

### `rename-id`

```
/kb journeys rename-id <old-id> <new-id>
```

Rewrites every occurrence of a step id across journeys, overview, roadmap items, and KB cross-refs. Shows a diff preview; requires `--apply` to write. Not reversible beyond git.

## Exit codes

Command-specific contracts above take precedence when they are narrower, such as `/kb journeys audit`.

| Code | Meaning |
|---|---|
| 0 | Operation succeeded |
| 1 | Configuration error |
| 2 | Audit violations, source ingestion failure, or render failure |
| 3 | Command completed with unresolved warnings, deferred resolutions, or generated-artifact drift |
| 4 | User aborted an interactive prompt |

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-06-02 | Added required version/changelog metadata so plugin specs and references are covered by the consistency check | Issue #144 |
| 2026-05-25 | Aligned `/kb journeys audit` with the canonical J1-J19 audit reference, including resolution flags, triple artifacts, policy knobs, and exit codes | PR #141 review |
| 2026-05-08 | Clarified the shipped `render`/`extract-mocks` helper behavior, discovery rules, and optional dependency fallbacks | Integration pass |
