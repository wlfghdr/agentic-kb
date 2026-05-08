# kb-journeys

Vendor-neutral skill for authoring and publishing user / customer / product journeys as living markdown with generated HTML views and standalone UI mocks.

Journeys are a first-class KB artifact:

- Hierarchical: **journey → phase → sub-journey → step**
- Every step has a stable id, an actor, a readiness chip, and (optionally) an extractable mock
- Every journey is self-contained but declares its interfaces to adjacent journeys

## Install

The skill ships with `agentic-kb`. Opt in by adding a `journeys:` block to your `.kb-config/layers.yaml` and a `journeys-template:` block to your `.kb-config/artifacts.yaml`. See the SKILL.md and `references/config-schema.md` for the full schema.

## Quick start

```bash
# Scaffold a new journey
/kb journeys new --slug 1-3-bugfix-loop --tier 1 --phase 3

# Render everything (HTML set + mocks index)
/kb journeys render

# Validate the source tree without writing
/kb journeys audit
```

## What you get

- `_kb-journeys/*.md` — source of truth
- `_kb-journeys/html/index.html` — overview with tier-grouped journey cards
- `_kb-journeys/html/<slug>.html` — one page per journey with view-mode toggle (description-only / mocks-only / both)
- `_kb-journeys/html/mocks/index.html` — every mock as a linkable standalone page
- `_kb-journeys/html/shared.css` — baseline CSS with your brand tokens merged in

## Authoring arc

`/kb journeys ideate` · `/kb journeys discuss` · `/kb journeys review` · `/kb journeys refine` — shared contract with `kb-roadmap`'s authoring commands, with journey-specific stance deltas. See `references/authoring.md`.

## Status

Draft (`v0.1.0`). Baseline contract stable. Adopters welcome.
