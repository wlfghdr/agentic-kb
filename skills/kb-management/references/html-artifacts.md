# HTML Artifact Generation — kb-management

Two families of artifacts:

1. **Always-current overviews** — regenerated after any state-mutating operation. Overwritten in place. No version number; timestamp watermark.
2. **Historical artifacts** — dated, immutable, versioned. Presentations, reports, pitches, daily + weekly summaries.

## Family 1 — Live overviews (auto-regenerated)

| File | Source of truth | Refresh trigger |
|------|-----------------|-----------------|
| `_kb-references/reports/inventory.html` | `.kb-config/layers.yaml` + `_kb-references/foundation/sources.md` + git status per layer | every mutation |
| `_kb-references/reports/open-decisions.html` | `_kb-decisions/*.md` across all layers | every mutation |
| `_kb-references/reports/open-tasks.html` | `_kb-tasks/focus.md` + `_kb-tasks/backlog.md` across all layers | every mutation |
| `_kb-references/reports/index.html` | chronological list of everything under `_kb-references/reports/` | every artifact create/update |

**Regenerate after**: `capture`, `review`, `promote`, `publish`, `digest`, `decide`, `decide-resolve`, `task-add`, `task-done`, `update-topic`, `audit`, and every ritual.

**Rules**:

- Deterministic (same state → byte-identical output).
- Fast (a few seconds max — runs after every operation).
- Bundled with the commit that triggered the change.
- Level 1: offer before regenerating. Level 2/3: silent.

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
6. **Versioned filenames** — `<slug>-v<major>.<minor>.html`. Regeneration writes a new file; does NOT overwrite old.

## Styling sources

Per `.kb-config/artifacts.yaml`:

- `source: builtin` — plain accessible template ships with the skill (`templates/artifact-base.html`).
- `source: website` — read the page at `reference-url`, derive colors/typography/spacing.
- `source: template` — use the HTML file at `reference-file` as base.

In all cases, build **both light and dark themes** into the output file with a toggle.

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

**Generator script**: `scripts/generate-index.py` — scans the repo for `.html` files, extracts titles from `<title>` tags, infers dates from filenames or git history, groups by category, and writes a self-contained `index.html` with Dynatrace/Strato design tokens and dark/light toggle.

**Auto-regeneration**: The root `index.html` MUST be regenerated after every operation that creates or modifies an HTML artifact:

- `/kb present`, `/kb report`, `/kb end-day`, `/kb end-week`
- Any Family 1 overview regeneration
- Any `/kb promote` that includes HTML files
- Manual trigger: `/kb status --refresh-overviews`

**Regeneration command**:

```bash
python3 scripts/generate-index.py REPO_ROOT --title "KB Name" --description "One-liner"
```

The generated `index.html`:

- Self-contained — Dynatrace design tokens, Inter font, dark/light toggle
- Groups artifacts by category (Reports, Strategy & Vision, Presentations, Journey Maps, Findings, Research, Prototypes & Mocks)
- Shows contributor badges for team KBs
- Displays creation dates (from filename pattern, git log, or mtime)
- Shows stats bar (total count, categories, contributors, latest date)
- Works on GitHub Pages with relative links

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
