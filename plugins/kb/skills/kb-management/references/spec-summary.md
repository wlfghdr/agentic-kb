# Spec Summary — for the kb-management skill

Condensed runtime reference for the skill. For the full spec, see `docs/REFERENCE.md`.

## Layer graph

- A workspace declares a named `layers:` list in `.kb-config/layers.yaml`.
- One layer is the `workspace.anchor-layer`.
- Each layer declares `scope`, `role`, `parent`, `path`, `features`, and optional `marketplace` or `connections`.
- `promote` walks upward through `parent`.
- `digest` walks downward from parent layers or reads declared `connections`.
- `role: consumer` means read-down only; promote or publish must refuse.

## Anchor layer layout

```text
anchor-layer/
├── .kb-config/
│   ├── layers.yaml
│   ├── automation.yaml
│   └── artifacts.yaml
├── _kb-inputs/
│   └── digested/YYYY/MM/
├── _kb-references/
│   ├── topics/
│   ├── findings/YYYY/
│   ├── foundation/
│   ├── strategy-digests/YYYY/
│   ├── legacy/
│   └── reports/
├── _kb-notes/YYYY/
├── _kb-ideas/
│   └── archive/YYYY/
├── _kb-decisions/
│   └── archive/YYYY/
├── _kb-tasks/
│   ├── focus.md
│   ├── backlog.md
│   └── archive/YYYY/
├── .kb-log/YYYY-MM-DD.log
├── .kb-scripts/
├── _kb-workstreams/
├── index.html
└── dashboard.html
```

## Shared contributor layer layout

```text
shared-layer/
├── _kb-decisions/
├── _kb-tasks/
├── _kb-notes/
├── _kb-references/foundation/
├── alice/
│   ├── _kb-inputs/digested/YYYY/MM/
│   └── _kb-references/{topics,findings}/
└── bob/
```

## Key config shape

```yaml
workspace:
  root: /path/to/workspace
  user: alice
  anchor-layer: alice-personal
  aliases: { personal: alice-personal, team: team-observability }

layers:
  - name: alice-personal
    scope: personal
    role: contributor
    parent: team-observability
    path: .
    features: [inputs, findings, topics, ideas, decisions, tasks, notes, workstreams, foundation, reports]
    workstreams:
      - { name: platform-signals, themes: [caching, reliability, observability] }
  - name: team-observability
    scope: team
    role: contributor
    parent: null
    path: ../team-observability
    features: [findings, topics, decisions, tasks, notes, foundation, reports]
    contributor-mode:
      notes: shared
```

## Log line format

```text
HH:MM:SSZ | <op> | <scope> | <target> | <details>
```

Ops include: `capture`, `digest`, `digest-connections`, `promote`, `publish`, `note`, `note-end`, `update-topic`, `task-add`, `task-done`, `decide`, `decide-resolve`, `audit`, `report`, `presentation`, `skipped`, `install`, `ritual-*`, `automation-failure`, `correction`.

Scopes are descriptive, not numbered: `personal`, `team`, `org-unit`, `company`, `workspace`, `personal→team`, `team→personal`, `team→company`, `marketplace`, `connections`.
