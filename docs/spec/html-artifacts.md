# HTML Artifacts — Overviews, Reports, Presentations

> **Version:** 0.3 | **Last updated:** 2026-04-18

HTML artifacts fall into two families:

1. **Always-current overviews** — snapshots of the current KB state. Overwritten, not versioned. Dashboards for "what does this KB look like right now".
2. **Historical artifacts** — dated, immutable, versioned. Presentations, reports, pitches, daily summaries, weekly summaries.

Both families share the same visual contract (self-contained, light + dark, watermark, CI-validated). They differ only in lifecycle: overviews overwrite themselves; historical artifacts never do.

> **v2.0 scope — manual regeneration.** The v2.0 reference implementation regenerates artifacts **on explicit `/kb present` / `/kb report` invocation** and on the two ritual commands (`/kb end-day`, `/kb end-week`). Automatic regeneration after every state-mutating `/kb` operation is specified below but ships as part of **v2.1** (see [roadmap.md](../roadmap.md) §Near-Term). Until v2.1, the "refresh trigger" column below is a target contract — not a guarantee. Users who want fresh dashboards between rituals run `/kb status --refresh-overviews` (or accept the suggested refresh that the skill offers after each mutation, when automation level ≥ 2).

The **default template is not part of this spec** — the reference implementation ships a plain accessible base; organizations contribute branded templates to their marketplace. This doc specifies the behavior, not the visual style.

## Family 1 — Always-current Overviews

These artifacts are snapshots of the current KB state. They overwrite in place, carry a **timestamp watermark** rather than a version number (the "version" is implicitly *latest*), and — **from v2.1 onward** — are regenerated automatically after any state-mutating `/kb` operation. In v2.0, regeneration is triggered by `/kb status --refresh-overviews`, the two ritual commands, or `/kb present` / `/kb report`.

| File | Source of truth | Refresh trigger |
|------|-----------------|-----------------|
| `references/reports/inventory.html` | `.kb-config.yaml` + `references/foundation/sources.md` + git status per configured layer | Every processing operation |
| `references/reports/open-decisions.html` | `decisions/active/*.md` across all configured layers | Every `decide`, `decide-resolve`, digest, or capture that advances a decision |
| `references/reports/open-todos.html` | `todo/focus.md` + `todo/backlog.md` across all configured layers | Every `todo-add`, `todo-done`, capture that adds TODOs, or ritual |
| `references/reports/index.html` | Chronological list of all artifacts in `references/reports/` | Every artifact create/update |

### `inventory.html` — what's in your KB ecosystem

One page that answers *"what repos and external sources does this KB process, and how are they doing?"*

Sections:

1. **Local layers** — one row per configured KB layer (personal, team(s), org-unit, marketplace). Columns: path, role, last-processed commit (watermark), pending `inputs/` count, uncommitted changes.
2. **External sources** — one row per entry in `references/foundation/sources.md`. Columns: alias, kind (repo / dashboard / website / cmdb / …), URL, last-checked timestamp, reachability status.
3. **Workstreams** — one row per `workstreams/*.md`. Columns: name, themes, active decisions count, recent activity.
4. **Marketplace** — installed skills + agents + their versions.

### `open-decisions.html` — everything waiting for a choice

One row per file in `decisions/active/` across all layers. Columns:

- Decision ID
- Title
- Scope (personal / team / org-unit)
- Status (`gathering-evidence` / `under-discussion` / `proposed` / `decided` — with visual state indicator)
- Stakeholders (+ RACI outside personal)
- Due date (highlight **overdue** in red; **due within 7 days** in amber)
- Days since last evidence update

Sorted by due date ascending; overdue at top.

### `open-todos.html` — what to work on

Three clear sections:

1. **Focus** — the (max 3) items from `todo/focus.md` across all layers.
2. **Waiting** — external blockers, grouped by the stakeholder who owes something.
3. **Backlog** — grouped by workstream, then by staleness (newest first).

Recent completions (last 7 days) are shown in a collapsed "Recently done" accordion at the bottom.

### `index.html` — the artifact index

Chronological list of every `.html` file under `references/reports/`. Regenerated on every artifact create/update. Split into two sections:

- **Current overviews** (inventory, open-decisions, open-todos — the live set).
- **Historical artifacts** (daily, weekly, presentations, reports, pitches — newest first).

Each entry carries title, version or timestamp, generation date, one-line summary, and a direct link.

### Regeneration rules

- **Fast** — overview regeneration must complete in under a few seconds; it runs after *every* processing operation.
- **Idempotent** — same KB state must yield byte-identical HTML (deterministic generation).
- **Automation-level aware**:
  - Level 1: regenerate, but only if the user confirms (the agent offers after each processing step).
  - Level 2: regenerate automatically; bundle with the commit.
  - Level 3: regenerate automatically; include in the next scheduled commit/push cycle.
- **CI-validated** — overview HTML files pass the same validator as versioned artifacts (self-contained, both themes, accessible).

### Watermark for overviews

Overviews replace the `v{version}` part of the standard watermark with `latest`:

```
latest · {YYYY-MM-DD HH:MM}
```

The timestamp is the moment of last regeneration, in the user's local timezone.

## Family 2 — Historical Artifacts

These are **dated, immutable, versioned** HTML files. They form part of the historical memory alongside `references/findings/`.

| Kind | Command / Trigger | Filename pattern | Source markdown |
|------|-------------------|------------------|-----------------|
| Presentation | `/kb present [topic]` | `references/reports/<slug>-v<version>.html` | topic file + linked findings + decisions |
| Report | `/kb report [scope]` | `references/reports/<slug>-v<version>.html` | activity over time range |
| Pitch | `/kb present --pitch [topic]` | `references/reports/<slug>-pitch-v<version>.html` | topic + decision ask |
| **Daily summary** | `/kb end-day` (ritual) | `references/reports/daily-YYYY-MM-DD.html` | `references/findings/YYYY-MM-DD-daily-summary.md` |
| **Weekly summary** | `/kb end-week` (Friday 15:00) | `references/reports/weekly-YYYY-WW.html` | `references/findings/YYYY-MM-DD-weekly-summary.md` |

### Daily summary

Generated by the `end-day` ritual. If `end-day` is skipped, the next `start-day` generates the missing day's summary from the log + git diff before producing its briefing.

The markdown source lives in `references/findings/` — it is a finding, and participates in all the normal finding rules (immutable, referenced by topics, listed in digests).

Content sections (both in the markdown and in the rendered HTML):

1. **At a glance** — counts: findings captured, decisions opened/advanced/resolved, TODOs added/completed, items skipped by the gate.
2. **By workstream** — per-workstream activity, cross-workstream connections flagged.
3. **Decisions** — anything opened, advanced, or resolved today. Link to each decision file.
4. **TODOs** — completed today + new items.
5. **Promotions / digests** — what flowed up or down.
6. **Skipped (with rationale)** — gate rejections, one-line reason each.
7. **Stakeholder mentions** — who was referenced and why.

### Weekly summary

Generated by the `end-week` ritual (Friday 15:00 default). Composes the week's dailies, adds:

- Per-workstream progress delta.
- Promotion candidates (mature findings / topics ready to move up).
- Presentation candidates (upcoming meetings, accumulated evidence).
- Stale items (overdue decisions, stale backlog, untouched topics).

Both the markdown source (in `findings/`) and the rendered HTML (in `reports/`) are produced.

## Shared Contract for All HTML Artifacts

### 1. Subtle version (or `latest`) watermark

```
v{version} · {date}               # historical artifacts
latest · {YYYY-MM-DD HH:MM}       # always-current overviews
```

Rendered in a de-emphasized style — readable but not distracting.

### 2. Changelog appendix

Final slide (presentations) or final section (reports / summaries / overviews). For overviews, the appendix lists recent regenerations (last 10 timestamps, rolling window).

### 3. Light + dark theme with toggle

Every artifact ships both themes in one file. An in-page toggle switches between them. Default follows `prefers-color-scheme` unless configured otherwise.

### 4. Self-contained

All CSS, JS, and images inline or base64. No external runtime fetches. Artifact renders on a disconnected machine.

### 5. Accessibility

Semantic HTML, WCAG AA contrast, keyboard navigation, screen-reader-friendly labels.

### 6. Immutable vs mutable filenames

- **Historical artifacts**: filename includes version; regeneration produces a new file; old versions remain on disk.
- **Overviews**: stable filename; regeneration overwrites; previous state is in git history.

## Kinds of Artifacts (command surface)

| Kind | Command | Content source | Typical use |
|------|---------|----------------|-------------|
| Presentation | `/kb present [topic]` | Topic + linked findings + decision outcomes | Stakeholder pitch, architecture review, meeting prep |
| Report | `/kb report [scope]` | Activity over a time range, per workstream | Personal weekly review, team status, org-unit digest |
| Pitch | `/kb present --pitch [topic]` | Opinionated narrative with a decision ask | Leadership buy-in, resource request |
| Daily summary | automatic on `end-day` | Log + git diff for the day | Keeps the week navigable |
| Weekly summary | automatic on `end-week` (Fri 15:00) | Aggregation of dailies + trend analysis | Week-in-review, promotion planning |
| Overview (inventory / decisions / todos / index) | automatic after every mutation | Current state of configured layers | Dashboard — always reflects now |

## Mandatory Behaviors

### 1. Subtle Version Watermark on the Intro Slide

Every generated artifact carries, on its intro/title slide, a **subtle** watermark:

```
v{version} · {date}
```

Rendered in a de-emphasized style (smaller, lower contrast than the title) — readable but not distracting. The format is configurable via `.kb-artifacts.yaml` (see [setup.md](setup.md)).

### 2. Changelog Appendix

The final slide (for presentations) or the final section (for reports) is a **changelog appendix**:

```
## Changelog

| Version | Date | What changed |
|---------|------|-------------|
| 1.2 | 2026-04-18 | Added coordination-patterns evidence |
| 1.1 | 2026-04-15 | Revised governance proposal |
| 1.0 | 2026-04-10 | Initial generation from topic file |
```

The appendix is rendered subtly — it is there for audit, not for the primary audience. Presenters can hide it if the audience doesn't need it, but it stays in the generated file.

### 3. Light + Dark Theme with Toggle

Every artifact ships **both themes in one file**. An in-page toggle switches between them. Defaults can be configured (`auto` follows `prefers-color-scheme`; `light` or `dark` pins the default).

### 4. Self-Contained

Artifacts must be distributable as a single `.html` file:

- All CSS inline (or in a single embedded `<style>`).
- All scripts inline (or in a single embedded `<script>`).
- All images base64-encoded or hosted on a public CDN with a visible attribution.
- No external runtime fetches — if the artifact is opened on an airplane, it still renders.

### 5. Accessibility

Artifacts must pass basic accessibility checks:

- Semantic HTML (`<section>`, `<h1>`–`<h6>`, `<nav>`).
- Colour contrast sufficient in both themes (WCAG AA minimum).
- Keyboard navigation between slides.
- Screen-reader-friendly slide titles.

### 6. Versioning on Regeneration

When an artifact is regenerated (content changed, template updated, theme swapped), the version increments:

- **PATCH** (`1.0 → 1.1`) — prose edits, minor content changes.
- **MINOR** (`1.0 → 1.1`) — new slides added, structural additions.
- **MAJOR** (`1.x → 2.0`) — template changed, narrative restructured.

The previous version's changelog entries are preserved in the appendix. Older artifact files are NOT overwritten; they remain on disk (filename carries the version: `governance-framework-v1.0.html`, `governance-framework-v1.1.html`) unless the user explicitly cleans up.

## Configuration — `.kb-artifacts.yaml`

```yaml
styling:
  source: builtin                   # builtin | website | template
  reference-url: https://example.org/brand       # if source=website
  reference-file: ../styling/org-template.html   # if source=template
  themes: [light, dark]
  default-theme: auto               # auto | light | dark

watermark:
  enabled: true
  position: intro-slide             # intro-slide | every-slide
  format: "v{version} · {date}"
  style: subtle                     # subtle | normal

appendix:
  changelog: true
  sources: true                     # include list of source findings/topics
  hidden-by-default: false          # toggle to hide in presenter view

output:
  directory: references/reports
  filename-template: "{slug}-v{version}.html"

github-pages:
  enabled: false                    # see "Publishing via GitHub Pages" below
  branch: gh-pages
  index-file: index.html
```

## Output Location

- **Personal KB**: `references/reports/<slug>-v<version>.html`
- **Team KB**: `<contributor>/outputs/reports/<slug>-v<version>.html`
- **Org-Unit KB**: `reports/<slug>-v<version>.html`

## Publishing via GitHub Pages (Optional)

When the KB is hosted on GitHub, the agent suggests publishing artifacts via GitHub Pages. Setup:

1. Enable Pages on the repo (source: `gh-pages` branch, `/` root, or `main` branch `/docs` folder).
2. Configure `.kb-artifacts.yaml → github-pages.enabled: true`.
3. The agent, on `end-day` or `end-week`, offers to commit new artifacts and push to the Pages branch.
4. An `index.html` is maintained by the agent — a chronological list of published artifacts with title, version, date, and one-line summary.

### The Pages Index

```html
<!DOCTYPE html>
<html>
<head>
  <title>KB Artifacts — <user>/<repo></title>
  <!-- same styling as individual artifacts, in light+dark -->
</head>
<body>
  <h1>Published Artifacts</h1>
  <ul>
    <li>
      <a href="governance-framework-v1.1.html">Governance Framework</a>
      <span>v1.1 · 2026-04-18</span>
      <p>Proposal for five-layer governance across teams.</p>
    </li>
    <li>
      <a href="2026-w16-report.html">Weekly Report — 2026 W16</a>
      <span>v1.0 · 2026-04-18</span>
      <p>Cross-workstream summary for week 16.</p>
    </li>
  </ul>
</body>
</html>
```

The agent regenerates the index on every publish; manual edits to the index are overwritten.

### Branch Protection

If the Pages branch is protected, the agent opens a PR instead of pushing directly — same rule as any other branch-protected push (see [commands.md](commands.md) §Commit/Push/PR Offer).

## CI Validation

Artifacts are **code**. CI validates them like any other code. The spec repo's reference CI (see `.github/workflows/validate.yml`) runs:

- **Syntactic HTML validity** — artifacts parse cleanly.
- **Self-contained check** — no external runtime fetches (beyond explicitly allowlisted CDNs).
- **Theme presence** — both `light` and `dark` stylesheets are embedded.
- **Watermark presence** — the configured watermark string is present on the intro slide.
- **Appendix presence** — the changelog section exists.
- **Accessibility lint** — headings are hierarchical, images have alt text, contrast ratios pass AA.

Consumer KB repos that publish artifacts are expected to run equivalent CI on their Pages branch.

## Daily-Business Suggestions

The agent watches for opportunities to suggest artifact generation:

| Trigger | Suggestion |
|---------|-----------|
| A TODO contains "present", "pitch", "demo", "share", "meeting prep" | *"Want me to generate a presentation draft for this?"* |
| A decision has been resolved and affects stakeholders | *"Generate a one-pager for @stakeholder about the outcome?"* |
| End of week | *"Want me to generate the weekly report?"* |
| A topic has accumulated ≥5 new findings since last artifact | *"The <topic> topic has moved — regenerate its artifact?"* |
| An org-level digest has been produced | *"Publish this as an HTML digest?"* |

## The Template Itself

The reference implementation ships a **plain** built-in template so the feature works out-of-the-box. Organizations that have a visual brand contribute their own template to their marketplace (or point the configuration at a website for style extraction).

**Important**: the visual template is NOT part of this spec repo. This repo defines only the contract (watermark, themes, appendix, self-contained, accessible, versioned). Branded templates belong in the marketplace.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | v0.3 — clarified that automatic regeneration of always-current overviews ships in v2.1; v2.0 reference implementation regenerates on explicit invocation (`/kb present`, `/kb report`, rituals, or `/kb status --refresh-overviews`) | Adopter feasibility review |
| 2026-04-18 | v0.2 — split into always-current overviews vs historical artifacts; added inventory.html, open-decisions.html, open-todos.html, index.html as live overviews; added daily + weekly summaries as historical findings with rendered HTML | New |
| 2026-04-18 | v0.1 — initial version | Spec bootstrapping |
