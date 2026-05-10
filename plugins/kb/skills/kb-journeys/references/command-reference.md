# Reference: `/kb journeys` command reference

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
/kb journeys audit [--journey SLUG]
```

Validates without writing:

- Metadata block parseable
- Required sections present and in order
- Step ids match pattern + unique
- Mock envelopes balanced + unique slugs
- Readiness coverage (warn only)
- Interface table rows reference existing journeys
- Cross-refs resolve

Exit code 0 on pass, 1 on fail. Useful as a CI gate.

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

| Code | Meaning |
|---|---|
| 0 | Operation succeeded |
| 1 | Configuration error |
| 2 | Audit failure |
| 3 | Render succeeded but warnings present (missing readiness, orphan mocks) |
| 4 | User aborted an interactive prompt |

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-08 | Clarified the shipped `render`/`extract-mocks` helper behavior, discovery rules, and optional dependency fallbacks | Integration pass |
