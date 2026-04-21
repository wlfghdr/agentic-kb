# Reference: `/kb journeys` command reference

## Base command

```
/kb journeys
```

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

1. Audit the source tree. Abort if structural errors.
2. Read `.kb-config/artifacts.yaml` `journeys-template.tokens`, emit `shared.css`.
3. Render each journey markdown → HTML via `templates/journey.html.hbs`.
4. Render `overview.md` → `index.html`.
5. Run mock extractor.
6. Update state markers in the changelog appendix.

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
