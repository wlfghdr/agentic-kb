# Reference: journey artifact contract

## Inputs

- The configured `journeys.source-dir` directory tree (default `_kb-journeys/`).
- The `journeys:` block in `.kb-config/layers.yaml`.
- The `journeys-template:` block in `.kb-config/artifacts.yaml`.

## Outputs per `render` run

Under `journeys.output-dir + journeys.html-subdir` (default `_kb-journeys/html/`):

```
<html-subdir>/
├── index.html                    # cross-journey overview — from overview.md
├── shared.css                    # brand tokens merged with skill baseline
├── <journey-slug>.html           # per journey (and per sub-journey if split)
└── mocks/
    ├── index.html                # every extracted mock listed + linked
    └── <journey-id>_<slug>.html  # standalone page per mock
```

All files are overwritten on every render. Never hand-edit.

## `shared.css` emission

The baseline `templates/shared.css.hbs` ships with vendor-neutral tokens:

```css
:root {
  --bg: #0e141b;
  --surface: #16202a;
  --surface2: #1d2a36;
  --border: #2d3d4d;
  --text: #eef4f8;
  --text-dim: #9aaebd;
  --accent-1: #66e3a4;
  --accent-2: #28b8c7;
  --accent-3: #6f8cff;
  --warn: #ffb84d;
  --risk: #ff6b6b;
}
```

When `.kb-config/artifacts.yaml` `journeys-template.tokens` is set, the renderer reads the adopter's CSS file, extracts the `:root` block(s), and **replaces** the baseline block. Everything else (layout, nav, cards, chips, print CSS) stays intact.

Tier and readiness chips are configured via `.kb-config/layers.yaml` `journeys.tiers` and `journeys.readiness-levels`. The renderer emits CSS classes per configured tier and readiness level, using the color tokens declared in `journeys.tiers[].color-token`.

## Per-journey HTML layout

Each `<journey-slug>.html` page has:

1. **Top nav** — links to every other journey and the overview, with tier-colored pill classes.
2. **View-mode toggle** — "Only Journey Description" | "Only Mocks" | "Show Both". Persists in `localStorage`.
3. **Header** — h1 from the markdown file, plus the metadata block rendered as grid cards (Persona, Entry Point, Value Proposition).
4. **Readiness strip** — tier-colored callout with target-duration + latest state marker.
5. **Step summary** — auto-generated ToC; every entry links to the step anchor.
6. **Flow** — each step rendered with id, actor chip, readiness chip, mock (with "↗ Open standalone" link), alternates.
7. **Interfaces** — the table rendered as a small graph.
8. **Footer** — watermark (version + last-updated) + theme toggle.

## Mock standalone pages

Every mock envelope becomes `<journey-id>_<slug>.html` in `mocks/`. Pages include:

- A crumb bar — "Overview · `<journey>` · `<mock-title>`" — with a "← Back to journey step" link to the originating anchor.
- The mock's container HTML, lifted verbatim from the journey file.
- Any `<style>` or `<script>` blocks nested inside the container.
- The shared.css stylesheet linked from the parent directory.

The mock's journey file is **patched in place** to inject an "↗ Open standalone" link into the mock header, pointing at the standalone page. The patch is idempotent — re-running the extractor updates the link, it does not duplicate.

## Mocks index

`mocks/index.html` lists every extracted mock, grouped by journey, with:

- Mock title + slug
- Source journey + step id (back-linked)
- Thumbnail or one-line description (extracted from the first `<h3>`/`<h4>` inside the container, or the container's `aria-label`)
- Standalone link

## Overview HTML

`index.html` renders from `overview.md` + the master journey map. Includes:

- Tier-grouped journey cards
- Persona → journey matrix
- Interface graph across all journeys
- Entry-point markers

## Watermark & versioning

Every generated page carries a `<meta name="generator" content="kb-journeys v<version>">` and a watermark string (footer + `<meta name="date">`) showing generation timestamp. Adopters can suppress the watermark via `.kb-config/artifacts.yaml` `watermark.enabled: false`.

## Idempotency

`render` is idempotent. Running twice with no source change produces byte-identical HTML. This makes git diffs on the generated HTML readable (only real changes show up).
