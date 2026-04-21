# Reference: Generated HTML roadmap — template contract

Every `/kb roadmap` run emits a **triple artifact** (`.md` + `.html` + `.json`) into `<output-dir>/<scope>/roadmap-<YYYY-MM-DD>.*`. This file documents the **HTML contract** — what sections must appear, how they are derived, and how adopters customize them without forking the renderer.

## Sections (required, in this order)

| # | Section id | Required | What it contains |
|---|-----------|----------|-------------------|
| 01 | `#overview` | yes | Hero banner (badge + title + subtitle + meta), chip strip (items · open · closed · in-delivery · shipped · GH milestones), and a short scope description. |
| 02 | `#timeline` | yes | Hierarchical **collapsible tree** timeline with one row per item along the full parent → child chain (e.g. `Theme → Initiative → Epic → GitHub workstream → GitHub issue → sub-issue`). Each row renders a bar spanning the target-quarter range of the item plus its descendants; color reflects the dominant phase. Controls (`Expand all` / `Collapse all` / `Lanes only` / `Lanes + Epics`, plus filter checkboxes for `show closed` / `show open`) appear above the timeline. Rows carry `data-state="open|closed"` so CSS can hide closed/open subtrees. The vertical `today-line` marks the current date. |
| 03 | `#landing-zones` | yes | Per-quarter drill-down cards. Each quarter card lists epics scheduled there plus GitHub-milestone rollups (native delivery landing zones) with `open` / `closed` counts and milestone due-date. Today's quarter is highlighted. |
| 04 | `#velocity` | yes | Velocity & forecast: burn-rate cards (closed in last 4w / 8w / 12w), issues/week 8-week average, ETA = `open ÷ weekly velocity` (guesstimate), plus per-lane open/closed breakdown with % done. |
| 05 | `#findings` | yes | Heuristic critical-path / discrepancy findings: overdue open items, container slippage (child target > parent target), unanchored GH issues, VIs with no GH implementation, GH-milestone vs Jira-parent quarter mismatches, critical-path current-quarter VIs sorted by % done. |
| 06 | `#kanban` | yes | One column per phase (`idea`, `defined`, `committed`, `in-delivery`, `shipped`, `archived`). **Container types (Theme, Initiative, Milestone) are excluded** — the board shows deliverables only. Cards show id · title · issue-type pill · target-quarter pill. |
| 07 | `#correlation` | yes | Tier-1 correlation matrix (items appearing in multiple trackers). Renders as a collapsible `<details>` block. |
| 08 | `#plan` | yes | Full plan table: id · title · type · phase · status · target · lane/milestone · tracker. Collapsible. |
| 09 | `#forward` | yes | Forward-plan callout pointing to `/kb roadmap refine <scope>` and `/kb roadmap audit`. |
| 10 | `#decisions` | yes | Decision callout. Populated from `_kb-decisions/D-*.md` once resolved against this scope. |

**Hard rule:** no roadmap artifact ships without sections 02 (timeline) and 03 (kanban). If the renderer cannot produce a timeline (no items with quarter metadata at all), it still emits the quarter axis centred on today with an empty track row labeled "no dated items". If the kanban would be entirely empty the renderer emits one `<div class="kanban-empty">` per column — never hides the section.

## Derivation rules

### Timeline swimlanes
- Items with a `parent` (milestone/theme id) → grouped under that parent's lane, labeled with the parent's title.
- Items that are themselves a `Milestone` / `Theme` → their own lane, labeled with their own title.
- Items with neither → an `Unscheduled` lane pinned to the bottom.
- Lane order: earliest target quarter first, `Unscheduled` last.

### Timeline bars
- Within each lane, items are bucketed by `phase`. Each phase with at least one item emits one bar.
- Bar start = earliest `target_quarter` of items in that bucket.
- Bar end = latest `target_quarter` of items in that bucket.
- Items without `target_quarter` are placed in the current quarter (today column) so they remain visible.
- Bar tooltip shows `<lane> · <phase> · <count> item(s)`.

### Quarter axis
- If `scopes.<name>.timeline.start` + `.end` are set, the axis spans that explicit range (capped at 8 quarters for layout).
- Otherwise it spans `min(item.target_quarter)` .. `max(item.target_quarter)`.
- Axis is always widened to include today ± 0 quarters.

### Kanban columns
- Columns are a fixed ordered list: `idea`, `defined`, `committed`, `in-delivery`, `shipped`, `archived`.
- A column renders at most 12 cards; if more exist, it shows `+N more in plan table`.
- Cards are sorted by `(target_quarter, id)` — earliest targets surface first.

### Phase mapping
Driven entirely by `roadmap.phases` in `.kb-config/layers.yaml`. The renderer never hard-codes status names. If an item's status does not appear in any phase list, it falls into `idea` (with an info note in the generated `.md`).

## Adopter customization (no fork required)

### 1. Brand tokens
`.kb-config/artifacts.yaml`:
```yaml
html-template:
  tokens: path/to/brand-tokens.css   # spliced verbatim into the HTML <style> block
  logo:
    light: path/to/logo-light.svg
    dark:  path/to/logo-dark.svg
```

The renderer's CSS defines the semantic tokens (`--bg`, `--surface`, `--accent-*`, `--phase-*`, `--text-dim`, etc.) with sensible dark + light defaults. Brand tokens override only what they override — there is no expectation that adopters redefine every variable.

### 2. Scope labels + descriptions
`.kb-config/layers.yaml` → `roadmap.scopes.<name>.label` + `.description` populate the hero banner. Markdown is **not** rendered — these are plain-text fields, HTML-escaped at render time.

### 3. Timeline window
`.kb-config/layers.yaml` → `roadmap.scopes.<name>.timeline.{start,end}` pins the quarter range regardless of item metadata. Useful when planning forward of all currently-tracked work.

### 4. Phase vocabulary
Adjust `roadmap.phases` to match the tracker's workflow. Column labels in the kanban are driven by the keys (`idea`, `defined`, …); the mapping values list every status string that maps into that key.

## What adopters do **not** customize

To keep artifacts comparable across scopes and KBs, these are deliberately not configurable:

- Section order and ids (navigation stability).
- The six phase keys (the ladder is a load-bearing concept across kb-roadmap · kb-journeys · kb-management).
- Data-attribute hooks (`data-phase`, `data-theme`) — the theme toggle and print/export scripts rely on them.
- The chip-strip summary metrics — they feed into `/kb status` and the cross-primitive audit.

If a customization would require changing any of the above, open an agentic-kb issue rather than patching the renderer. The goal is one generator producing comparable reports across every adopter KB.
