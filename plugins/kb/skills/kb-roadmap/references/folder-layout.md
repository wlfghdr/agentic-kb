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
│   ├── exec/                         # cross-workstream roll-up
│   │   ├── roadmap-exec-YYYY-MM-DD.md
│   │   ├── roadmap-exec-YYYY-MM-DD.html
│   │   └── roadmap-exec-YYYY-MM-DD.json
│   ├── index.html                    # auto-generated; links to latest per scope
│   └── archive/                      # reserved for future retention handling
```

## Two views

### Detail view (per workstream)

Default output of `/kb roadmap --scope <workstream>`. Seven sections A–G as declared in `artifact-contract.md` — full plan baseline, delivery baseline, correlation matrix, delta, mismatches, forward plan, decisions.

Optimized for the team driving that workstream: ticket-level detail, commit-level detail, correlation audit trail.

### Roll-up view (exec / C-level)

Output of `/kb roadmap --scope exec` (or any scope configured with `kind: roll-up` in `.kb-config/layers.yaml`). The shipped helper aggregates items from the configured `aggregates:` scopes and renders them through the same timeline / findings / status-board frame as a detail scope, with the roll-up scope name baked into the filename.

The broader leadership-specific `X1`–`X7` section split remains part of the draft behavioral target, but it is not a distinct helper-script layout in this repo yet.

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

Running `/kb roadmap --scope exec` iterates the `aggregates` list, loads each configured child scope through the same source-resolution path as a detail render, de-duplicates identical `(tracker, id)` pairs, then writes `roadmap-exec-YYYY-MM-DD.{md,html,json}` plus the refreshed root `_kb-roadmaps/index.html`.

## Cadence (non-normative)

A common adopter pattern:

- **Status** (short-form) — weekly per workstream
- **Roadmap** (detail) — monthly per workstream
- **Roadmap exec** (roll-up) — monthly or per leadership rhythm

The skill does not enforce cadence. Adopters wire it through `.kb-automation.yaml` schedules or external CI.

## Folder naming convention

The skill uses `_kb-roadmaps/` by default. Adopters may override via `roadmap.output-dir`; the skill reads the configured value verbatim.

## Retention + archive

The `archive/` directory is reserved for future retention handling. The shipped helper script does not currently move files automatically; it only refreshes `index.html` so the latest artifact per scope stays discoverable at a stable path.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-08 | Removed unimplemented `status-*` outputs and clarified the current helper-script behavior for roll-up scopes and root index generation | Integration pass |
