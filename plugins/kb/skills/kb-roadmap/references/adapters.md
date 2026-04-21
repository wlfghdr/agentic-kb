# Reference: source adapters

Adapters normalize heterogeneous plan and delivery sources into a common item shape. The skill ships a minimum neutral set; adopters can add more.

## Common item shape

Every adapter's `load(config)` returns a list of normalized items:

```python
@dataclass
class Item:
    kind: str                  # "plan" | "delivery"
    id: str                    # stable source-specific id
    title: str
    body: str | None
    status: str | None         # normalized: open | in-progress | closed
    author: str | None
    assignee: str | None
    labels: list[str]
    created_at: datetime | None
    updated_at: datetime | None
    closed_at: datetime | None
    hierarchy: list[str]       # e.g. ["Program", "Package", "Item"]
    source: str                # adapter name
    url: str | None
    raw: dict                  # adapter-specific original payload
```

## Shipped plan adapters

### `ticket-export-markdown`

Reads a directory of markdown files with YAML frontmatter. Each file is one ticket.

Expected frontmatter keys:

- `id` (required)
- `title` (required)
- `status`, `assignee`, `labels`, `created`, `updated`, `closed`
- `hierarchy`: list, e.g. `[Program, Package, Item]`

Config:

```yaml
plan-sources:
  - name: tickets
    adapter: ticket-export-markdown
    path: ../ticket-export
    filter:
      labels-any: [roadmap:active]
      status-exclude: [Closed, Won't Do]
    hierarchy: [Program, Package, Item]
```

### `milestone-markdown`

Reads one or more markdown files. Items are extracted from sections under a `## Milestones` heading, one bullet per milestone.

Config:

```yaml
plan-sources:
  - name: milestones
    adapter: milestone-markdown
    path: _kb-references/workstreams/*.md
```

## Cross-tracker parent linking

Roadmap items frequently live in more than one tracker: a high-level initiative in one tracker, and the concrete workstream issues in the team's GitHub repository. kb-roadmap attaches GitHub issues to their structural parent using two mechanisms (in order):

### 1. Body-reference linking (automatic)

When a Jira item's body contains `(#N)` references (for example `Workstream A (#27) — DONE`), every matching GitHub issue `#N` in the same scope is assigned that Jira item as its structural parent. Comments sections are ignored to reduce noise.

No configuration needed — this runs on every `/kb roadmap` call.

### 2. Label / title fallback mapping (adopter-configured)

For GitHub issues that are not yet cited from any Jira body, scopes can declare per-tracker fallback rules. The first matching rule wins; already-linked items are never overwritten.

```yaml
issue-trackers:
  - name: <github-tracker-name>
    adapter: github-issues
    config:
      repo: <owner/repo>
      parent-mappings:
        - when: { labels-any: [workstream:onboarding] }
          parent: <JIRA-KEY>          # the VI that owns this workstream
        - when: { title-matches: "SSO|OIDC" }
          parent: <JIRA-KEY>          # infrastructure VI for SSO-related issues
        - when:
            labels-all: [workstream:backend, tier-1]
          parent: <JIRA-KEY>
```

`when` supports:

- `labels-any`: OR — item matches if any listed label is present (case-insensitive).
- `labels-all`: AND — item matches only if every listed label is present.
- `title-matches`: regex tested against the item title (case-insensitive).

**Order the rules narrow-to-broad.** Parent resolution walks up through lane resolution (Initiative / Milestone / Theme), so assigning a parent initiative automatically places the GitHub issue under the correct swimlane.


## Shipped delivery adapters

### `git-repo`

Reads a git checkout. Emits delivery items for each signal configured.

Supported signals:

- `commits` — one item per commit in window
- `prs` — one item per merged PR in window (requires GitHub CLI `gh` on PATH)
- `tags` — one item per annotated tag in window
- `adrs` — one item per file matching `adr-glob` in window

Config:

```yaml
delivery-sources:
  - name: repo
    adapter: git-repo
    path: ../product-repo
    signals: [commits, prs, tags, adrs]
    adr-glob: docs/architecture/adr-*.md
    ignore-paths:
      - "package-lock.json"
      - "**/*.lock"
      - "CHANGELOG.md"
```

### `release-log`

Reads `CHANGELOG.md` or `RELEASES.md`. One item per release entry.

Config:

```yaml
delivery-sources:
  - name: releases
    adapter: release-log
    path: ../product-repo/CHANGELOG.md
```

## Writing a custom adapter

Drop a Python module at `<adopter-kb>/.kb-scripts/roadmap-adapters/<name>.py`. The skill discovers it when config references `adapter: <name>`.

```python
# .kb-scripts/roadmap-adapters/my-tracker.py
from kb_roadmap import Item

def load(config) -> list[Item]:
    # ... fetch + normalize
    return items
```

Contracts:

- `load` must be pure — no side effects on sources.
- `load` must be deterministic given the same inputs + config.
- `load` must never include credentials or tokens in `Item.raw`.

## Adapter discovery order

1. Built-in adapters (shipped with the skill)
2. Adapters in the adopter's `.kb-scripts/roadmap-adapters/`
3. Adapters in any team/org-unit KB referenced by `.kb-config/layers.yaml`

Collisions raise an explicit error — no silent override.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-22 | Replaced an internal example label with a generic one to keep the roadmap adapter reference vendor-neutral | Vendor-neutrality rescreen |
