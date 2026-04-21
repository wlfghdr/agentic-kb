---
name: kb-journeys
description: Author and publish user/customer/product journeys as living markdown with generated HTML views and standalone UI mocks. Journeys are hierarchical (journey → phase → sub-journey → step) with entry/exit conditions, interfaces, and readiness assessments. The skill ships authoring commands (ideate, discuss, review, refine) shared with kb-roadmap's contract, a neutral HTML template whose tokens are set by the adopter's `.kb-config/artifacts.yaml`, and a mock-extraction pipeline that renders every embedded UI mock as a linkable standalone page. Triggered by `/kb journeys` and journey-authoring phrases.
version: 0.1.0
status: draft
triggers:
  - "/kb journeys"
  - "/kb journey"
  - "user journey"
  - "customer journey"
  - "product journey"
  - "journey map"
  - "sub-journey"
  - "journey phase"
  - "journey mock"
tools: []
requires:
  - kb-management
author: agentic-kb contributors
homepage: https://github.com/wlfghdr/agentic-kb
license: Apache-2.0
---

# Skill: KB Journeys

Journeys describe how a persona moves through a product, service, or process — as a **hierarchy** (journey → phase → sub-journey → step) with explicit entry conditions, exit conditions, cross-journey interfaces, and readiness assessments per visible step. They are a first-class KB artifact, separate from roadmaps (plan↔delivery) and topics (positions).

This skill turns markdown journey specs into:

1. A **browsable HTML set** (one HTML per journey + an index) that respects the adopter's brand tokens.
2. An automatic **standalone-mock index** — every embedded UI or terminal mock is also rendered as its own page and back-linked.
3. A four-command authoring arc shared with `kb-roadmap`: `ideate`, `discuss`, `review`, `refine`.

## When to invoke

Invoke whenever the user:

- Types `/kb journeys` (optionally followed by `new`, `render`, `extract-mocks`, `audit`, `ideate`, `discuss`, `review`, `refine`).
- Describes a user flow, a phase map, an onboarding path, an incident response path, or any multi-step persona-centric narrative.
- Asks *"how does a user / customer / operator move through X?"*.

## Core rules (always apply)

1. **Markdown is the source of truth.** HTML is generated; never hand-edit the HTML.
2. **Every journey is self-contained.** Readable without loading any other journey, but with explicit `## Interfaces` to adjacent journeys.
3. **Every visible step has a stable id** (`J<journey>.<phase>-S<step>`, e.g. `J1.1-S3`). Ids do not change once assigned — they are link targets across the KB.
4. **Every visible step carries a readiness chip** — green / amber / red, with a one-line rationale. Journeys without readiness are draft only.
5. **Every embedded mock is extractable** — wrap in the mock envelope so the extractor can lift it out into a standalone page.
6. **Zero vendor strings.** Brand colors, fonts, logos come from the adopter's `.kb-config/artifacts.yaml`. The skill's template ships with neutral tokens.
7. **Dual output always.** Every `render` run emits the per-journey HTMLs + the mocks index in the same pass. They never drift.
8. **Journeys are ground truth for the roadmap.** When a scope in `kb-roadmap` declares `journey-refs` pointing here, every roadmap item is cross-checked against its cited step(s). Journey steps are the definition of what the product must do; roadmap items exist to move step readiness forward. A journey is **never** silently updated from roadmap findings — drift findings trigger `/kb journeys review <step>`, which is a deliberate authoring pass.
9. **Log every run** to `.kb-log/YYYY-MM-DD.log`.

## Hierarchy

```
Journey (tier N)
└── Phase (ordered)
    └── Sub-Journey (optional; a Phase may be a Sub-Journey directly)
        └── Step (Sn; has id, title, actor, artifact, readiness)
            └── Mock (0..N; extracted into standalone page)
```

Numbering reflects tier: `1.x` = tier 1, `2` = tier 2, etc. Sub-journeys within a phase get dotted suffixes (`1.4.2`). Steps use `-S<n>`.

## Directory contract (adopter's KB)

```
my-kb/
├── _kb-journeys/                        # configurable via journeys.output-dir
│   ├── <journey-slug>.md                # source of truth
│   ├── <tiered-journey>/                # if the journey has sub-journey files
│   │   ├── README.md
│   │   ├── <sub-journey-slug>.md
│   │   └── ...
│   ├── overview.md                      # master journey map (cross-journey)
│   ├── html/                            # generated; do not hand-edit
│   │   ├── index.html
│   │   ├── shared.css                   # emitted from .kb-config/artifacts.yaml tokens
│   │   ├── <journey-slug>.html
│   │   └── mocks/
│   │       ├── index.html
│   │       └── <journey>-<step>-<mock-slug>.html
│   └── scripts/
│       └── (optional adopter overrides)
└── .kb-log/YYYY-MM-DD.log
```

## Journey markdown contract

Every journey file opens with a metadata block and required sections. See `references/structure.md` for the full template.

```markdown
# <tier>.<phase> — <Journey Title>

> **Sub-Journey**: <one-line path summary>
> **Tier**: <tier label>
> **Target duration**: <duration>
> **Version**: <n.n> | **Last updated**: YYYY-MM-DD

## Entry Conditions
- ...

## Exit Conditions
- ...

## Interfaces
| Direction | Sub-Journey | What |
|-----------|-------------|------|
| OUT → | <slug> | ... |

## Flow

### Step 1: <title> · `J<tier>.<phase>-S1` · `[ACTOR]`
<description>

#### Readiness
<span class="status-chip feasible">green</span> — <one-liner>

#### Mock (optional)
<!-- mock-begin: <mock-slug> -->
<div class="mockup-block" data-mock="<mock-slug>">
  ... mock HTML ...
</div>
<!-- mock-end: <mock-slug> -->
```

## Commands

Full reference: `references/command-reference.md`.

| Command | Purpose |
|---|---|
| `/kb journeys` | Scan state; surface next action (unrendered journey, stale mock, missing readiness) |
| `/kb journeys new [slug]` | Scaffold a new journey markdown from the template |
| `/kb journeys render [--journey slug]` | Generate HTML set + mock index |
| `/kb journeys extract-mocks` | Refresh standalone mock pages only |
| `/kb journeys audit` | Validate structure, ids, readiness coverage, mock envelopes |
| `/kb journeys ideate \| discuss \| review \| refine [journey]` | Authoring arc — same stance contract as `kb-roadmap` authoring-commands |

## Configuration

Adopter config in `.kb-config/layers.yaml`:

```yaml
journeys:
  output-dir: _kb-journeys
  source-dir: _kb-journeys           # where the .md files live (can be same as output-dir)
  html-subdir: html
  mocks-subdir: html/mocks
  tiers:
    - { key: t1, label: "Individual", color-token: accent-1 }
    - { key: t2, label: "Team",       color-token: accent-2 }
    - { key: t3, label: "Enterprise", color-token: accent-3 }
  readiness-levels:
    - { key: feasible, label: "Green",  chip-class: "feasible" }
    - { key: partial,  label: "Amber",  chip-class: "partial" }
    - { key: blocked,  label: "Red",    chip-class: "blocked" }
  mock-envelope:
    begin-marker: "<!-- mock-begin: "
    end-marker:   "<!-- mock-end: "
    container-selector: ".mockup-block"
  include-terminal-anim: false        # opt-in: embeds shared-terminal-anim.js when mocks use terminal blocks
```

Styling in `.kb-config/artifacts.yaml`:

```yaml
journeys-template:
  base: kb-journeys/templates/journey.html
  tokens: <path to brand tokens CSS>    # reuses the adopter's existing brand tokens
  logo:
    light: <path>
    dark: <path>
  themes: [light, dark, auto]
```

The journey template reads the same tokens block as `kb-roadmap` (`--fg`, `--bg`, `--accent`, `--border`, tier color tokens). Adopters with a brand tokens file already configured for roadmaps get journey styling for free.

## References (load on demand)

- `references/structure.md` — full markdown contract: metadata block, required sections, step id scheme, readiness chips, mock envelope
- `references/authoring.md` — `ideate`/`discuss`/`review`/`refine` stance rules for journeys (shared contract with kb-roadmap, with journey-specific deltas)
- `references/artifact-contract.md` — HTML output shape, shared.css emission, mock index contract
- `references/mocks.md` — mock envelope, extraction, standalone-page layout
- `references/folder-layout.md` — `_kb-journeys/` layout
- `references/config-schema.md` — full `.kb-config/layers.yaml` `journeys:` block
- `references/command-reference.md` — subcommand details

## Templates

- `templates/journey.md.hbs` — single-journey markdown template
- `templates/journey-overview.md.hbs` — cross-journey overview template
- `templates/journey.html.hbs` — per-journey HTML template (neutral tokens; brand tokens merged from adopter's config)
- `templates/overview.html.hbs` — index/overview HTML template
- `templates/mock-standalone.html.hbs` — standalone mock page template
- `templates/shared.css.hbs` — base CSS; adopter's brand tokens block is inlined at render time

## Scripts

- `scripts/render_journeys.py` — markdown → HTML set (neutral baseline; brand tokens merged from `.kb-config/artifacts.yaml`)
- `scripts/extract_mocks.py` — standalone-mock pipeline (generalized from upstream inspiration in `bluebox/docs/journeys/scripts/extract-mocks.py`)

## Status

Draft (`v0.1.0`). Not scaffolded by default. Opt in by declaring `journeys:` in `.kb-config/layers.yaml` + `journeys-template:` in `.kb-config/artifacts.yaml`.
