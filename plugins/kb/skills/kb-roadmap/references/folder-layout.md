# Reference: folder layout and views

The skill emits into a dedicated `_kb-roadmaps/` folder at the adopter's KB root. This folder is a peer of `_kb-references/`, `_kb-decisions/`, `_kb-ideas/`, `_kb-tasks/` — not a subdirectory of reports — because roadmaps are a distinct primitive from strategic reports.

## Layout

```
my-kb/
├── _kb-roadmaps/                     # dedicated root
│   ├── <workstream-name>/            # per-workstream view (one dir per scope)
│   │   ├── roadmap-YYYY-MM-DD.md     # living roadmap (detail)
│   │   ├── roadmap-YYYY-MM-DD.html
│   │   ├── roadmap-YYYY-MM-DD.json
│   │   ├── status-YYYY-MM-DD.md      # short-form status (digest output)
│   │   ├── status-YYYY-MM-DD.html
│   │   └── status-YYYY-MM-DD.json
│   ├── exec/                         # cross-workstream roll-up
│   │   ├── roadmap-exec-YYYY-MM-DD.md
│   │   ├── roadmap-exec-YYYY-MM-DD.html
│   │   └── roadmap-exec-YYYY-MM-DD.json
│   ├── index.html                    # auto-generated; links to latest per scope
│   └── archive/                      # roadmaps older than retention window
```

## Two views

### Detail view (per workstream)

Default output of `/kb roadmap --scope <workstream>`. Seven sections A–G as declared in `artifact-contract.md` — full plan baseline, delivery baseline, correlation matrix, delta, mismatches, forward plan, decisions.

Optimized for the team driving that workstream: ticket-level detail, commit-level detail, correlation audit trail.

### Roll-up view (exec / C-level)

Output of `/kb roadmap --scope exec` (or any scope configured with `kind: roll-up` in `.kb-config/layers.yaml`). Different section set — optimized for a leadership audience reading across workstreams.

Sections:

| Section | Content | Aggregation |
|---|---|---|
| **X1. Portfolio state** | One card per workstream: status traffic light, top-3 in-flight items, % complete vs plan | Rolled up from each workstream's detail view |
| **X2. Momentum** | Delta summary per workstream: items shipped, items opened, net change | From delta sections |
| **X3. Risks** | Stalled items, execution risks, cross-workstream dependencies at risk | Aggregated from mismatches + stalled |
| **X4. Shifts** | Items moved between workstreams; scope changes; re-prioritizations | From plan-source diff over window |
| **X5. Scope changes** | Newly added or removed plan items with reason (or "reason unknown") | From plan-source diff, with audit trail |
| **X6. Decisions needed** | Open `_kb-decisions/` items across workstreams + gaps surfaced by the engine | Aggregated |
| **X7. Next period focus** | Top plan items per workstream for next window | From forward-plan sections |

Roll-up view deliberately **does not** include commit-level detail, per-ticket tables, or correlation-tier counts. Those live in the detail view one click away. The exec artifact links to each workstream's latest detail artifact under X1.

## Roll-up configuration

Roll-up scopes are declared in `.kb-config/layers.yaml`:

```yaml
roadmap:
  output-dir: _kb-roadmaps
  scopes:
    <workstream-name>:
      kind: detail
      plan-sources: [...]
      delivery-sources: [...]
    exec:
      kind: roll-up
      aggregates: [<workstream-a>, <workstream-b>, <workstream-c>]
      sections: [X1, X2, X3, X4, X5, X6, X7]   # all by default
      max-items-per-workstream: 3               # for X1, X7
```

Running `/kb roadmap --scope exec` iterates the `aggregates` list, loads each workstream's latest JSON sidecar (or generates fresh if `--fresh`), then composes the roll-up.

## Cadence (non-normative)

A common adopter pattern:

- **Status** (short-form) — weekly per workstream
- **Roadmap** (detail) — monthly per workstream
- **Roadmap exec** (roll-up) — monthly or per leadership rhythm

The skill does not enforce cadence. Adopters wire it through `.kb-automation.yaml` schedules or external CI.

## Folder naming convention

The skill uses `_kb-roadmaps/` by default. Adopters may override via `roadmap.output-dir`; the skill reads the configured value verbatim.

## Retention + archive

Files older than `roadmap.retention-days` (default 180) are moved to `<output-dir>/archive/` on the next run. The `index.html` always links to the latest file per scope; archive is a flat directory with date-prefixed filenames.
