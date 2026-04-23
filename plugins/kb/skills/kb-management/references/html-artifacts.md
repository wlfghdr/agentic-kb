# HTML Artifact Generation — kb-management

Two families of artifacts:

1. **Always-current overviews** — regenerated after any state-mutating operation. Overwritten in place. No version number; timestamp watermark.
2. **Historical artifacts** — dated, immutable, versioned. Presentations, reports, pitches, daily + weekly summaries.

## Family 1 — Live overviews (auto-regenerated)

| File | Source of truth | Refresh trigger | Generator |
|------|-----------------|-----------------|-----------|
| `dashboard.html` (owner-facing command center) | `_kb-tasks/focus.md` + `_kb-tasks/backlog.md` + `_kb-inputs/` + `_kb-ideas/` + `_kb-decisions/` + `_kb-references/{topics,findings,reports,digests}/` + `_kb-workstreams/` + optional GitHub/Jira | every mutation | `scripts/generate-dashboard.py` |
| `index.html` (public GitHub Pages landing page — artifact inventory) | every `*.html` under the repo (deduped per `.kb-config/artifacts.yaml`) plus every `*.md` under `_kb-references/{findings,topics}/`, `_kb-ideas/`, `_kb-decisions/` (archived subdirs excluded) | every mutation | `scripts/generate-index.py` |

The dashboard is the single owner-facing surface for live state — it renders focus, backlog, pending inputs, active ideas, open decisions, topics, recent findings/digests/reports, workstreams, and optional GitHub/Jira panels. There are no separate `inventory.html`, `open-decisions.html`, or `open-tasks.html` files; the equivalent signals are panels inside `dashboard.html`.

**Regenerate after**: `capture`, `review`, `promote`, `publish`, `digest`, `decide`, `decide-resolve`, `task-add`, `task-done`, `update-topic`, `audit`, and every ritual.

**Rules**:

- Deterministic (same state → byte-identical output).
- Fast (a few seconds max — runs after every operation).
- Bundled with the commit that triggered the change.
- Regenerated automatically at every layer. Mention the refreshed paths in the operation summary, but do not make freshness depend on a follow-up confirmation.

**Watermark** uses `latest · {YYYY-MM-DD HH:MM}` instead of a version number.

## Family 2 — Historical artifacts

| Kind | Command / Trigger | Filename |
|------|-------------------|----------|
| Presentation | `/kb present [topic]` | `reports/<slug>-v<version>.html` |
| Report | `/kb report [scope]` | `reports/<slug>-v<version>.html` |
| Pitch | `/kb present --pitch [topic]` | `reports/<slug>-pitch-v<version>.html` |
| Daily summary | `/kb end-day` (automatic) | `reports/daily-YYYY-MM-DD.html` + finding `findings/YYYY-MM-DD-daily-summary.md` |
| Weekly summary | `/kb end-week` (Friday 15:00) | `reports/weekly-YYYY-WW.html` + finding `findings/YYYY-MM-DD-weekly-summary.md` |

**Daily + weekly summaries live as findings** (the markdown source). The HTML is a rendered presentation layer. Both are part of historical memory.

### Daily summary content

1. At a glance — counts (findings, decisions, todos, skipped).
2. By workstream — per-workstream activity + cross-workstream connections.
3. Decisions — opened / advanced / resolved.
4. TODOs — completed + new.
5. Promotions / digests — what flowed up or down.
6. Skipped — gate rejections with one-line reasons.
7. Stakeholder mentions.

### Weekly summary content

Aggregates the week's dailies + adds:

- Per-workstream progress delta.
- Promotion candidates (ready to move up).
- Presentation candidates (upcoming meetings, accumulated evidence).
- Stale items (overdue decisions, stale backlog, untouched topics).

### If `end-day` was skipped

Next `start-day` generates the missing day's summary from the log + git diff before producing its briefing.

## Trigger for on-demand presentations (Family 2)

The skill offers HTML artifact generation when:

| Signal | Suggestion |
|--------|-----------|
| TODO contains present / pitch / demo / share / slide / meeting prep | *"Want me to generate a presentation draft for this?"* |
| Decision resolved + affects stakeholders | *"Generate a one-pager for @stakeholder about the outcome?"* |
| End of week | *"Generate the weekly report?"* |
| Topic accumulated ≥5 new findings since last artifact | *"Regenerate the artifact for <topic>?"* |
| Org-level digest produced | *"Publish this as an HTML digest?"* |

## Commands

| Command | Output |
|---------|--------|
| `/kb present [topic/file]` | Presentation — slides |
| `/kb report [scope]` | Report — flowing document |
| `/kb present --pitch [topic]` | Pitch-style presentation (opinionated narrative + decision ask) |

## Mandatory contract

Every generated artifact:

1. **Self-contained** — no external runtime fetches (all CSS/JS inline or embedded).
2. **Light + dark theme** embedded, with an in-page toggle. Default theme per `.kb-config/artifacts.yaml`.
3. **Version watermark** on the intro slide / top of report — subtle, format: `v{version} · {date}`.
4. **Changelog appendix** — the final slide (presentation) or section (report) lists versions.
5. **Accessible** — semantic HTML, WCAG AA contrast, keyboard nav, alt text on images.
6. **Versioned, dated filenames** — default pattern `YYYY-MM-DD-<slug>-v<major>.<minor>.html` for any topic-bound artifact (presentations, reports, pitches). Regeneration writes a new file; does NOT overwrite old. Dateless filenames are permitted only for always-current Family-1 overviews (`index.html`, `dashboard.html`). The rule is **layer-agnostic** — same filename convention for personal, team, and org-unit KBs.
7. **Layer-agnostic styling** — the configured reference template in `.kb-config/artifacts.yaml` (`styling.reference-file`) is THE template for every Family-2 artifact in that layer. Never hand-roll a fresh palette or layout per run. If the user works in a workspace with multiple KB layers, each layer reuses its own configured template — but within one layer, every artifact looks like it comes from one brand.

## Styling sources

Per `.kb-config/artifacts.yaml`:

- `source: builtin` — plain accessible template ships with the skill (`templates/artifact-base.html`).
- `source: website` — read the page at `reference-url`, derive colors/typography/spacing.
- `source: template` — use the HTML file at `reference-file` as base.

In all cases, build **both light and dark themes** into the output file with a toggle.

### Corporate design contract (mandatory for every artifact)

`/kb present`, `/kb report`, `/kb-report`, `/kb end-day`, `/kb end-week`, and every Family 1 overview MUST reuse the CSS variables declared in the configured reference template. They MUST NOT invent a fresh palette per run.

Concrete rules every generator implements:

1. **Read `.kb-config/artifacts.yaml` first.** If `styling.source: template`, load the `reference-file`, parse its `:root` / `[data-theme="dark"]` / `[data-theme="light"]` blocks, and reuse those token values (`--*-bg*`, `--*-border*`, `--*-text*`, `--*-brand*`, semantic colors, radius, shadow). If `source: website`, reuse the token file generated at setup time. If `source: builtin`, use `templates/artifact-base.html`.
2. **Same tokens across all artifacts.** The root `index.html`, every presentation, every report, and every daily/weekly summary share the same token set — one visual system per KB. A user opening any two artifacts side by side sees a single brand.
3. **Both themes always.** Emit `[data-theme="dark"]` and `[data-theme="light"]` blocks, plus the keyboard-accessible toggle. Default theme per `artifacts.yaml → styling.default-theme`.
4. **Never hard-code hex values in generator logic.** Hex values belong in token blocks only. Report-specific components (metrics grid, changelog table) reference tokens via `var(--...)`.
5. **Failure mode.** If the reference template is missing, unreadable, or lacks both theme blocks, fall back to `builtin` AND warn the user in the generator output — never silently publish with the wrong brand.

## Output location

| Layer | Directory |
|-------|-----------|
| Personal KB | `_kb-references/reports/` |
| Team KB | `<contributor>/_kb-references/reports/` |
| Org-Unit KB | `reports/` |

Filename: `<slug>-v<version>.html` (per `.kb-config/artifacts.yaml → output.filename-template`).

## Versioning rules

- PATCH (1.0 → 1.1): prose edits, minor content changes.
- MINOR (1.0 → 1.1): added slides / structural additions.
- MAJOR (1.x → 2.0): template changed, narrative restructured.

The previous file remains on disk (different filename). Changelog appendix preserves entries across versions.

## Slide / section layout (presentation)

1. **Intro** — title, one-line abstract, watermark (`v<version> · <date>`).
2. **Problem** — the friction or gap this addresses.
3. **Pattern / Mechanism** — the approach.
4. **Evidence** — grounding in findings + decisions.
5. **Proposal / Ask** — what's being asked.
6. **Next Steps** — concrete follow-ups.
7. **Appendix — Changelog + sources**.

## Root artifact index (`index.html`)

Every KB layer MUST maintain a root `index.html` that indexes all HTML artifacts in the repository. This is the GitHub Pages landing page and the local entry point for browsing artifacts.

**Generator script**: `scripts/generate-index.py` — scans the repo for `.html` files, extracts titles from `<title>` tags, extracts a short "what is this" summary from the meta description / first heading / first paragraph, infers dates from filenames or git history, groups by category, deduplicates versioned artifacts, and writes a self-contained `index.html` (three-column table: Artifact | Summary | Meta) with neutral design tokens and a dark/light toggle.

### Index rules (all generators MUST implement)

1. **Pinned categories first** — configured via `index.pinned-categories` in `.kb-config/artifacts.yaml` (defaults: `Journey Maps`, `Roadmap & Status`). These always render at the top regardless of artifact recency.
2. **Remaining categories ordered by recency** — newest artifact in the category wins. A category with a 2026-04-18 item appears above one whose newest is 2026-04-01. Default: `index.category-order: recency`.
3. **Dedup versioned artifacts** — only the newest artifact per family is shown. Family key = directory + stem with trailing version/date markers stripped (`-v3`, `-v5`, `-2026-04-15`, `-draft`, `-final`, `-wip`). Variant markers like `-pitch`, `-exec`, `-presentation` are preserved so different derivative kinds stay separate. Older versions remain on disk. Disable with `index.dedup-versioned: false`.
4. **Hide referenced sub-pages** — when one indexed HTML links to another indexed HTML via a relative `href`/`src` (e.g. a journey map linking to its step pages), the linked sub-page is dropped from the index so only the hub is listed. An artifact that itself references other artifacts is always kept (two hubs cross-linking each other both stay visible). Disable with `index.drop-referenced-subpages: false`.
5. **Stale badge** — artifacts older than `index.stale-after-days` (default: `14`) get a `<span class="badge-stale">stale</span>` badge and a warning in the legend. The legend states the cutoff date explicitly.
6. **Legend block** — the generated index MUST include a visible legend line below the stats bar explaining the ordering, dedup, and stale rules, so any user opening the file understands the conventions.
7. **Neutral default theme** — when no `.kb-config/artifacts.yaml` is present, the generator ships a vendor-neutral token set (blue accent, purple badge, neutral surfaces). Consumers can override via the `styling.source: template` pointer to their own reference file to match a house style.
8. **Self-contained button glyphs** — theme toggle and any icons MUST use actual Unicode characters (e.g. `☾`, `☀`) in the HTML output, never escape sequences (`\u263E`) which render literally in markup contexts.

### Configuration contract (`.kb-config/artifacts.yaml`)

```yaml
styling:
  source: template                 # builtin | template | website
  reference-file: _kb-references/templates/house-style.html

index:
  stale-after-days: 14             # threshold for "stale" badge
  pinned-categories:               # always rendered first, in this order
    - Journey Maps
    - Roadmap & Status
  dedup-versioned: true            # collapse -v3, -v4, -v5 to latest
  drop-referenced-subpages: true   # hide leaf HTMLs that a hub HTML already links to
  category-order: recency          # recency | fixed
```

**Auto-regeneration with confirmation**: After every operation that creates or modifies an HTML artifact, the skill MUST **offer** to regenerate the affected layer's root `index.html` — and proceed only on user confirmation (unless automation level is `2` or `3` per `.kb-config/automation.yaml`, in which case it runs silently). Regeneration targets the repo that received the new artifact, not every layer in the workspace.

Triggers that prompt the offer:

- `/kb present`, `/kb report`, `/kb end-day`, `/kb end-week`
- Any Family 1 overview regeneration
- Any `/kb promote` that copies HTML files across layers (offer for both source and destination layer)
- Manual trigger: `/kb status --refresh-overviews` (repair/rebuild path; runs without prompting since it was explicitly invoked)

**Regeneration command**:

```bash
python3 scripts/generate-index.py REPO_ROOT --title "KB Name" --description "One-liner"
```

### Snapshot artifacts (cross-repo copies)

When an HTML artifact is **copied** from another repo for reference (e.g. pulling a journey map or roadmap from a product repo into a strategy KB), the copy MUST include a snapshot banner:

```html
<div style="position:fixed;top:8px;left:8px;z-index:99999;background:rgba(245,180,0,0.95);color:#1a1a1a;font:600 11px/1.4 -apple-system,sans-serif;padding:6px 10px;border-radius:6px;max-width:360px;">
  Content: {original-date-range} · Snapshot copied {YYYY-MM-DD} · Source: {source-repo-path}<br>
  <span style="font-weight:500;opacity:0.85;">⚠ May be out of date — see source for latest</span>
</div>
```

This makes it obvious to any reader that the file is a point-in-time copy, not the canonical source. The snapshot banner is separate from the stale-date heuristic in the index — they complement each other.

**For team/org-unit KBs**, the index scans all contributor directories and tags each artifact with a contributor badge.

## GitHub Pages publishing

If `github-pages.enabled: true`:

1. On `end-day` / `end-week`, offer to commit + push new artifacts to the Pages branch.
2. The root `index.html` serves as the GitHub Pages landing page — auto-regenerated on every artifact publish.
3. If branch protection on Pages branch: open a PR instead of pushing.

## CI validation

Artifacts are validated by `scripts/check_html_artifacts.py` in consumer repos. Keep the artifact format compatible with that validator.

## Base template

The base template (in `templates/artifact-base.html`) includes:

- `<style>` with CSS variables defined in both `[data-theme="light"]` and `[data-theme="dark"]`.
- `<script>` for the theme toggle (keyboard accessible).
- `<section>` elements per slide with semantic heading hierarchy.
- Watermark placeholder `{{WATERMARK}}`.
- Changelog appendix placeholder `{{CHANGELOG}}`.

The generator fills placeholders from `.kb-config/artifacts.yaml` + topic content.

### Presentation-grade template

For `/kb present` (and any slide-style report), the richer **`kb-setup/templates/presentation-template.html`** is the canonical starting point. kb-setup Q13 copies it into the adopter's KB under `_kb-references/templates/presentation-template.html` (or `<brand>-presentation.html` when a brand is supplied). It ships with:

- Dark + light theme token blocks (all customization points marked `CUSTOMIZE:`).
- Slide types: `.cover`, `.section-title`, `.content`, `.full-image`, `.closing`.
- Helpers: `.columns` / `.thirds`, `.card` variants, `.callout` variants, `.badge` variants, `.table-wrap`, `.metric-big`, `.img-placeholder`.
- Header with brand-logo slot and theme toggle.
- Cover slide with large visible brand-mark (`.bg-brand`), title, subtitle, and **exact creation timestamp** (`Created {{CREATED_DATE}} · {{CREATED_TIME}}`).
- Nav bar with keyboard shortcuts (←/→, Home, End, PgUp/PgDn, Space), progress bar, print CSS.
- Built-in appendix/changelog slide.

Every `/kb present` MUST use this file (as customized by Q13) rather than regenerating a fresh layout.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-23 | Family-2 filename default is now `YYYY-MM-DD-<slug>-v<major>.<minor>.html` across every KB layer; styling contract is explicitly layer-agnostic (configured reference template is THE template per layer); root-`index.html` regeneration is now an explicit offer-then-confirm step after every Family-2 create/update (automation levels 2/3 still run silently) | ISO 42001 presentation generation friction |
| 2026-04-22 | Root `index.html` source-of-truth row now lists findings/topics/ideas/decisions markdown alongside HTML artifacts, matching the shipped generator behavior | Fixes #21 |
| 2026-04-22 | Added topics to the dashboard Family-1 contract and source-of-truth table so living positions are visible alongside findings, ideas, and decisions | Fixes #22 |
| 2026-04-22 | Dropped the three phantom Family-1 overviews (`inventory.html`, `open-decisions.html`, `open-tasks.html`) that had no shipped generator; their signals already live in `dashboard.html` panels | Fixes #18 |
| 2026-04-20 | Clarified that automatic overview refresh runs at every layer, while `/kb status --refresh-overviews` remains a manual repair/rebuild trigger | v3.2.0 live-overview refresh |
