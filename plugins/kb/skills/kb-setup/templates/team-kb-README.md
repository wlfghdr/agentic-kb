# {{TEAM_NAME}} — Team KB

Shared knowledge base for the {{TEAM_NAME}} team, built on the `agentic-kb` specification.

## Structure

```
.
├── _kb-decisions/
│   ├── D-YYYY-MM-DD-slug.md  open decisions with RACIs
│   └── archive/
├── _kb-tasks/
│   ├── focus.md              team focus (with RACIs)
│   └── backlog.md
├── .kb-log/                  team processing log
└── <contributor>/
    ├── _kb-inputs/
    │   └── digested/YYYY-MM/
    └── _kb-references/
        ├── topics/           living team-facing positions
        └── findings/         dated analyses / reviews
```

## Contributor workflow

1. Drop inputs into your own `<contributor>/_kb-inputs/`.
2. `/kb review` in the team KB context — process to `_kb-references/`.
3. Cross-reference other contributors via `/kb sync team`.
4. Promote mature topics / findings up to org-unit via `/kb promote org`.

## Decisions & Tasks

Every team decision and task carries a RACI (Responsible, Accountable, Consulted, Informed).
